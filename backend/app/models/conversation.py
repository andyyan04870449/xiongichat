"""對話相關模型"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.utils.timezone import to_taiwan_time


class Conversation(Base):
    """對話模型"""
    __tablename__ = "conversations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String, nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 關聯
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("user_id != ''", name="conversations_user_id_check"),
    )
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "started_at": to_taiwan_time(self.started_at).isoformat() if self.started_at else None,
            "ended_at": to_taiwan_time(self.ended_at).isoformat() if self.ended_at else None,
            "last_message_at": to_taiwan_time(self.last_message_at).isoformat() if self.last_message_at else None,
            "updated_at": to_taiwan_time(self.updated_at).isoformat() if self.updated_at else None,
        }


class ConversationMessage(Base):
    """對話訊息模型"""
    __tablename__ = "conversation_messages"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(PGUUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    meta = Column(JSON, nullable=True)  # 存儲策略追蹤和其他擴展數據
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # 關聯
    conversation = relationship("Conversation", back_populates="messages")
    
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="conversation_messages_role_check"),
        CheckConstraint("content != ''", name="conversation_messages_content_check"),
    )
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "conversation_id": str(self.conversation_id),
            "role": self.role,
            "content": self.content,
            "meta": self.meta,  # JSON數據直接返回
            "created_at": to_taiwan_time(self.created_at).isoformat() if self.created_at else None,
        }