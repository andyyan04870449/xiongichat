"""
上傳處理服務
"""
import os
import uuid
import json
import csv
import mimetypes
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException
from PIL import Image
from PIL.ExifTags import TAGS

from app.database import get_db_context
from app.models.upload import UploadRecord, UploadStatus, UploadType, AuthoritativeMedia, AuthoritativeContacts
from app.models.knowledge import KnowledgeDocument
from app.services.embeddings import EmbeddingService
from app.services.chunker import DocumentChunker
from app.services.knowledge_manager import KnowledgeManager
from app.schemas.upload import (
    MediaUploadRequest, ContactsUploadRequest, ArticleUploadRequest, TextUploadRequest
)

logger = logging.getLogger(__name__)


class UploadService:
    """上傳處理服務"""
    
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        self.embedding_service = EmbeddingService()
        self.chunker = DocumentChunker()
        self.knowledge_manager = KnowledgeManager()
        logger.info("UploadService initialized")
    
    async def create_upload_record(
        self, 
        filename: str, 
        upload_type: UploadType,
        file_size: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UploadRecord:
        """建立上傳記錄"""
        try:
            async with get_db_context() as db:
                upload_record = UploadRecord(
                    filename=filename,
                    upload_type=upload_type,
                    status=UploadStatus.PENDING,
                    file_size=file_size,
                    metadata=metadata
                )
                db.add(upload_record)
                await db.commit()
                await db.refresh(upload_record)
                logger.info(f"Created upload record: {upload_record.id}")
                return upload_record
        except Exception as e:
            logger.error(f"Error creating upload record: {e}")
            raise HTTPException(status_code=500, detail="建立上傳記錄失敗")
    
    async def update_upload_status(
        self, 
        upload_id: uuid.UUID, 
        status: UploadStatus,
        error_message: Optional[str] = None,
        processing_log: Optional[Dict[str, Any]] = None
    ):
        """更新上傳狀態"""
        try:
            async with get_db_context() as db:
                await db.execute(
                    update(UploadRecord)
                    .where(UploadRecord.id == upload_id)
                    .values(
                        status=status,
                        error_message=error_message,
                        processing_log=processing_log,
                        updated_at=datetime.utcnow()
                    )
                )
                await db.commit()
                logger.info(f"Updated upload record {upload_id} status to {status}")
        except Exception as e:
            logger.error(f"Error updating upload status: {e}")
            raise HTTPException(status_code=500, detail="更新上傳狀態失敗")
    
    async def save_uploaded_file(self, file: UploadFile, upload_id: uuid.UUID) -> str:
        """儲存上傳檔案"""
        try:
            # 建立檔案路徑
            file_extension = Path(file.filename).suffix
            file_path = self.upload_dir / f"{upload_id}{file_extension}"
            
            # 重置檔案指標到開頭
            await file.seek(0)
            
            # 儲存檔案
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            logger.info(f"Saved file: {file_path}, size: {len(content)} bytes")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise HTTPException(status_code=500, detail="儲存檔案失敗")
    
    async def process_media_upload(
        self, 
        file: UploadFile, 
        upload_id: uuid.UUID,
        request: MediaUploadRequest
    ) -> AuthoritativeMedia:
        """處理媒體上傳"""
        try:
            # 更新狀態為處理中
            await self.update_upload_status(upload_id, UploadStatus.PROCESSING)
            
            # 儲存檔案
            file_path = await self.save_uploaded_file(file, upload_id)
            
            # 取得檔案資訊
            file_size = os.path.getsize(file_path)
            mime_type, _ = mimetypes.guess_type(file.filename)
            
            # 處理 EXIF 資料 (如果是圖片)
            exif_data = None
            if mime_type and mime_type.startswith('image/'):
                try:
                    with Image.open(file_path) as img:
                        exif_dict = img._getexif()
                        if exif_dict:
                            exif_data = {}
                            for tag_id, value in exif_dict.items():
                                tag = TAGS.get(tag_id, tag_id)
                                exif_data[tag] = str(value)
                except Exception as e:
                    logger.warning(f"Could not extract EXIF data: {e}")
            
            # 儲存到資料庫
            async with get_db_context() as db:
                media_record = AuthoritativeMedia(
                    upload_id=upload_id,
                    filename=file.filename,
                    file_path=file_path,
                    file_size=file_size,
                    mime_type=mime_type,
                    tags=request.tags,
                    description=request.description,
                    exif_data=exif_data
                )
                db.add(media_record)
                await db.commit()
                await db.refresh(media_record)
            
            # 建立 RAG 索引
            await self._create_media_rag_index(media_record)
            
            # 更新狀態為完成
            await self.update_upload_status(
                upload_id, 
                UploadStatus.COMPLETED,
                processing_log={"media_id": str(media_record.id)}
            )
            
            logger.info(f"Processed media upload: {media_record.id}")
            return media_record
            
        except Exception as e:
            logger.error(f"Error processing media upload: {e}")
            await self.update_upload_status(upload_id, UploadStatus.FAILED, str(e))
            raise HTTPException(status_code=500, detail=f"處理媒體上傳失敗: {str(e)}")
    
    async def process_contacts_upload_with_content(
        self,
        file_content: bytes,
        filename: str,
        upload_id: uuid.UUID,
        request: ContactsUploadRequest
    ) -> List[AuthoritativeContacts]:
        """處理聯絡人上傳（使用已讀取的檔案內容）"""
        try:
            # 更新狀態為處理中
            await self.update_upload_status(upload_id, UploadStatus.PROCESSING)
            
            # 儲存檔案
            file_path = self.upload_dir / f"{upload_id}.csv"
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"Saved file: {file_path}, size: {len(file_content)} bytes")
            
            # 解析 CSV 檔案
            contacts_data = await self._parse_contacts_file(str(file_path), request.field_mapping)
            
            # 儲存到資料庫
            contacts_records = []
            async with get_db_context() as db:
                for contact_data in contacts_data:
                    # 確保 organization 欄位存在
                    if 'organization' not in contact_data or not contact_data['organization']:
                        logger.warning(f"Skipping contact without organization: {contact_data}")
                        continue
                    
                    contact_record = AuthoritativeContacts(
                        upload_id=upload_id,
                        organization=contact_data['organization'],
                        phone=contact_data.get('phone'),
                        email=contact_data.get('email'),
                        address=contact_data.get('address'),
                        tags=contact_data.get('tags'),
                        notes=contact_data.get('notes')
                    )
                    db.add(contact_record)
                    contacts_records.append(contact_record)
                
                await db.commit()
                
                for record in contacts_records:
                    await db.refresh(record)
            
            # 建立 RAG 索引
            for contact_record in contacts_records:
                await self._create_contact_rag_index(contact_record)
            
            # 更新狀態為完成
            await self.update_upload_status(
                upload_id, 
                UploadStatus.COMPLETED,
                processing_log={'contacts_count': len(contacts_records)}
            )
            
            logger.info(f"Processed contacts upload: {len(contacts_records)} contacts")
            return contacts_records
            
        except Exception as e:
            logger.error(f"Error processing contacts upload: {e}")
            await self.update_upload_status(upload_id, UploadStatus.FAILED, str(e))
            raise HTTPException(status_code=500, detail=f"處理聯絡人上傳失敗: {str(e)}")
    
    async def process_contacts_upload(
        self, 
        file: UploadFile, 
        upload_id: uuid.UUID,
        request: ContactsUploadRequest
    ) -> List[AuthoritativeContacts]:
        """處理聯絡人上傳"""
        try:
            # 更新狀態為處理中
            await self.update_upload_status(upload_id, UploadStatus.PROCESSING)
            
            # 儲存檔案
            file_path = await self.save_uploaded_file(file, upload_id)
            
            # 解析 CSV/Excel 檔案
            contacts_data = await self._parse_contacts_file(file_path, request.field_mapping)
            
            # 儲存到資料庫
            contacts_records = []
            async with get_db_context() as db:
                for contact_data in contacts_data:
                    # 確保 organization 欄位存在
                    if 'organization' not in contact_data or not contact_data['organization']:
                        logger.warning(f"Skipping contact without organization: {contact_data}")
                        continue
                    
                    contact_record = AuthoritativeContacts(
                        upload_id=upload_id,
                        organization=contact_data['organization'],
                        phone=contact_data.get('phone'),
                        email=contact_data.get('email'),
                        address=contact_data.get('address'),
                        tags=contact_data.get('tags'),
                        notes=contact_data.get('notes')
                    )
                    db.add(contact_record)
                    contacts_records.append(contact_record)
                
                await db.commit()
                
                for record in contacts_records:
                    await db.refresh(record)
            
            # 建立 RAG 索引
            for contact_record in contacts_records:
                await self._create_contact_rag_index(contact_record)
            
            # 更新狀態為完成
            await self.update_upload_status(
                upload_id, 
                UploadStatus.COMPLETED,
                processing_log={"contacts_count": len(contacts_records)}
            )
            
            logger.info(f"Processed contacts upload: {len(contacts_records)} contacts")
            return contacts_records
            
        except Exception as e:
            logger.error(f"Error processing contacts upload: {e}")
            await self.update_upload_status(upload_id, UploadStatus.FAILED, str(e))
            raise HTTPException(status_code=500, detail=f"處理聯絡人上傳失敗: {str(e)}")
    
    async def process_article_upload(
        self, 
        file: UploadFile, 
        upload_id: uuid.UUID,
        request: ArticleUploadRequest
    ) -> KnowledgeDocument:
        """處理文章上傳"""
        try:
            # 更新狀態為處理中
            await self.update_upload_status(upload_id, UploadStatus.PROCESSING)
            
            # 儲存檔案
            file_path = await self.save_uploaded_file(file, upload_id)
            
            # 解析文件內容
            content = await self._extract_text_from_file(file_path)
            title = Path(file.filename).stem  # 使用檔名作為標題
            
            # 建立知識文件
            document = await self.knowledge_manager.add_document(
                title=title,
                content=content,
                source=request.source,
                category=request.category,
                lang=request.lang,
                published_date=request.published_date
            )
            
            # 更新狀態為完成
            await self.update_upload_status(
                upload_id, 
                UploadStatus.COMPLETED,
                processing_log={"document_id": str(document.id)}
            )
            
            logger.info(f"Processed article upload: {document.id}")
            return document
            
        except Exception as e:
            logger.error(f"Error processing article upload: {e}")
            await self.update_upload_status(upload_id, UploadStatus.FAILED, str(e))
            raise HTTPException(status_code=500, detail=f"處理文章上傳失敗: {str(e)}")
    
    async def process_text_upload(
        self, 
        upload_id: uuid.UUID,
        request: TextUploadRequest
    ) -> KnowledgeDocument:
        """處理文字上傳"""
        try:
            # 更新狀態為處理中
            await self.update_upload_status(upload_id, UploadStatus.PROCESSING)
            
            # 建立知識文件
            document = await self.knowledge_manager.add_document(
                title=request.title,
                content=request.content,
                source=request.source,
                category=request.category,
                lang=request.lang,
                published_date=request.published_date
            )
            
            # 更新狀態為完成
            await self.update_upload_status(
                upload_id, 
                UploadStatus.COMPLETED,
                processing_log={"document_id": str(document.id)}
            )
            
            logger.info(f"Processed text upload: {document.id}")
            return document
            
        except Exception as e:
            logger.error(f"Error processing text upload: {e}")
            await self.update_upload_status(upload_id, UploadStatus.FAILED, str(e))
            raise HTTPException(status_code=500, detail=f"處理文字上傳失敗: {str(e)}")
    
    async def _create_media_rag_index(self, media_record: AuthoritativeMedia):
        """為媒體建立 RAG 索引"""
        try:
            # 建立關鍵字摘要
            keywords = []
            if media_record.tags:
                keywords.extend(media_record.tags)
            if media_record.description:
                keywords.append(media_record.description)
            
            # 建立摘要文字
            summary_text = f"媒體檔案: {media_record.filename}"
            if keywords:
                summary_text += f" 標籤: {', '.join(keywords)}"
            if media_record.description:
                summary_text += f" 描述: {media_record.description}"
            
            # 建立知識文件 (用於 RAG 索引)
            document = await self.knowledge_manager.add_document(
                title=f"媒體: {media_record.filename}",
                content=summary_text,
                source="authoritative_media",
                category="media",
                lang="zh-TW"
            )
            
            logger.info(f"Created RAG index for media: {media_record.id}")
            
        except Exception as e:
            logger.error(f"Error creating media RAG index: {e}")
    
    async def _create_contact_rag_index(self, contact_record: AuthoritativeContacts):
        """為機構聯絡資訊建立 RAG 索引"""
        try:
            # 建立關鍵字摘要
            keywords = [contact_record.organization]
            if contact_record.tags:
                keywords.extend(contact_record.tags)
            
            # 建立摘要文字
            summary_text = f"機構聯絡資訊: {contact_record.organization}"
            
            # 添加聯絡方式說明（不直接包含實際號碼）
            contact_methods = []
            if contact_record.phone:
                contact_methods.append("提供電話聯絡")
            if contact_record.email:
                contact_methods.append("提供電子郵件")
            if contact_record.address:
                contact_methods.append("提供地址資訊")
            
            if contact_methods:
                summary_text += f" 聯絡方式: {'、'.join(contact_methods)}"
            
            if contact_record.notes:
                summary_text += f" 服務說明: {contact_record.notes}"
            
            if keywords:
                summary_text += f" 關鍵字: {', '.join(keywords)}"
            
            # 建立知識文件 (用於 RAG 索引)
            document = await self.knowledge_manager.add_document(
                title=f"機構聯絡資訊: {contact_record.organization}",
                content=summary_text,
                source="authoritative_contacts",
                category="contacts",
                lang="zh-TW"
            )
            
            logger.info(f"Created RAG index for contact: {contact_record.id}")
            
        except Exception as e:
            logger.error(f"Error creating contact RAG index: {e}")
    
    async def _parse_contacts_file(
        self, 
        file_path: str, 
        field_mapping: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """解析聯絡人檔案"""
        contacts_data = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # 嘗試自動偵測分隔符號
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row in reader:
                    contact_data = {}
                    
                    # 根據欄位映射轉換資料
                    for db_field, csv_field in field_mapping.items():
                        if csv_field in row and row[csv_field]:
                            value = row[csv_field].strip()
                            # 特殊處理 tags 欄位，轉換成列表
                            if db_field == 'tags' and value:
                                contact_data[db_field] = [tag.strip() for tag in value.split(',')]
                            else:
                                contact_data[db_field] = value
                    
                    # 驗證必要欄位：organization 是必填，phone 或 email 至少要有一個
                    if contact_data.get('organization') and \
                       (contact_data.get('phone') or contact_data.get('email')):
                        contacts_data.append(contact_data)
                
                logger.info(f"Parsed {len(contacts_data)} contacts from file")
                return contacts_data
                
        except Exception as e:
            logger.error(f"Error parsing contacts file: {e}")
            raise HTTPException(status_code=400, detail=f"解析聯絡人檔案失敗: {str(e)}")
    
    async def _extract_text_from_file(self, file_path: str) -> str:
        """從檔案中提取文字"""
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            elif file_extension == '.md':
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                # 對於其他格式，暫時返回檔名
                return f"文件內容: {Path(file_path).name}"
                
        except Exception as e:
            logger.error(f"Error extracting text from file: {e}")
            raise HTTPException(status_code=400, detail=f"提取檔案文字失敗: {str(e)}")
    
    async def get_upload_record(self, upload_id: uuid.UUID) -> Optional[UploadRecord]:
        """取得上傳記錄"""
        try:
            async with get_db_context() as db:
                result = await db.execute(
                    select(UploadRecord).where(UploadRecord.id == upload_id)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting upload record: {e}")
            return None
    
    async def get_recent_uploads(self, limit: int = 10) -> List[UploadRecord]:
        """取得最近上傳記錄"""
        try:
            async with get_db_context() as db:
                result = await db.execute(
                    select(UploadRecord)
                    .order_by(UploadRecord.created_at.desc())
                    .limit(limit)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting recent uploads: {e}")
            return []
