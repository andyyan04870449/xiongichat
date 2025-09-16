"""聊天服務"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4
import logging

# 避免循環引用，延遲導入
# from app.langgraph import create_chat_workflow, WorkflowState
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.memory import MemoryService
from app.utils.timezone import get_taiwan_time

logger = logging.getLogger(__name__)


class ChatService:
    """聊天服務 - 處理聊天邏輯"""
    
    def __init__(self):
        self.workflow = None
        self.memory_service = MemoryService()
        self._initialize_workflow()
    
    def _initialize_workflow(self):
        """初始化工作流"""
        try:
            # 延遲導入以避免循環引用
            from app.langgraph import create_chat_workflow
            self.workflow = create_chat_workflow()
            logger.info("Chat workflow initialized")
        except Exception as e:
            logger.error(f"Failed to initialize workflow: {str(e)}")
            raise
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """處理聊天訊息"""
        try:
            # 延遲導入 WorkflowState
            from app.langgraph import WorkflowState
            
            # 確保有 conversation_id
            conversation_id = str(request.conversation_id) if request.conversation_id else str(uuid4())
            
            # 載入對話記憶
            memory = []
            try:
                memory = await self.memory_service.load_conversation_memory(conversation_id)
                logger.info(f"Loaded {len(memory)} messages from memory for conversation {conversation_id}")
            except Exception as e:
                logger.warning(f"Failed to load memory: {str(e)}, using empty memory")
                memory = []
            
            # 準備工作流狀態
            state = WorkflowState(
                user_id=request.user_id,
                conversation_id=conversation_id,
                input_text=request.message,
                memory=memory,  # 使用載入的記憶
                semantic_analysis=None,
                mentioned_substances=None,
                user_intent=None,
                emotional_state=None,
                drug_info=None,
                risk_level=None,
                response_strategy=None,
                need_knowledge=None,
                intent_category=None,
                retrieved_knowledge=None,
                reply="",
                user_message_id=None,
                assistant_message_id=None,
                error=None,
                timestamp=get_taiwan_time()
            )
            
            # 執行工作流
            logger.info(f"Processing message for user {request.user_id}")
            result = await self.workflow.ainvoke(state)
            
            # 檢查錯誤
            if result.get("error"):
                logger.error(f"Workflow error: {result['error']}")
                raise Exception(result["error"])
            
            # 建立回應，確保使用相同的 conversation_id
            response = ChatResponse(
                conversation_id=UUID(conversation_id),  # 使用一致的 conversation_id
                user_message_id=UUID(result["user_message_id"]) if result.get("user_message_id") else None,
                assistant_message_id=UUID(result["assistant_message_id"]) if result.get("assistant_message_id") else None,
                reply=result.get("reply", ""),
                timestamp=result.get("timestamp", get_taiwan_time())
            )
            
            logger.info(f"Message processed successfully for user {request.user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise