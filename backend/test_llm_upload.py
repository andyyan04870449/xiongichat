#!/usr/bin/env python3
"""
測試 LLM 聯絡人上傳功能
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent))
os.environ["PYTHONPATH"] = str(Path(__file__).parent)

import requests
import time

# API 基礎 URL
API_BASE = "http://localhost:8000/api/v1"

def test_llm_contact_upload():
    """測試使用 LLM 辨識聯絡人資訊的上傳功能"""
    
    # 建立測試文字檔案，包含多個機構資訊
    test_content = """
    高雄市毒品危害防制中心資訊：
    
    1. 高雄市立凱旋醫院
    地址：高雄市苓雅區凱旋二路130號
    電話：07-7513171
    服務項目：藥癮戒治、心理諮商、替代療法
    聯絡人：成癮防治科
    服務時間：週一至週五 08:00-17:00
    電子郵件：ksph@ksph.kcg.gov.tw
    
    2. 高雄市政府毒品防制局
    地址：高雄市前金區成功一路420號11樓
    電話：07-2118800
    服務內容：毒品防制政策規劃、個案管理、家庭支持服務
    聯絡人：個案管理組
    類別：政府機關
    
    3. 高雄市立民生醫院
    地址：高雄市苓雅區凱旋二路134號
    聯絡電話：07-7511131 分機2117
    提供服務：美沙冬替代治療、藥癮門診、心理輔導
    負責人：藥癮科主任
    機構類型：醫療院所
    
    4. 財團法人利伯他茲教育基金會
    地址：高雄市三民區九如一路775號
    電話：07-3801736
    服務項目：藥癮者職業訓練、就業輔導、社會復歸
    電子信箱：libertas@gmail.com
    聯絡窗口：社工部
    機構性質：民間團體
    
    5. 高雄市生命線協會
    地址：高雄市新興區大同一路181-6號3樓
    電話：07-2865580
    24小時專線：1995
    服務內容：自殺防治、心理諮商、危機處理
    聯絡人：值班社工
    備註：提供24小時電話協談服務
    """
    
    # 儲存為檔案
    test_file_path = "test_contacts.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print(f"建立測試檔案: {test_file_path}")
    
    # 上傳檔案
    print("\n開始上傳檔案...")
    with open(test_file_path, "rb") as f:
        files = {"file": ("test_contacts.txt", f, "text/plain")}
        data = {"field_mapping": "{}"}  # 空的欄位映射
        
        response = requests.post(f"{API_BASE}/upload/contacts", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        upload_id = result.get("id")
        print(f"✅ 上傳成功！Upload ID: {upload_id}")
        
        # 等待處理
        print("\n等待 LLM 處理...")
        max_attempts = 30
        for i in range(max_attempts):
            time.sleep(2)
            
            # 查詢狀態
            status_response = requests.get(f"{API_BASE}/batch/file/{upload_id}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                progress = status_data.get("progress", 0)
                
                print(f"狀態: {status}, 進度: {progress}%")
                
                if status == "completed":
                    print("\n✅ 處理完成！")
                    print(f"處理日誌: {status_data.get('processing_log')}")
                    break
                elif status == "failed":
                    print(f"\n❌ 處理失敗: {status_data.get('error_message')}")
                    break
            else:
                print(f"無法查詢狀態: {status_response.status_code}")
        else:
            print("\n⏱️ 處理超時")
    else:
        print(f"❌ 上傳失敗: {response.status_code}")
        print(response.text)
    
    # 清理測試檔案
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print(f"\n已清理測試檔案: {test_file_path}")

def test_search_contacts():
    """測試搜尋聯絡人功能"""
    print("\n" + "="*50)
    print("測試搜尋功能")
    print("="*50)
    
    search_queries = [
        "凱旋醫院",
        "美沙冬",
        "24小時",
        "民間團體"
    ]
    
    for query in search_queries:
        print(f"\n搜尋: {query}")
        response = requests.post(
            f"{API_BASE}/knowledge/search",
            json={
                "query": query,
                "k": 5,
                "threshold": 0.5
            }
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"找到 {len(results)} 筆結果")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result.get('title', 'No title')}")
                print(f"     相似度: {result.get('similarity_score', 0):.2f}")
        else:
            print(f"搜尋失敗: {response.status_code}")

if __name__ == "__main__":
    print("="*50)
    print("測試 LLM 聯絡人上傳功能")
    print("="*50)
    
    try:
        # 測試上傳
        test_llm_contact_upload()
        
        # 等待一下讓資料完全寫入
        time.sleep(3)
        
        # 測試搜尋
        test_search_contacts()
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()