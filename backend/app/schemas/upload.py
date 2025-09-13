"""
上傳相關的 Pydantic schemas
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID

from app.models.upload import UploadStatus, UploadType


class UploadRecordResponse(BaseModel):
    """上傳記錄回應"""
    id: UUID
    filename: str
    upload_type: UploadType
    status: UploadStatus
    file_size: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_log: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class MediaUploadRequest(BaseModel):
    """媒體上傳請求"""
    tags: Optional[List[str]] = Field(default_factory=list, description="標籤列表")
    description: Optional[str] = Field(None, description="備註")
    
    @validator('tags')
    def validate_tags(cls, v):
        if v is not None and len(v) > 10:
            raise ValueError('標籤數量不能超過10個')
        return v


class ContactsUploadRequest(BaseModel):
    """聯絡人上傳請求"""
    field_mapping: Optional[Dict[str, str]] = Field(default_factory=dict, description="欄位映射")
    use_llm: bool = Field(default=True, description="是否使用 LLM 自動辨識聯絡人資訊")
    
    @validator('field_mapping')
    def validate_field_mapping(cls, v, values):
        # 如果使用 LLM，不需要驗證 field_mapping
        use_llm = values.get('use_llm', True)
        
        # 只有當不使用 LLM 且有映射時才驗證
        if not use_llm and v is not None and v:
            # organization 是必填欄位
            if 'organization' not in v.values():
                raise ValueError('不使用 LLM 時必須包含 organization（機構）欄位')
            # phone 或 email 至少需要一個
            contact_fields = ['phone', 'email']
            has_contact = any(field in v.values() for field in contact_fields)
            if not has_contact:
                raise ValueError('不使用 LLM 時必須包含 phone 或 email 其中一個欄位')
        return v


class ArticleUploadRequest(BaseModel):
    """文章上傳請求"""
    category: str = Field(..., description="分類")
    source: str = Field(..., description="來源")
    lang: str = Field(default="zh-TW", description="語言")
    published_date: Optional[datetime] = Field(None, description="發布日期")
    
    @validator('category', 'source')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('分類和來源不能為空')
        return v.strip()
    
    @validator('lang')
    def validate_lang(cls, v):
        allowed_langs = ['zh-TW', 'en', 'vi', 'id', 'th']
        if v not in allowed_langs:
            raise ValueError(f'語言必須是以下之一: {", ".join(allowed_langs)}')
        return v


class TextUploadRequest(BaseModel):
    """文字上傳請求"""
    title: str = Field(..., description="標題")
    content: str = Field(..., description="內容")
    category: str = Field(..., description="分類")
    source: str = Field(..., description="來源")
    lang: str = Field(default="zh-TW", description="語言")
    published_date: Optional[datetime] = Field(None, description="發布日期")
    
    @validator('title', 'content', 'category', 'source')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('標題、內容、分類和來源不能為空')
        return v.strip()
    
    @validator('lang')
    def validate_lang(cls, v):
        allowed_langs = ['zh-TW', 'en', 'vi', 'id', 'th']
        if v not in allowed_langs:
            raise ValueError(f'語言必須是以下之一: {", ".join(allowed_langs)}')
        return v


class SearchRequest(BaseModel):
    """搜尋請求"""
    query: str = Field(..., description="搜尋查詢")
    k: int = Field(default=10, ge=1, le=50, description="返回結果數量")
    threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="相似度閾值")
    filter_type: Optional[str] = Field(None, description="篩選類型: authority, article, all")
    category: Optional[str] = Field(None, description="分類篩選")
    lang: Optional[str] = Field(None, description="語言篩選")
    date_from: Optional[datetime] = Field(None, description="開始日期")
    date_to: Optional[datetime] = Field(None, description="結束日期")
    
    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('搜尋查詢不能為空')
        return v.strip()
    
    @validator('filter_type')
    def validate_filter_type(cls, v):
        if v is not None and v not in ['authority', 'article', 'all']:
            raise ValueError('篩選類型必須是 authority、article 或 all')
        return v


class SearchResult(BaseModel):
    """搜尋結果"""
    id: str
    type: str  # "authority" 或 "article"
    title: str
    content: str
    similarity_score: Optional[float] = None
    source: Optional[str] = None
    category: Optional[str] = None
    lang: Optional[str] = None
    published_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """搜尋回應"""
    results: List[SearchResult]
    total_count: int
    authority_count: int
    article_count: int
    query_params: Dict[str, Any]


class AuthoritativeMediaResponse(BaseModel):
    """權威媒體回應"""
    id: UUID
    upload_id: Optional[UUID] = None
    filename: str
    file_size: int
    mime_type: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    exif_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class AuthoritativeContactsResponse(BaseModel):
    """權威機構聯絡資訊回應"""
    id: UUID
    upload_id: Optional[UUID] = None
    organization: str  # 機構名稱（必填）
    phone: Optional[str] = None  # 聯絡電話
    email: Optional[str] = None  # 電子郵件
    tags: Optional[List[str]] = None  # 標籤分類
    notes: Optional[str] = None  # 備註（服務時間、服務內容等）
    created_at: datetime
    updated_at: datetime
