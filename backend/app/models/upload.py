"""
上傳相關的資料模型
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, CheckConstraint, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import UUID, uuid4
import enum

from app.database import Base


class UploadStatus(str, enum.Enum):
    """上傳狀態"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadType(str, enum.Enum):
    """上傳類型"""
    AUTHORITY_MEDIA = "authority_media"
    AUTHORITY_CONTACTS = "authority_contacts"
    ARTICLE = "article"


class UploadRecord(Base):
    """上傳記錄模型"""
    __tablename__ = "upload_records"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    filename = Column(String(255), nullable=False)
    upload_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    file_path = Column(String(500), nullable=True)  # 檔案儲存路徑
    file_size = Column(Integer, nullable=True)  # 檔案大小 (bytes)
    mime_type = Column(String(100), nullable=True)  # MIME 類型
    description = Column(Text, nullable=True)  # 檔案描述
    metadata_json = Column("metadata", JSONB, nullable=True)  # 額外資訊 (tags, category 等)
    error_message = Column(Text, nullable=True)  # 錯誤訊息
    processing_log = Column(JSONB, nullable=True)  # 處理日誌
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 批次上傳相關欄位
    batch_id = Column(PGUUID(as_uuid=True), ForeignKey("batch_tasks.id", ondelete="SET NULL"))
    relative_path = Column(String(500))  # 保留檔案原始路徑
    processing_progress = Column(Integer, default=0)  # 處理進度 0-100
    
    # 關聯
    batch_task = relationship("BatchTask", back_populates="upload_records")
    
    __table_args__ = (
        CheckConstraint("filename != ''", name="upload_records_filename_check"),
        CheckConstraint("file_size >= 0", name="upload_records_file_size_check"),
    )
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "filename": self.filename,
            "upload_type": self.upload_type,  # 已經是字串
            "status": self.status,  # 已經是字串
            "file_size": self.file_size,
            "metadata": self.metadata_json,
            "error_message": self.error_message,
            "processing_log": self.processing_log,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_response(self):
        """轉換為 API 回應格式（將字串轉換為枚舉）"""
        return {
            "id": self.id,
            "filename": self.filename,
            "upload_type": UploadType(self.upload_type),
            "status": UploadStatus(self.status),
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "metadata": self.metadata_json,
            "error_message": self.error_message,
            "processing_log": self.processing_log,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class AuthoritativeMedia(Base):
    """權威媒體資料模型"""
    __tablename__ = "authoritative_media"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    upload_id = Column(PGUUID(as_uuid=True), nullable=True)  # 關聯的上傳記錄
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=True)
    tags = Column(JSONB, nullable=True)  # 標籤列表
    description = Column(Text, nullable=True)  # 備註
    exif_data = Column(JSONB, nullable=True)  # EXIF 資料
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint("filename != ''", name="authoritative_media_filename_check"),
        CheckConstraint("file_size >= 0", name="authoritative_media_file_size_check"),
    )
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "upload_id": str(self.upload_id) if self.upload_id else None,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "tags": self.tags,
            "description": self.description,
            "exif_data": self.exif_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AuthoritativeContacts(Base):
    """權威機構聯絡資料模型"""
    __tablename__ = "authoritative_contacts"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    upload_id = Column(PGUUID(as_uuid=True), nullable=True)  # 關聯的上傳記錄
    name = Column(String(255), nullable=True)  # 機構名稱（新增）
    organization = Column(String(255), nullable=True)  # 機構/單位名稱（保留相容性）
    category = Column(String(100), nullable=True)  # 機構類別（新增）
    phone = Column(String(50), nullable=True)  # 聯絡電話
    email = Column(String(255), nullable=True)  # 電子郵件
    address = Column(String(500), nullable=True)  # 地址
    services = Column(Text, nullable=True)  # 服務項目（新增）
    contact_person = Column(String(100), nullable=True)  # 聯絡人（新增）
    tags = Column(JSONB, nullable=True)  # 標籤分類（如：戒毒諮詢、醫療、法律援助）
    notes = Column(Text, nullable=True)  # 備註（服務時間、服務內容等）
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint("name IS NOT NULL OR organization IS NOT NULL", name="authoritative_contacts_name_or_org_check"),
    )
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "upload_id": str(self.upload_id) if self.upload_id else None,
            "name": self.name,
            "organization": self.organization,
            "category": self.category,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "services": self.services,
            "contact_person": self.contact_person,
            "tags": self.tags,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
