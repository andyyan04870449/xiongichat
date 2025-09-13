"""快速驗證記憶修復效果的測試"""

import asyncio
import json
from datetime import datetime
from app.langgraph.ultimate_workflow import create_ultimate_workflow

async def quick_verify_test():
    """快速驗證記憶系統修復"""
    
    print("🧪 開始快速記憶驗證測試...")
    
    # 創建工作流
    workflow = create_ultimate_workflow()
    
    # 測試案例
    test_cases = [
        {
            "user": "memory_verify_test_user",
            "messages": [
                "你好，我叫小明",
                "我還記得我告訴過你我叫什麼嗎？"
            ]
        }
    ]
    
    results = []
    
    for case in test_cases:
        user_id = case["user"]
        conversation_id = None
        
        print(f"\n📋 測試用戶: {user_id}")
        
        case_result = {
            "user": user_id,
            "success": False,
            "error": None,
            "responses": []
        }
        
        try:
            for i, message in enumerate(case["messages"], 1):
                print(f"  {i}. 發送: {message}")
                
                # 準備輸入
                input_data = {
                    "user_id": user_id,
                    "message": message
                }
                
                if conversation_id:
                    input_data["conversation_id"] = conversation_id
                
                # 執行工作流
                result = await workflow.ainvoke(input_data)
                
                # 保存對話ID
                if conversation_id is None:
                    conversation_id = result.get("conversation_id")
                    print(f"     → 對話ID: {conversation_id}")
                
                response = result.get("response", "無回應")
                print(f"     → 回應: {response[:100]}...")
                
                case_result["responses"].append({
                    "message": message,
                    "response": response
                })
            
            # 檢查第二個回應是否包含記憶內容
            if len(case_result["responses"]) >= 2:
                second_response = case_result["responses"][1]["response"].lower()
                if "小明" in second_response or "告訴過" in second_response or "記得" in second_response:
                    case_result["success"] = True
                    print("  ✅ 記憶測試成功！")
                else:
                    print("  ❌ 記憶測試失敗：未體現記憶能力")
            
        except Exception as e:
            case_result["error"] = str(e)
            print(f"  ❌ 測試失敗: {str(e)}")
        
        results.append(case_result)
    
    # 統計結果
    successful_cases = sum(1 for r in results if r["success"])
    total_cases = len(results)
    success_rate = (successful_cases / total_cases) * 100 if total_cases > 0 else 0
    
    print(f"\n📊 快速驗證結果:")
    print(f"總測試案例: {total_cases}")
    print(f"成功案例: {successful_cases}")
    print(f"成功率: {success_rate:.1f}%")
    
    # 保存報告
    report = {
        "test_info": {
            "timestamp": datetime.now().isoformat(),
            "test_type": "quick_memory_verification",
            "total_cases": total_cases,
            "successful_cases": successful_cases,
            "success_rate": success_rate
        },
        "detailed_results": results
    }
    
    report_filename = f"quick_memory_verify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 報告已保存: {report_filename}")
    
    return success_rate > 0

if __name__ == "__main__":
    result = asyncio.run(quick_verify_test())
    if result:
        print("\n🎉 驗證成功：記憶系統修復有效！")
    else:
        print("\n⚠️ 驗證失敗：仍需進一步調試")