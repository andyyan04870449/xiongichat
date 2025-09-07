"""優化的工作流程 - 基於智能路由的自適應執行"""

from typing import Dict, Any, List
import logging
import time
from app.langgraph.state import WorkflowState
from app.config import settings
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
from app.langgraph.nodes.intelligent_router import IntelligentRouterNode
from app.services.memory import MemoryService
from app.services.response_validator import ResponseValidator
from app.utils.ai_logger import get_ai_logger

logger = logging.getLogger(__name__)


class OptimizedChatWorkflow:
    """優化的聊天工作流程 - 根據複雜度自適應執行"""
    
    def __init__(self):
        # 初始化節點
        self.intelligent_router = IntelligentRouterNode()  # 新的智能路由器
        self.context_understanding = ContextUnderstandingNode()
        self.semantic_analyzer = SemanticAnalyzerNode()
        self.drug_safety_check = DrugSafetyCheckNode()
        self.intent_router = IntentRouterNode()
        self.rag_retrieval = RAGRetrievalNode()
        self.safe_response_generator = SafeResponseGeneratorNode()
        self.response_validator = ResponseValidator()
        self.conversation_logger = ConversationLoggerNode()
        self.memory_service = MemoryService()
        
        logger.info("OptimizedChatWorkflow initialized with intelligent routing")
    
    async def ainvoke(self, state: WorkflowState) -> WorkflowState:
        """執行優化的工作流程"""
        start_time = time.time()
        ai_logger = get_ai_logger(state.get("session_id"))
        
        try:
            # 記錄請求開始
            ai_logger.log_request_start(
                user_id=state.get("user_id", "unknown"),
                message=state.get("input_text", ""),
                conversation_id=state.get("conversation_id")
            )
            
            # 1. 載入記憶（必須第一步）
            state = await self._load_memory(state, ai_logger)
            
            # 2. 智能路由分析（1次 LLM）
            state = await self.intelligent_router(state)
            routing_info = state.get("routing_info", {})
            complexity = state.get("complexity", "complex")
            
            ai_logger.log_routing_decision(
                complexity=complexity,
                confidence=routing_info.get("confidence", 0),
                factors=routing_info  # 傳遞完整的 routing_info
            )
            
            # 3. 根據複雜度執行對應流程
            if complexity == "simple":
                state = await self._execute_simple_flow(state, ai_logger)
            elif complexity == "moderate":
                state = await self._execute_moderate_flow(state, ai_logger)
            else:  # complex
                state = await self._execute_complex_flow(state, ai_logger)
            
            # 4. 記錄對話
            state = await self.conversation_logger(state)
            
            # 記錄最終回應
            processing_time = time.time() - start_time
            ai_logger.log_final_response(
                final_response=state.get("reply", ""),
                processing_time=processing_time
            )
            
            logger.info(
                f"Optimized workflow completed: "
                f"complexity={complexity}, "
                f"time={processing_time:.2f}s"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Optimized workflow error: {str(e)}")
            ai_logger.log_error("WORKFLOW", e)
            state["error"] = str(e)
            state["reply"] = "抱歉，系統遇到問題。請稍後再試。"
            
            processing_time = time.time() - start_time
            ai_logger.log_final_response(
                final_response=state.get("reply", ""),
                processing_time=processing_time
            )
            return state
    
    async def _load_memory(self, state: WorkflowState, ai_logger) -> WorkflowState:
        """載入對話記憶"""
        if state.get("conversation_id"):
            memory = await self.memory_service.load_conversation_memory(
                state["conversation_id"]
            )
            state["memory"] = memory if memory is not None else []
        else:
            state["memory"] = []
        
        # 確保memory不是None
        if state["memory"] is None:
            state["memory"] = []
            
        ai_logger.log_memory_loaded(state["memory"])
        return state
    
    async def _execute_simple_flow(self, state: WorkflowState, ai_logger) -> WorkflowState:
        """簡單流程：2次 LLM（路由 + 回應）"""
        logger.info("Executing simple flow")
        
        routing_info = state.get("routing_info", {})
        
        # 檢查是否真的簡單（無記憶依賴）
        if any(routing_info.get("memory_factors", {}).values()):
            logger.info("Memory factors detected, upgrading to moderate flow")
            return await self._execute_moderate_flow(state, ai_logger)
        
        # 簡單RAG檢索（如需要）
        if routing_info.get("content_analysis", {}).get("needs_factual_info"):
            state = await self.rag_retrieval(state)
            if state.get("retrieved_knowledge"):
                ai_logger.log_retrieved_knowledge(state["retrieved_knowledge"])
        
        # 直接生成回應（第2次 LLM）
        state = await self.safe_response_generator(state)
        ai_logger.log_response_generation(
            response=state.get("reply", ""),
            used_knowledge=len(state.get("retrieved_knowledge") or []) > 0
        )
        
        # 驗證回應
        if state.get("reply"):
            validated_reply = await self.response_validator.validate_and_fix(
                state, state["reply"]
            )
            state["reply"] = validated_reply
        
        return state
    
    async def _execute_moderate_flow(self, state: WorkflowState, ai_logger) -> WorkflowState:
        """中等流程：3次 LLM（路由 + 合併分析 + 回應）"""
        logger.info("Executing moderate flow")
        
        routing_info = state.get("routing_info", {})
        
        # 合併分析：上下文理解 + 語意分析（第2次 LLM）
        state = await self._combined_analysis(state, ai_logger)
        
        # 條件性毒品檢查（基於分析結果）
        if state.get("mentioned_substances") or routing_info.get("risk_signals", {}).get("has_drug_reference"):
            state = await self.drug_safety_check(state)
            ai_logger.log_drug_safety_check(
                is_safe=not state.get("has_drug_risk", False),
                warnings=state.get("risk_warnings", [])
            )
        
        # RAG檢索（如需要）
        if routing_info.get("required_processing", {}).get("need_knowledge_retrieval") or \
           state.get("need_knowledge"):
            state = await self.rag_retrieval(state)
            if state.get("retrieved_knowledge"):
                ai_logger.log_retrieved_knowledge(state["retrieved_knowledge"])
        
        # 生成回應（第3次 LLM）
        state = await self.safe_response_generator(state)
        ai_logger.log_response_generation(
            response=state.get("reply", ""),
            used_knowledge=len(state.get("retrieved_knowledge") or []) > 0
        )
        
        # 驗證回應
        if state.get("reply"):
            validated_reply = await self.response_validator.validate_and_fix(
                state, state["reply"]
            )
            state["reply"] = validated_reply
        
        return state
    
    async def _execute_complex_flow(self, state: WorkflowState, ai_logger) -> WorkflowState:
        """複雜流程：4-5次 LLM（完整原始流程）"""
        logger.info("Executing complex flow - full analysis")
        
        # 執行完整的分析鏈
        
        # 深度對話理解（第2次 LLM）
        state = await self.context_understanding(state)
        if state.get("context_understanding"):
            ai_logger.log_context_understanding(state["context_understanding"])
        
        # 語意分析（第3次 LLM）
        state = await self.semantic_analyzer(state)
        if state.get("semantic_analysis"):
            ai_logger.log_semantic_analysis(state["semantic_analysis"])
        
        # 毒品安全檢查
        state = await self.drug_safety_check(state)
        ai_logger.log_drug_safety_check(
            is_safe=not state.get("has_drug_risk", False),
            warnings=state.get("risk_warnings", [])
        )
        
        # 意圖路由（第4次 LLM）
        state = await self.intent_router(state)
        ai_logger.log_intent_routing(
            need_knowledge=state.get("need_knowledge", False),
            category=state.get("intent_category", "unknown")
        )
        
        # RAG檢索
        if state.get("need_knowledge") or \
           state.get("context_understanding", {}).get("search_strategy", {}).get("should_search"):
            state = await self.rag_retrieval(state)
            if state.get("retrieved_knowledge"):
                ai_logger.log_retrieved_knowledge(state["retrieved_knowledge"])
        
        # 生成安全回應（第5次 LLM）
        state = await self.safe_response_generator(state)
        ai_logger.log_response_generation(
            response=state.get("reply", ""),
            used_knowledge=len(state.get("retrieved_knowledge") or []) > 0
        )
        
        # 驗證並優化回應
        if state.get("reply"):
            validated_reply = await self.response_validator.validate_and_fix(
                state, state["reply"]
            )
            state["reply"] = validated_reply
            
            ai_logger.log_response_validation(
                is_valid=(state["reply"] == validated_reply),
                modifications=None if state["reply"] == validated_reply else "Response modified"
            )
        
        return state
    
    async def _combined_analysis(self, state: WorkflowState, ai_logger) -> WorkflowState:
        """合併的分析節點（用於中等複雜度）"""
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage, SystemMessage
        import json
        from app.config import settings
        
        llm = ChatOpenAI(
            model=settings.openai_model_analysis,  # 使用mini模型進行分析
            temperature=0.1,
            api_key=settings.openai_api_key,
            model_kwargs={
                "response_format": {"type": "json_object"}
            }
        )
        
        routing_info = state.get("routing_info", {})
        memory = state.get("memory", [])
        
        # 構建合併分析提示
        prompt = f"""
基於完整對話歷史進行綜合分析：

【對話歷史】
{self._format_memory(memory)}

【當前輸入】
{state['input_text']}

【路由資訊】
複雜度：{routing_info.get('complexity')}
風險信號：{routing_info.get('risk_signals')}
記憶因素：{routing_info.get('memory_factors')}

請進行綜合分析並返回JSON：
{{
    "semantic_analysis": {{
        "mentioned_substances": [],
        "user_intent": "獲取物質/尋求幫助/情緒抒發/詢問資訊/閒聊/其他",
        "emotional_state": "正面/中性/負面/焦慮/憂鬱",
        "risk_indicators": []
    }},
    "context_understanding": {{
        "entities": {{}},
        "pronouns_resolution": {{}},
        "topic_flow": "",
        "search_query": "",
        "user_intent": {{
            "category": "資訊查詢/尋求幫助/情感支持/自我介紹/閒聊/其他",
            "specific": "具體意圖描述（例如：介紹自己的名字、詢問天氣、表達情緒等）",
            "confidence": 0.0-1.0
        }},
        "information_needs": {{
            "explicit": "用戶明確表達的資訊需求（如果沒有，填'無'）",
            "implicit": "可能的隱含需求（如果沒有，填'無'）",
            "priority": "最優先的需求類型（社交互動/資訊獲取/情感支持/無）"
        }}
    }},
    "crisis_assessment": {{
        "crisis_level": "none/low/medium/high",
        "crisis_indicators": [],
        "immediate_risk": true/false,
        "intervention_needed": true/false,
        "reasoning": "評估理由"
    }},
    "need_knowledge": true/false,
    "intent_category": "服務資訊/法律條文/醫療資源/一般對話"
}}

【重要：知識需求判斷規則】
必須設定 need_knowledge: true 的情況：
1. 詢問任何地點、地址、位置、怎麼去、在哪裡、哪裡
2. 詢問電話、聯絡方式、Line、email、信箱、怎麼聯絡
3. 詢問時間、幾點、星期幾、營業時間、服務時間、什麼時候
4. 詢問費用、價格、收費、多少錢、要錢嗎
5. 詢問具體機構名稱（醫院、診所、中心、防制局、單位）
6. 詢問具體人名、醫生、專家、負責人、誰負責
7. 詢問具體服務內容、流程、如何申請、怎麼辦理

關鍵詞檢測規則：
- 出現「哪裡」「在哪」「位置」「地址」「怎麼去」→ need_knowledge: true
- 出現「電話」「聯絡」「號碼」「打給」→ need_knowledge: true
- 出現「幾點」「時間」「什麼時候」「營業」→ need_knowledge: true
- 出現「多少錢」「費用」「價格」「收費」→ need_knowledge: true
- 出現「醫院」「診所」「中心」「局」「單位」→ need_knowledge: true
- 出現「凱旋」「毒防」「防制」等機構關鍵字 → need_knowledge: true

只有以下情況可設定 need_knowledge: false：
- 純粹情感表達（我很難過、壓力大、睡不著）
- 社交互動（你好、謝謝、再見、我是XXX）
- 一般閒聊（今天天氣、最近如何）

【危機評估標準】
crisis_level 判斷規則：
- none: 一般對話、社交互動、單純詢問資訊
- low: 輕微壓力、輕度負面情緒、初步尋求支持
- medium: 明顯情緒困擾、成癮相關諮詢、家人擔憂、尋求專業協助
- high: 自傷暗示、極度絕望、立即危險、明確求救信號

crisis_indicators 包括但不限於：
- 「想不開」「撐不下去」「消失」「結束」→ 自傷風險
- 「沒有希望」「沒有意義」「活著很痛苦」→ 絕望感
- 「控制不住」「停不下來」「越來越嚴重」→ 失控感
- 「需要幫助」「救救我」「怎麼辦」→ 求助信號
- 情緒累積：多輪對話中負面情緒逐漸加重

重要：當 crisis_level 為 medium 或 high 時：
- 必須設定 need_knowledge: true（需要提供專業資源）
- intervention_needed: true（需要主動介入）

重要提醒：
1. user_intent 和 information_needs 必須填充實際內容，不能為空物件
2. 即使是簡單的打招呼或自我介紹，也要識別其意圖（如：社交互動）
3. 沒有明確資訊需求時，information_needs.priority 應填"社交互動"或"情感支持"
4. 解析所有代詞指向
5. 識別話題演變
6. 追蹤情緒變化
7. 檢測任何毒品相關暗示
8. 寧可多設 need_knowledge: true，也不要遺漏需要事實資訊的查詢
9. 危機評估要考慮整體對話脈絡，不只看單一訊息
"""
        
        messages = [
            SystemMessage(content="你是專業的對話分析系統，擅長理解上下文和識別風險。"),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = await llm.ainvoke(messages)
            analysis = json.loads(response.content)
            
            # 更新狀態
            state["semantic_analysis"] = analysis.get("semantic_analysis", {})
            
            # 確保 context_understanding 包含完整的結構
            context_understanding = analysis.get("context_understanding", {})
            # 如果 user_intent 或 information_needs 缺失或為空，設置預設值
            if not context_understanding.get("user_intent") or context_understanding.get("user_intent") == {}:
                context_understanding["user_intent"] = {
                    "category": "閒聊",
                    "specific": "一般對話",
                    "confidence": 0.5
                }
            if not context_understanding.get("information_needs") or context_understanding.get("information_needs") == {}:
                context_understanding["information_needs"] = {
                    "explicit": "無",
                    "implicit": "無",
                    "priority": "社交互動"
                }
            state["context_understanding"] = context_understanding
            
            # 處理危機評估
            crisis_assessment = analysis.get("crisis_assessment", {})
            state["crisis_assessment"] = crisis_assessment
            state["crisis_level"] = crisis_assessment.get("crisis_level", "none")
            
            # 記錄危機評估
            if crisis_assessment and state["crisis_level"] != "none":
                ai_logger.log_crisis_assessment(
                    crisis_level=state["crisis_level"],
                    indicators=crisis_assessment.get("crisis_indicators", []),
                    intervention_needed=crisis_assessment.get("intervention_needed", False)
                )
            
            # 如果危機等級為 medium 或 high，強制需要知識檢索
            if state["crisis_level"] in ["medium", "high"]:
                state["need_knowledge"] = True
                logger.info(f"Crisis level {state['crisis_level']} detected, forcing knowledge retrieval")
            
            state["mentioned_substances"] = analysis["semantic_analysis"].get("mentioned_substances", [])
            state["user_intent"] = analysis["semantic_analysis"].get("user_intent", "unknown")
            state["emotional_state"] = analysis["semantic_analysis"].get("emotional_state", "neutral")
            state["need_knowledge"] = analysis.get("need_knowledge", False) or state.get("need_knowledge", False)
            state["intent_category"] = analysis.get("intent_category", "一般對話")
            
            if analysis["context_understanding"].get("search_query"):
                state["enhanced_query"] = analysis["context_understanding"]["search_query"]
            
            ai_logger.log_combined_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Combined analysis error: {str(e)}")
            # 設定安全預設值
            state["semantic_analysis"] = {}
            state["mentioned_substances"] = []
            state["user_intent"] = "unclear"
            state["emotional_state"] = "neutral"
        
        return state
    
    def _format_memory(self, memory: List[Dict]) -> str:
        """格式化對話歷史"""
        if not memory:
            return "（無歷史對話）"
        
        formatted = []
        # 確保memory不是None
        if memory is None:
            return "（無歷史對話）"
            
        recent_memory = memory[-6:] if len(memory) > 6 else memory
        for msg in recent_memory:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                role = "用戶" if msg["role"] == "user" else "助理"
                formatted.append(f"{role}：{msg['content']}")
        
        return "\n".join(formatted) if formatted else "（無歷史對話）"


def create_optimized_workflow():
    """建立優化的聊天工作流程"""
    return OptimizedChatWorkflow()