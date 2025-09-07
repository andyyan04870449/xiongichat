"""統一分析節點 - 整合所有理解與分析功能"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import logging

from app.config import settings
from app.langgraph.state import WorkflowState

logger = logging.getLogger(__name__)


class UnifiedAnalyzerNode:
    """統一分析節點 - 一次LLM調用完成所有分析"""
    
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
        """執行統一分析"""
        try:
            # 構建綜合分析提示
            analysis_prompt = self._build_comprehensive_prompt(
                state["input_text"],
                state.get("memory", [])
            )
            
            messages = [
                SystemMessage(content=UNIFIED_ANALYSIS_PROMPT),
                HumanMessage(content=analysis_prompt)
            ]
            
            # 執行一次性深度分析
            logger.info(f"Performing unified analysis for user {state['user_id']}")
            response = await self.llm.ainvoke(messages)
            
            # 解析並更新狀態
            try:
                analysis = json.loads(response.content)
                
                # 更新所有分析結果到狀態
                state["unified_analysis"] = analysis
                
                # 提取關鍵信息到頂層（為了兼容性）
                state["user_intent"] = analysis["intent"]["category"]
                state["emotional_state"] = analysis["emotional"]["current_state"]
                state["risk_level"] = analysis["risk"]["level"]
                state["need_knowledge"] = analysis["knowledge"]["need_retrieval"]
                
                # 設置增強查詢
                if analysis["knowledge"].get("search_query"):
                    state["enhanced_query"] = analysis["knowledge"]["search_query"]
                
                # 提取提及的物質
                if analysis["risk"].get("mentioned_substances"):
                    state["mentioned_substances"] = analysis["risk"]["mentioned_substances"]
                
                # 設置回應策略
                state["response_strategy"] = analysis["strategy"]["approach"]
                
                logger.info(
                    f"Unified analysis completed: "
                    f"intent={analysis['intent']['category']}, "
                    f"risk={analysis['risk']['level']}, "
                    f"strategy={analysis['strategy']['approach']}"
                )
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse unified analysis: {e}")
                # 設置安全預設值
                state["unified_analysis"] = self._get_default_analysis()
                state["risk_level"] = "unknown"
                state["need_knowledge"] = False
            
        except Exception as e:
            logger.error(f"UnifiedAnalyzer error: {str(e)}")
            state["unified_analysis"] = self._get_default_analysis()
            state["error"] = str(e)
        
        return state
    
    def _build_comprehensive_prompt(self, input_text: str, memory: List[Dict]) -> str:
        """構建綜合分析提示"""
        conversation = self._format_conversation(memory)
        
        return f"""
請對以下對話進行全面分析：

【對話歷史】
{conversation}

【當前輸入】
{input_text}

請進行深度綜合分析並返回JSON格式：
{{
    "context": {{
        "entities": {{
            "people": ["識別的人物"],
            "locations": ["提到的地點"],
            "organizations": ["提到的機構"],
            "substances": ["提到的物質"],
            "topics": ["討論的主題"]
        }},
        "pronouns": {{
            "resolution": {{"代詞": "指向的實體"}},
            "ambiguous": ["無法確定的代詞"]
        }},
        "temporal": {{
            "references": ["時間參照"],
            "continuity": "是否延續前話題"
        }}
    }},
    
    "intent": {{
        "category": "資訊查詢/尋求幫助/情感支持/閒聊/其他",
        "specific": "具體意圖描述",
        "confidence": 0.0-1.0
    }},
    
    "emotional": {{
        "current_state": "positive/neutral/negative/anxious/depressed",
        "intensity": "low/medium/high",
        "trajectory": "improving/stable/deteriorating",
        "support_needed": true/false
    }},
    
    "risk": {{
        "level": "none/low/medium/high",
        "mentioned_substances": ["提及的管制物質"],
        "crisis_indicators": ["危機指標"],
        "immediate_concern": true/false
    }},
    
    "knowledge": {{
        "need_retrieval": true/false,
        "search_query": "最佳搜索查詢",
        "search_scope": "narrow/broad",
        "expected_info": "預期需要的資訊類型"
    }},
    
    "strategy": {{
        "approach": "informative/supportive/preventive/crisis/casual",
        "tone": "professional/friendly/empathetic/serious",
        "key_points": ["回應要點"],
        "avoid": ["應避免的內容"]
    }},
    
    "summary": "對話核心需求的簡短摘要"
}}

分析原則：
1. 深入理解上下文關係
2. 準確解析所有指代
3. 識別情緒和風險信號
4. 判斷知識需求
5. 制定回應策略

必須返回有效的JSON格式。
"""
    
    def _format_conversation(self, memory: List[Dict]) -> str:
        """格式化對話歷史"""
        if not memory:
            return "（無歷史對話）"
        
        formatted = []
        # 只取最近的對話避免prompt過長
        recent_memory = memory[-10:] if len(memory) > 10 else memory
        
        for msg in recent_memory:
            role = "用戶" if msg.get("role") == "user" else "助理"
            content = msg.get("content", "")
            formatted.append(f"{role}：{content}")
        
        return "\n".join(formatted)
    
    def _get_default_analysis(self) -> Dict:
        """返回預設分析結果"""
        return {
            "context": {"entities": {}, "pronouns": {}},
            "intent": {"category": "其他", "confidence": 0.5},
            "emotional": {"current_state": "neutral", "support_needed": False},
            "risk": {"level": "unknown", "immediate_concern": False},
            "knowledge": {"need_retrieval": False},
            "strategy": {"approach": "casual", "tone": "friendly"},
            "summary": "無法完成分析"
        }


# 系統提示詞
UNIFIED_ANALYSIS_PROMPT = """你是一個專業的對話分析系統，需要在一次分析中完成所有理解任務。

核心能力：
1. 上下文理解：追蹤實體、解析代詞、理解話題演變
2. 意圖識別：準確判斷用戶的真實需求
3. 情緒評估：識別情緒狀態和支持需求
4. 風險檢測：發現毒品相關和危機信號
5. 知識判斷：決定是否需要檢索外部知識
6. 策略制定：為回應生成提供明確指引

重要原則：
- 整體理解：將所有分析視為一個整體，避免片面判斷
- 深度洞察：不只看表面，理解深層需求
- 風險敏感：對任何風險信號保持警覺
- 策略清晰：提供具體可執行的回應建議

請確保分析全面、準確、可操作。"""