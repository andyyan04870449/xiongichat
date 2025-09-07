"""RAG 檢索服務"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from dataclasses import dataclass

from app.database import get_db_context
from app.services.embeddings import EmbeddingService
from app.models.knowledge import KnowledgeDocument, KnowledgeEmbedding

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """檢索結果"""
    content: str
    title: str
    source: str
    category: str
    similarity_score: float
    metadata: Dict[str, Any]


class RAGRetriever:
    """RAG 檢索器"""
    
    def __init__(self, embedding_service: EmbeddingService = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.default_k = 5
        self.similarity_threshold = 0.5
    
    async def retrieve(
        self,
        query: str,
        k: int = None,
        filters: Dict[str, Any] = None,
        similarity_threshold: float = None
    ) -> List[RetrievalResult]:
        """檢索相關文件"""
        
        k = k or self.default_k
        threshold = similarity_threshold or self.similarity_threshold
        
        try:
            # 生成查詢向量
            query_embedding = await self.embedding_service.embed_text(query)
            
            # 執行向量檢索
            results = await self._vector_search(
                query_embedding,
                k=k,
                filters=filters,
                threshold=threshold
            )
            
            # 轉換為檢索結果
            retrieval_results = []
            for result in results:
                retrieval_result = RetrievalResult(
                    content=result["content"],
                    title=result["title"],
                    source=result["source"],
                    category=result["category"],
                    similarity_score=result["similarity_score"],
                    metadata=result.get("metadata", {})
                )
                retrieval_results.append(retrieval_result)
            
            logger.info(f"Retrieved {len(retrieval_results)} results for query")
            return retrieval_results
            
        except Exception as e:
            logger.error(f"Error in retrieval: {str(e)}")
            return []
    
    async def _vector_search(
        self,
        query_embedding: List[float],
        k: int,
        filters: Dict[str, Any] = None,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """執行向量檢索"""
        
        try:
            async with get_db_context() as db:
                # 將向量轉換為字符串格式
                embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
                
                # 構建基礎 SQL 查詢
                sql_query = f"""
                SELECT 
                    ke.content,
                    ke.metadata,
                    ke.chunk_index,
                    kd.title,
                    kd.source,
                    kd.category,
                    kd.lang,
                    kd.published_date,
                    1 - (ke.embedding <=> '{embedding_str}'::vector) as similarity_score
                FROM knowledge_embeddings ke
                JOIN knowledge_documents kd ON ke.document_id = kd.id
                WHERE 1 - (ke.embedding <=> '{embedding_str}'::vector) > {threshold}
                """
                
                # 添加過濾條件
                if filters:
                    if "category" in filters:
                        sql_query += f" AND kd.category = '{filters['category']}'"
                    
                    if "lang" in filters:
                        sql_query += f" AND kd.lang = '{filters['lang']}'"
                    
                    if "source" in filters:
                        sql_query += f" AND kd.source = '{filters['source']}'"
                
                # 排序和限制
                sql_query += f" ORDER BY similarity_score DESC LIMIT {k}"
                
                # 執行查詢
                result = await db.execute(text(sql_query))
                rows = result.fetchall()
                
                # 轉換結果
                results = []
                for row in rows:
                    result_dict = {
                        "content": row[0],
                        "metadata": row[1] or {},
                        "chunk_index": row[2],
                        "title": row[3],
                        "source": row[4],
                        "category": row[5],
                        "lang": row[6],
                        "published_date": row[7].isoformat() if row[7] else None,
                        "similarity_score": float(row[8])
                    }
                    results.append(result_dict)
                
                return results
                
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            return []
    
    async def retrieve_with_reranking(
        self,
        query: str,
        k: int = None,
        filters: Dict[str, Any] = None,
        rerank_k: int = None
    ) -> List[RetrievalResult]:
        """檢索並重排序"""
        
        k = k or self.default_k
        rerank_k = rerank_k or (k * 3)  # 先取更多結果進行重排序
        
        try:
            # 先檢索更多結果
            initial_results = await self.retrieve(
                query=query,
                k=rerank_k,
                filters=filters,
                similarity_threshold=0.5  # 降低初始閾值
            )
            
            if not initial_results:
                return []
            
            # 重排序（這裡可以加入更複雜的重排序邏輯）
            reranked_results = await self._rerank_results(query, initial_results, k)
            
            return reranked_results
            
        except Exception as e:
            logger.error(f"Error in retrieval with reranking: {str(e)}")
            return []
    
    async def _rerank_results(
        self,
        query: str,
        results: List[RetrievalResult],
        k: int
    ) -> List[RetrievalResult]:
        """重排序結果"""
        
        # 簡單的重排序策略：結合相似度分數和內容長度
        def rerank_score(result: RetrievalResult) -> float:
            # 基礎相似度分數
            similarity_score = result.similarity_score
            
            # 內容長度調整（適中的長度得分更高）
            content_length = len(result.content)
            length_score = 1.0 - abs(content_length - 200) / 1000  # 200字左右最佳
            length_score = max(0.0, min(1.0, length_score))
            
            # 類別權重（可以根據查詢調整）
            category_weights = {
                "services": 1.2,
                "legal": 1.1,
                "medical": 1.1,
                "faq": 1.0
            }
            category_weight = category_weights.get(result.category, 1.0)
            
            # 綜合分數
            final_score = similarity_score * 0.7 + length_score * 0.2 + (category_weight - 1.0) * 0.1
            
            return final_score
        
        # 重新計算分數並排序
        for result in results:
            result.similarity_score = rerank_score(result)
        
        # 按新分數排序
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return results[:k]
    
    async def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """根據ID取得文件"""
        try:
            async with get_db_context() as db:
                stmt = select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
                result = await db.execute(stmt)
                document = result.scalar_one_or_none()
                
                if document:
                    return {
                        "id": str(document.id),
                        "title": document.title,
                        "content": document.content,
                        "source": document.source,
                        "category": document.category,
                        "lang": document.lang,
                        "published_date": document.published_date.isoformat() if document.published_date else None,
                        "created_at": document.created_at.isoformat(),
                        "updated_at": document.updated_at.isoformat()
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting document by ID: {str(e)}")
            return None
    
    async def search_by_keywords(
        self,
        keywords: List[str],
        k: int = None,
        filters: Dict[str, Any] = None
    ) -> List[RetrievalResult]:
        """關鍵字搜尋"""
        
        k = k or self.default_k
        
        try:
            async with get_db_context() as db:
                # 構建關鍵字搜尋查詢
                keyword_conditions = []
                params = []
                
                # 構建查詢參數
                query_params = {}
                param_counter = 0
                
                for keyword in keywords:
                    param_counter += 1
                    title_param = f"keyword_title_{param_counter}"
                    content_param = f"keyword_content_{param_counter}"
                    keyword_conditions.append(f"(kd.title ILIKE :{title_param} OR kd.content ILIKE :{content_param})")
                    query_params[title_param] = f"%{keyword}%"
                    query_params[content_param] = f"%{keyword}%"
                
                sql_query = f"""
                SELECT DISTINCT
                    kd.title,
                    kd.content,
                    kd.source,
                    kd.category,
                    kd.lang,
                    kd.published_date,
                    kd.created_at
                FROM knowledge_documents kd
                WHERE {' OR '.join(keyword_conditions)}
                """
                
                # 添加過濾條件
                if filters:
                    if "category" in filters:
                        sql_query += " AND kd.category = :category"
                        query_params["category"] = filters["category"]
                    
                    if "lang" in filters:
                        sql_query += " AND kd.lang = :lang"
                        query_params["lang"] = filters["lang"]
                
                sql_query += " ORDER BY kd.created_at DESC LIMIT :limit"
                query_params["limit"] = k
                
                # 執行查詢
                result = await db.execute(text(sql_query), query_params)
                rows = result.fetchall()
                
                # 轉換結果
                results = []
                for row in rows:
                    retrieval_result = RetrievalResult(
                        content=row[1],
                        title=row[0],
                        source=row[2],
                        category=row[3],
                        similarity_score=1.0,  # 關鍵字搜尋沒有相似度分數
                        metadata={
                            "lang": row[4],
                            "published_date": row[5].isoformat() if row[5] else None,
                            "created_at": row[6].isoformat()
                        }
                    )
                    results.append(retrieval_result)
                
                return results
                
        except Exception as e:
            logger.error(f"Error in keyword search: {str(e)}")
            return []
