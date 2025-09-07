"""測試 Moderate 流程修復"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_moderate_scenarios():
    """測試修復後的 Moderate 流程"""
    
    base_url = "http://localhost:8000"
    
    # Moderate 流程的測試案例
    test_cases = [
        {
            "id": "self_intro",
            "message": "我是andy",
            "expected_not_contain": ["抱歉", "無法提供"],
            "expected_type": "greeting_response"
        },
        {
            "id": "stress",
            "message": "最近壓力好大",
            "expected_contain": ["了解", "理解", "支持", "幫助", "壓力"],
            "expected_not_contain": ["抱歉", "無法提供"],
            "expected_type": "empathy_response"
        },
        {
            "id": "mood",
            "message": "我心情不好",
            "expected_contain": ["了解", "理解", "心情", "支持", "聊"],
            "expected_not_contain": ["抱歉", "無法提供"],
            "expected_type": "empathy_response"
        },
        {
            "id": "sleep",
            "message": "睡不著",
            "expected_contain": ["睡", "休息", "放鬆"],
            "expected_not_contain": ["抱歉", "無法提供"],
            "expected_type": "support_response"
        }
    ]
    
    print("="*60)
    print("Moderate 流程修復測試")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        results = []
        
        for test in test_cases:
            print(f"\n測試案例: {test['id']}")
            print(f"輸入: {test['message']}")
            
            try:
                # 發送請求
                response = await client.post(
                    f"{base_url}/api/v1/chat/",
                    json={
                        "user_id": f"test_moderate_{test['id']}",
                        "message": test['message']
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply", "")
                    
                    print(f"回應: {reply}")
                    
                    # 檢查結果
                    passed = True
                    issues = []
                    
                    # 檢查不應包含的內容（最重要）
                    if "expected_not_contain" in test:
                        for keyword in test["expected_not_contain"]:
                            if keyword in reply:
                                passed = False
                                issues.append(f"❌ 包含不應有的內容: {keyword}")
                    
                    # 檢查應包含的內容
                    if "expected_contain" in test:
                        found_any = False
                        for keyword in test["expected_contain"]:
                            if keyword in reply:
                                found_any = True
                                break
                        if not found_any:
                            passed = False
                            issues.append(f"⚠️ 未包含預期關鍵詞")
                    
                    # 顯示結果
                    if passed:
                        print("✅ 測試通過 - 不再返回道歉訊息")
                    else:
                        print("❌ 測試失敗")
                        for issue in issues:
                            print(f"   {issue}")
                    
                    results.append({
                        "test_id": test["id"],
                        "passed": passed,
                        "reply": reply,
                        "issues": issues
                    })
                    
                else:
                    print(f"❌ API錯誤: {response.status_code}")
                    results.append({
                        "test_id": test["id"],
                        "passed": False,
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                print(f"❌ 錯誤: {str(e)}")
                results.append({
                    "test_id": test["id"],
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
    
    # 特別檢查：是否還有道歉訊息
    apology_count = sum(1 for r in results if "抱歉" in r.get("reply", ""))
    if apology_count == 0:
        print("\n✅ 成功！沒有任何道歉訊息")
    else:
        print(f"\n⚠️ 仍有 {apology_count} 個回應包含道歉訊息")
    
    # 保存結果
    with open(f"moderate_fix_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results


if __name__ == "__main__":
    asyncio.run(test_moderate_scenarios())