"""測試品質評估日誌系統"""

import asyncio
import os
from datetime import datetime
from app.services.chat import ChatService
from app.schemas.chat import ChatRequest
from app.utils.quality_logger import get_quality_logger

# 確保使用UltimateWorkflow
os.environ["USE_ULTIMATE_WORKFLOW"] = "true"


async def test_quality_logging():
    """測試品質日誌記錄"""
    
    print("\n" + "="*80)
    print("品質評估日誌測試")
    print("="*80)
    
    chat_service = ChatService()
    
    # 測試對話
    test_conversations = [
        ("我想死了", "crisis_test"),
        ("哪裡可以戒毒", "help_test"),
        ("我很難過", "emotion_test"),
        ("你好", "greeting_test"),
        ("今天天氣不錯", "general_test"),
        ("毒防局電話多少", "info_test"),
        ("我該怎麼辦", "advice_test"),
        ("謝謝你", "thanks_test"),
    ]
    
    print(f"\n執行 {len(test_conversations)} 個測試對話...")
    
    for message, user_id in test_conversations:
        request = ChatRequest(
            user_id=user_id,
            message=message
        )
        
        try:
            response = await chat_service.process_message(request)
            print(f"✅ {user_id}: {message[:20]}... -> {response.reply[:30]}...")
        except Exception as e:
            print(f"❌ {user_id}: {str(e)}")
    
    print("\n" + "="*80)
    print("查看品質日誌統計")
    print("="*80)
    
    # 取得統計資料
    quality_logger = get_quality_logger()
    stats = quality_logger.get_statistics()
    
    print(f"\n總對話數: {stats['total_conversations']}")
    print(f"平均回應長度: {stats['average_output_length']} 字")
    
    print("\n意圖分布:")
    for intent, count in stats['intents'].items():
        print(f"  {intent}: {count} 次")
    
    print("\n風險等級分布:")
    for risk, count in stats['risk_levels'].items():
        print(f"  {risk}: {count} 次")
    
    print(f"\n日誌檔案: {stats['log_file']}")
    
    # 匯出CSV供評估
    print("\n" + "="*80)
    print("匯出品質評估資料")
    print("="*80)
    
    export_file = quality_logger.export_for_evaluation()
    if export_file:
        print(f"✅ 已匯出至: {export_file}")
    
    # 顯示前幾筆記錄
    print("\n" + "="*80)
    print("品質日誌範例（前3筆）")
    print("="*80)
    
    logs = quality_logger.get_today_logs()
    for i, log in enumerate(logs[:3], 1):
        print(f"\n記錄 {i}:")
        print(f"  時間: {log['timestamp']}")
        print(f"  對話ID: {log['conversation_id']}")
        print(f"  用戶輸入: {log['user_input']}")
        print(f"  機器人輸出: {log['bot_output']}")
        print(f"  輸出長度: {log['output_length']} 字")
        print(f"  意圖: {log.get('intent', 'N/A')}")
        print(f"  風險等級: {log.get('risk_level', 'N/A')}")


async def main():
    """執行測試"""
    print("\n" + "="*80)
    print("品質評估日誌系統測試")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    await test_quality_logging()
    
    print("\n" + "="*80)
    print("測試完成！")
    print("="*80)
    
    # 提示檢視檔案
    today = datetime.now().strftime("%Y%m%d")
    print(f"\n📁 相關檔案位置:")
    print(f"  JSONL日誌: logs/quality_assessment/quality_{today}.jsonl")
    print(f"  CSV匯出: logs/quality_assessment/quality_export_{today}.csv")
    print(f"  可用於品質評分和分析")


if __name__ == "__main__":
    asyncio.run(main())