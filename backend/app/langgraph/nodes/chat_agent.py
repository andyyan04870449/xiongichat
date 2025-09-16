"""聊天代理節點"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from datetime import datetime
import logging

from app.config import settings
from app.langgraph.state import WorkflowState
from app.langgraph.prompts import CHAT_SYSTEM_PROMPT
from app.utils.timezone import get_taiwan_time

logger = logging.getLogger(__name__)


class ChatAgentNode:
    """聊天代理節點 - 生成回覆"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model_chat,  # 使用 gpt-4o
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            api_key=settings.openai_api_key,
        )
        self.max_memory_turns = settings.langgraph_max_memory_turns
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行節點邏輯"""
        try:
            # 準備系統提示
            system_prompt = CHAT_SYSTEM_PROMPT.format(
                user_id=state["user_id"],
                timestamp=get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # 如果有檢索到知識，加入到系統提示中
            if state.get("retrieved_knowledge"):
                knowledge_context = self._format_knowledge_context(state["retrieved_knowledge"])
                if knowledge_context:
                    system_prompt += f"\n\n【參考資訊】\n{knowledge_context}\n請根據以上資訊回答，但回應仍需符合角色設定和字數限制。"
            
            # 構建訊息列表
            messages = [SystemMessage(content=system_prompt)]
            
            # 加入對話歷史（限制最近N輪）
            memory = state.get("memory", [])
            if memory:
                # 只保留最近的對話，但不包含當前還沒回覆的訊息
                # 記憶中應該都是成對的 user-assistant 訊息
                recent_memory = memory[-(self.max_memory_turns * 2):]  # *2 因為包含 user 和 assistant
                
                # 確保按照正確的順序添加訊息
                for msg in recent_memory:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            # 加入當前使用者輸入
            messages.append(HumanMessage(content=state["input_text"]))
            
            # 生成回覆
            logger.info(f"Generating reply for user {state['user_id']}")
            response = await self.llm.ainvoke(messages)
            
            # 更新狀態
            state["reply"] = response.content
            
            # 更新記憶
            new_memory = memory.copy() if memory else []
            new_memory.append({"role": "user", "content": state["input_text"]})
            new_memory.append({"role": "assistant", "content": response.content})
            state["memory"] = new_memory
            
            logger.info(f"Reply generated successfully for user {state['user_id']}")
            
        except Exception as e:
            logger.error(f"ChatAgent error: {str(e)}")
            state["error"] = f"ChatAgent error: {str(e)}"
            state["reply"] = "抱歉，我遇到了一些技術問題。請稍後再試。"
        
        return state
    
    def _format_knowledge_context(self, knowledge_items: List[Dict[str, Any]]) -> str:
        """格式化知識庫檢索結果為上下文"""
        if not knowledge_items:
            return ""
        
        # 只取最相關的前 2 筆，避免上下文過長
        top_items = knowledge_items[:2]
        
        context_parts = []
        for idx, item in enumerate(top_items, 1):
            # 精簡內容，只保留重點資訊
            content = item.get("content", "")
            if len(content) > 150:
                content = content[:150] + "..."
            
            title = item.get("title", "")
            if title:
                context_parts.append(f"{idx}. {title}: {content}")
            else:
                context_parts.append(f"{idx}. {content}")
        
        return "\n".join(context_parts)