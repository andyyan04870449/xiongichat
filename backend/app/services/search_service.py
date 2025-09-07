"""
搜尋服務 - 實現混合查詢邏輯
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_context
from app.models.upload import AuthoritativeMedia, AuthoritativeContacts
from app.models.knowledge import KnowledgeDocument
from app.services.embeddings import EmbeddingService
from app.services.rag_retriever import RAGRetriever
from app.schemas.upload import SearchRequest, SearchResult, SearchResponse

logger = logging.getLogger(__name__)


class SearchService:
    """搜尋服務"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.rag_retriever = RAGRetriever()
        logger.info("SearchService initialized")
    
    def _get_attr(self, obj, attr, default=None):
        """安全地獲取物件屬性，支持 dataclass 和字典"""
        if hasattr(obj, attr):
            return getattr(obj, attr, default)
        elif hasattr(obj, 'get'):
            return obj.get(attr, default)
        else:
            return default
    
    async def search(
        self, 
        request: SearchRequest
    ) -> SearchResponse:
        """執行混合搜尋"""
        try:
            # 執行 RAG 搜尋（使用關鍵字搜尋）
            keywords = [request.query]  # 將查詢字串作為關鍵字
            rag_results = await self.rag_retriever.search_by_keywords(
                keywords=keywords,
                k=request.k,
                filters=self._build_filters(request)
            )
            
            # 處理搜尋結果
            processed_results = []
            authority_count = 0
            article_count = 0
            
            for result in rag_results:
                source = self._get_attr(result, 'source')
                if source in ['authoritative_media', 'authoritative_contacts']:
                    # 權威資料 - 從 RDB 回補完整資料
                    authority_data = await self._get_authority_data(result)
                    if authority_data:
                        processed_results.append(authority_data)
                        authority_count += 1
                else:
                    # 文章資料 - 直接使用 RAG 結果
                    article_data = self._format_article_result(result)
                    processed_results.append(article_data)
                    article_count += 1
            
            # 根據篩選條件過濾結果
            if request.filter_type == 'authority':
                processed_results = [r for r in processed_results if r['type'] == 'authority']
                authority_count = len(processed_results)
                article_count = 0
            elif request.filter_type == 'article':
                processed_results = [r for r in processed_results if r['type'] == 'article']
                article_count = len(processed_results)
                authority_count = 0
            
            # 建立回應
            response = SearchResponse(
                results=[SearchResult(**result) for result in processed_results],
                total_count=len(processed_results),
                authority_count=authority_count,
                article_count=article_count,
                query_params=request.dict()
            )
            
            logger.info(f"Search completed: {len(processed_results)} results")
            return response
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            raise HTTPException(status_code=500, detail=f"搜尋失敗: {str(e)}")
    
    async def _get_authority_data(self, rag_result) -> Optional[Dict[str, Any]]:
        """從 RDB 取得權威資料"""
        try:
            source = self._get_attr(rag_result, 'source')
            
            if source == 'authoritative_media':
                return await self._get_media_data(rag_result)
            elif source == 'authoritative_contacts':
                return await self._get_contacts_data(rag_result)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting authority data: {e}")
            return None
    
    async def _get_media_data(self, rag_result) -> Optional[Dict[str, Any]]:
        """取得媒體資料"""
        try:
            # 從 RAG 結果中提取關鍵資訊
            content = self._get_attr(rag_result, 'content', '')
            
            # 嘗試從內容中提取檔名
            filename = None
            if '媒體檔案:' in content:
                filename = content.split('媒體檔案:')[1].split()[0]
            
            async with get_db_context() as db:
                # 搜尋匹配的媒體記錄
                if filename:
                    result = await db.execute(
                        select(AuthoritativeMedia)
                        .where(AuthoritativeMedia.filename == filename)
                        .limit(1)
                    )
                    media_record = result.scalar_one_or_none()
                else:
                    # 如果無法提取檔名，使用相似度搜尋
                    result = await db.execute(
                        select(AuthoritativeMedia)
                        .order_by(AuthoritativeMedia.created_at.desc())
                        .limit(1)
                    )
                    media_record = result.scalar_one_or_none()
                
                if media_record:
                    return {
                        'id': str(media_record.id),
                        'type': 'authority',
                        'title': f"媒體: {media_record.filename}",
                        'content': self._format_media_content(media_record),
                        'similarity_score': self._get_attr(rag_result, 'similarity_score'),
                        'source': 'authoritative_media',
                        'category': 'media',
                        'lang': 'zh-TW',
                        'published_date': media_record.created_at,
                        'metadata': {
                            'filename': media_record.filename,
                            'file_size': media_record.file_size,
                            'mime_type': media_record.mime_type,
                            'tags': media_record.tags,
                            'description': media_record.description,
                            'exif_data': media_record.exif_data
                        }
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting media data: {e}")
            return None
    
    async def _get_contacts_data(self, rag_result) -> Optional[Dict[str, Any]]:
        """取得聯絡人資料"""
        try:
            # 從 RAG 結果中提取關鍵資訊
            content = self._get_attr(rag_result, 'content', '')
            
            async with get_db_context() as db:
                # 根據內容中的關鍵字搜尋聯絡人
                query = select(AuthoritativeContacts)
                
                # 嘗試從內容中提取機構名稱
                if '機構:' in content:
                    org_name = content.split('機構:')[1].split()[0]
                    query = query.where(AuthoritativeContacts.organization.ilike(f'%{org_name}%'))
                elif '部門:' in content:
                    dept_name = content.split('部門:')[1].split()[0]
                    query = query.where(AuthoritativeContacts.department.ilike(f'%{dept_name}%'))
                else:
                    # 如果無法提取特定資訊，返回最新的聯絡人
                    query = query.order_by(AuthoritativeContacts.created_at.desc())
                
                result = await db.execute(query.limit(1))
                contact_record = result.scalar_one_or_none()
                
                if contact_record:
                    return {
                        'id': str(contact_record.id),
                        'type': 'authority',
                        'title': f"聯絡人: {contact_record.organization or '未知機構'}",
                        'content': self._format_contact_content(contact_record),
                        'similarity_score': self._get_attr(rag_result, 'similarity_score'),
                        'source': 'authoritative_contacts',
                        'category': 'contacts',
                        'lang': 'zh-TW',
                        'published_date': contact_record.created_at,
                        'metadata': {
                            'phone': contact_record.phone,
                            'email': contact_record.email,
                            'address': contact_record.address,
                            'organization': contact_record.organization,
                            'tags': contact_record.tags,
                            'notes': contact_record.notes
                        }
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting contacts data: {e}")
            return None
    
    def _format_media_content(self, media_record: AuthoritativeMedia) -> str:
        """格式化媒體內容"""
        content_parts = [f"檔案: {media_record.filename}"]
        
        if media_record.tags:
            content_parts.append(f"標籤: {', '.join(media_record.tags)}")
        
        if media_record.description:
            content_parts.append(f"描述: {media_record.description}")
        
        if media_record.mime_type:
            content_parts.append(f"類型: {media_record.mime_type}")
        
        return " | ".join(content_parts)
    
    def _format_contact_content(self, contact_record: AuthoritativeContacts) -> str:
        """格式化機構聯絡內容"""
        content_parts = []
        
        # 機構名稱（必填）
        content_parts.append(f"機構: {contact_record.organization}")
        
        # 聯絡方式
        contact_methods = []
        if contact_record.phone:
            contact_methods.append("電話")
        if contact_record.email:
            contact_methods.append("電子郵件")
        if contact_record.address:
            contact_methods.append("地址")
        if contact_methods:
            content_parts.append(f"提供聯絡方式: {', '.join(contact_methods)}")
        
        if contact_record.tags:
            content_parts.append(f"服務類型: {', '.join(contact_record.tags)}")
        
        if contact_record.notes:
            content_parts.append(f"服務說明: {contact_record.notes}")
        
        return " | ".join(content_parts)
    
    def _format_article_result(self, rag_result: Dict[str, Any]) -> Dict[str, Any]:
        """格式化文章結果"""
        return {
            'id': str(self._get_attr(rag_result, 'document_id', '')),
            'type': 'article',
            'title': self._get_attr(rag_result, 'title', ''),
            'content': self._get_attr(rag_result, 'content', ''),
            'similarity_score': self._get_attr(rag_result, 'similarity_score'),
            'source': self._get_attr(rag_result, 'source', ''),
            'category': self._get_attr(rag_result, 'category', ''),
            'lang': self._get_attr(rag_result, 'lang', ''),
            'published_date': self._get_attr(rag_result, 'published_date'),
            'metadata': {
                'chunk_index': self._get_attr(rag_result, 'chunk_index'),
                'metadata': self._get_attr(rag_result, 'metadata', {})
            }
        }
    
    def _build_filters(self, request: SearchRequest) -> Dict[str, Any]:
        """建立搜尋篩選條件"""
        filters = {}
        
        if request.category:
            filters['category'] = request.category
        
        if request.lang:
            filters['lang'] = request.lang
        
        return filters
    
    async def get_authority_media(
        self, 
        tags: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50
    ) -> List[AuthoritativeMedia]:
        """取得權威媒體列表"""
        try:
            async with get_db_context() as db:
                query = select(AuthoritativeMedia)
                
                if tags:
                    # 使用 JSONB 查詢標籤
                    for tag in tags:
                        query = query.where(AuthoritativeMedia.tags.contains([tag]))
                
                if date_from:
                    query = query.where(AuthoritativeMedia.created_at >= date_from)
                
                if date_to:
                    query = query.where(AuthoritativeMedia.created_at <= date_to)
                
                query = query.order_by(AuthoritativeMedia.created_at.desc()).limit(limit)
                
                result = await db.execute(query)
                return result.scalars().all()
                
        except Exception as e:
            logger.error(f"Error getting authority media: {e}")
            return []
    
    async def get_authority_contacts(
        self, 
        organization: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[AuthoritativeContacts]:
        """取得權威機構聯絡列表"""
        try:
            async with get_db_context() as db:
                query = select(AuthoritativeContacts)
                
                if organization:
                    query = query.where(AuthoritativeContacts.organization.ilike(f'%{organization}%'))
                
                if tags:
                    for tag in tags:
                        query = query.where(AuthoritativeContacts.tags.contains([tag]))
                
                query = query.order_by(AuthoritativeContacts.created_at.desc()).limit(limit)
                
                result = await db.execute(query)
                return result.scalars().all()
                
        except Exception as e:
            logger.error(f"Error getting authority contacts: {e}")
            return []
