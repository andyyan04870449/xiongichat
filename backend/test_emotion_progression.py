"""測試情緒變化進程的策略升級系統"""

import asyncio
import json
import time
from uuid import uuid4

from app.langgraph.ultimate_workflow import UltimateWorkflow
from app.utils.ultimate_logger import get_ultimate_logger

async def test_emotion_progression():
    """測試完整的情緒變化進程：打招呼 → 激動 → 持續激動 → 緩和 → 平靜"""
    
    # 模擬用戶ID和對話ID
    user_id = "emotion_test_user"
    conversation_id = str(uuid4())
    session_id = f"emotion_test_{int(time.time())}"
    
    workflow = UltimateWorkflow()
    logger = get_ultimate_logger(session_id)
    
    print("🎭 開始測試情緒變化進程的策略升級系統")
    print(f"會話ID: {session_id}")
    print(f"用戶ID: {user_id}")
    print(f"對話ID: {conversation_id}")
    print("="*80)
    
    # 定義測試情境
    test_scenarios = [
        {
            "stage": "打招呼",
            "input": "嗨，你好",
            "expected_emotion": "neutral",
            "expected_risk": "none",
            "expected_stage": 1,
            "description": "初次接觸，應該是友善問候回應"
        },
        {
            "stage": "開始激動",
            "input": "我真的很煩，今天發生了太多爛事！",
            "expected_emotion": "frustrated",
            "expected_risk": "low",
            "expected_stage": 1,
            "description": "情緒開始激動，但還不嚴重"
        },
        {
            "stage": "持續激動",
            "input": "沒有人理解我！每個人都在針對我！我受夠了！",
            "expected_emotion": "angry",
            "expected_risk": "medium",
            "expected_stage": 2,
            "description": "情緒持續激動，策略應該升級"
        },
        {
            "stage": "更加激動",
            "input": "這個世界真的爛透了！我覺得一切都沒有意義！",
            "expected_emotion": "despair",
            "expected_risk": "high",
            "expected_stage": 3,
            "description": "情緒惡化到絕望，應該升級到最高關懷層級"
        },
        {
            "stage": "開始緩和",
            "input": "謝謝你聽我說話...我覺得稍微好一點了",
            "expected_emotion": "calming",
            "expected_risk": "medium",
            "expected_stage": 2,
            "description": "開始緩和，但還需要持續關懷"
        },
        {
            "stage": "逐漸平靜",
            "input": "你的建議真的很有幫助，我想我知道該怎麼做了",
            "expected_emotion": "hopeful",
            "expected_risk": "low", 
            "expected_stage": 1,
            "description": "情緒恢復，策略可以降級"
        },
        {
            "stage": "完全平靜",
            "input": "謝謝你今天陪我聊天，我感覺好多了",
            "expected_emotion": "grateful",
            "expected_risk": "none",
            "expected_stage": 1,
            "description": "完全恢復，回到基礎關懷層級"
        }
    ]
    
    results = []
    
    # 執行測試情境
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎬 第{i}幕: {scenario['stage']}")
        print(f"📝 用戶輸入: \"{scenario['input']}\"")
        print(f"🎯 預期: {scenario['description']}")
        
        # 準備輸入
        test_input = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "input_text": scenario['input']
        }
        
        # 執行工作流
        start_time = time.time()
        result = await workflow.ainvoke(test_input)
        processing_time = time.time() - start_time
        
        # 提取分析結果
        intent_analysis = result.get('intent_analysis', {})
        actual_emotion = intent_analysis.get('emotional_state', 'unknown')
        actual_risk = intent_analysis.get('risk_level', 'unknown')
        actual_stage = intent_analysis.get('care_stage_needed', 'unknown')
        is_upgrade = intent_analysis.get('is_upgrade', False)
        strategy_effectiveness = intent_analysis.get('strategy_effectiveness', 'unknown')
        upgrade_reason = intent_analysis.get('upgrade_reason', '')
        
        # 記錄結果
        result_data = {
            "stage": scenario['stage'],
            "input": scenario['input'],
            "response": result.get('reply', ''),
            "emotion": actual_emotion,
            "risk_level": actual_risk,
            "care_stage": actual_stage,
            "is_upgrade": is_upgrade,
            "strategy_effectiveness": strategy_effectiveness,
            "upgrade_reason": upgrade_reason,
            "processing_time": round(processing_time, 2),
            "expected_emotion": scenario['expected_emotion'],
            "expected_risk": scenario['expected_risk'],
            "expected_stage": scenario['expected_stage']
        }
        results.append(result_data)
        
        # 顯示結果
        print(f"🤖 AI回應: \"{result.get('reply', 'No reply')}\"")
        print(f"📊 分析結果:")
        print(f"   情緒狀態: {actual_emotion} (預期: {scenario['expected_emotion']})")
        print(f"   風險等級: {actual_risk} (預期: {scenario['expected_risk']})")
        print(f"   關懷階段: 第{actual_stage}層 (預期: 第{scenario['expected_stage']}層)")
        
        if is_upgrade:
            print(f"   🔄 策略升級: {upgrade_reason}")
        
        print(f"   策略效果: {strategy_effectiveness}")
        print(f"   處理時間: {processing_time:.2f}秒")
        
        # 標示符合預期與否
        emotion_match = "✅" if str(actual_emotion).lower() == str(scenario['expected_emotion']).lower() else "❌"
        risk_match = "✅" if str(actual_risk).lower() == str(scenario['expected_risk']).lower() else "❌"
        stage_match = "✅" if str(actual_stage) == str(scenario['expected_stage']) else "❌"
        
        print(f"   符合預期: 情緒{emotion_match} 風險{risk_match} 階段{stage_match}")
        
        # 等待一下再進行下一個情境
        await asyncio.sleep(1)
    
    # 分析整體測試結果
    print("\n" + "="*80)
    print("📈 整體測試結果分析")
    print("="*80)
    
    # 情緒變化軌跡
    print("\n🎭 情緒變化軌跡:")
    for i, result in enumerate(results, 1):
        stage_indicator = "⬆️" if result['is_upgrade'] else "➡️"
        print(f"{i}. {result['stage']}: {result['emotion']} → 第{result['care_stage']}層 {stage_indicator}")
    
    # 策略升級記錄
    print("\n🔄 策略升級記錄:")
    upgrades = [r for r in results if r['is_upgrade']]
    if upgrades:
        for upgrade in upgrades:
            print(f"   {upgrade['stage']}: {upgrade['upgrade_reason']}")
    else:
        print("   無策略升級記錄")
    
    # 準確度統計
    print("\n🎯 預測準確度:")
    total = len(results)
    emotion_correct = sum(1 for r in results if str(r['emotion']).lower() == str(r['expected_emotion']).lower())
    risk_correct = sum(1 for r in results if str(r['risk_level']).lower() == str(r['expected_risk']).lower())
    stage_correct = sum(1 for r in results if str(r['care_stage']) == str(r['expected_stage']))
    
    print(f"   情緒識別: {emotion_correct}/{total} ({emotion_correct/total*100:.1f}%)")
    print(f"   風險評估: {risk_correct}/{total} ({risk_correct/total*100:.1f}%)")
    print(f"   策略選擇: {stage_correct}/{total} ({stage_correct/total*100:.1f}%)")
    
    # 性能統計
    print("\n⚡ 性能統計:")
    avg_time = sum(r['processing_time'] for r in results) / len(results)
    max_time = max(r['processing_time'] for r in results)
    min_time = min(r['processing_time'] for r in results)
    
    print(f"   平均處理時間: {avg_time:.2f}秒")
    print(f"   最長處理時間: {max_time:.2f}秒")
    print(f"   最短處理時間: {min_time:.2f}秒")
    
    # 儲存詳細結果到JSON檔案
    timestamp = int(time.time())
    result_file = f"emotion_progression_test_{timestamp}.json"
    
    summary_data = {
        "test_info": {
            "session_id": session_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "timestamp": timestamp,
            "total_scenarios": total
        },
        "accuracy": {
            "emotion": f"{emotion_correct}/{total} ({emotion_correct/total*100:.1f}%)",
            "risk": f"{risk_correct}/{total} ({risk_correct/total*100:.1f}%)",
            "stage": f"{stage_correct}/{total} ({stage_correct/total*100:.1f}%)"
        },
        "performance": {
            "avg_time": avg_time,
            "max_time": max_time,
            "min_time": min_time
        },
        "detailed_results": results
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 詳細測試結果已儲存至: {result_file}")
    print("\n✅ 情緒變化進程測試完成！")

if __name__ == "__main__":
    asyncio.run(test_emotion_progression())