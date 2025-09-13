#!/usr/bin/env python
"""快速測試批次上傳 - 自動建立測試檔案並上傳"""

import asyncio
import aiohttp
from pathlib import Path
import tempfile

BASE_URL = "http://localhost:8000/api/v1"

async def quick_test():
    """快速測試批次上傳功能"""
    
    # 建立臨時測試檔案
    temp_dir = Path(tempfile.mkdtemp())
    test_files = []
    
    # 建立測試文件
    (temp_dir / "測試文件1.txt").write_text("這是測試文件1的內容\n包含多行文字\n用於測試批次上傳功能")
    test_files.append(temp_dir / "測試文件1.txt")
    
    (temp_dir / "測試文件2.md").write_text("# 測試文件2\n\n## 章節一\n\n這是Markdown格式的測試文件")
    test_files.append(temp_dir / "測試文件2.md")
    
    (temp_dir / "資料.csv").write_text("名稱,數值,說明\n項目A,100,第一個項目\n項目B,200,第二個項目")
    test_files.append(temp_dir / "資料.csv")
    
    print(f"建立了 {len(test_files)} 個測試檔案")
    
    async with aiohttp.ClientSession() as session:
        # 1. 建立批次
        async with session.post(
            f"{BASE_URL}/batch/create",
            params={"file_count": len(test_files)}
        ) as resp:
            batch_data = await resp.json()
            batch_id = batch_data["batch_id"]
            print(f"✅ 建立批次: {batch_id}")
        
        # 2. 上傳檔案
        for file_path in test_files:
            with open(file_path, 'rb') as f:
                form_data = aiohttp.FormData()
                form_data.add_field('file', f, filename=file_path.name)
                form_data.add_field('category', 'test')
                form_data.add_field('source', 'test_upload')
                form_data.add_field('lang', 'zh-TW')
                
                async with session.post(
                    f"{BASE_URL}/batch/{batch_id}/upload",
                    data=form_data
                ) as resp:
                    if resp.status == 200:
                        print(f"✅ 上傳成功: {file_path.name}")
                    else:
                        error = await resp.text()
                        print(f"❌ 上傳失敗: {file_path.name} - {error}")
        
        # 3. 等待處理完成
        print("\n⏳ 等待處理...")
        for _ in range(10):  # 最多等待20秒
            await asyncio.sleep(2)
            
            async with session.get(f"{BASE_URL}/batch/{batch_id}/status") as resp:
                status = await resp.json()
                completed = status["completed_files"]
                failed = status["failed_files"]
                total = status["total_files"]
                
                print(f"進度: 完成 {completed}/{total}, 失敗 {failed}")
                
                # 顯示每個檔案狀態
                for file_info in status["files"]:
                    icon = "✅" if file_info["status"] == "completed" else "❌" if file_info["status"] == "failed" else "⏳"
                    print(f"  {icon} {file_info['filename']}: {file_info['status']}")
                
                if completed + failed >= total:
                    print(f"\n{'✅' if failed == 0 else '⚠️'} 批次處理完成！")
                    break
        
        # 清理臨時檔案
        for f in test_files:
            f.unlink()
        temp_dir.rmdir()
        
        print("\n測試結束")

if __name__ == "__main__":
    print("開始批次上傳測試...\n")
    asyncio.run(quick_test())