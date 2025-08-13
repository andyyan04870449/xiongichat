"""主要工作流定義"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any
import logging

from app.langgraph.state import WorkflowState
from app.langgraph.nodes import ChatAgentNode, ConversationLoggerNode
from app.services.memory import MemoryService

logger = logging.getLogger(__name__)


def create_chat_workflow() -> StateGraph:
    """建立聊天工作流"""
    
    # 初始化節點
    chat_agent = ChatAgentNode()
    conversation_logger = ConversationLoggerNode()
    memory_service = MemoryService()
    
    # 建立工作流
    workflow = StateGraph(WorkflowState)
    
    # 定義載入記憶節點
    async def load_memory(state: WorkflowState) -> WorkflowState:
        """載入對話記憶"""
        if state.get("conversation_id"):
            memory = await memory_service.load_conversation_memory(state["conversation_id"])
            state["memory"] = memory
        else:
            state["memory"] = []
        return state
    
    # 定義節點
    workflow.add_node("load_memory", load_memory)
    workflow.add_node("chat_agent", chat_agent)
    workflow.add_node("conversation_logger", conversation_logger)
    
    # 定義邊（執行順序）
    workflow.set_entry_point("load_memory")
    workflow.add_edge("load_memory", "chat_agent")
    workflow.add_edge("chat_agent", "conversation_logger")
    workflow.add_edge("conversation_logger", END)
    
    # 編譯工作流
    app = workflow.compile()
    
    logger.info("Chat workflow created successfully")
    return app