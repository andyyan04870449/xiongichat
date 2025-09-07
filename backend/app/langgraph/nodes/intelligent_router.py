"""智能路由器節點 - 根據對話複雜度決定執行流程"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import logging

from app.config import settings
from app.langgraph.state import WorkflowState

logger = logging.getLogger(__name__)


class IntelligentRouterNode:
    """智能路由器 - 評估對話複雜度並決定執行路徑"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model_chat,
            temperature=0.1,
            api_key=settings.openai_api_key,
            model_kwargs={
                "response_format": {"type": "json_object"}
            }
        )
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行路由分析"""
        try:
            # 構建包含記憶的分析提示
            analysis_prompt = self._build_routing_prompt(
                state["input_text"],
                state.get("memory", [])
            )
            
            messages = [
                SystemMessage(content=INTELLIGENT_ROUTING_PROMPT),
                HumanMessage(content=analysis_prompt)
            ]
            
            # 執行路由分析
            logger.info(f"Performing intelligent routing for user {state['user_id']}")
            response = await self.llm.ainvoke(messages)
            
            # 解析結果
            try:
                routing_result = json.loads(response.content)
                
                # 根據記憶因素調整複雜度
                routing_result = self._adjust_complexity_by_memory(
                    routing_result, 
                    state.get("memory", [])
                )
                
                # 更新狀態
                state["routing_info"] = routing_result
                state["complexity"] = routing_result["complexity"]
                
                logger.info(
                    f"Routing completed: complexity={routing_result['complexity']}, "
                    f"confidence={routing_result.get('confidence')}"
                )
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse routing result: {e}")
                # 安全降級到複雜流程
                state["complexity"] = "complex"
                state["routing_info"] = {"complexity": "complex", "error": str(e)}
            
        except Exception as e:
            logger.error(f"IntelligentRouter error: {str(e)}")
            # 錯誤時使用完整流程確保安全
            state["complexity"] = "complex"
            state["routing_info"] = {"complexity": "complex", "error": str(e)}
        
        return state
    
    def _format_memory(self, memory: List[Dict]) -> str:
        """格式化對話歷史"""
        if not memory:
            return "（無歷史對話）"
        
        formatted = []
        recent_memory = memory[-10:] if len(memory) > 10 else memory
        
        for idx, msg in enumerate(recent_memory):
            role = "用戶" if msg["role"] == "user" else "助理"
            formatted.append(f"{role}：{msg['content']}")
        
        return "\n".join(formatted)
    
    def _build_routing_prompt(self, input_text: str, memory: List[Dict]) -> str:
        """構建路由分析提示"""
        memory_context = self._format_memory(memory)
        memory_length = len(memory)
        
        return f"""
分析當前輸入與歷史對話，判斷處理複雜度：

【對話歷史】共{memory_length}條
{memory_context}

【當前輸入】
{input_text}

請進行全面評估並返回JSON格式：
{{
    "complexity": "simple/moderate/complex",
    "reasoning": "判斷理由",
    
    "memory_factors": {{
        "has_pronoun_reference": true/false,
        "topic_continuation": true/false,
        "emotional_buildup": true/false,
        "progressive_disclosure": true/false,
        "conversation_rounds": {memory_length}
    }},
    
    "risk_signals": {{
        "has_drug_reference": true/false,
        "has_emotional_distress": true/false,
        "has_safety_concern": true/false,
        "has_crisis_indicators": true/false
    }},
    
    "content_analysis": {{
        "is_greeting": true/false,
        "needs_factual_info": true/false,
        "needs_emotional_support": true/false,
        "is_general_chat": true/false,
        "mentioned_substances": [],
        "emotional_state": "positive/neutral/negative/distressed"
    }},
    
    "required_processing": {{
        "need_deep_analysis": true/false,
        "need_context_understanding": true/false,
        "need_semantic_analysis": true/false,
        "need_drug_safety_check": true/false,
        "need_knowledge_retrieval": true/false
    }},
    
    "context_summary": "對話脈絡摘要",
    "risk_level": "none/low/medium/high",
    "suggested_strategy": "direct/supportive/educational/preventive/crisis",
    "confidence": 0.0-1.0
}}

