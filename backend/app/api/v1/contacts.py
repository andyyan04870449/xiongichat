"""
權威機構聯絡資訊 CRUD API
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from datetime import datetime

from app.database import get_db_context
from app.models.upload import AuthoritativeContacts
from app.services.authoritative_sync import AuthoritativeKnowledgeSync
from sqlalchemy import select, or_
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["contacts"])

# 初始化同步服務
sync_service = AuthoritativeKnowledgeSync()


class ContactCreate(BaseModel):
    """建立聯絡資訊請求"""
    organization: str = Field(..., description="機構名稱")
    phone: Optional[str] = Field(None, description="聯絡電話")
    email: Optional[str] = Field(None, description="電子郵件")
    address: Optional[str] = Field(None, description="地址")
    tags: Optional[List[str]] = Field(default_factory=list, description="服務標籤")
    notes: Optional[str] = Field(None, description="備註說明")


class ContactUpdate(BaseModel):
    """更新聯絡資訊請求"""
    organization: Optional[str] = Field(None, description="機構名稱")
    phone: Optional[str] = Field(None, description="聯絡電話")
    email: Optional[str] = Field(None, description="電子郵件")
    address: Optional[str] = Field(None, description="地址")
    tags: Optional[List[str]] = Field(None, description="服務標籤")
    notes: Optional[str] = Field(None, description="備註說明")


class ContactResponse(BaseModel):
    """聯絡資訊回應"""
    id: UUID
    organization: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    tags: Optional[List[str]]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


@router.get("/contacts", response_model=List[ContactResponse])
async def get_contacts(
    search: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """取得聯絡資訊列表"""
    try:
        async with get_db_context() as db:
            query = select(AuthoritativeContacts)
            
            # 搜尋條件
            if search:
                search_pattern = f"%{search}%"
                query = query.where(
                    or_(
                        AuthoritativeContacts.organization.ilike(search_pattern),
                        AuthoritativeContacts.phone.ilike(search_pattern),
                        AuthoritativeContacts.email.ilike(search_pattern),
                        AuthoritativeContacts.notes.ilike(search_pattern)
                    )
                )
            
            # 標籤過濾
            if tag:
                # 使用 JSONB 包含運算符
                query = query.where(
                    AuthoritativeContacts.tags.contains([tag])
                )
            
            # 排序和分頁
            query = query.order_by(AuthoritativeContacts.organization)
            query = query.offset(offset).limit(limit)
            
            result = await db.execute(query)
            contacts = result.scalars().all()
            
            return [
                ContactResponse(
                    id=contact.id,
                    organization=contact.organization,
                    phone=contact.phone,
                    email=contact.email,
                    address=contact.address,
                    tags=contact.tags or [],
                    notes=contact.notes,
                    created_at=contact.created_at,
                    updated_at=contact.updated_at
                )
                for contact in contacts
            ]
            
    except Exception as e:
        logger.error(f"Error getting contacts: {e}")
        raise HTTPException(status_code=500, detail=f"取得聯絡資訊失敗: {str(e)}")


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: UUID):
    """取得單一聯絡資訊"""
    try:
        async with get_db_context() as db:
            query = select(AuthoritativeContacts).where(
                AuthoritativeContacts.id == contact_id
            )
            result = await db.execute(query)
            contact = result.scalar_one_or_none()
            
            if not contact:
                raise HTTPException(status_code=404, detail="聯絡資訊不存在")
            
            return ContactResponse(
                id=contact.id,
                organization=contact.organization,
                phone=contact.phone,
                email=contact.email,
                address=contact.address,
                tags=contact.tags or [],
                notes=contact.notes,
                created_at=contact.created_at,
                updated_at=contact.updated_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contact: {e}")
        raise HTTPException(status_code=500, detail=f"取得聯絡資訊失敗: {str(e)}")


@router.post("/contacts", response_model=ContactResponse)
async def create_contact(contact: ContactCreate):
    """建立新的聯絡資訊"""
    try:
        async with get_db_context() as db:
            # 檢查是否已存在相同機構
            existing = await db.execute(
                select(AuthoritativeContacts).where(
                    AuthoritativeContacts.organization == contact.organization
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="該機構已存在")
            
            # 建立新記錄
            new_contact = AuthoritativeContacts(
                organization=contact.organization,
                phone=contact.phone,
                email=contact.email,
                address=contact.address,
                tags=contact.tags,
                notes=contact.notes
            )
            
            db.add(new_contact)
            await db.commit()
            await db.refresh(new_contact)
            
            # 自動同步到知識庫
            try:
                await sync_service.sync_create(new_contact)
                logger.info(f"Created contact and synced to knowledge: {new_contact.id}")
            except Exception as sync_error:
                logger.error(f"Failed to sync contact to knowledge: {sync_error}")
                # 不中斷API響應，但記錄錯誤
            
            return ContactResponse(
                id=new_contact.id,
                organization=new_contact.organization,
                phone=new_contact.phone,
                email=new_contact.email,
                address=new_contact.address,
                tags=new_contact.tags or [],
                notes=new_contact.notes,
                created_at=new_contact.created_at,
                updated_at=new_contact.updated_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating contact: {e}")
        raise HTTPException(status_code=500, detail=f"建立聯絡資訊失敗: {str(e)}")


@router.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: UUID, contact: ContactUpdate):
    """更新聯絡資訊"""
    try:
        async with get_db_context() as db:
            # 查詢現有記錄
            query = select(AuthoritativeContacts).where(
                AuthoritativeContacts.id == contact_id
            )
            result = await db.execute(query)
            existing_contact = result.scalar_one_or_none()
            
            if not existing_contact:
                raise HTTPException(status_code=404, detail="聯絡資訊不存在")
            
            # 更新欄位
            if contact.organization is not None:
                existing_contact.organization = contact.organization
            if contact.phone is not None:
                existing_contact.phone = contact.phone
            if contact.email is not None:
                existing_contact.email = contact.email
            if contact.address is not None:
                existing_contact.address = contact.address
            if contact.tags is not None:
                existing_contact.tags = contact.tags
            if contact.notes is not None:
                existing_contact.notes = contact.notes
            
            await db.commit()
            await db.refresh(existing_contact)
            
            # 自動同步更新到知識庫
            try:
                await sync_service.sync_update(existing_contact)
                logger.info(f"Updated contact and synced to knowledge: {contact_id}")
            except Exception as sync_error:
                logger.error(f"Failed to sync contact update to knowledge: {sync_error}")
                # 不中斷API響應，但記錄錯誤
            
            return ContactResponse(
                id=existing_contact.id,
                organization=existing_contact.organization,
                phone=existing_contact.phone,
                email=existing_contact.email,
                address=existing_contact.address,
                tags=existing_contact.tags or [],
                notes=existing_contact.notes,
                created_at=existing_contact.created_at,
                updated_at=existing_contact.updated_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact: {e}")
        raise HTTPException(status_code=500, detail=f"更新聯絡資訊失敗: {str(e)}")


@router.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: UUID):
    """刪除聯絡資訊"""
    try:
        async with get_db_context() as db:
            # 查詢現有記錄
            query = select(AuthoritativeContacts).where(
                AuthoritativeContacts.id == contact_id
            )
            result = await db.execute(query)
            contact = result.scalar_one_or_none()
            
            if not contact:
                raise HTTPException(status_code=404, detail="聯絡資訊不存在")
            
            # 記錄機構名稱（刪除前）
            organization_name = contact.organization
            
            # 刪除記錄
            await db.delete(contact)
            await db.commit()
            
            # 自動同步刪除知識庫記錄
            try:
                await sync_service.sync_delete(organization_name)
                logger.info(f"Deleted contact and synced to knowledge: {contact_id}")
            except Exception as sync_error:
                logger.error(f"Failed to sync contact deletion to knowledge: {sync_error}")
                # 不中斷API響應，但記錄錯誤
            
            return {"message": "刪除成功", "id": str(contact_id)}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contact: {e}")
        raise HTTPException(status_code=500, detail=f"刪除聯絡資訊失敗: {str(e)}")


@router.get("/contacts/stats/summary")
async def get_contacts_stats():
    """取得聯絡資訊統計"""
    try:
        async with get_db_context() as db:
            # 總數
            total_result = await db.execute(
                select(AuthoritativeContacts)
            )
            total_contacts = len(total_result.scalars().all())
            
            # 取得所有聯絡資訊以計算標籤統計
            all_contacts = total_result.scalars().all()
            
            # 標籤統計
            tag_counts = {}
            for contact in all_contacts:
                if contact.tags:
                    for tag in contact.tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # 有電話的機構數
            phone_result = await db.execute(
                select(AuthoritativeContacts).where(
                    AuthoritativeContacts.phone.isnot(None)
                )
            )
            with_phone = len(phone_result.scalars().all())
            
            # 有Email的機構數
            email_result = await db.execute(
                select(AuthoritativeContacts).where(
                    AuthoritativeContacts.email.isnot(None)
                )
            )
            with_email = len(email_result.scalars().all())
            
            return {
                "total_contacts": total_contacts,
                "with_phone": with_phone,
                "with_email": with_email,
                "tag_distribution": tag_counts,
                "coverage": {
                    "phone_coverage": f"{(with_phone/total_contacts*100):.1f}%" if total_contacts > 0 else "0%",
                    "email_coverage": f"{(with_email/total_contacts*100):.1f}%" if total_contacts > 0 else "0%"
                }
            }
            
    except Exception as e:
        logger.error(f"Error getting contact stats: {e}")
        raise HTTPException(status_code=500, detail=f"取得統計資訊失敗: {str(e)}")


@router.post("/contacts/sync/repair")
async def repair_contact_sync():
    """修復遺漏的權威資料同步"""
    try:
        synced_count = await sync_service.repair_missing_syncs()
        
        return {
            "message": "同步修復完成",
            "synced_count": synced_count
        }
        
    except Exception as e:
        logger.error(f"Error repairing contact sync: {e}")
        raise HTTPException(status_code=500, detail=f"修復同步失敗: {str(e)}")