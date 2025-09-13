"""測試修改後的自然對話流程 - 避免過度提供聯絡資訊"""

import asyncio
import json
from uuid import uuid4
from app.langgraph.ultimate_workflow import UltimateWorkflow

async def test_natural_conversation_flow():
    """測試自然對話流程，確保不過度提供聯絡資訊"""
    
    user_id = "natural_test"
    conversation_id = str(uuid4())
    workflow = UltimateWorkflow()
    
    print("🧪 測試修改後的自然對話流程")
    print("=" * 60)
    
    # 測試場景：從情緒困擾到逐漸好轉，觀察AI是否適當控制資源提供
    test_scenarios = [
        {
            "stage": "初始情緒困擾",
            "input": "我今天心情很不好，覺得很累",
            "expected_behavior": "應該提供情緒支持，不應主動提供聯絡資訊",
            "expected_rag": False
        },
        {
            "stage": "繼續表達困擾", 
            "input": "感覺生活沒什麼意思，每天都很痛苦",
            "expected_behavior": "應該升級關懷策略，但仍不應主動推送聯絡資訊",
            "expected_rag": False
        },
        {
            "stage": "表達需要幫助",
            "input": "我覺得我需要找人聊聊，有什麼地方可以幫助我嗎？",
            "expected_behavior": "用戶主動詢問，此時可以提供資源",
            "expected_rag": True
        },
        {
            "stage": "情緒緩和",
            "input": "謝謝你的建議，我感覺好一點了",
            "expected_behavior": "情緒改善，不需要再推送資源",
            "expected_rag": False
        },
        {
            "stage": "一般對話",
            "input": "今天天氣不錯呢",
            "expected_behavior": "輕鬆對話，絕對不應提供聯絡資訊",
            "expected_rag": False
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 {i}. {scenario['stage']}")
        print("-" * 40)
        print(f"用戶輸入: \"{scenario['input']}\"")
        
        test_input = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "input_text": scenario['input']
        }
        
        # 執行工作流
        result = await workflow.ainvoke(test_input)
        
        # 取得分析結果
        intent_analysis = result.get('intent_analysis', {})
        actual_rag = intent_analysis.get('need_rag', False)
        risk_level = intent_analysis.get('risk_level', 'unknown')
        care_stage = intent_analysis.get('care_stage_needed', 1)
        
        # 取得AI回應
        ai_response = result.get('reply', '')
        
        # 檢查是否包含聯絡資訊
        contains_contact = "072865580" in ai_response or "高雄市毒品防制局" in ai_response
        
        # 評估結果
        rag_correct = (actual_rag == scenario['expected_rag'])
        appropriate_response = not (contains_contact and not scenario['expected_rag'])
        
        status = "✅" if (rag_correct and appropriate_response) else "❌"
        
        print(f"{status} AI回應: \"{ai_response}\"")
        print(f"   RAG觸發: {actual_rag} (預期: {scenario['expected_rag']}) {'✅' if rag_correct else '❌'}")
        print(f"   包含聯絡資訊: {contains_contact} {'✅' if appropriate_response else '❌'}")
        print(f"   風險等級: {risk_level} | 關懷階段: {care_stage}")
        
        results.append({
            "stage": scenario['stage'],
            "input": scenario['input'],
            "response": ai_response,
            "expected_rag": scenario['expected_rag'],
            "actual_rag": actual_rag,
            "contains_contact": contains_contact,
            "rag_correct": rag_correct,
            "appropriate_response": appropriate_response,
            "risk_level": risk_level,
            "care_stage": care_stage
        })
        
        await asyncio.sleep(0.5)  # 避免過快請求
    
    # 總結評估
    print("\n" + "=" * 60)
    print("📊 自然對話流程測試總結")
    print("=" * 60)
    
    rag_accuracy = sum(1 for r in results if r['rag_correct']) / len(results) * 100
    response_appropriateness = sum(1 for r in results if r['appropriate_response']) / len(results) * 100
    
    print(f"\n🎯 RAG觸發準確率: {rag_accuracy:.1f}%")
    print(f"🎯 回應適當性: {response_appropriateness:.1f}%")
    
    # 問題分析
    print("\n🔍 詳細分析:")
    for i, result in enumerate(results, 1):
        problems = []
        if not result['rag_correct']:
            problems.append(f"RAG觸發錯誤(預期:{result['expected_rag']}, 實際:{result['actual_rag']})")
        if not result['appropriate_response']:
            problems.append("不適當地提供聯絡資訊")
        
        if problems:
            print(f"  {i}. {result['stage']}: {', '.join(problems)}")
        else:
            print(f"  {i}. {result['stage']}: 正常 ✅")
    
    # 改善建議
    if rag_accuracy < 100 or response_appropriateness < 100:
        print("\n💡 改善建議:")
        if rag_accuracy < 100:
            print("  - RAG觸發邏輯需要進一步調整")
        if response_appropriateness < 100:
            print("  - 資源提供的條件判斷需要更嚴格")
    else:
        print("\n🏆 測試通過！對話流程已達到自然互動標準")

if __name__ == "__main__":
    asyncio.run(test_natural_conversation_flow())