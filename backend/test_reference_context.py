"""測試GPT-4o參考回覆是否能理解對話上下文"""

import asyncio
from uuid import uuid4
from app.langgraph.ultimate_workflow import UltimateWorkflow

async def test_reference_with_context():
    """測試GPT-4o參考回覆的上下文理解能力"""
    
    user_id = "context_test"
    conversation_id = str(uuid4())
    workflow = UltimateWorkflow()
    
    print("🧪 測試GPT-4o參考回覆的上下文理解")
    print("=" * 60)
    
    # 模擬一個需要上下文的對話流程
    conversation_flow = [
        {
            "input": "我最近工作壓力很大，經常失眠",
            "description": "建立背景資訊"
        },
        {
            "input": "醫生說我可能有憂鬱症的傾向",
            "description": "加入重要資訊"
        },
        {
            "input": "你剛才提到的方法真的有用嗎？",
            "description": "測試上下文引用 - 需要參考前面的建議"
        }
    ]
    
    for i, step in enumerate(conversation_flow, 1):
        print(f"\n📝 {i}. {step['description']}")
        print("-" * 40)
        print(f"用戶輸入: \"{step['input']}\"")
        
        test_input = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "input_text": step['input']
        }
        
        # 執行工作流
        result = await workflow.ainvoke(test_input)
        
        # 取得參考回答和最終回應
        reference_answer = result.get('reference_answer', '')
        final_reply = result.get('reply', '')
        
        print(f"GPT-4o參考: \"{reference_answer}\"")
        print(f"最終回應: \"{final_reply}\"")
        
        # 對於第3步，檢查是否能理解上下文
        if i == 3:
            has_context_awareness = any(word in final_reply.lower() for word in [
                '之前', '剛才', '前面', '建議', '方法', '提到'
            ])
            
            print(f"上下文理解: {'✅ 有引用前面建議' if has_context_awareness else '❌ 沒有上下文連結'}")
        
        await asyncio.sleep(1)  # 讓對話有間隔
    
    print("\n" + "=" * 60)
    print("📊 測試完成")
    print("檢查最後一個回應是否能正確引用對話歷史中的建議")

if __name__ == "__main__":
    asyncio.run(test_reference_with_context())