判斷標準：
- simple: 簡單問候、基本閒聊、純社交互動（無需查詢資料、無歷史依賴、無風險信號）
- moderate: 一般對話、需要查詢資訊、輕度情緒支持、簡單諮詢、有歷史參照
- complex: 涉及毒品、心理危機、複雜上下文、多輪深度對話、低信心度

重要規則：
1. 如果memory_factors有任何true → complexity不能是simple
2. 如果risk_signals有任何true → complexity至少是moderate
3. 如果對話超過5輪且情緒負面 → complexity必須是complex
4. 如果confidence < 0.7 → complexity升級一級
5. 任何毒品相關內容 → complexity必須是complex
6. 如果needs_factual_info=true → complexity至少是moderate（需要知識檢索）
"""
    
    def _adjust_complexity_by_memory(self, routing: Dict, memory: List[Dict]) -> Dict:
        """根據記憶因素調整複雜度"""
        
        # 需要事實資訊查詢自動升級
        content_analysis = routing.get("content_analysis", {})
        if content_analysis.get("needs_factual_info") and routing["complexity"] == "simple":
            routing["complexity"] = "moderate"
            routing["adjustment_reason"] = "Needs factual information"
        
        # 長對話自動升級
        if len(memory) > 10 and routing["complexity"] == "simple":
            routing["complexity"] = "moderate"
            routing["adjustment_reason"] = "Long conversation history"
        
        # 記憶因素檢查
        memory_factors = routing.get("memory_factors", {})
        if any(memory_factors.values()) and routing["complexity"] == "simple":
            routing["complexity"] = "moderate"
            routing["adjustment_reason"] = "Memory dependencies detected"
        
        # 風險信號檢查
        risk_signals = routing.get("risk_signals", {})
        if any(risk_signals.values()):
            if routing["complexity"] == "simple":
                routing["complexity"] = "moderate"
            routing["adjustment_reason"] = "Risk signals detected"
        
        # 信心度檢查
        if routing.get("confidence", 1.0) < 0.7:
            if routing["complexity"] == "simple":
                routing["complexity"] = "moderate"
            elif routing["complexity"] == "moderate":
                routing["complexity"] = "complex"
            routing["adjustment_reason"] = "Low confidence"
        
        # 情緒累積檢查
        if self._detect_emotional_buildup(memory) and routing["complexity"] != "complex":
            routing["complexity"] = "complex"
            routing["adjustment_reason"] = "Emotional buildup detected"
        
        return routing
    
    def _detect_emotional_buildup(self, memory: List[Dict]) -> bool:
        """檢測情緒累積"""
        if len(memory) < 4:
            return False
        
        # 檢查最近的對話是否有負面情緒關鍵詞累積
        negative_keywords = [
            "壓力", "睡不著", "難過", "憂鬱", "焦慮", "害怕",
            "撐不下去", "沒希望", "想放棄", "累", "煩", "痛苦"
        ]
        
        recent_messages = memory[-6:]
        negative_count = 0
        
        for msg in recent_messages:
            if msg["role"] == "user":
                content = msg["content"]
                if any(keyword in content for keyword in negative_keywords):
                    negative_count += 1
        
        return negative_count >= 2  # 最近6條中有2條以上負面


# 系統提示詞
INTELLIGENT_ROUTING_PROMPT = """你是一個專業的對話複雜度分析系統，負責評估對話的處理需求。

核心任務：
1. 分析當前輸入與完整對話歷史
2. 識別所有風險信號和記憶依賴
3. 判斷需要的處理深度
4. 決定最適合的執行流程

分析要點：
- 代詞解析：識別「他」「那個」「這個」等指代
- 話題連續：判斷是否延續之前的話題
- 情緒追蹤：觀察情緒的累積和變化
- 風險評估：識別毒品、自傷、危機信號
- 知識需求：判斷是否需要查詢知識庫

請保持高度敏感性，寧可高估複雜度也不要低估風險。"""