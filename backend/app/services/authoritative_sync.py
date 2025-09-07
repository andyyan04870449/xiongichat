"""
權威資料與知識庫同步服務
"""
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db_context
from app.models.upload import AuthoritativeContacts
from app.models.knowledge import KnowledgeDocument
from app.services.knowledge_manager import KnowledgeManager

logger = logging.getLogger(__name__)


class AuthoritativeKnowledgeSync:
    """權威資料與知識庫同步服務"""
    
    def __init__(self):
        self.knowledge_manager = KnowledgeManager()
    
    def format_contact_content(self, contact: AuthoritativeContacts) -> str:
        """格式化權威聯絡資料為知識內容"""
        content_parts = [contact.organization]
        
        if contact.phone:
            content_parts.append(f"電話：{contact.phone}")
        if contact.email:
            content_parts.append(f"電子郵件：{contact.email}")
        if contact.tags:
            tags_str = "、".join(contact.tags)
            content_parts.append(f"服務類型：{tags_str}")
        if contact.notes:
            content_parts.append(f"服務說明：{contact.notes}")
        
        return "\n".join(content_parts)
    
    async def sync_create(self, contact: AuthoritativeContacts) -> Optional[KnowledgeDocument]:
        """同步新增權威資料到知識庫"""
        try:
            title = f"機構聯絡資訊: {contact.organization}"
            content = self.format_contact_content(contact)
            
            # 檢查是否已存在
            async with get_db_context() as db:
                existing = await db.execute(
                    select(KnowledgeDocument).where(
                        KnowledgeDocument.title == title,
                        KnowledgeDocument.source == "authoritative_contacts"
                    )
                )
                if existing.scalar_one_or_none():
                    logger.info(f"Knowledge document already exists for {contact.organization}")
                    return existing.scalar_one_or_none()
            
            # 使用KnowledgeManager創建知識文件
            doc_id = await self.knowledge_manager.add_document(
                title=title,
                content=content,
                source="authoritative_contacts",
                category="contacts"
            )
            
            # 返回創建的文件
            async with get_db_context() as db:
                result = await db.execute(
                    select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id)
                )
                knowledge_doc = result.scalar_one()
            
            logger.info(f"Synced authoritative contact to knowledge: {contact.organization}")
            return knowledge_doc
            
        except Exception as e:
            logger.error(f"Error syncing create for {contact.organization}: {str(e)}")
            raise
    
    async def sync_update(self, contact: AuthoritativeContacts) -> Optional[KnowledgeDocument]:
        """同步更新權威資料到知識庫"""
        try:
            title = f"機構聯絡資訊: {contact.organization}"
            new_content = self.format_contact_content(contact)
            
            async with get_db_context() as db:
                # 查找對應的知識文件
                result = await db.execute(
                    select(KnowledgeDocument).where(
                        KnowledgeDocument.title == title,
                        KnowledgeDocument.source == "authoritative_contacts"
                    )
                )
                knowledge_doc = result.scalar_one_or_none()
                
                if knowledge_doc:
                    # 更新現有文件
                    await self.knowledge_manager.update_document(
                        str(knowledge_doc.id),
                        content=new_content
                    )
                    logger.info(f"Updated knowledge document for {contact.organization}")
                    return knowledge_doc
                else:
                    # 如果不存在就創建
                    return await self.sync_create(contact)
                    
        except Exception as e:
            logger.error(f"Error syncing update for {contact.organization}: {str(e)}")
            raise
    
    async def sync_delete(self, organization_name: str) -> bool:
        """同步刪除權威資料對應的知識庫記錄"""
        try:
            title = f"機構聯絡資訊: {organization_name}"
            
            async with get_db_context() as db:
                # 查找對應的知識文件
                result = await db.execute(
                    select(KnowledgeDocument).where(
                        KnowledgeDocument.title == title,
                        KnowledgeDocument.source == "authoritative_contacts"
                    )
                )
                knowledge_doc = result.scalar_one_or_none()
                
                if knowledge_doc:
                    # 刪除知識文件（包括embeddings）
                    await self.knowledge_manager.delete_document(str(knowledge_doc.id))
                    logger.info(f"Deleted knowledge document for {organization_name}")
                    return True
                else:
                    logger.info(f"No knowledge document found for {organization_name}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error syncing delete for {organization_name}: {str(e)}")
            raise
    
    async def repair_missing_syncs(self) -> int:
        """修復遺漏的同步"""
        try:
            synced_count = 0
            
            async with get_db_context() as db:
                # 獲取所有權威聯絡資料
                result = await db.execute(select(AuthoritativeContacts))
                contacts = result.scalars().all()
                
                for contact in contacts:
                    title = f"機構聯絡資訊: {contact.organization}"
                    
                    # 檢查是否已有對應的知識文件
                    existing = await db.execute(
                        select(KnowledgeDocument).where(
                            KnowledgeDocument.title == title,
                            KnowledgeDocument.source == "authoritative_contacts"
                        )
                    )
                    
                    if not existing.scalar_one_or_none():
                        # 缺失的同步，補上
                        await self.sync_create(contact)
                        synced_count += 1
                        logger.info(f"Repaired missing sync for {contact.organization}")
            
            logger.info(f"Repaired {synced_count} missing syncs")
            return synced_count
            
        except Exception as e:
            logger.error(f"Error repairing missing syncs: {str(e)}")
            raise