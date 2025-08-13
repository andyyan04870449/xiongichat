"""聊天 API"""

from fastapi import APIRouter, HTTPException, status
from typing import Any
import logging

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatService

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化服務
chat_service = ChatService()


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="發送聊天訊息",
    description="發送訊息給AI助手並取得回覆"
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    處理聊天請求
    
    - **user_id**: 使用者識別碼
    - **message**: 使用者訊息內容
    - **conversation_id**: 對話ID（選填，延續對話時提供）
    """
    try:
        logger.info(f"Chat request from user: {request.user_id}")
        
        # 處理訊息
        response = await chat_service.process_message(request)
        
        return response
        
    except ValueError as e:
        logger.warning(f"Invalid request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="處理訊息時發生錯誤，請稍後再試"
        )