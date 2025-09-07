"""簡化的工作流程實作"""

from typing import Dict, Any
import logging
from app.langgraph.state import WorkflowState
from app.langgraph.nodes import (
    ChatAgentNode,
    ConversationLoggerNode,
    IntentRouterNode,
    RAGRetrievalNode,
    SemanticAnalyzerNode,
    DrugSafetyCheckNode,
    SafeResponseGeneratorNode
)
from app.langgraph.nodes.context_understanding import ContextUnderstandingNode
from app.services.memory import MemoryService
from app.services.response_validator import ResponseValidator
from app.utils.ai_logger import get_ai_logger
import time

logger = logging.getLogger(__name__)


class SimpleChatWorkflow:
    """簡化的聊天工作流程"""
    
    def __init__(self):
        # 初始化節點
        self.context_understanding = ContextUnderstandingNode()  # 新增對話理解
        self.semantic_analyzer = SemanticAnalyzerNode()
        self.drug_safety_check = DrugSafetyCheckNode()
        self.intent_router = IntentRouterNode()
        self.rag_retrieval = RAGRetrievalNode()
        self.safe_response_generator = SafeResponseGeneratorNode()
        self.response_validator = ResponseValidator()  # 新增回應驗證
        self.conversation_logger = ConversationLoggerNode()
        self.memory_service = MemoryService()
        
        logger.info("SimpleChatWorkflow initialized with context understanding")
    
    async def ainvoke(self, state: WorkflowState) -> WorkflowState:
        """執行工作流程"""
        start_time = time.time()
        ai_logger = get_ai_logger(state.get("session_id"))
        
        try:
            # 記錄請求開始
            ai_logger.log_request_start(
                user_id=state.get("user_id", "unknown"),
                message=state.get("input_text", ""),
                conversation_id=state.get("conversation_id")
            )
            
            # 1. 載入記憶
            if state.get("conversation_id"):
                memory = await self.memory_service.load_conversation_memory(state["conversation_id"])
                state["memory"] = memory
            else:
                state["memory"] = []
            ai_logger.log_memory_loaded(state["memory"])
            
            # 2. 深度對話理解（新增）
            state = await self.context_understanding(state)
            if state.get("context_understanding"):
                ai_logger.log_context_understanding(state["context_understanding"])
            
            # 3. 語意分析
            state = await self.semantic_analyzer(state)
            if state.get("semantic_analysis"):
                ai_logger.log_semantic_analysis(state["semantic_analysis"])
            
            # 4. 毒品安全檢查
            state = await self.drug_safety_check(state)
            ai_logger.log_drug_safety_check(
                is_safe=not state.get("has_drug_risk", False),
                warnings=state.get("risk_warnings", [])
            )
            
            # 5. 意圖路由
            state = await self.intent_router(state)
            ai_logger.log_intent_routing(
                need_knowledge=state.get("need_knowledge", False),
                category=state.get("intent_category", "unknown")
            )
            
            # 6. RAG 檢索（使用增強查詢）
            if state.get("need_knowledge") or state.get("context_understanding", {}).get("search_strategy", {}).get("should_search"):
                query = state.get("enhanced_query", state.get("input_text"))
                # 先執行檢索
                state = await self.rag_retrieval(state)
                # 再記錄結果
                ai_logger.log_rag_retrieval(
                    query=query,
                    filters=state.get("filters", {}),
                    results_count=len(state.get("retrieved_knowledge", [])),
                    similarity_threshold=0.3
                )
            else:
                state = await self.rag_retrieval(state)
            if state.get("retrieved_knowledge"):
                ai_logger.log_retrieved_knowledge(state["retrieved_knowledge"])
            
            # 7. 生成安全回應
            state = await self.safe_response_generator(state)
            ai_logger.log_response_generation(
                response=state.get("reply", ""),
                used_knowledge=len(state.get("retrieved_knowledge", [])) > 0
            )
            
            # 8. 驗證並優化回應（新增）
            if state.get("reply"):
                original_reply = state["reply"]
                validated_reply = await self.response_validator.validate_and_fix(state, state["reply"])
                state["reply"] = validated_reply
                
                ai_logger.log_response_validation(
                    is_valid=(original_reply == validated_reply),
                    modifications=None if original_reply == validated_reply else "Response modified"
                )
            
            # 9. 記錄對話
            state = await self.conversation_logger(state)
            
            # 記錄最終回應
            processing_time = time.time() - start_time
            ai_logger.log_final_response(
                final_response=state.get("reply", ""),
                processing_time=processing_time
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Workflow error: {str(e)}")
            ai_logger.log_error("WORKFLOW", e)
            state["error"] = str(e)
            state["reply"] = "抱歉，系統遇到問題。請稍後再試。"
            
            # 記錄錯誤的最終回應
            processing_time = time.time() - start_time
            ai_logger.log_final_response(
                final_response=state.get("reply", ""),
                processing_time=processing_time
            )
            return state


def create_chat_workflow():
    """建立聊天工作流程"""
    return SimpleChatWorkflow()