"""
上傳相關的 API endpoints
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import logging

from app.schemas.upload import (
    UploadRecordResponse, MediaUploadRequest, ContactsUploadRequest, 
    ArticleUploadRequest, TextUploadRequest, SearchRequest, SearchResponse,
    AuthoritativeMediaResponse, AuthoritativeContactsResponse
)
from app.services.upload_service import UploadService
from app.services.search_service import SearchService
from app.models.upload import UploadType

logger = logging.getLogger(__name__)

router = APIRouter(tags=["upload"])

# 服務實例
upload_service = UploadService()
search_service = SearchService()


@router.post("/media", response_model=UploadRecordResponse)
async def upload_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tags: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """上傳媒體檔案"""
    try:
        # 驗證檔案類型
        if not file.content_type or not file.content_type.startswith(('image/', 'video/', 'audio/')):
            raise HTTPException(status_code=400, detail="不支援的檔案類型")
        
        # 解析標籤
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # 建立上傳記錄
        upload_record = await upload_service.create_upload_record(
            filename=file.filename,
            upload_type=UploadType.AUTHORITY_MEDIA,
            file_size=file.size,
            metadata={"tags": tag_list, "description": description}
        )
        
        # 建立請求物件
        request = MediaUploadRequest(
            tags=tag_list,
            description=description
        )
        
        # 在背景處理上傳
        background_tasks.add_task(
            upload_service.process_media_upload,
            file, upload_record.id, request
        )
        
        logger.info(f"Media upload initiated: {upload_record.id}")
        return upload_record
        
    except Exception as e:
        logger.error(f"Error in media upload: {e}")
        raise HTTPException(status_code=500, detail=f"上傳失敗: {str(e)}")


@router.post("/contacts", response_model=UploadRecordResponse)
async def upload_contacts(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    field_mapping: Optional[str] = Form(None)
):
    """上傳聯絡人檔案"""
    try:
        # 驗證檔案類型
        if not file.filename.endswith(('.csv', '.xlsx', '.json')):
            raise HTTPException(status_code=400, detail="不支援的檔案類型，請使用 CSV、Excel 或 JSON 格式")
        
        # 解析欄位映射
        mapping_dict = {}
        if field_mapping:
            try:
                import json
                mapping_dict = json.loads(field_mapping)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="欄位映射格式錯誤")
        
        # 建立上傳記錄
        upload_record = await upload_service.create_upload_record(
            filename=file.filename,
            upload_type=UploadType.AUTHORITY_CONTACTS,
            file_size=file.size,
            metadata={"field_mapping": mapping_dict}
        )
        
        # 建立請求物件
        request = ContactsUploadRequest(field_mapping=mapping_dict)
        
        # 先讀取檔案內容（在背景任務執行前）
        file_content = await file.read()
        await file.seek(0)  # 重置檔案指標
        
        # 在背景處理上傳
        background_tasks.add_task(
            upload_service.process_contacts_upload_with_content,
            file_content, file.filename, upload_record.id, request
        )
        
        logger.info(f"Contacts upload initiated: {upload_record.id}")
        return upload_record
        
    except Exception as e:
        logger.error(f"Error in contacts upload: {e}")
        raise HTTPException(status_code=500, detail=f"上傳失敗: {str(e)}")


@router.post("/article", response_model=UploadRecordResponse)
async def upload_article(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: str = Form(...),
    source: str = Form(...),
    lang: str = Form("zh-TW"),
    published_date: Optional[str] = Form(None)
):
    """上傳文章檔案"""
    try:
        # 驗證檔案類型
        allowed_extensions = ['.pdf', '.docx', '.txt', '.md', '.html']
        if not any(file.filename.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="不支援的檔案類型")
        
        # 解析發布日期
        parsed_date = None
        if published_date:
            try:
                from datetime import datetime
                parsed_date = datetime.fromisoformat(published_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="發布日期格式錯誤")
        
        # 建立上傳記錄
        upload_record = await upload_service.create_upload_record(
            filename=file.filename,
            upload_type=UploadType.ARTICLE,
            file_size=file.size,
            metadata={
                "category": category,
                "source": source,
                "lang": lang,
                "published_date": parsed_date.isoformat() if parsed_date else None
            }
        )
        
        # 建立請求物件
        request = ArticleUploadRequest(
            category=category,
            source=source,
            lang=lang,
            published_date=parsed_date
        )
        
        # 在背景處理上傳
        background_tasks.add_task(
            upload_service.process_article_upload,
            file, upload_record.id, request
        )
        
        logger.info(f"Article upload initiated: {upload_record.id}")
        return upload_record
        
    except Exception as e:
        logger.error(f"Error in article upload: {e}")
        raise HTTPException(status_code=500, detail=f"上傳失敗: {str(e)}")


@router.post("/text", response_model=UploadRecordResponse)
async def upload_text(
    background_tasks: BackgroundTasks,
    request: TextUploadRequest
):
    """上傳文字內容"""
    try:
        # 建立上傳記錄
        upload_record = await upload_service.create_upload_record(
            filename=f"text_{request.title[:50]}.txt",
            upload_type=UploadType.ARTICLE,
            metadata=request.dict()
        )
        
        # 在背景處理上傳
        background_tasks.add_task(
            upload_service.process_text_upload,
            upload_record.id, request
        )
        
        logger.info(f"Text upload initiated: {upload_record.id}")
        return upload_record
        
    except Exception as e:
        logger.error(f"Error in text upload: {e}")
        raise HTTPException(status_code=500, detail=f"上傳失敗: {str(e)}")


@router.get("/status/{upload_id}", response_model=UploadRecordResponse)
async def get_upload_status(upload_id: UUID):
    """取得上傳狀態"""
    try:
        upload_record = await upload_service.get_upload_record(upload_id)
        if not upload_record:
            raise HTTPException(status_code=404, detail="上傳記錄不存在")
        
        return upload_record.to_response()
        
    except Exception as e:
        logger.error(f"Error getting upload status: {e}")
        raise HTTPException(status_code=500, detail=f"取得上傳狀態失敗: {str(e)}")


@router.get("/recent", response_model=List[UploadRecordResponse])
async def get_recent_uploads(limit: int = 10):
    """取得最近上傳記錄"""
    try:
        uploads = await upload_service.get_recent_uploads(limit)
        # 轉換為回應格式
        return [upload.to_response() for upload in uploads]
        
    except Exception as e:
        logger.error(f"Error getting recent uploads: {e}")
        raise HTTPException(status_code=500, detail=f"取得最近上傳記錄失敗: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(request: SearchRequest):
    """搜尋知識庫"""
    try:
        results = await search_service.search(request)
        return results
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail=f"搜尋失敗: {str(e)}")


@router.get("/authority/media", response_model=List[AuthoritativeMediaResponse])
async def get_authority_media(
    tags: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 50
):
    """取得權威媒體列表"""
    try:
        # 解析標籤
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # 解析日期
        parsed_date_from = None
        parsed_date_to = None
        if date_from:
            try:
                from datetime import datetime
                parsed_date_from = datetime.fromisoformat(date_from)
            except ValueError:
                raise HTTPException(status_code=400, detail="開始日期格式錯誤")
        
        if date_to:
            try:
                from datetime import datetime
                parsed_date_to = datetime.fromisoformat(date_to)
            except ValueError:
                raise HTTPException(status_code=400, detail="結束日期格式錯誤")
        
        media_list = await search_service.get_authority_media(
            tags=tag_list,
            date_from=parsed_date_from,
            date_to=parsed_date_to,
            limit=limit
        )
        
        return media_list
        
    except Exception as e:
        logger.error(f"Error getting authority media: {e}")
        raise HTTPException(status_code=500, detail=f"取得權威媒體失敗: {str(e)}")


@router.get("/authority/contacts", response_model=List[AuthoritativeContactsResponse])
async def get_authority_contacts(
    organization: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = 50
):
    """取得權威機構聯絡列表"""
    try:
        # 解析標籤
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        contacts_list = await search_service.get_authority_contacts(
            organization=organization,
            tags=tag_list,
            limit=limit
        )
        
        return contacts_list
        
    except Exception as e:
        logger.error(f"Error getting authority contacts: {e}")
        raise HTTPException(status_code=500, detail=f"取得權威機構聯絡資訊失敗: {str(e)}")
