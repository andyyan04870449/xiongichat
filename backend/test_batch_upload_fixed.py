#!/usr/bin/env python
"""測試修復後的批次上傳 API"""

import asyncio
import aiohttp
import json
from pathlib import Path
import tempfile
import os
from typing import List, Dict
import time

BASE_URL = "http://localhost:8000/api/v1"

async def create_test_files() -> List[Path]:
    """建立測試檔案"""
    test_files = []
    temp_dir = Path(tempfile.mkdtemp())
    
    # 建立文字檔案
    txt_file = temp_dir / "test_document.txt"
    txt_file.write_text("This is a test document with some content.\nLine 2\nLine 3")
    test_files.append(txt_file)
    
    # 建立 Markdown 檔案
    md_file = temp_dir / "test_readme.md"
    md_file.write_text("# Test README\n\n## Section 1\n\nSome content here.\n\n## Section 2\n\nMore content.")
    test_files.append(md_file)
    
    # 建立 CSV 檔案
    csv_file = temp_dir / "test_data.csv"
    csv_file.write_text("name,value,description\nItem1,100,First item\nItem2,200,Second item\nItem3,300,Third item")
    test_files.append(csv_file)
    
    return test_files

async def test_batch_upload():
    """測試批次上傳流程"""
    async with aiohttp.ClientSession() as session:
        # 建立測試檔案
        test_files = await create_test_files()
        print(f"建立了 {len(test_files)} 個測試檔案")
        
        # 1. 建立批次任務
        print("\n1. 建立批次任務...")
        async with session.post(
            f"{BASE_URL}/batch/create",
            params={"file_count": len(test_files)}
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                print(f"❌ 建立批次失敗: {resp.status} - {error_text}")
                return
            
            batch_data = await resp.json()
            batch_id = batch_data["batch_id"]
            print(f"✅ 批次任務建立成功: {batch_id}")
        
        # 2. 上傳檔案到批次
        upload_ids = []
        for i, file_path in enumerate(test_files, 1):
            print(f"\n2.{i} 上傳檔案: {file_path.name}")
            
            with open(file_path, 'rb') as f:
                form_data = aiohttp.FormData()
                form_data.add_field('file', f, filename=file_path.name)
                form_data.add_field('relative_path', f"test/{file_path.name}")
                form_data.add_field('category', 'test')
                form_data.add_field('source', 'test_upload')
                form_data.add_field('lang', 'zh-TW')
                
                async with session.post(
                    f"{BASE_URL}/batch/{batch_id}/upload",
                    data=form_data
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        print(f"❌ 上傳失敗: {resp.status} - {error_text}")
                        continue
                    
                    upload_data = await resp.json()
                    upload_ids.append(upload_data["upload_id"])
                    print(f"✅ 檔案上傳成功: {upload_data['upload_id']}")
        
        # 3. 等待處理並檢查狀態
        print("\n3. 等待檔案處理...")
        await asyncio.sleep(2)  # 等待背景任務啟動
        
        max_wait = 30  # 最多等待 30 秒
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            async with session.get(f"{BASE_URL}/batch/{batch_id}/status") as resp:
                if resp.status != 200:
                    print(f"❌ 取得狀態失敗: {resp.status}")
                    break
                
                status_data = await resp.json()
                completed = status_data.get("completed_files", 0)
                failed = status_data.get("failed_files", 0)
                processing = status_data.get("processing_files", 0)
                total = status_data.get("total_files", 0)
                
                print(f"狀態: 完成 {completed}/{total}, 失敗 {failed}, 處理中 {processing}")
                
                # 顯示每個檔案的狀態
                for file_info in status_data.get("files", []):
                    status = file_info["status"]
                    progress = file_info.get("progress", 0)
                    filename = file_info["filename"]
                    
                    if status == "failed":
                        print(f"  ❌ {filename}: {status} - {file_info.get('error', 'Unknown error')}")
                    elif status == "completed":
                        print(f"  ✅ {filename}: {status}")
                    else:
                        print(f"  ⏳ {filename}: {status} ({progress}%)")
                
                # 如果所有檔案都處理完成（成功或失敗），退出循環
                if completed + failed >= total:
                    print(f"\n批次處理完成！成功: {completed}, 失敗: {failed}")
                    break
            
            await asyncio.sleep(2)
        
        # 4. 檢查上傳的檔案是否正確儲存
        print("\n4. 檢查儲存的檔案...")
        uploads_dir = Path("uploads")
        if uploads_dir.exists():
            saved_files = list(uploads_dir.glob("*"))
            print(f"找到 {len(saved_files)} 個儲存的檔案")
            
            # 檢查最近的檔案大小
            for upload_id in upload_ids[-3:]:  # 檢查最後3個
                matching_files = list(uploads_dir.glob(f"{upload_id}*"))
                if matching_files:
                    file_path = matching_files[0]
                    size = file_path.stat().st_size
                    print(f"  檔案 {file_path.name}: {size} bytes")
                    if size == 0:
                        print(f"    ⚠️ 警告: 檔案大小為 0!")
                    else:
                        # 顯示檔案內容的前100個字元
                        try:
                            content = file_path.read_text()[:100]
                            print(f"    內容預覽: {content}...")
                        except:
                            print(f"    (二進位檔案)")
        
        # 清理測試檔案
        for file_path in test_files:
            file_path.unlink()
        test_files[0].parent.rmdir()
        
        print("\n✅ 測試完成！")

if __name__ == "__main__":
    asyncio.run(test_batch_upload())