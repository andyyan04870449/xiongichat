"""重構的簡化工作流程 - 兩階段架構"""

from typing import Dict, Any
import logging
import time
from app.langgraph.state import WorkflowState
from app.langgraph.nodes.unified_analyzer import UnifiedAnalyzerNode
from app.langgraph.nodes.rag_retrieval import RAGRetrievalNode
from app.langgraph.nodes.intelligent_response_generator import IntelligentResponseGeneratorNode
from app.langgraph.nodes.conversation_logger import ConversationLoggerNode
from app.services.memory import MemoryService
from app.services.drug_checker import DrugChecker
from app.utils.ai_logger import get_ai_logger

logger = logging.getLogger(__name__)


class RefactoredChatWorkflow:
    """重構的聊天工作流程 - 簡化為兩階段處理"""
    
    def __init__(self):
        # 初始化核心節點
        self.unified_analyzer = UnifiedAnalyzerNode()  # 統一分析
        self.rag_retrieval = RAGRetrievalNode()  # RAG檢索
        self.response_generator = IntelligentResponseGeneratorNode()  # 智能生成
        self.conversation_logger = ConversationLoggerNode()  # 對話記錄
        self.memory_service = MemoryService()  # 記憶管理
        self.drug_checker = DrugChecker()  # 快速毒品檢查
        
        logger.info("RefactoredChatWorkflow initialized with 2-phase architecture")
    
    async def ainvoke(self, state: WorkflowState) -> WorkflowState:
        """執行簡化的工作流程"""
        start_time = time.time()
        ai_logger = get_ai_logger(state.get("session_id"))
        
        try:
            # 記錄請求開始
            ai_logger.log_request_start(
                user_id=state.get("user_id", "unknown"),
                message=state.get("input_text", ""),
                conversation_id=state.get("conversation_id")
            )
            
            # ========== Phase 0: 預處理 ==========
            # 載入記憶（必須）
            state = await self._load_memory(state, ai_logger)
            
            # 快速毒品檢查（規則基礎，不用LLM）
            drug_keywords = self.drug_checker.quick_check(state["input_text"])
            if drug_keywords:
                state["detected_drug_keywords"] = drug_keywords
                logger.info(f"Quick drug check found keywords: {drug_keywords}")
            
            # ========== Phase 1: 統一分析（1次LLM）==========
            logger.info("Phase 1: Unified Analysis")
            state = await self.unified_analyzer(state)
            
            analysis = state.get("unified_analysis", {})
            ai_logger.log_unified_analysis(
                intent=analysis.get("intent", {}),
                risk=analysis.get("risk", {}),
                emotional=analysis.get("emotional", {}),
                strategy=analysis.get("strategy", {})
            )
            
            # ========== Phase 1.5: 條件性RAG檢索 ==========
            if state.get("need_knowledge", False):
                logger.info("Phase 1.5: RAG Retrieval")
                state = await self.rag_retrieval(state)
                
                if state.get("retrieved_knowledge"):
                    ai_logger.log_rag_retrieval(
                        query=state.get("enhanced_query", state["input_text"]),
                        results_count=len(state["retrieved_knowledge"]),
                        similarity_threshold=0.3
                    )
            
            # ========== Phase 2: 智能生成（1次LLM）==========
            logger.info("Phase 2: Intelligent Response Generation")
            state = await self.response_generator(state)
            
            ai_logger.log_response_generation(
                response=state.get("reply", ""),
                strategy=state.get("response_strategy", ""),
                used_knowledge=len(state.get("retrieved_knowledge", [])) > 0
            )
            
            # ========== Phase 3: 後處理 ==========
            # 記錄對話
            state = await self.conversation_logger(state)
            
            # 記錄最終回應
            processing_time = time.time() - start_time
            ai_logger.log_final_response(
                final_response=state.get("reply", ""),
                processing_time=processing_time,
                llm_calls=2 if not state.get("need_knowledge") else 2,
                workflow_version="refactored_v2"
            )
            
            logger.info(
                f"Refactored workflow completed in {processing_time:.2f}s "
                f"(Analysis: 1 LLM, Generation: 1 LLM, RAG: {state.get('need_knowledge', False)})"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Refactored workflow error: {str(e)}")
            ai_logger.log_error("WORKFLOW", e)
            state["error"] = str(e)
            state["reply"] = "抱歉，系統遇到問題。請稍後再試。"
            
            processing_time = time.time() - start_time
            ai_logger.log_final_response(
                final_response=state.get("reply", ""),
                processing_time=processing_time,
                error=True
            )
            return state
    
    async def _load_memory(self, state: WorkflowState, ai_logger) -> WorkflowState:
        """載入對話記憶"""
        if state.get("conversation_id"):
            memory = await self.memory_service.load_conversation_memory(
                state["conversation_id"]
            )
            state["memory"] = memory if memory else []
        else:
            state["memory"] = []
        
        ai_logger.log_memory_loaded(
            memory_count=len(state["memory"]),
            conversation_id=state.get("conversation_id")
        )
        
        logger.info(f"Loaded {len(state['memory'])} messages from memory")
        return state


class DrugChecker:
    """快速毒品關鍵詞檢查器（規則基礎）"""
    
    def __init__(self):
        # 管制物質關鍵詞
        self.drug_keywords = {
            "一級毒品": ["海洛因", "嗎啡", "鴉片", "古柯鹼", "海洛英"],
            "二級毒品": ["安非他命", "安非他明", "大麻", "搖頭丸", "MDMA", "冰毒"],
            "三級毒品": ["K他命", "愷他命", "FM2", "小白板", "紅中", "青發"],
            "俗稱": ["毒品", "藥", "貨", "東西", "料子", "飯", "糖果"]
        }
    
    def quick_check(self, text: str) -> List[str]:
        """快速檢查文本中的毒品關鍵詞"""
        detected = []
        text_lower = text.lower()
        
        for category, keywords in self.drug_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    detected.append(keyword)
        
        return detected


def create_refactored_workflow():
    """建立重構的聊天工作流程"""
    return RefactoredChatWorkflow()