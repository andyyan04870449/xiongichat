"""測試資訊回答控制 - 確保AI不隨意提供未經驗證的資料"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_information_control():
    """測試AI是否正確控制資訊來源"""
    
    base_url = "http://localhost:8000"
    
    # 測試案例：詢問具體資訊
    test_cases = [
        {
            "id": "location_query",
            "message": "凱旋醫院在哪裡",
            "description": "詢問地址（應該不提供具體地址）",
            "should_not_contain": [
                "苓雅區", "凱旋二路", "130號", "地址"
            ],
            "should_contain_any": [
                "建議", "諮詢", "毒防局", "官方", "聯繫"
            ]
        },
        {
            "id": "phone_query",
            "message": "毒防局電話多少",
            "description": "詢問電話（除非知識庫有）",
            "should_not_contain": [
                "07-", "電話是", "號碼是"
            ],
            "should_contain_any": [
                "建議", "查詢", "官方網站", "諮詢"
            ]
        },
        {
            "id": "time_query",
            "message": "你們幾點上班",
            "description": "詢問時間（需要準確資訊）",
            "should_not_contain": [
                "早上8點", "下午5點", "週一到週五"
            ],
            "should_contain_any": [
                "服務時間", "建議", "詢問", "確認"
            ]
        },
        {
            "id": "general_chat",
            "message": "我心情不太好",
            "description": "一般對話（可以自由回答）",
            "should_not_contain": [
                "建議您可以"  # 不應該用資訊查詢的模板
            ],
            "should_contain_any": [
                "心情", "聊", "什麼", "發生", "理解"
            ]
        }
    ]
    
    print("="*60)
    print("資訊回答控制測試")
    print("="*60)
    print("\n測試目標：確保AI不會使用內建知識回答具體資訊\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        results = []
        
        for test in test_cases:
            print(f"測試 {test['id']}: {test['description']}")
            print(f"輸入: {test['message']}")
            
            try:
                # 發送請求
                response = await client.post(
                    f"{base_url}/api/v1/chat/",
                    json={
                        "user_id": f"test_control_{test['id']}",
                        "message": test['message']
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply", "")
                    
                    print(f"回應: {reply}\n")
                    
                    # 檢查結果
                    passed = True
                    issues = []
                    
                    # 檢查不應包含的內容（最重要）
                    for forbidden in test.get("should_not_contain", []):
                        if forbidden in reply:
                            passed = False
                            issues.append(f"❌ 包含具體資訊: {forbidden}")
                    
                    # 檢查應包含的替代方案
                    if "should_contain_any" in test:
                        found_any = False
                        for expected in test["should_contain_any"]:
                            if expected in reply:
                                found_any = True
                                break
                        if not found_any:
                            issues.append(f"⚠️ 未提供替代方案")
                    
                    # 顯示結果
                    if passed and not issues:
                        print("✅ 通過 - 正確控制資訊來源")
                    else:
                        print("❌ 失敗")
                        for issue in issues:
                            print(f"   {issue}")
                    
                    results.append({
                        "test_id": test["id"],
                        "description": test["description"],
                        "passed": passed and not issues,
                        "reply": reply,
                        "issues": issues
                    })
                    
                else:
                    print(f"❌ API錯誤: {response.status_code}\n")
                    
            except Exception as e:
                print(f"❌ 錯誤: {str(e)}\n")
            
            print("-"*40)
            await asyncio.sleep(2)
    
    # 總結
    print("\n" + "="*60)
    print("測試總結")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    
    print(f"總測試數: {total}")
    print(f"通過: {passed}")
    print(f"失敗: {total - passed}")
    print(f"通過率: {(passed/total)*100:.1f}%")
    
    # 分析結果
    print("\n重點發現:")
    
    # 檢查是否還在提供具體地址
    address_leaks = [r for r in results if any(
        addr in r["reply"] for addr in ["苓雅區", "凱旋二路", "130號"]
    )]
    
    if not address_leaks:
        print("✅ 成功：不再洩露具體地址資訊")
    else:
        print(f"⚠️ 警告：{len(address_leaks)} 個回應仍包含具體地址")
    
    # 檢查是否提供替代方案
    good_alternatives = [r for r in results if any(
        alt in r["reply"] for alt in ["建議", "諮詢", "官方"]
    ) and "心情" not in r["reply"]]  # 排除情感類回應
    
    if good_alternatives:
        print(f"✅ 良好：{len(good_alternatives)} 個查詢提供了替代方案")
    
    # 保存結果
    with open(f"info_control_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results


if __name__ == "__main__":
    asyncio.run(test_information_control())