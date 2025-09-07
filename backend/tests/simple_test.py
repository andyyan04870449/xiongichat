"""簡單測試腳本 - 測試關鍵問題場景"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_chat_api():
    """測試聊天API的關鍵場景"""
    
    base_url = "http://localhost:8000"
    
    # 測試案例
    test_cases = [
        {
            "id": "greeting_001",
            "description": "簡單問候",
            "message": "你好",
            "expected_not_contain": ["抱歉", "無法提供", "建議試試"]
        },
        {
            "id": "greeting_002", 
            "description": "詢問身份",
            "message": "你是誰",
            "expected_contain": ["雄i聊", "助理"],
            "expected_not_contain": ["抱歉", "無法提供"]
        },
        {
            "id": "info_001",
            "description": "地點查詢",
            "message": "毒防局在哪裡",
            "expected_contain": ["高雄", "地址"]
        },
        {
            "id": "emotion_001",
            "description": "情緒支持",
            "message": "最近壓力好大",
            "expected_contain": ["了解", "理解", "支持", "幫助"]
        }
    ]
    
    print("="*60)
    print("AI聊天系統測試")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        results = []
        
        for test in test_cases:
            print(f"\n測試: {test['description']}")
            print(f"輸入: {test['message']}")
            
            try:
                # 發送請求
                response = await client.post(
                    f"{base_url}/api/v1/chat/",  # 加上尾部斜線
                    json={
                        "user_id": f"test_{test['id']}",
                        "message": test['message']
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply", "")
                    
                    print(f"回應: {reply[:100]}...")
                    
                    # 檢查預期內容
                    passed = True
                    issues = []
                    
                    if "expected_contain" in test:
                        for keyword in test["expected_contain"]:
                            if keyword not in reply:
                                passed = False
                                issues.append(f"缺少預期內容: {keyword}")
                    
                    if "expected_not_contain" in test:
                        for keyword in test["expected_not_contain"]:
                            if keyword in reply:
                                passed = False
                                issues.append(f"包含不應有的內容: {keyword}")
                    
                    if passed:
                        print("✅ 測試通過")
                    else:
                        print(f"❌ 測試失敗")
                        for issue in issues:
                            print(f"   - {issue}")
                    
                    results.append({
                        "test_id": test["id"],
                        "description": test["description"],
                        "passed": passed,
                        "reply": reply,
                        "issues": issues
                    })
                    
                else:
                    print(f"❌ API錯誤: {response.status_code}")
                    results.append({
                        "test_id": test["id"],
                        "description": test["description"],
                        "passed": False,
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                print(f"❌ 錯誤: {str(e)}")
                results.append({
                    "test_id": test["id"],
                    "description": test["description"],
                    "passed": False,
                    "error": str(e)
                })
            
            # 避免過快請求
            await asyncio.sleep(2)
    
    # 總結
    print("\n" + "="*60)
    print("測試總結")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for r in results if r.get("passed", False))
    
    print(f"總測試數: {total}")
    print(f"通過: {passed}")
    print(f"失敗: {total - passed}")
    print(f"通過率: {(passed/total)*100:.1f}%")
    
    # 保存結果
    with open(f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results


if __name__ == "__main__":
    asyncio.run(test_chat_api())