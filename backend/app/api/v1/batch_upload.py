"""批次上傳 API 端點"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
import json
import logging

from app.database import get_db
from app.models.batch import BatchTask
from app.models.upload import UploadRecord, UploadType, UploadStatus
from app.services.upload_service import UploadService
from app.schemas.upload import ArticleUploadRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/batch", tags=["batch"])
upload_service = UploadService()


@router.post("/create")
async def create_batch(
    file_count: int,
    db: AsyncSession = Depends(get_db)
):
    """建立批次任務"""
    try:
        batch = BatchTask(total_files=file_count)
        db.add(batch)
        await db.commit()
        await db.refresh(batch)
        
        logger.info(f"Created batch task: {batch.id} with {file_count} files")
        return {"batch_id": str(batch.id), "status": "created"}
        
    except Exception as e:
        logger.error(f"Error creating batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{batch_id}/upload")
async def upload_to_batch(
    background_tasks: BackgroundTasks,
    batch_id: UUID,
    file: UploadFile = File(...),
    relative_path: Optional[str] = Form(None),
    category: str = Form("general"),
    source: str = Form("batch_upload"),
    lang: str = Form("zh-TW"),
    db: AsyncSession = Depends(get_db)
):
    """上傳檔案到批次"""
    try:
        # 檢查批次是否存在
        batch = await db.get(BatchTask, batch_id)
        if not batch:
            raise HTTPException(status_code=404, detail="批次任務不存在")
        
        # 偵測檔案類型
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            upload_type = UploadType.AUTHORITY_MEDIA
        else:
            upload_type = UploadType.ARTICLE
        
        # 建立上傳記錄
        upload_record = await upload_service.create_upload_record(
            filename=file.filename,
            upload_type=upload_type,
            file_size=file.size if hasattr(file, 'size') else None,
            metadata={
                "category": category,
                "source": source,
                "lang": lang,
                "relative_path": relative_path,
                "batch_id": str(batch_id)
            }
        )
        
        # 更新上傳記錄的批次關聯
        record = await db.get(UploadRecord, upload_record.id)
        record.batch_id = batch_id
        record.relative_path = relative_path
        await db.commit()
        
        # 先讀取檔案內容（在背景任務之前）
        await file.seek(0)
        file_content = await file.read()
        
        # 根據檔案類型處理
        if upload_type == UploadType.ARTICLE:
            # 建立文章上傳請求
            request = ArticleUploadRequest(
                category=category,
                source=source,
                lang=lang,
                published_date=None
            )
            
            # 背景處理文章上傳 - 使用檔案內容而非檔案物件
            background_tasks.add_task(
                upload_service.process_article_upload_with_content,
                file_content, file.filename, upload_record.id, request
            )
        else:
            # 處理媒體檔案 - 使用檔案內容而非檔案物件
            background_tasks.add_task(
                upload_service.process_media_upload_with_content,
                file_content, file.filename, upload_record.id, {"tags": [], "description": relative_path}
            )
        
        logger.info(f"File {file.filename} added to batch {batch_id}")
        return {
            "upload_id": str(upload_record.id),
            "batch_id": str(batch_id),
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading to batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{batch_id}/status")
async def get_batch_status(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """取得批次狀態"""
    try:
        # 取得批次任務
        batch = await db.get(BatchTask, batch_id)
        if not batch:
            raise HTTPException(status_code=404, detail="批次任務不存在")
        
        # 計算檔案狀態統計
        result = await db.execute(
            select(
                func.count(UploadRecord.id).label('total'),
                func.sum(case((UploadRecord.status == 'completed', 1), else_=0)).label('completed'),
                func.sum(case((UploadRecord.status == 'failed', 1), else_=0)).label('failed'),
                func.sum(case((UploadRecord.status == 'processing', 1), else_=0)).label('processing'),
                func.sum(case((UploadRecord.status == 'pending', 1), else_=0)).label('pending')
            ).where(UploadRecord.batch_id == batch_id)
        )
        stats = result.first()
        
        # 更新批次完成數量
        if stats.completed != batch.completed_files:
            batch.completed_files = stats.completed or 0
            batch.update_status()
            await db.commit()
        
        # 取得檔案列表
        files_result = await db.execute(
            select(UploadRecord)
            .where(UploadRecord.batch_id == batch_id)
            .order_by(UploadRecord.created_at)
        )
        files = files_result.scalars().all()
        
        return {
            "batch_id": str(batch_id),
            "status": batch.status,
            "total_files": batch.total_files,
            "completed_files": stats.completed or 0,
            "failed_files": stats.failed or 0,
            "processing_files": stats.processing or 0,
            "pending_files": stats.pending or 0,
            "progress": batch.calculate_progress(),
            "created_at": batch.created_at.isoformat() if batch.created_at else None,
            "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
            "files": [
                {
                    "id": str(f.id),
                    "filename": f.filename,
                    "relative_path": f.relative_path,
                    "status": f.status,
                    "progress": f.processing_progress,
                    "error": f.error_message
                } for f in files
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting batch status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/{upload_id}/status")
async def get_file_status(
    upload_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """取得單一檔案處理狀態"""
    try:
        upload_record = await db.get(UploadRecord, upload_id)
        if not upload_record:
            raise HTTPException(status_code=404, detail="上傳記錄不存在")
        
        return {
            "upload_id": str(upload_id),
            "filename": upload_record.filename,
            "status": upload_record.status,
            "progress": upload_record.processing_progress,
            "error_message": upload_record.error_message,
            "processing_log": upload_record.processing_log,
            "created_at": upload_record.created_at.isoformat() if upload_record.created_at else None,
            "updated_at": upload_record.updated_at.isoformat() if upload_record.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_batches(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """列出所有批次任務"""
    try:
        result = await db.execute(
            select(BatchTask)
            .order_by(BatchTask.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        batches = result.scalars().all()
        
        return {
            "batches": [batch.to_dict() for batch in batches],
            "total": len(batches)
        }
        
    except Exception as e:
        logger.error(f"Error listing batches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{batch_id}")
async def delete_batch(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """刪除批次任務（不會刪除已上傳的檔案）"""
    try:
        batch = await db.get(BatchTask, batch_id)
        if not batch:
            raise HTTPException(status_code=404, detail="批次任務不存在")
        
        # 只刪除批次任務，不刪除檔案（因為設定了 ON DELETE SET NULL）
        await db.delete(batch)
        await db.commit()
        
        logger.info(f"Deleted batch task: {batch_id}")
        return {"message": "批次任務已刪除", "batch_id": str(batch_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))