#!/usr/bin/env python3
"""
測試 CSV 檔案上傳（使用 LLM 辨識）
"""
import requests
import time
import sys

# API 基礎 URL
API_BASE = "http://localhost:8000/api/v1"

def test_csv_upload():
    """測試上傳 CSV 檔案"""
    
    csv_file = "institution_contacts_analysis.csv"
    
    print(f"準備上傳檔案: {csv_file}")
    
    # 上傳檔案
    print("\n開始上傳檔案...")
    with open(csv_file, "rb") as f:
        files = {"file": (csv_file, f, "text/csv")}
        data = {
            "use_llm": "true",  # 使用 LLM 辨識
            "field_mapping": "{}"  # 空的欄位映射
        }
        
        response = requests.post(f"{API_BASE}/upload/contacts", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        upload_id = result.get("id")
        print(f"✅ 上傳成功！Upload ID: {upload_id}")
        
        # 等待處理
        print("\n等待處理...")
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
                    
                    # 查詢聯絡人資料
                    print("\n查詢已上傳的聯絡人資料...")
                    contacts_response = requests.get(f"{API_BASE}/contacts/authoritative")
                    if contacts_response.status_code == 200:
                        contacts = contacts_response.json().get("contacts", [])
                        print(f"找到 {len(contacts)} 筆聯絡人資料")
                        
                        # 顯示前5筆
                        for i, contact in enumerate(contacts[:5], 1):
                            print(f"\n{i}. {contact.get('name', contact.get('organization'))}")
                            print(f"   類別: {contact.get('category')}")
                            print(f"   電話: {contact.get('phone')}")
                            print(f"   服務: {contact.get('services')}")
                    
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

def test_search():
    """測試搜尋功能"""
    print("\n" + "="*50)
    print("測試搜尋功能")
    print("="*50)
    
    search_queries = [
        "凱旋醫院",
        "戒癮",
        "24小時",
        "職業訓練"
    ]
    
    for query in search_queries:
        print(f"\n搜尋: {query}")
        
        # 使用 GET 方法搜尋
        response = requests.get(
            f"{API_BASE}/knowledge/search",
            params={
                "query": query,
                "k": 5,
                "threshold": 0.5
            }
        )
        
        if response.status_code == 200:
            results = response.json()
            if isinstance(results, dict):
                results = results.get("results", [])
            
            print(f"找到 {len(results)} 筆結果")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result.get('title', 'No title')}")
                print(f"     相似度: {result.get('similarity_score', 0):.2f}")
        else:
            print(f"搜尋失敗: {response.status_code}")
            print(f"回應: {response.text[:200]}")

if __name__ == "__main__":
    print("="*50)
    print("測試 CSV 檔案上傳（使用 LLM）")
    print("="*50)
    
    try:
        # 測試上傳
        test_csv_upload()
        
        # 等待一下讓資料完全寫入
        time.sleep(3)
        
        # 測試搜尋
        test_search()
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()