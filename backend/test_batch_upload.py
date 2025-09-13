#!/usr/bin/env python3
"""
批次上傳API測試腳本
測試所有批次上傳相關的API端點
"""

import requests
import json
import time
import os
from pathlib import Path
import tempfile
from typing import Dict, Any

# API基礎URL
BASE_URL = "http://localhost:8000/api/v1"
BATCH_API = f"{BASE_URL}/batch"

# 顏色定義
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_test(test_name: str):
    """印出測試名稱"""
    print(f"\n{BLUE}{BOLD}測試: {test_name}{RESET}")


def print_success(message: str):
    """印出成功訊息"""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message: str):
    """印出錯誤訊息"""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message: str):
    """印出資訊"""
    print(f"{YELLOW}ℹ {message}{RESET}")


def create_test_files():
    """建立測試檔案"""
    test_files = []
    temp_dir = tempfile.mkdtemp()
    
    # 建立測試文字檔
    test_txt = Path(temp_dir) / "test_document.txt"
    test_txt.write_text("這是測試文件內容\n測試批次上傳功能")
    test_files.append(test_txt)
    
    # 建立測試Markdown檔
    test_md = Path(temp_dir) / "test_readme.md"
    test_md.write_text("# 測試文件\n\n這是一個測試用的Markdown文件。")
    test_files.append(test_md)
    
    # 建立假的PDF檔案（實際測試時應該用真實PDF）
    test_pdf = Path(temp_dir) / "test_doc.pdf"
    test_pdf.write_bytes(b"%PDF-1.4\ntest content")
    test_files.append(test_pdf)
    
    return test_files


def test_create_batch():
    """測試建立批次任務"""
    print_test("建立批次任務")
    
    try:
        response = requests.post(
            f"{BATCH_API}/create",
            params={"file_count": 3}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"批次任務建立成功: {data}")
            return data.get("batch_id")
        else:
            print_error(f"建立失敗: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"請求失敗: {e}")
        return None


def test_upload_file_to_batch(batch_id: str, file_path: Path):
    """測試上傳檔案到批次"""
    print_test(f"上傳檔案: {file_path.name}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            data = {
                'relative_path': f"test/{file_path.name}",
                'category': 'test',
                'source': 'test_script',
                'lang': 'zh-TW'
            }
            
            response = requests.post(
                f"{BATCH_API}/{batch_id}/upload",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"檔案上傳成功: {result}")
                return result.get("upload_id")
            else:
                print_error(f"上傳失敗: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print_error(f"上傳失敗: {e}")
        return None


def test_get_batch_status(batch_id: str):
    """測試取得批次狀態"""
    print_test("取得批次狀態")
    
    try:
        response = requests.get(f"{BATCH_API}/{batch_id}/status")
        
        if response.status_code == 200:
            data = response.json()
            print_success("取得批次狀態成功")
            print_info(f"狀態: {data.get('status')}")
            print_info(f"總檔案數: {data.get('total_files')}")
            print_info(f"完成數: {data.get('completed_files')}")
            print_info(f"失敗數: {data.get('failed_files')}")
            print_info(f"進度: {data.get('progress')}%")
            return data
        else:
            print_error(f"取得狀態失敗: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"請求失敗: {e}")
        return None


def test_get_file_status(upload_id: str):
    """測試取得單一檔案狀態"""
    print_test(f"取得檔案狀態: {upload_id}")
    
    try:
        response = requests.get(f"{BATCH_API}/file/{upload_id}/status")
        
        if response.status_code == 200:
            data = response.json()
            print_success("取得檔案狀態成功")
            print_info(f"檔名: {data.get('filename')}")
            print_info(f"狀態: {data.get('status')}")
            print_info(f"進度: {data.get('progress')}%")
            return data
        else:
            print_error(f"取得狀態失敗: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"請求失敗: {e}")
        return None


def test_list_batches():
    """測試列出所有批次"""
    print_test("列出所有批次")
    
    try:
        response = requests.get(f"{BATCH_API}/list")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"取得批次列表成功: 共 {data.get('total', 0)} 個批次")
            
            for batch in data.get('batches', [])[:3]:  # 只顯示前3個
                print_info(f"批次 {batch.get('id')}: {batch.get('status')} ({batch.get('progress')}%)")
            
            return data
        else:
            print_error(f"取得列表失敗: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"請求失敗: {e}")
        return None


def test_delete_batch(batch_id: str):
    """測試刪除批次"""
    print_test(f"刪除批次: {batch_id}")
    
    try:
        response = requests.delete(f"{BATCH_API}/{batch_id}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"批次刪除成功: {data.get('message')}")
            return True
        else:
            print_error(f"刪除失敗: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print_error(f"請求失敗: {e}")
        return False


def monitor_batch_progress(batch_id: str, max_wait: int = 30):
    """監控批次處理進度"""
    print_test("監控批次處理進度")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        status = test_get_batch_status(batch_id)
        if not status:
            break
            
        if status.get('status') in ['completed', 'failed']:
            print_success(f"批次處理完成: {status.get('status')}")
            break
            
        time.sleep(2)  # 每2秒檢查一次
    
    if time.time() - start_time >= max_wait:
        print_info("達到最大等待時間")


def run_all_tests():
    """執行所有測試"""
    print(f"\n{BOLD}{'='*50}")
    print("批次上傳API測試")
    print(f"{'='*50}{RESET}")
    
    # 1. 建立批次
    batch_id = test_create_batch()
    if not batch_id:
        print_error("無法建立批次，測試中止")
        return
    
    # 2. 建立測試檔案
    test_files = create_test_files()
    print_info(f"建立了 {len(test_files)} 個測試檔案")
    
    # 3. 上傳檔案到批次
    upload_ids = []
    for file_path in test_files:
        upload_id = test_upload_file_to_batch(batch_id, file_path)
        if upload_id:
            upload_ids.append(upload_id)
    
    # 4. 取得批次狀態
    time.sleep(1)  # 等待一下讓處理開始
    test_get_batch_status(batch_id)
    
    # 5. 取得單一檔案狀態
    if upload_ids:
        test_get_file_status(upload_ids[0])
    
    # 6. 列出所有批次
    test_list_batches()
    
    # 7. 監控處理進度（等待最多30秒）
    monitor_batch_progress(batch_id, max_wait=30)
    
    # 8. 刪除測試批次（可選）
    # test_delete_batch(batch_id)
    
    # 清理測試檔案
    for file_path in test_files:
        try:
            file_path.unlink()
        except:
            pass
    
    print(f"\n{GREEN}{BOLD}測試完成！{RESET}")


def test_health_check():
    """測試服務是否運行"""
    print_test("健康檢查")
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print_success("後端服務運行正常")
            return True
        else:
            print_error(f"服務異常: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"無法連接到後端服務: {e}")
        print_info("請確認後端服務是否已啟動: python -m uvicorn app.main:app --reload")
        return False


if __name__ == "__main__":
    # 先檢查服務是否運行
    if test_health_check():
        run_all_tests()
    else:
        print(f"\n{RED}請先啟動後端服務再執行測試{RESET}")