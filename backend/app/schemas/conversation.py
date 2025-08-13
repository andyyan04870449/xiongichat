"""對話相關資料結構"""

from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """訊息回應"""
    id: UUID = Field(..., description="訊息ID")
    role: str = Field(..., description="角色（user/assistant/system）")
    content: str = Field(..., description="訊息內容")
    created_at: datetime = Field(..., description="建立時間")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "role": "user",
                "content": "你好",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class ConversationResponse(BaseModel):
    """對話回應"""
    id: UUID = Field(..., description="對話ID")
    user_id: str = Field(..., description="使用者ID")
    started_at: datetime = Field(..., description="開始時間")
    ended_at: Optional[datetime] = Field(None, description="結束時間")
    last_message_at: Optional[datetime] = Field(None, description="最後訊息時間")
    messages: List[MessageResponse] = Field(default_factory=list, description="訊息列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user_001",
                "started_at": "2024-01-15T10:00:00Z",
                "ended_at": None,
                "last_message_at": "2024-01-15T10:30:00Z",
                "messages": []
            }
        }