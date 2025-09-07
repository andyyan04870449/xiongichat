"""意圖路由節點 - 判斷是否需要查詢知識庫"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import logging

from app.config import settings
from app.langgraph.state import WorkflowState
from app.langgraph.prompts import ROUTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class IntentRouterNode:
    """意圖路由節點 - 分析使用者輸入判斷是否需要查詢知識庫"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model_analysis,  # 使用mini模型進行路由分類
            temperature=0,  # 使用較低溫度確保穩定分類
            api_key=settings.openai_api_key,
            model_kwargs={
                "response_format": {"type": "json_object"}  # 強制JSON格式輸出
            }
        )
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行節點邏輯"""
        try:
            # 構建分析提示
            analysis_prompt = f"""
分析以下使用者輸入，判斷是否需要查詢知識庫：

使用者輸入：{state["input_text"]}

必須返回有效的 JSON 格式，不要包含任何其他文字或markdown標記。
請返回：
{{
    "need_knowledge": true/false,
    "category": "服務資訊/法律條文/醫療資源/替代療法/社會資源/一般對話",
    "reason": "判斷原因"
}}
"""
            
            messages = [
                SystemMessage(content=ROUTER_SYSTEM_PROMPT),
                HumanMessage(content=analysis_prompt)
            ]
            
            # 使用 LLM 判斷意圖
            logger.info(f"Analyzing intent for user {state['user_id']}")
            response = await self.llm.ainvoke(messages)
            
            # 解析回應
            try:
                result = json.loads(response.content)
                state["need_knowledge"] = result.get("need_knowledge", False)
                state["intent_category"] = result.get("category", "一般對話")
                
                logger.info(f"Intent analysis: need_knowledge={state['need_knowledge']}, category={state['intent_category']}")
                
            except json.JSONDecodeError:
                # 預設不查詢知識庫
                logger.warning("Failed to parse intent analysis, defaulting to no knowledge retrieval")
                state["need_knowledge"] = False
                state["intent_category"] = "一般對話"
            
        except Exception as e:
            logger.error(f"IntentRouter error: {str(e)}")
            # 出錯時預設不查詢知識庫，讓對話繼續
            state["need_knowledge"] = False
            state["intent_category"] = "一般對話"
        
        return state