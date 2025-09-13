"""測試AI關懷策略升級系統"""

import asyncio
import json
import time
from uuid import uuid4

from app.langgraph.ultimate_workflow import UltimateWorkflow
from app.utils.ultimate_logger import get_ultimate_logger

async def test_strategy_upgrade():
    """測試策略升級功能"""
    
    # 模擬用戶ID和對話ID
    user_id = "test_user"
    conversation_id = str(uuid4())
    session_id = f"test_{int(time.time())}"
    
    workflow = UltimateWorkflow()
    logger = get_ultimate_logger(session_id)
    
    print("🚀 開始測試AI關懷策略升級系統")
    print(f"會話ID: {session_id}")
    print(f"用戶ID: {user_id}")
    print(f"對話ID: {conversation_id}")
    print("="*60)
    
    # 測試場景1: 第一次對話 - 應該使用第1層策略
    print("\n📝 測試場景1: 首次對話 (預期: 第1層策略)")
    test1_input = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "input_text": "我最近心情很差，覺得很沮喪"
    }
    
    result1 = await workflow.ainvoke(test1_input)
    print(f"回應: {result1.get('reply', 'No reply')}")
    print(f"使用策略: 第{result1.get('intent_analysis', {}).get('care_stage_needed', 'unknown')}層")
    print(f"是否升級: {result1.get('intent_analysis', {}).get('is_upgrade', False)}")
    
    # 等待一下
    await asyncio.sleep(1)
    
    # 測試場景2: 用戶沒有改善 - 應該升級到第2層
    print("\n📝 測試場景2: 用戶持續沮喪 (預期: 升級到第2層)")
    test2_input = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "input_text": "還是很難過，感覺沒什麼幫助"
    }
    
    result2 = await workflow.ainvoke(test2_input)
    print(f"回應: {result2.get('reply', 'No reply')}")
    print(f"使用策略: 第{result2.get('intent_analysis', {}).get('care_stage_needed', 'unknown')}層")
    print(f"是否升級: {result2.get('intent_analysis', {}).get('is_upgrade', False)}")
    print(f"升級原因: {result2.get('intent_analysis', {}).get('upgrade_reason', '')}")
    
    # 等待一下
    await asyncio.sleep(1)
    
    # 測試場景3: 用戶仍然困難 - 應該升級到第3層
    print("\n📝 測試場景3: 用戶仍然需要幫助 (預期: 升級到第3層)")
    test3_input = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "input_text": "我覺得我需要更多實際的幫助，但不知道怎麼辦"
    }
    
    result3 = await workflow.ainvoke(test3_input)
    print(f"回應: {result3.get('reply', 'No reply')}")
    print(f"使用策略: 第{result3.get('intent_analysis', {}).get('care_stage_needed', 'unknown')}層")
    print(f"是否升級: {result3.get('intent_analysis', {}).get('is_upgrade', False)}")
    print(f"升級原因: {result3.get('intent_analysis', {}).get('upgrade_reason', '')}")
    
    # 等待一下  
    await asyncio.sleep(1)
    
    # 測試場景4: 用戶情況改善 - 應該保持或降級
    print("\n📝 測試場景4: 用戶情況改善 (預期: 策略調整)")
    test4_input = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "input_text": "謝謝你的建議，我感覺好一點了"
    }
    
    result4 = await workflow.ainvoke(test4_input)
    print(f"回應: {result4.get('reply', 'No reply')}")
    print(f"使用策略: 第{result4.get('intent_analysis', {}).get('care_stage_needed', 'unknown')}層")
    print(f"是否升級: {result4.get('intent_analysis', {}).get('is_upgrade', False)}")
    print(f"策略效果: {result4.get('intent_analysis', {}).get('strategy_effectiveness', '')}")
    
    print("\n="*60)
    print("✅ 測試完成！")
    
    # 總結測試結果
    print("\n📊 測試總結:")
    print(f"場景1 策略: 第{result1.get('intent_analysis', {}).get('care_stage_needed', '?')}層")
    print(f"場景2 策略: 第{result2.get('intent_analysis', {}).get('care_stage_needed', '?')}層 (升級: {result2.get('intent_analysis', {}).get('is_upgrade', False)})")
    print(f"場景3 策略: 第{result3.get('intent_analysis', {}).get('care_stage_needed', '?')}層 (升級: {result3.get('intent_analysis', {}).get('is_upgrade', False)})")
    print(f"場景4 策略: 第{result4.get('intent_analysis', {}).get('care_stage_needed', '?')}層 (效果: {result4.get('intent_analysis', {}).get('strategy_effectiveness', '?')})")

if __name__ == "__main__":
    asyncio.run(test_strategy_upgrade())