#!/usr/bin/env python
"""批次上傳範例程式"""

import asyncio
import aiohttp
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

async def batch_upload_files(file_paths):
    """批次上傳檔案
    
    Args:
        file_paths: 檔案路徑列表
    """
    async with aiohttp.ClientSession() as session:
        # 1. 建立批次任務
        async with session.post(
            f"{BASE_URL}/batch/create",
            params={"file_count": len(file_paths)}
        ) as resp:
            batch_data = await resp.json()
            batch_id = batch_data["batch_id"]
            print(f"建立批次: {batch_id}")
        
        # 2. 上傳每個檔案
        for file_path in file_paths:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"檔案不存在: {file_path}")
                continue
                
            with open(file_path, 'rb') as f:
                form_data = aiohttp.FormData()
                form_data.add_field('file', f, filename=file_path.name)
                form_data.add_field('category', 'knowledge')  # 分類
                form_data.add_field('source', 'manual_upload')  # 來源
                form_data.add_field('lang', 'zh-TW')  # 語言
                
                async with session.post(
                    f"{BASE_URL}/batch/{batch_id}/upload",
                    data=form_data
                ) as resp:
                    if resp.status == 200:
                        print(f"✅ 上傳成功: {file_path.name}")
                    else:
                        print(f"❌ 上傳失敗: {file_path.name}")
        
        # 3. 檢查批次狀態
        print("\n等待處理完成...")
        while True:
            await asyncio.sleep(2)
            async with session.get(f"{BASE_URL}/batch/{batch_id}/status") as resp:
                status = await resp.json()
                completed = status["completed_files"]
                total = status["total_files"]
                failed = status["failed_files"]
                
                print(f"進度: {completed}/{total} (失敗: {failed})")
                
                if completed + failed >= total:
                    print("批次處理完成！")
                    break

# 使用範例
if __name__ == "__main__":
    # 準備要上傳的檔案列表
    files_to_upload = [
        "/path/to/document1.pdf",
        "/path/to/document2.txt",
        "/path/to/document3.md",
        # 加入你的檔案路徑
    ]
    
    # 執行批次上傳
    asyncio.run(batch_upload_files(files_to_upload))