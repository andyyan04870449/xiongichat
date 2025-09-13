"""對話記錄節點"""

from datetime import datetime
from uuid import uuid4, UUID
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
                
                # 準備策略元數據
                intent_analysis = state.get("intent_analysis", {})
                strategy_meta = {
                    "care_stage_used": intent_analysis.get("care_stage_needed", 2),
                    "risk_level": intent_analysis.get("risk_level", "none"),
                    "intent": intent_analysis.get("intent", "一般對話"),
                    "strategy_effectiveness": intent_analysis.get("strategy_effectiveness", "unknown"),
                    "upgrade_reason": intent_analysis.get("upgrade_reason", ""),
                    "is_upgrade": intent_analysis.get("is_upgrade", False),
                    "treatment_progress": intent_analysis.get("treatment_progress", "initial"),
                    "previous_stages_tried": intent_analysis.get("previous_stages_tried", []),
                    "emotion_trend": intent_analysis.get("emotion_trend", "unknown"),
                    "confidence_level": intent_analysis.get("confidence_level", 0.7),
                    "used_knowledge": bool(state.get("knowledge", "")),
                    "used_reference": bool(state.get("reference_answer", "")),
                    "response_length": len(state.get("reply", "")),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # 儲存助手回覆（使用稍微晚一點的時間戳確保順序）
                from datetime import timedelta
                assistant_time = user_time + timedelta(microseconds=1)
                assistant_message = ConversationMessage(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=state.get("reply", ""),
                    meta=strategy_meta,  # 存儲策略元數據
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
            try:
                # 將字串轉換為 UUID 對象
                conversation_uuid = UUID(conversation_id) if isinstance(conversation_id, str) else conversation_id
                
                # 查詢現有對話
                stmt = select(Conversation).where(
                    Conversation.id == conversation_uuid,
                    Conversation.user_id == user_id
                )
                result = await db.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if conversation:
                    logger.info(f"Found existing conversation {conversation_id} for user {user_id}")
                    return conversation
                else:
                    logger.warning(f"Conversation {conversation_id} not found for user {user_id}, creating new one")
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid conversation_id format: {conversation_id}, error: {e}")
        
        # 建立新對話，如果有指定的 conversation_id 就使用它
        if conversation_id:
            try:
                conversation_uuid = UUID(conversation_id) if isinstance(conversation_id, str) else conversation_id
                conversation = Conversation(
                    id=conversation_uuid,
                    user_id=user_id,
                    started_at=datetime.utcnow(),
                )
            except (ValueError, TypeError):
                # 如果 conversation_id 格式不正確，創建新的
                conversation = Conversation(
                    user_id=user_id,
                    started_at=datetime.utcnow(),
                )
        else:
            conversation = Conversation(
                user_id=user_id,
                started_at=datetime.utcnow(),
            )
        
        db.add(conversation)
        await db.flush()
        
        logger.info(f"Created new conversation {conversation.id} for user {user_id}")
        return conversation