"""RAG 檢索節點 - 從知識庫檢索相關資訊"""

from typing import Dict, Any
import logging

from app.langgraph.state import WorkflowState
from app.services.rag_retriever import RAGRetriever
from app.services.query_builder import QueryBuilder

logger = logging.getLogger(__name__)


class RAGRetrievalNode:
    """RAG 檢索節點 - 根據使用者輸入檢索相關知識"""
    
    def __init__(self):
        self.retriever = RAGRetriever()
        self.query_builder = QueryBuilder()
        self.default_k = 3  # 預設檢索 3 筆最相關的資料
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行節點邏輯"""
        try:
            # 檢查是否需要檢索
            understanding = state.get("context_understanding", {})
            search_strategy = understanding.get("search_strategy", {})
            
            # 優先使用理解結果判斷
            should_search = search_strategy.get("should_search", state.get("need_knowledge", False))
            
            if not should_search:
                logger.info(f"Skipping RAG retrieval for user {state['user_id']} - knowledge not needed")
                state["retrieved_knowledge"] = []
                return state
            
            # 使用增強查詢或構建查詢
            if state.get("enhanced_query"):
                query = state["enhanced_query"]
            else:
                query = self.query_builder.build_query(understanding, state["input_text"])
            
            # 獲取搜索參數
            search_params = self.query_builder.get_search_parameters(understanding)
            
            # 獲取過濾條件
            filters = self.query_builder.get_filters(understanding)
            
            # 執行檢索
            logger.info(
                f"Retrieving knowledge for user {state['user_id']}, "
                f"query: {query}, params: {search_params}"
            )
            
            results = await self.retriever.retrieve(
                query=query,
                k=search_params.get("k", self.default_k),
                filters=filters,
                similarity_threshold=search_params.get("similarity_threshold", 0.3)
            )
            
            # 轉換檢索結果為字典格式
            retrieved_knowledge = []
            for result in results:
                knowledge_item = {
                    "content": result.content,
                    "title": result.title,
                    "source": result.source,
                    "category": result.category,
                    "similarity_score": result.similarity_score,
                    "metadata": result.metadata
                }
                retrieved_knowledge.append(knowledge_item)
            
            state["retrieved_knowledge"] = retrieved_knowledge
            
            # 如果使用關鍵字搜索作為備選
            if not retrieved_knowledge and self.query_builder.should_use_keywords(understanding):
                logger.info("No results with vector search, trying keyword search")
                keywords = self.query_builder.extract_keywords(understanding, state["input_text"])
                if keywords:
                    keyword_results = await self.retriever.search_by_keywords(
                        keywords=keywords,
                        k=search_params.get("k", self.default_k),
                        filters=filters
                    )
                    for result in keyword_results:
                        knowledge_item = {
                            "content": result.content,
                            "title": result.title,
                            "source": result.source,
                            "category": result.category,
                            "similarity_score": result.similarity_score,
                            "metadata": result.metadata
                        }
                        retrieved_knowledge.append(knowledge_item)
            
            logger.info(f"Retrieved {len(retrieved_knowledge)} knowledge items for user {state['user_id']}")
            
        except Exception as e:
            logger.error(f"RAGRetrieval error: {str(e)}")
            # 檢索失敗時設為空列表，讓對話繼續
            state["retrieved_knowledge"] = []
        
        return state