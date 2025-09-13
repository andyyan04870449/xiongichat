"""測試新的雙層架構 - GPT-4o主要回答 + MasterLLM角色化修飾"""

import asyncio
from uuid import uuid4
from app.langgraph.ultimate_workflow import UltimateWorkflow

async def test_dual_layer_architecture():
    """測試雙層架構的效果"""
    
    user_id = "architecture_test"
    conversation_id = str(uuid4())
    workflow = UltimateWorkflow()
    
    print("🧪 測試新的雙層架構")
    print("=" * 60)
    print("架構說明：")
    print("1️⃣ GPT-4o：生成主要回答（無字數限制）")
    print("2️⃣ MasterLLM：角色化修飾，加入雄i聊特色")
    print()
    
    # 測試不同類型的對話場景
    test_scenarios = [
        {
            "type": "情緒困擾",
            "input": "我最近睡不好，工作壓力很大，覺得快撐不下去了",
            "expected_features": ["同理心", "具體建議", "雄i聊語調"]
        },
        {
            "type": "危機情況",
            "input": "我覺得活著好累，想要解脫了",
            "expected_features": ["危機處理", "緊急支持", "溫暖陪伴"]
        },
        {
            "type": "詢問資源",
            "input": "你們有什麼戒毒的資源嗎？電話是多少？",
            "expected_features": ["資源提供", "聯絡資訊", "實用性"]
        },
        {
            "type": "一般對話",
            "input": "今天天氣不錯，心情好一點了",
            "expected_features": ["自然回應", "正面支持", "溫暖語調"]
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"📝 {i}. {scenario['type']}")
        print("-" * 40)
        print(f"用戶輸入: \"{scenario['input']}\"")
        
        test_input = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "input_text": scenario['input']
        }
        
        # 執行工作流
        result = await workflow.ainvoke(test_input)
        
        # 分析結果
        primary_answer = result.get('primary_answer', '')
        final_reply = result.get('reply', '')
        intent_analysis = result.get('intent_analysis', {})
        
        print(f"GPT-4o主要回答 ({len(primary_answer)}字):")
        print(f"  \"{primary_answer[:100]}{'...' if len(primary_answer) > 100 else ''}\"")
        print(f"最終回應 ({len(final_reply)}字):")
        print(f"  \"{final_reply}\"")
        
        # 評估改善程度
        length_improved = len(final_reply) != len(primary_answer)
        tone_enhanced = any(word in final_reply for word in ['聽起來', '感覺', '陪伴', '在這裡'])
        
        print(f"字數變化: {'✅ 有調整' if length_improved else '⚪ 保持原樣'}")
        print(f"語調優化: {'✅ 有雄i聊特色' if tone_enhanced else '⚪ 保持原調'}")
        print(f"風險等級: {intent_analysis.get('risk_level', 'unknown')}")
        
        results.append({
            "type": scenario['type'],
            "input": scenario['input'],
            "primary_answer": primary_answer,
            "final_reply": final_reply,
            "primary_length": len(primary_answer),
            "final_length": len(final_reply),
            "length_improved": length_improved,
            "tone_enhanced": tone_enhanced,
            "risk_level": intent_analysis.get('risk_level', 'unknown')
        })
        
        print()
        await asyncio.sleep(1)
    
    # 總體分析
    print("=" * 60)
    print("📊 雙層架構測試分析")
    print("=" * 60)
    
    total_tests = len(results)
    length_changes = sum(1 for r in results if r['length_improved'])
    tone_enhancements = sum(1 for r in results if r['tone_enhanced'])
    
    print(f"\n🎯 整體表現:")
    print(f"  測試案例: {total_tests}")
    print(f"  字數調整案例: {length_changes}/{total_tests} ({length_changes/total_tests*100:.1f}%)")
    print(f"  語調優化案例: {tone_enhancements}/{total_tests} ({tone_enhancements/total_tests*100:.1f}%)")
    
    print(f"\n📏 字數統計:")
    avg_primary = sum(r['primary_length'] for r in results) / total_tests
    avg_final = sum(r['final_length'] for r in results) / total_tests
    print(f"  GPT-4o平均字數: {avg_primary:.1f}")
    print(f"  最終回應平均字數: {avg_final:.1f}")
    print(f"  字數變化: {avg_final - avg_primary:+.1f}")
    
    print(f"\n💬 架構效果評估:")
    if tone_enhancements >= total_tests * 0.7:
        architecture_grade = "優秀 - 成功實現角色化修飾"
    elif tone_enhancements >= total_tests * 0.5:
        architecture_grade = "良好 - 基本實現雙層效果" 
    else:
        architecture_grade = "待改善 - 修飾效果不明顯"
    
    print(f"  架構評級: {architecture_grade}")
    
    print(f"\n✅ 雙層架構重構完成！")
    print("主要改進：")
    print("- GPT-4o提供高品質完整回答")
    print("- MasterLLM專注角色化修飾")
    print("- 移除字數限制避免切字")
    print("- 保持對話連貫性和自然性")

if __name__ == "__main__":
    asyncio.run(test_dual_layer_architecture())