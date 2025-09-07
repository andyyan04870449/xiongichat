"""對話理解節點 - 深度理解對話上下文"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import logging

from app.config import settings
from app.langgraph.state import WorkflowState

logger = logging.getLogger(__name__)


class ContextUnderstandingNode:
    """深度理解對話上下文，適用所有場景"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model_analysis,  # 使用mini模型進行結構化分析
            temperature=0.1,
            api_key=settings.openai_api_key,
            model_kwargs={
                "response_format": {"type": "json_object"}
            }
        )
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行對話理解分析"""
        try:
            # 構建分析提示
            analysis_prompt = self._build_analysis_prompt(
                state["input_text"],
                state.get("memory", [])
            )
            
            messages = [
                SystemMessage(content=CONTEXT_UNDERSTANDING_PROMPT),
                HumanMessage(content=analysis_prompt)
            ]
            
            # 執行深度分析
            logger.info(f"Performing context understanding for user {state['user_id']}")
            response = await self.llm.ainvoke(messages)
            
            # 解析結果
            try:
                understanding = json.loads(response.content)
                
                # 更新狀態
                state["context_understanding"] = understanding
                
                # 設定增強查詢
                search_strategy = understanding.get("search_strategy", {})
                if search_strategy.get("search_query"):
                    state["enhanced_query"] = search_strategy["search_query"]
                else:
                    state["enhanced_query"] = self._build_fallback_query(understanding, state["input_text"])
                
                logger.info(
                    f"Context understanding completed: "
                    f"confidence={understanding.get('confidence_score')}, "
                    f"intent={understanding.get('user_intent', {}).get('category')}"
                )
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse context understanding: {e}")
                # 設定預設值
                state["context_understanding"] = {}
                state["enhanced_query"] = state["input_text"]
            
        except Exception as e:
            logger.error(f"ContextUnderstanding error: {str(e)}")
            state["context_understanding"] = {"error": str(e)}
            state["enhanced_query"] = state["input_text"]
        
        return state
    
    def _format_conversation(self, memory: List[Dict]) -> str:
        """格式化對話歷史"""
        if not memory:
            return "（無歷史對話）"
        
        formatted = []
        for msg in memory[-6:]:  # 最近6條訊息
            role = "用戶" if msg["role"] == "user" else "助理"
            formatted.append(f"{role}：{msg['content']}")
        
        return "\n".join(formatted)
    
    def _build_analysis_prompt(self, input_text: str, memory: List[Dict]) -> str:
        """構建分析提示"""
        conversation = self._format_conversation(memory)
        
        return f"""
對話歷史：
{conversation}

當前輸入：{input_text}

請進行全面分析並返回 JSON 格式：
{{
    "entities": {{
        "主要實體": {{
            "name": "實體名稱",
            "type": "人物/地點/機構/物品/概念/其他",
            "context": "在對話中的角色"
        }},
        "次要實體": []
    }},
    "pronouns_resolution": {{
        "代詞": "指向的實體",
        "說明": "為什麼這樣解析"
    }},
    "user_intent": {{
        "immediate": "當前句子的直接意圖",
        "underlying": "結合上下文的深層意圖",
        "category": "資訊查詢/尋求幫助/情感支持/閒聊/任務執行/其他"
    }},
    "information_needs": {{
        "explicit": "明確表達的資訊需求",
        "implicit": "可能需要但未明說的資訊",
        "priority": "最優先滿足的需求"
    }},
    "conversation_context": {{
        "topic_flow": "話題演進路徑",
        "emotional_trajectory": "情緒變化趨勢",
        "stage": "開場/探索/深入/收尾"
    }},
    "search_strategy": {{
        "should_search": true/false,
        "search_query": "最佳搜索詞組",
        "search_scope": "精確/相關/廣泛",
        "fallback_queries": ["備選查詢1", "備選查詢2"]
    }},
    "confidence_score": 0.0-1.0,
    "reasoning": "分析邏輯說明"
}}

必須返回有效的 JSON 格式，不要包含任何其他文字或markdown標記。
"""
    
    def _build_fallback_query(self, understanding: Dict, input_text: str) -> str:
        """構建備用查詢"""
        entities = understanding.get("entities", {})
        intent = understanding.get("user_intent", {})
        
        main_entity = entities.get("主要實體", {}).get("name", "")
        underlying_intent = intent.get("underlying", "")
        
        if main_entity and underlying_intent:
            return f"{main_entity} {underlying_intent}"
        elif main_entity:
            return main_entity
        else:
            return input_text


# 系統提示詞
CONTEXT_UNDERSTANDING_PROMPT = """你是一個專業的對話理解系統，需要深入分析用戶的真實意圖。

分析原則：
1. 不要只看表面文字，理解話語背後的需求
2. 注意對話的連貫性和邏輯關係
3. 識別並解析所有指代關係（他、它、這個、那個等）
4. 判斷資訊需求的緊急程度
5. 考慮文化背景和語境暗示

重點任務：
- 追蹤對話中提到的所有實體（人物、地點、機構等）
- 解析代詞指向什麼
- 理解用戶的真實需求（可能與字面表達不同）
- 判斷是否需要搜索知識庫
- 生成最佳的搜索查詢詞

請保持客觀、準確的分析。"""