"""語意分析節點 - 理解用戶輸入的深層含義"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import logging

from app.config import settings
from app.langgraph.state import WorkflowState

logger = logging.getLogger(__name__)


class SemanticAnalyzerNode:
    """語意分析節點 - 不依賴關鍵字，純粹理解語意"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model_analysis,  # 使用mini模型進行語義分析
            temperature=0.1,  # 低溫度確保分析穩定
            api_key=settings.openai_api_key,
            model_kwargs={
                "response_format": {"type": "json_object"}  # 強制JSON格式輸出
            }
        )
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行語意分析"""
        try:
            # 構建分析提示
            analysis_prompt = self._build_analysis_prompt(
                state["input_text"],
                state.get("memory", [])
            )
            
            messages = [
                SystemMessage(content=SEMANTIC_ANALYSIS_PROMPT),
                HumanMessage(content=analysis_prompt)
            ]
            
            # 執行語意分析
            logger.info(f"Performing semantic analysis for user {state['user_id']}")
            response = await self.llm.ainvoke(messages)
            
            # 解析結果
            try:
                analysis_result = json.loads(response.content)
                
                # 更新狀態
                state["semantic_analysis"] = analysis_result
                state["mentioned_substances"] = analysis_result.get("mentioned_substances", [])
                state["user_intent"] = analysis_result.get("user_intent", "unknown")
                state["emotional_state"] = analysis_result.get("emotional_state", "neutral")
                
                # 處理危機評估
                crisis_assessment = analysis_result.get("crisis_assessment", {})
                state["crisis_assessment"] = crisis_assessment
                state["crisis_level"] = crisis_assessment.get("crisis_level", "none")
                
                # 如果危機等級為 medium 或 high，標記需要知識檢索
                if state["crisis_level"] in ["medium", "high"]:
                    state["need_knowledge"] = True
                    logger.info(f"Crisis level {state['crisis_level']} detected in semantic analysis")
                    
                # 記錄危機評估到 AI 日誌（如果有）
                if crisis_assessment and state["crisis_level"] != "none":
                    try:
                        from app.utils.ai_logger import get_ai_logger
                        ai_logger = get_ai_logger()
                        if ai_logger:
                            ai_logger.log_crisis_assessment(
                                crisis_level=state["crisis_level"],
                                indicators=crisis_assessment.get("crisis_indicators", []),
                                intervention_needed=crisis_assessment.get("intervention_needed", False)
                            )
                    except:
                        pass  # 日誌失敗不影響主流程
                
                logger.info(f"Semantic analysis completed: intent={state['user_intent']}, emotion={state['emotional_state']}, crisis={state['crisis_level']}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse semantic analysis: {e}")
                # 設定預設值
                state["semantic_analysis"] = {}
                state["mentioned_substances"] = []
                state["user_intent"] = "unclear"
                state["emotional_state"] = "neutral"
            
        except Exception as e:
            logger.error(f"SemanticAnalyzer error: {str(e)}")
            # 錯誤時設定安全預設值
            state["semantic_analysis"] = {"error": str(e)}
            state["mentioned_substances"] = []
            state["user_intent"] = "error"
            state["emotional_state"] = "neutral"
        
        return state
    
    def _build_analysis_prompt(self, input_text: str, memory: List[Dict]) -> str:
        """構建分析提示，包含上下文"""
        
        # 提取最近的對話歷史
        recent_context = ""
        if memory and len(memory) > 0:
            recent_messages = memory[-4:]  # 最近2輪對話
            for msg in recent_messages:
                role = "用戶" if msg["role"] == "user" else "助理"
                recent_context += f"{role}：{msg['content']}\n"
        
        return f"""
請分析以下對話內容：

最近對話歷史：
{recent_context if recent_context else "（無歷史對話）"}

當前用戶輸入：「{input_text}」

必須返回有效的 JSON 格式，不要包含任何其他文字或markdown標記。
請深入分析並返回：
{{
    "mentioned_substances": ["提及的物質名稱列表，包含可能的俗名、暗語"],
    "user_intent": "獲取物質/尋求幫助/情緒抒發/詢問資訊/閒聊/其他",
    "emotional_state": "正面/中性/負面/焦慮/憂鬱/憤怒/絕望",
    "crisis_assessment": {{
        "crisis_level": "none/low/medium/high",
        "crisis_indicators": ["具體的危機指標"],
        "immediate_risk": true/false,
        "intervention_needed": true/false,
        "reasoning": "評估理由"
    }},
    "context_clues": ["有助於理解的上下文線索"],
    "risk_indicators": ["任何風險指標，如自傷、違法意圖等"],
    "needs_support": true/false,
    "topic": "主要討論主題"
}}

【危機評估標準】
crisis_level 判斷：
- none: 一般對話、單純詢問資訊
- low: 輕微壓力、輕度負面情緒
- medium: 明顯困擾、成癮相關、尋求幫助
- high: 自傷暗示、極度絕望、立即危險

crisis_indicators 包括：
- 「想不開」「撐不下去」「消失」→ 自傷風險
- 「沒希望」「活不下去」「不想活」→ 絕望感
- 「控制不住」「停不下來」→ 失控感
- 多輪對話中負面情緒累積
"""


# 語意分析系統提示詞
SEMANTIC_ANALYSIS_PROMPT = """你是一個專業的語意分析系統，專門分析毒品防制相關對話。

分析原則：
1. 不要被表面文字誤導，理解深層含義
2. 注意俗語、暗語、隱喻的使用
3. 考慮上下文的影響
4. 識別情緒狀態和潛在需求
5. 偵測任何風險信號

物質識別注意事項：
- 毒品有許多俗名（如：冰塊、糖果、K仔、安公子等）
- 注意模糊或間接的表達方式
- 考慮語境中的暗示

意圖判斷要點：
- 區分「想要獲取」vs「尋求幫助」vs「純粹好奇」
- 注意隱藏在其他話題下的真實需求
- 識別求助信號，即使表達不直接

請保持客觀、專業的分析，不做道德判斷。"""