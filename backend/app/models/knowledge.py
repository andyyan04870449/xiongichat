"""知識庫相關模型"""

from datetime import datetime, date
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Date, Text, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.database import Base


class KnowledgeDocument(Base):
    """知識文件模型"""
    __tablename__ = "knowledge_documents"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    lang = Column(String, nullable=False, default="zh-TW", index=True)
    # meta_data = Column("metadata", JSONB, nullable=True, default={})  # 暫時註解，資料庫尚未有此欄位
    published_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 關聯
    embeddings = relationship("KnowledgeEmbedding", back_populates="document", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("title != ''", name="knowledge_documents_title_check"),
        CheckConstraint("content != ''", name="knowledge_documents_content_check"),
        CheckConstraint("source != ''", name="knowledge_documents_source_check"),
        CheckConstraint("category != ''", name="knowledge_documents_category_check"),
        CheckConstraint("lang IN ('zh-TW', 'en', 'vi', 'id', 'th')", name="knowledge_documents_lang_check"),
    )
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "category": self.category,
            "lang": self.lang,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class KnowledgeEmbedding(Base):
    """知識向量嵌入模型"""
    __tablename__ = "knowledge_embeddings"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(PGUUID(as_uuid=True), ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)  # OpenAI text-embedding-3-small 的維度
    metadata_json = Column("metadata", JSONB, nullable=True)  # 使用 metadata_json 作為屬性名，但資料庫欄位名為 metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # 關聯
    document = relationship("KnowledgeDocument", back_populates="embeddings")
    
    __table_args__ = (
        CheckConstraint("content != ''", name="knowledge_embeddings_content_check"),
        CheckConstraint("chunk_index >= 0", name="knowledge_embeddings_chunk_index_check"),
    )
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "document_id": str(self.document_id),
            "chunk_index": self.chunk_index,
            "content": self.content,
            "metadata": self.metadata_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Case(Base):
    """個案檔案模型"""
    __tablename__ = "cases"
    
    user_id = Column(String, primary_key=True)
    nickname = Column(String, nullable=True)
    lang = Column(String, nullable=False, default="zh-TW")
    stage = Column(String, nullable=False, default="assessment")
    goals = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint("user_id != ''", name="cases_user_id_check"),
        CheckConstraint("lang IN ('zh-TW', 'en', 'vi', 'id', 'th')", name="cases_lang_check"),
        CheckConstraint("stage IN ('assessment', 'treatment', 'recovery')", name="cases_stage_check"),
    )
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "nickname": self.nickname,
            "lang": self.lang,
            "stage": self.stage,
            "goals": self.goals,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
