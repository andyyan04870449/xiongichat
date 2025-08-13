"""聊天相關資料結構"""

from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator


class ChatRequest(BaseModel):
    """聊天請求"""
    user_id: str = Field(..., description="使用者ID", min_length=1, max_length=100)
    message: str = Field(..., description="訊息內容", min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = Field(None, description="對話ID（延續對話時提供）")
    
    @validator("message")
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("訊息不能為空")
        return v.strip()
    
    @validator("user_id")
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError("使用者ID不能為空")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "message": "你好，我想了解戒毒相關資訊",
                "conversation_id": None
            }
        }


class ChatResponse(BaseModel):
    """聊天回應"""
    conversation_id: UUID = Field(..., description="對話ID")
    user_message_id: UUID = Field(..., description="使用者訊息ID")
    assistant_message_id: UUID = Field(..., description="助手訊息ID")
    reply: str = Field(..., description="回覆內容")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="時間戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_message_id": "123e4567-e89b-12d3-a456-426614174001",
                "assistant_message_id": "123e4567-e89b-12d3-a456-426614174002",
                "reply": "您好！我很樂意協助您了解戒毒相關資訊。請問您想了解哪方面的內容呢？",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }