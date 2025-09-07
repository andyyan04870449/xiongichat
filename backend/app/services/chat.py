"""聊天服務"""

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import logging

from app.langgraph import create_chat_workflow, WorkflowState
from app.schemas.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)


class ChatService:
    """聊天服務 - 處理聊天邏輯"""
    
    def __init__(self):
        self.workflow = None
        self._initialize_workflow()
    
    def _initialize_workflow(self):
        """初始化工作流"""
        try:
            self.workflow = create_chat_workflow()
            logger.info("Chat workflow initialized")
        except Exception as e:
            logger.error(f"Failed to initialize workflow: {str(e)}")
            raise
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """處理聊天訊息"""
        try:
            # 準備工作流狀態
            state = WorkflowState(
                user_id=request.user_id,
                conversation_id=str(request.conversation_id) if request.conversation_id else None,
                input_text=request.message,
                memory=[],
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
                timestamp=datetime.utcnow()
            )
            
            # 執行工作流
            logger.info(f"Processing message for user {request.user_id}")
            result = await self.workflow.ainvoke(state)
            
            # 檢查錯誤
            if result.get("error"):
                logger.error(f"Workflow error: {result['error']}")
                raise Exception(result["error"])
            
            # 建立回應
            response = ChatResponse(
                conversation_id=UUID(result["conversation_id"]) if result.get("conversation_id") else None,
                user_message_id=UUID(result["user_message_id"]) if result.get("user_message_id") else None,
                assistant_message_id=UUID(result["assistant_message_id"]) if result.get("assistant_message_id") else None,
                reply=result.get("reply", ""),
                timestamp=result.get("timestamp", datetime.utcnow())
            )
            
            logger.info(f"Message processed successfully for user {request.user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise