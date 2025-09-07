import asyncio
import sys
sys.path.insert(0, '/Users/yangandy/KaohsiungCare/backend')

from app.services.upload_service import UploadService
from app.services.knowledge_manager import KnowledgeManager
from app.models.upload import UploadType
import uuid

async def test_direct_upload():
    """直接測試上傳功能"""
    
    upload_service = UploadService()
    
    # 建立測試資料
    contacts_data = [
        {
            'organization': '高雄市毒品危害防制中心',
            'phone': '07-2134875',
            'email': 'khdrugprev@kcg.gov.tw',
            'tags': ['戒毒諮詢', '個案管理'],
            'notes': '提供24小時戒毒成功專線及個案管理服務'
        },
        {
            'organization': '高雄市立凱旋醫院',
            'phone': '07-7513171',
            'email': 'info@ksph.kcg.gov.tw',
            'tags': ['醫療服務', '成癮治療'],
            'notes': '成癮治療門診、美沙冬替代療法'
        }
    ]
    
    # 建立上傳記錄
    upload_record = await upload_service.create_upload_record(
        filename='test_direct.csv',
        upload_type=UploadType.AUTHORITY_CONTACTS,
        metadata={'test': True}
    )
    
    print(f"建立上傳記錄: {upload_record.id}")
    
    # 直接儲存到資料庫
    from app.database import get_db_context
    from app.models.upload import AuthoritativeContacts
    
    contacts_records = []
    async with get_db_context() as db:
        for contact_data in contacts_data:
            contact_record = AuthoritativeContacts(
                upload_id=upload_record.id,
                organization=contact_data['organization'],
                phone=contact_data.get('phone'),
                email=contact_data.get('email'),
                tags=contact_data.get('tags'),
                notes=contact_data.get('notes')
            )
            db.add(contact_record)
            contacts_records.append(contact_record)
        
        await db.commit()
        
        for record in contacts_records:
            await db.refresh(record)
            print(f"儲存聯絡資料: {record.organization}")
    
    # 建立 RAG 索引
    for contact_record in contacts_records:
        try:
            await upload_service._create_contact_rag_index(contact_record)
            print(f"建立 RAG 索引: {contact_record.organization}")
        except Exception as e:
            print(f"建立 RAG 索引失敗: {e}")
    
    # 更新狀態為完成
    await upload_service.update_upload_status(
        upload_record.id,
        UploadStatus.COMPLETED,
        processing_log={'contacts_count': len(contacts_records)}
    )
    
    print(f"處理完成，共 {len(contacts_records)} 筆資料")
    
    # 驗證資料
    async with get_db_context() as db:
        from sqlalchemy import select
        stmt = select(AuthoritativeContacts)
        result = await db.execute(stmt)
        all_contacts = result.scalars().all()
        print(f"\n資料庫中共有 {len(all_contacts)} 筆聯絡資料")
        for contact in all_contacts:
            print(f"  - {contact.organization}: {contact.phone}")

if __name__ == "__main__":
    from app.models.upload import UploadStatus
    asyncio.run(test_direct_upload())