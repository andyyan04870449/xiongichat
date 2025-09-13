"""測試增強記憶系統"""

import asyncio
import json
import logging
from datetime import datetime
from app.services.enhanced_memory import EnhancedMemoryService
from app.langgraph.ultimate_workflow import UltimateWorkflow
from app.langgraph.state import WorkflowState

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_memory_enhancement():
    """測試增強記憶功能"""
    
    print("\n=== 測試增強記憶系統 ===\n")
    
    # 初始化
    memory_service = EnhancedMemoryService()
    workflow = UltimateWorkflow()
    
    # 模擬對話歷史
    test_messages = [
        {"role": "user", "content": "我叫小明，最近在戒毒", "timestamp": "2024-01-01T10:00:00"},
        {"role": "assistant", "content": "小明你好，很高興認識你。戒毒需要勇氣，我會陪伴你。", "timestamp": "2024-01-01T10:00:10"},
        {"role": "user", "content": "我已經戒了3個月了，但最近壓力很大", "timestamp": "2024-01-01T10:01:00"},
        {"role": "assistant", "content": "3個月很不容易！壓力大時可以找人聊聊。", "timestamp": "2024-01-01T10:01:10"},
        {"role": "user", "content": "我擔心會復發，家人都不理解我", "timestamp": "2024-01-01T10:02:00"},
        {"role": "assistant", "content": "擔心復發是正常的，要不要試試參加支持團體？", "timestamp": "2024-01-01T10:02:10"},
    ]
    
    # 測試記憶增強功能
    print("1. 測試關鍵事實提取")
    key_facts = memory_service._extract_key_facts(test_messages)
    print(f"   - 使用者資訊: {key_facts['user_mentions']}")
    print(f"   - 討論話題: {key_facts['topics']}")
    print(f"   - 情緒狀態數: {len(key_facts['emotional_states'])}")
    
    print("\n2. 測試上下文標記")
    markers = memory_service._create_context_markers(test_messages)
    for marker in markers:
        print(f"   - {marker}")
    
    print("\n3. 測試對話流程分析")
    flow = memory_service._analyze_conversation_flow(test_messages)
    for turn in flow:
        print(f"   - 第{turn['turn']}輪: {turn['user_intent']} -> {turn['assistant_action']}")
    
    print("\n4. 測試記憶格式化")
    memory_data = {
        "messages": test_messages,
        "conversation_id": "test-123",
        "total_messages": len(test_messages),
        "key_facts": key_facts,
        "context_markers": markers,
        "conversation_flow": flow
    }
    
    formatted_memory = memory_service.format_for_llm(memory_data)
    print("   格式化記憶內容:")
    print("-" * 50)
    print(formatted_memory[:500] + "..." if len(formatted_memory) > 500 else formatted_memory)
    print("-" * 50)
    
    print("\n5. 測試記憶檢查點")
    checkpoint = memory_service.create_memory_checkpoint(memory_data)
    checkpoint_data = json.loads(checkpoint)
    print(f"   - 對話ID: {checkpoint_data['conversation_id']}")
    print(f"   - 訊息數: {checkpoint_data['message_count']}")
    print(f"   - 關鍵話題: {checkpoint_data['key_topics']}")
    print(f"   - 檢查點Hash: {checkpoint_data['hash']}")
    
    print("\n6. 測試記憶回想驗證")
    # 測試好的回應（包含記憶）
    good_response = "小明，我記得你說已經戒毒3個月了，真的很不容易。家人的理解需要時間，持續努力他們會看到的。"
    validation1 = await memory_service.validate_memory_recall(good_response, checkpoint)
    print(f"   好的回應驗證: {validation1}")
    
    # 測試差的回應（忽略記憶）
    bad_response = "你好，有什麼可以幫助你的嗎？"
    validation2 = await memory_service.validate_memory_recall(bad_response, checkpoint)
    print(f"   差的回應驗證: {validation2}")
    
    print("\n7. 測試實際工作流整合")
    state = WorkflowState(
        input_text="我之前跟你說過的戒毒進度怎麼樣了？",
        user_id="test_user",
        conversation_id="test-123",
        memory=test_messages
    )
    
    print("   執行工作流...")
    result = await workflow.ainvoke(state)
    print(f"   AI回應: {result.get('reply', '無回應')}")
    
    # 驗證回應是否包含記憶
    if "小明" in result.get('reply', '') or "3個月" in result.get('reply', ''):
        print("   ✅ 回應成功引用了對話記憶！")
    else:
        print("   ⚠️ 回應可能沒有充分利用對話記憶")


async def test_long_conversation():
    """測試長對話記憶保持"""
    
    print("\n=== 測試長對話記憶保持 ===\n")
    
    workflow = UltimateWorkflow()
    conversation_id = "long-test-456"
    memory = []
    
    # 模擬長對話
    conversations = [
        "我是阿華，想戒除安非他命",
        "已經用了5年，最近身體越來越差",
        "上週去看了醫生，他建議我來找你們",
        "我住在高雄前鎮區",
        "你還記得我剛剛說的情況嗎？",
        "我之前說的醫生建議是什麼？",
        "我住在哪裡來著？"
    ]
    
    for i, user_input in enumerate(conversations, 1):
        print(f"\n輪次 {i}:")
        print(f"使用者: {user_input}")
        
        state = WorkflowState(
            input_text=user_input,
            user_id="test_user_long",
            conversation_id=conversation_id,
            memory=memory
        )
        
        result = await workflow.ainvoke(state)
        reply = result.get('reply', '無回應')
        
        print(f"AI: {reply}")
        
        # 更新記憶
        memory.append({"role": "user", "content": user_input})
        memory.append({"role": "assistant", "content": reply})
        
        # 檢查關鍵資訊保持
        if i >= 5:  # 從第5輪開始檢查
            if i == 5 and ("阿華" in reply or "安非他命" in reply or "5年" in reply):
                print("✅ 記得使用者基本資訊")
            elif i == 6 and ("醫生" in reply or "建議" in reply):
                print("✅ 記得醫生建議")
            elif i == 7 and ("前鎮" in reply or "高雄" in reply):
                print("✅ 記得地址資訊")


if __name__ == "__main__":
    asyncio.run(test_memory_enhancement())
    asyncio.run(test_long_conversation())