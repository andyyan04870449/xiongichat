"""對話管理 API"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
import logging

from app.database import get_db
from app.models import Conversation, ConversationMessage
from app.schemas.conversation import ConversationResponse, MessageResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="取得對話歷史",
    description="根據對話ID取得完整對話歷史"
)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ConversationResponse:
    """
    取得指定對話的歷史記錄
    
    - **conversation_id**: 對話ID
    """
    try:
        # 查詢對話
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await db.execute(stmt)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="對話不存在"
            )
        
        # 查詢訊息
        stmt = select(ConversationMessage).where(
            ConversationMessage.conversation_id == conversation_id
        ).order_by(ConversationMessage.created_at)
        
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        # 建立回應
        response = ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            started_at=conversation.started_at,
            ended_at=conversation.ended_at,
            last_message_at=conversation.last_message_at,
            messages=[
                MessageResponse(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at
                )
                for msg in messages
            ]
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="取得對話時發生錯誤"
        )


@router.get(
    "/user/{user_id}",
    response_model=List[ConversationResponse],
    status_code=status.HTTP_200_OK,
    summary="取得使用者對話列表",
    description="取得指定使用者的所有對話"
)
async def get_user_conversations(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> List[ConversationResponse]:
    """
    取得使用者的對話列表
    
    - **user_id**: 使用者ID
    - **limit**: 限制筆數（預設10）
    - **offset**: 偏移量（預設0）
    """
    try:
        # 查詢對話
        stmt = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(
            Conversation.updated_at.desc()
        ).limit(limit).offset(offset)
        
        result = await db.execute(stmt)
        conversations = result.scalars().all()
        
        # 建立回應列表
        responses = []
        for conv in conversations:
            responses.append(
                ConversationResponse(
                    id=conv.id,
                    user_id=conv.user_id,
                    started_at=conv.started_at,
                    ended_at=conv.ended_at,
                    last_message_at=conv.last_message_at,
                    messages=[]  # 列表不包含訊息詳情
                )
            )
        
        return responses
        
    except Exception as e:
        logger.error(f"Error getting user conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="取得對話列表時發生錯誤"
        )