"""統一知識庫管理API"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_, and_, func

from app.database import get_db
from app.models.knowledge import KnowledgeDocument
from app.models.upload import (
    UploadRecord, 
    AuthoritativeMedia, 
    AuthoritativeContacts
)
# from app.schemas.knowledge import KnowledgeResponse, KnowledgeStatsResponse
from app.services.rag_retriever import RAGRetriever
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def get_mime_type_from_filename(filename):
    """根據檔名判斷 MIME 類型"""
    if not filename:
        return None
    
    filename_lower = filename.lower()
    if filename_lower.endswith('.pdf'):
        return 'application/pdf'
    elif filename_lower.endswith(('.jpg', '.jpeg')):
        return 'image/jpeg'
    elif filename_lower.endswith('.png'):
        return 'image/png'
    elif filename_lower.endswith('.gif'):
        return 'image/gif'
    else:
        return 'application/octet-stream'

@router.get("/", response_model=Dict[str, Any])
async def get_knowledge_overview(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(30, description="限制返回數量"),
    search: Optional[str] = Query(None, description="搜尋關鍵字")
):
    """
    獲取知識庫概覽，包含：
    - 統計資訊
    - 權威資料（重要資訊優先顯示）
    - 最近上傳的檔案
    """
    try:
        # 1. 獲取統計資訊
        stats = await get_knowledge_stats(db)
        
        # 2. 獲取權威資料（聯絡資訊）
        contacts_query = select(AuthoritativeContacts).limit(10)
        contacts_result = await db.execute(contacts_query)
        contacts = contacts_result.scalars().all()
        
        # 3. 獲取最近上傳的檔案 (不包含 mime_type 欄位)
        files_query = select(
            UploadRecord.id,
            UploadRecord.filename,
            UploadRecord.upload_type,
            UploadRecord.status,
            UploadRecord.file_path,
            UploadRecord.file_size,
            UploadRecord.metadata_json,
            UploadRecord.created_at
        ).where(
            UploadRecord.status == 'completed'
        ).order_by(desc(UploadRecord.created_at)).limit(limit)
        
        if search:
            files_query = files_query.where(
                UploadRecord.filename.ilike(f"%{search}%")
            )
        
        files_result = await db.execute(files_query)
        files_rows = files_result.fetchall()
        
        # 將查詢結果轉換為字典列表
        files = []
        for row in files_rows:
            files.append({
                'id': row.id,
                'filename': row.filename,
                'upload_type': row.upload_type,
                'status': row.status,
                'file_path': row.file_path,
                'file_size': row.file_size,
                'metadata_json': row.metadata_json,
                'created_at': row.created_at
            })
        
        # 4. 獲取知識文檔
        docs_query = select(KnowledgeDocument).order_by(
            desc(KnowledgeDocument.created_at)
        ).limit(limit)
        
        if search:
            docs_query = docs_query.where(
                or_(
                    KnowledgeDocument.title.ilike(f"%{search}%"),
                    KnowledgeDocument.content.ilike(f"%{search}%")
                )
            )
        
        docs_result = await db.execute(docs_query)
        documents = docs_result.scalars().all()
        
        return {
            "stats": stats,
            "authority_data": {
                "contacts": [
                    {
                        "id": str(c.id),
                        "organization": c.organization,
                        "phone": c.phone,
                        "email": c.email,
                        "tags": c.tags or [],
                        "notes": c.notes
                    } for c in contacts
                ]
            },
            "recent_files": [
                {
                    "id": str(f['id']),
                    "filename": f['filename'],
                    "type": f['upload_type'],
                    "size": f['file_size'],
                    "mime_type": get_mime_type_from_filename(f['filename']),
                    "status": f['status'],
                    "created_at": f['created_at'].isoformat(),
                    "description": f.get('metadata_json', {}).get('description', '') if f.get('metadata_json') else ''
                } for f in files
            ],
            "documents": [
                {
                    "id": str(d.id),
                    "title": d.title,
                    "content_preview": d.content[:200] if d.content else "",
                    "category": d.category,
                    "source": d.source,
                    "created_at": d.created_at.isoformat()
                } for d in documents
            ]
        }
        
    except Exception as e:
        logger.error(f"獲取知識庫概覽失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=Dict[str, Any])
async def get_knowledge_stats(db: AsyncSession = Depends(get_db)):
    """獲取知識庫統計資訊"""
    try:
        # 總檔案數
        total_files = await db.scalar(
            select(func.count()).select_from(UploadRecord).where(
                UploadRecord.status == 'completed'
            )
        )
        
        # PDF文件數 - 暫時用檔名判斷
        pdf_count = await db.scalar(
            select(func.count()).select_from(UploadRecord).where(
                and_(
                    UploadRecord.status == 'completed',
                    UploadRecord.filename.ilike('%.pdf')
                )
            )
        )
        
        # 圖片數 - 暫時用檔名判斷
        image_count = await db.scalar(
            select(func.count()).select_from(UploadRecord).where(
                and_(
                    UploadRecord.status == 'completed',
                    or_(
                        UploadRecord.filename.ilike('%.jpg'),
                        UploadRecord.filename.ilike('%.jpeg'),
                        UploadRecord.filename.ilike('%.png'),
                        UploadRecord.filename.ilike('%.gif')
                    )
                )
            )
        )
        
        # 權威資料數（聯絡資訊）
        authority_count = await db.scalar(
            select(func.count()).select_from(AuthoritativeContacts)
        )
        
        # 知識文檔數
        doc_count = await db.scalar(
            select(func.count()).select_from(KnowledgeDocument)
        )
        
        return {
            "total_files": total_files or 0,
            "pdf_count": pdf_count or 0,
            "image_count": image_count or 0,
            "authority_count": authority_count or 0,
            "document_count": doc_count or 0,
            "total_items": (total_files or 0) + (authority_count or 0) + (doc_count or 0)
        }
        
    except Exception as e:
        logger.error(f"獲取統計資訊失敗: {e}")
        return {
            "total_files": 0,
            "pdf_count": 0,
            "image_count": 0,
            "authority_count": 0,
            "document_count": 0,
            "total_items": 0
        }

@router.get("/search", response_model=Dict[str, Any])
async def unified_search(
    query: str = Query(..., description="搜尋關鍵字"),
    k: int = Query(10, description="返回結果數量"),
    search_type: Optional[str] = Query("all", description="搜尋類型: all, files, authority, documents"),
    db: AsyncSession = Depends(get_db)
):
    """
    統一搜尋接口，同時搜尋：
    - 檔案（向量搜尋 + 關鍵字搜尋）
    - 權威資料
    - 知識文檔
    """
    try:
        results = {
            "query": query,
            "files": [],
            "authority_data": [],
            "documents": [],
            "total_results": 0
        }
        
        # 1. 搜尋檔案
        if search_type in ["all", "files"]:
            files_query = select(
                UploadRecord.id,
                UploadRecord.filename,
                UploadRecord.upload_type,
                UploadRecord.created_at
            ).where(
                and_(
                    UploadRecord.status == 'completed',
                    UploadRecord.filename.ilike(f"%{query}%")
                )
            ).limit(k)
            
            files_result = await db.execute(files_query)
            files_rows = files_result.fetchall()
            
            results["files"] = [
                {
                    "id": str(row.id),
                    "filename": row.filename,
                    "type": row.upload_type,
                    "mime_type": get_mime_type_from_filename(row.filename),
                    "created_at": row.created_at.isoformat(),
                    "match_type": "keyword"
                } for row in files_rows
            ]
        
        # 2. 搜尋權威資料
        if search_type in ["all", "authority"]:
            contacts_query = select(AuthoritativeContacts).where(
                or_(
                    AuthoritativeContacts.organization.ilike(f"%{query}%"),
                    AuthoritativeContacts.phone.ilike(f"%{query}%"),
                    AuthoritativeContacts.notes.ilike(f"%{query}%")
                )
            ).limit(k)
            
            contacts_result = await db.execute(contacts_query)
            contacts = contacts_result.scalars().all()
            
            results["authority_data"] = [
                {
                    "id": str(c.id),
                    "type": "contact",
                    "organization": c.organization,
                    "phone": c.phone,
                    "email": c.email,
                    "tags": c.tags or [],
                    "match_type": "keyword"
                } for c in contacts
            ]
        
        # 3. 使用RAG搜尋知識文檔（向量搜尋）
        if search_type in ["all", "documents"]:
            retriever = RAGRetriever()
            doc_results = await retriever.search(
                query=query,
                k=k,
                threshold=0.7
            )
            
            results["documents"] = [
                {
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "content_preview": doc.get("content", "")[:200],
                    "similarity": doc.get("similarity", 0),
                    "category": doc.get("metadata", {}).get("category"),
                    "match_type": "semantic"
                } for doc in doc_results
            ]
        
        # 計算總結果數
        results["total_results"] = (
            len(results["files"]) + 
            len(results["authority_data"]) + 
            len(results["documents"])
        )
        
        return results
        
    except Exception as e:
        logger.error(f"統一搜尋失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file/{file_id}", response_model=Dict[str, Any])
async def get_file_details(
    file_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """獲取檔案詳細資訊"""
    try:
        result = await db.execute(
            select(
                UploadRecord.id,
                UploadRecord.filename,
                UploadRecord.upload_type,
                UploadRecord.file_size,
                UploadRecord.status,
                UploadRecord.created_at,
                UploadRecord.file_path
            ).where(UploadRecord.id == file_id)
        )
        file = result.fetchone()
        
        if not file:
            raise HTTPException(status_code=404, detail="檔案不存在")
        
        mime_type = get_mime_type_from_filename(file.filename)
        
        return {
            "id": str(file.id),
            "filename": file.filename,
            "type": file.upload_type,
            "mime_type": mime_type,
            "size": file.file_size,
            "status": file.status,
            "description": "",
            "created_at": file.created_at.isoformat(),
            "file_path": file.file_path,
            "can_preview": mime_type in ['application/pdf', 'image/jpeg', 'image/png', 'image/gif']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取檔案詳情失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file/{file_id}/preview")
async def get_file_preview(
    file_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """獲取檔案預覽URL或內容"""
    try:
        result = await db.execute(
            select(
                UploadRecord.id,
                UploadRecord.filename
            ).where(UploadRecord.id == file_id)
        )
        file = result.fetchone()
        
        if not file:
            raise HTTPException(status_code=404, detail="檔案不存在")
        
        mime_type = get_mime_type_from_filename(file.filename)
        
        # 根據檔案類型返回不同的預覽方式
        if mime_type == 'application/pdf':
            return {
                "type": "pdf",
                "url": f"/static/uploads/{file.filename}",
                "viewer": "pdf"
            }
        elif mime_type and mime_type.startswith('image/'):
            return {
                "type": "image",
                "url": f"/static/uploads/{file.filename}",
                "viewer": "image"
            }
        else:
            raise HTTPException(status_code=400, detail="此檔案類型不支援預覽")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取檔案預覽失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/file/{file_id}")
async def delete_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """刪除檔案（需要確認）"""
    try:
        result = await db.execute(
            select(UploadRecord).where(UploadRecord.id == file_id)
        )
        file = result.scalar_one_or_none()
        
        if not file:
            raise HTTPException(status_code=404, detail="檔案不存在")
        
        # 刪除相關的知識文檔
        await db.execute(
            select(KnowledgeDocument).where(
                KnowledgeDocument.upload_id == file_id
            ).delete()
        )
        
        # 刪除檔案記錄
        await db.delete(file)
        await db.commit()
        
        return {"message": "檔案已刪除", "id": str(file_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"刪除檔案失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))