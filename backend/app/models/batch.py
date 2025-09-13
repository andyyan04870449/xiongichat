"""批次上傳相關模型"""

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.database import Base


class BatchTask(Base):
    """批次任務模型（精簡版）"""
    __tablename__ = "batch_tasks"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    total_files = Column(Integer, nullable=False)
    completed_files = Column(Integer, default=0)
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # 關聯
    upload_records = relationship("UploadRecord", back_populates="batch_task")
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            "id": str(self.id),
            "total_files": self.total_files,
            "completed_files": self.completed_files,
            "status": self.status,
            "progress": self.calculate_progress(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    def calculate_progress(self):
        """計算批次進度百分比"""
        if self.total_files == 0:
            return 0
        return round((self.completed_files / self.total_files) * 100)
    
    def update_status(self):
        """根據完成情況更新批次狀態"""
        if self.completed_files == 0 and self.status == 'pending':
            return
        
        if self.completed_files > 0 and self.status == 'pending':
            self.status = 'processing'
        
        if self.completed_files >= self.total_files:
            self.status = 'completed'
            self.completed_at = func.now()