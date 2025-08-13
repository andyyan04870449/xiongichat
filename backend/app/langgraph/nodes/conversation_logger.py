"""對話記錄節點"""

from datetime import datetime
from uuid import uuid4
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import Conversation, ConversationMessage
from app.langgraph.state import WorkflowState
from app.database import get_db_context

logger = logging.getLogger(__name__)


class ConversationLoggerNode:
    """對話記錄節點 - 儲存對話到資料庫"""
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行節點邏輯"""
        try:
            async with get_db_context() as db:
                # 取得或建立對話
                conversation = await self._get_or_create_conversation(
                    db, 
                    state["user_id"], 
                    state.get("conversation_id")
                )
                
                # 儲存使用者訊息（使用稍微早一點的時間戳確保順序）
                user_time = datetime.utcnow()
                user_message = ConversationMessage(
                    conversation_id=conversation.id,
                    role="user",
                    content=state["input_text"],
                    created_at=user_time,
                )
                db.add(user_message)
                await db.flush()
                state["user_message_id"] = str(user_message.id)
                
                # 儲存助手回覆（使用稍微晚一點的時間戳確保順序）
                from datetime import timedelta
                assistant_time = user_time + timedelta(microseconds=1)
                assistant_message = ConversationMessage(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=state.get("reply", ""),
                    created_at=assistant_time,
                )
                db.add(assistant_message)
                await db.flush()
                state["assistant_message_id"] = str(assistant_message.id)
                
                # 更新對話的最後訊息時間
                conversation.last_message_at = datetime.utcnow()
                
                # 更新狀態中的 conversation_id
                state["conversation_id"] = str(conversation.id)
                
                await db.commit()
                
                logger.info(f"Messages saved for conversation {conversation.id}")
                
        except Exception as e:
            logger.error(f"ConversationLogger error: {str(e)}")
            state["error"] = f"ConversationLogger error: {str(e)}"
        
        return state
    
    async def _get_or_create_conversation(
        self, 
        db: AsyncSession, 
        user_id: str, 
        conversation_id: Optional[str]
    ) -> Conversation:
        """取得或建立對話"""
        
        if conversation_id:
            # 查詢現有對話
            stmt = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            result = await db.execute(stmt)
            conversation = result.scalar_one_or_none()
            
            if conversation:
                return conversation
        
        # 建立新對話
        conversation = Conversation(
            user_id=user_id,
            started_at=datetime.utcnow(),
        )
        db.add(conversation)
        await db.flush()
        
        logger.info(f"Created new conversation {conversation.id} for user {user_id}")
        return conversation