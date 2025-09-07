#!/usr/bin/env python
"""測試最近上傳記錄查詢"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.upload_service import UploadService
from app.database import get_db_context
from sqlalchemy import select
from app.models.upload import UploadRecord

async def test_recent_uploads():
    """測試最近上傳記錄"""
    
    print("1. 直接查詢資料庫...")
    try:
        async with get_db_context() as db:
            result = await db.execute(
                select(UploadRecord)
                .order_by(UploadRecord.created_at.desc())
                .limit(5)
            )
            records = result.scalars().all()
            
            print(f"   找到 {len(records)} 筆記錄")
            for record in records:
                print(f"   - {record.filename} ({record.upload_type}) - {record.status}")
                print(f"     ID: {record.id}")
                print(f"     Created: {record.created_at}")
    except Exception as e:
        print(f"   ❌ 查詢失敗: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n2. 使用 UploadService...")
    try:
        service = UploadService()
        records = await service.get_recent_uploads(5)
        
        print(f"   找到 {len(records)} 筆記錄")
        for record in records:
            print(f"   - {record.filename} ({record.upload_type}) - {record.status}")
    except Exception as e:
        print(f"   ❌ 查詢失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_recent_uploads())