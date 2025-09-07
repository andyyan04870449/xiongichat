#!/usr/bin/env python3
"""
測試 address 欄位功能
"""
import asyncio
import aiohttp
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

async def test_contact_with_address():
    """測試創建包含地址的聯絡人"""
    async with aiohttp.ClientSession() as session:
        # 創建新聯絡人
        contact_data = {
            "organization": "測試機構",
            "phone": "07-1234567",
            "email": "test@example.com",
            "address": "高雄市前金區中正四路211號",
            "tags": ["測試", "示範"],
            "notes": "這是測試用的聯絡資訊"
        }
        
        async with session.post(
            f"{BASE_URL}/api/v1/contacts",
            json=contact_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✓ 成功創建聯絡人: {result['id']}")
                print(f"  組織: {result['organization']}")
                print(f"  地址: {result.get('address', 'N/A')}")
                return result['id']
            else:
                print(f"✗ 創建失敗: {await response.text()}")
                return None

async def test_batch_upload():
    """測試批次上傳包含地址的聯絡人"""
    async with aiohttp.ClientSession() as session:
        # 準備 CSV 檔案
        csv_file = Path("test_data/test_contacts.csv")
        
        data = aiohttp.FormData()
        data.add_field('file',
                      open(csv_file, 'rb'),
                      filename='test_contacts.csv',
                      content_type='text/csv')
        
        # 欄位映射
        field_mapping = {
            "organization": "organization",
            "phone": "phone",
            "email": "email",
            "address": "address",
            "tags": "tags",
            "notes": "notes"
        }
        
        data.add_field('field_mapping', json.dumps(field_mapping))
        
        async with session.post(
            f"{BASE_URL}/api/v1/upload/contacts",
            data=data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✓ 批次上傳成功")
                print(f"  上傳ID: {result.get('upload_id')}")
                print(f"  聯絡人數: {result.get('contacts_count', 0)}")
            else:
                print(f"✗ 批次上傳失敗: {await response.text()}")

async def test_search_with_address():
    """測試搜尋功能是否包含地址資訊"""
    async with aiohttp.ClientSession() as session:
        search_data = {
            "query": "高雄市毒品危害防制中心",
            "k": 5,
            "filter_type": "authority"
        }
        
        async with session.post(
            f"{BASE_URL}/api/v1/search",
            json=search_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✓ 搜尋成功，找到 {result.get('total_count', 0)} 筆結果")
                
                for item in result.get('results', [])[:3]:
                    print(f"\n  標題: {item.get('title')}")
                    metadata = item.get('metadata', {})
                    if metadata.get('address'):
                        print(f"  地址: {metadata['address']}")
                    else:
                        print(f"  地址: (無)")
            else:
                print(f"✗ 搜尋失敗: {await response.text()}")

async def main():
    """執行測試"""
    print("=" * 50)
    print("測試 Address 欄位功能")
    print("=" * 50)
    
    # 測試 1: 創建單一聯絡人
    print("\n1. 測試創建包含地址的聯絡人:")
    contact_id = await test_contact_with_address()
    
    # 測試 2: 批次上傳
    print("\n2. 測試批次上傳包含地址的聯絡人:")
    await test_batch_upload()
    
    # 等待索引建立
    print("\n等待索引建立...")
    await asyncio.sleep(2)
    
    # 測試 3: 搜尋功能
    print("\n3. 測試搜尋功能是否返回地址資訊:")
    await test_search_with_address()
    
    print("\n" + "=" * 50)
    print("測試完成!")

if __name__ == "__main__":
    asyncio.run(main())