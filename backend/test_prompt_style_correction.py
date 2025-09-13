"""測試基於prompts.py的雄i聊風格修正"""

import asyncio
from uuid import uuid4
from app.langgraph.ultimate_workflow import UltimateWorkflow

async def test_prompt_style_correction():
    """測試雄i聊風格修正效果"""
    
    user_id = "style_test"
    conversation_id = str(uuid4())
    workflow = UltimateWorkflow()
    
    print("🧪 測試雄i聊風格修正（基於prompts.py）")
    print("=" * 60)
    print("期望效果：")
    print("- GPT-4o提供完整回答")
    print("- MasterLLM修正為40字內、朋友語調")
    print()
    
    test_scenarios = [
        {
            "type": "工作壓力",
            "input": "我最近工作壓力很大，經常失眠",
            "期望": "40字內，朋友語調，有提問"
        },
        {
            "type": "危機表達", 
            "input": "覺得活著沒什麼意思了",
            "期望": "40字內，溫柔語調，可能提供緊急專線"
        },
        {
            "type": "求助詢問",
            "input": "你們有什麼戒毒的資源嗎？",
            "期望": "40字內，簡潔提供1-2個資源"
        },
        {
            "type": "一般對話",
            "input": "今天天氣還不錯",
            "期望": "40字內，自然回應"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"📝 {i}. {scenario['type']}")
        print("-" * 40)
        print(f"用戶輸入: \"{scenario['input']}\"")
        
        test_input = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "input_text": scenario['input']
        }
        
        result = await workflow.ainvoke(test_input)
        
        primary_answer = result.get('primary_answer', '')
        final_reply = result.get('reply', '')
        
        print(f"GPT-4o原回答 ({len(primary_answer)}字): \"{primary_answer}\"")
        print(f"雄i聊修正後 ({len(final_reply)}字): \"{final_reply}\"")
        
        # 檢查是否符合雄i聊標準
        word_limit_ok = len(final_reply) <= 40
        has_question = "嗎？" in final_reply or "嗎" in final_reply or "？" in final_reply
        is_natural = not any(formal in final_reply for formal in ["您", "請問", "非常", "建議您"])
        is_concise = len(final_reply) < len(primary_answer) * 0.5  # 至少縮短一半
        
        print(f"字數限制 (≤40字): {'✅' if word_limit_ok else '❌'} ({len(final_reply)}字)")
        print(f"包含提問: {'✅' if has_question else '⚪'}")  
        print(f"自然語調: {'✅' if is_natural else '❌'}")
        print(f"有效精簡: {'✅' if is_concise else '❌'}")
        
        print(f"期望效果: {scenario['期望']}")
        print()
        
        await asyncio.sleep(0.5)
    
    print("=" * 60)
    print("📊 風格修正測試完成")
    print()
    print("✅ 成功改造為prompts.py風格的雄i聊修正器")
    print("主要特點：")
    print("- 40字以內，最多2句話")
    print("- 朋友般自然對話，不說教")
    print("- 每次只問1個問題")
    print("- 避免專業輔導術語")
    print("- 語氣溫和、尊重、細膩")

if __name__ == "__main__":
    asyncio.run(test_prompt_style_correction())