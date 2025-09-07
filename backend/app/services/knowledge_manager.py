"""知識庫管理服務"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db_context
from app.models.knowledge import KnowledgeDocument, KnowledgeEmbedding
from app.services.embeddings import EmbeddingService
from app.services.chunker import DocumentChunker
from app.services.rag_retriever import RAGRetriever

logger = logging.getLogger(__name__)


class KnowledgeManager:
    """知識庫管理器"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.chunker = DocumentChunker(chunk_size=500, overlap=50)
        self.retriever = RAGRetriever(self.embedding_service)
    
    async def add_document(
        self,
        title: str,
        content: str,
        source: str,
        category: str,
        lang: str = "zh-TW",
        published_date: str = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """添加文件到知識庫"""
        try:
            async with get_db_context() as db:
                # 建立文件記錄
                document = KnowledgeDocument(
                    title=title,
                    content=content,
                    source=source,
                    category=category,
                    lang=lang,
                    published_date=published_date
                    # 暫時不使用 metadata 欄位，直到資料庫結構更新
                )
                db.add(document)
                await db.flush()  # 取得ID
                
                # 切塊文件
                chunks = self.chunker.chunk_document(
                    title=title,
                    content=content,
                    source=source,
                    category=category,
                    lang=lang,
                    published_date=published_date
                )
                
                # 為每個塊生成嵌入
                for chunk in chunks:
                    embedding = await self.embedding_service.embed_text(chunk.content)
                    
                    embedding_record = KnowledgeEmbedding(
                        document_id=document.id,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        embedding=embedding,
                        metadata_json=chunk.metadata
                    )
                    db.add(embedding_record)
                
                await db.commit()
                
                logger.info(f"Added document '{title}' with {len(chunks)} chunks")
                return str(document.id)
                
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            raise
    
    async def update_document(
        self,
        document_id: str,
        title: str = None,
        content: str = None,
        source: str = None,
        category: str = None,
        lang: str = None,
        published_date: str = None
    ) -> bool:
        """更新文件"""
        try:
            async with get_db_context() as db:
                # 查詢文件
                stmt = select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
                result = await db.execute(stmt)
                document = result.scalar_one_or_none()
                
                if not document:
                    return False
                
                # 更新文件資訊
                if title is not None:
                    document.title = title
                if content is not None:
                    document.content = content
                if source is not None:
                    document.source = source
                if category is not None:
                    document.category = category
                if lang is not None:
                    document.lang = lang
                if published_date is not None:
                    document.published_date = published_date
                
                # 如果內容有變更，重新生成嵌入
                if content is not None:
                    # 刪除舊的嵌入
                    await db.execute(
                        delete(KnowledgeEmbedding).where(
                            KnowledgeEmbedding.document_id == document_id
                        )
                    )
                    
                    # 重新切塊和生成嵌入
                    chunks = self.chunker.chunk_document(
                        title=document.title,
                        content=document.content,
                        source=document.source,
                        category=document.category,
                        lang=document.lang,
                        published_date=document.published_date.isoformat() if document.published_date else None
                    )
                    
                    for chunk in chunks:
                        embedding = await self.embedding_service.embed_text(chunk.content)
                        
                        embedding_record = KnowledgeEmbedding(
                            document_id=document.id,
                            chunk_index=chunk.chunk_index,
                            content=chunk.content,
                            embedding=embedding,
                            metadata_json=chunk.metadata
                        )
                        db.add(embedding_record)
                
                await db.commit()
                
                logger.info(f"Updated document {document_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            raise
    
    async def add_knowledge_document(self, document_data: Dict[str, Any]) -> str:
        """
        添加知識文件的便捷方法，用於批次上傳
        
        Args:
            document_data: 包含以下欄位的字典
                - title: 文件標題
                - content: 文件內容
                - source: 來源
                - category: 分類
                - metadata: 結構化資料（可選）
                - lang: 語言（預設 zh-TW）
                - published_date: 發布日期（可選）
        
        Returns:
            document_id: 文件ID
        """
        return await self.add_document(
            title=document_data.get("title"),
            content=document_data.get("content"),
            source=document_data.get("source", "drug_database"),
            category=document_data.get("category", "drug_information"),
            lang=document_data.get("lang", "zh-TW"),
            published_date=document_data.get("published_date"),
            metadata=document_data.get("metadata", {})
        )
    
    async def list_knowledge_documents(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        列出知識文件
        
        Args:
            filters: 過濾條件
            skip: 跳過筆數
            limit: 限制筆數
        
        Returns:
            文件列表
        """
        try:
            async with get_db_context() as db:
                query = select(KnowledgeDocument)
                
                # 應用過濾條件
                if filters:
                    if "category" in filters:
                        query = query.where(KnowledgeDocument.category == filters["category"])
                    if "source" in filters:
                        query = query.where(KnowledgeDocument.source == filters["source"])
                    if "lang" in filters:
                        query = query.where(KnowledgeDocument.lang == filters["lang"])
                
                # 排序和分頁
                query = query.order_by(KnowledgeDocument.created_at.desc())
                query = query.offset(skip).limit(limit)
                
                result = await db.execute(query)
                documents = result.scalars().all()
                
                # 轉換為字典
                return [
                    {
                        "id": str(doc.id),
                        "title": doc.title,
                        "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                        "source": doc.source,
                        "category": doc.category,
                        "lang": doc.lang,
                        "metadata": doc.meta_data,
                        "published_date": doc.published_date.isoformat() if doc.published_date else None,
                        "created_at": doc.created_at.isoformat(),
                        "updated_at": doc.updated_at.isoformat()
                    }
                    for doc in documents
                ]
                
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return []
    
    async def delete_knowledge_document(self, document_id: str) -> bool:
        """刪除知識文件（包含毒品知識）"""
        return await self.delete_document(document_id)
    
    async def delete_document(self, document_id: str) -> bool:
        """刪除文件"""
        try:
            async with get_db_context() as db:
                # 查詢文件
                stmt = select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
                result = await db.execute(stmt)
                document = result.scalar_one_or_none()
                
                if not document:
                    return False
                
                # 刪除文件（會自動刪除相關的嵌入）
                await db.delete(document)
                await db.commit()
                
                logger.info(f"Deleted document {document_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """取得文件"""
        try:
            async with get_db_context() as db:
                stmt = select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
                result = await db.execute(stmt)
                document = result.scalar_one_or_none()
                
                if document:
                    return document.to_dict()
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise
    
    async def list_documents(
        self,
        category: str = None,
        lang: str = None,
        source: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """列出文件"""
        try:
            async with get_db_context() as db:
                stmt = select(KnowledgeDocument)
                
                # 添加過濾條件
                if category:
                    stmt = stmt.where(KnowledgeDocument.category == category)
                if lang:
                    stmt = stmt.where(KnowledgeDocument.lang == lang)
                if source:
                    stmt = stmt.where(KnowledgeDocument.source == source)
                
                # 排序和分頁
                stmt = stmt.order_by(KnowledgeDocument.created_at.desc())
                stmt = stmt.limit(limit).offset(offset)
                
                result = await db.execute(stmt)
                documents = result.scalars().all()
                
                return [doc.to_dict() for doc in documents]
                
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise
    
    async def search_documents(
        self,
        query: str,
        k: int = 5,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """搜尋文件"""
        try:
            results = await self.retriever.retrieve(
                query=query,
                k=k,
                filters=filters
            )
            
            # 轉換為字典格式
            search_results = []
            for result in results:
                search_results.append({
                    "content": result.content,
                    "title": result.title,
                    "source": result.source,
                    "category": result.category,
                    "similarity_score": result.similarity_score,
                    "metadata": result.metadata
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """取得知識庫統計資訊"""
        try:
            async with get_db_context() as db:
                # 文件總數
                stmt = select(KnowledgeDocument)
                result = await db.execute(stmt)
                total_documents = len(result.scalars().all())
                
                # 嵌入總數
                stmt = select(KnowledgeEmbedding)
                result = await db.execute(stmt)
                total_embeddings = len(result.scalars().all())
                
                # 按類別統計
                stmt = select(KnowledgeDocument.category, func.count(KnowledgeDocument.id))
                stmt = stmt.group_by(KnowledgeDocument.category)
                result = await db.execute(stmt)
                category_stats = {row[0]: row[1] for row in result.fetchall()}
                
                # 按語言統計
                stmt = select(KnowledgeDocument.lang, func.count(KnowledgeDocument.id))
                stmt = stmt.group_by(KnowledgeDocument.lang)
                result = await db.execute(stmt)
                lang_stats = {row[0]: row[1] for row in result.fetchall()}
                
                return {
                    "total_documents": total_documents,
                    "total_embeddings": total_embeddings,
                    "category_stats": category_stats,
                    "lang_stats": lang_stats
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            raise
    
    async def bulk_add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """批量添加文件"""
        document_ids = []
        
        for doc in documents:
            try:
                doc_id = await self.add_document(
                    title=doc["title"],
                    content=doc["content"],
                    source=doc["source"],
                    category=doc["category"],
                    lang=doc.get("lang", "zh-TW"),
                    published_date=doc.get("published_date")
                )
                document_ids.append(doc_id)
                
            except Exception as e:
                logger.error(f"Error adding document '{doc.get('title', 'Unknown')}': {str(e)}")
                continue
        
        logger.info(f"Bulk added {len(document_ids)} documents")
        return document_ids
