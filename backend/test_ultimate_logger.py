"""測試新的UltimateLogger日誌輸出"""

import asyncio
import os
from datetime import datetime
from app.services.chat import ChatService
from app.schemas.chat import ChatRequest

# 確保使用UltimateWorkflow
os.environ["USE_ULTIMATE_WORKFLOW"] = "true"
os.environ["USE_FAST_WORKFLOW"] = "false"
os.environ["USE_OPTIMIZED_WORKFLOW"] = "false"


async def test_logger_output():
    """測試不同場景的日誌輸出"""
    
    print("\n" + "="*80)
    print("測試 UltimateLogger 日誌輸出")
    print("="*80)
    
    chat_service = ChatService()
    
    # 測試場景
    test_cases = [
        {
            "name": "🚨 危機情境",
            "message": "我想死了，活不下去了",
            "expected": "應該觸發危機處理，需要RAG檢索"
        },
        {
            "name": "💊 求助諮詢",
            "message": "哪裡可以戒毒",
            "expected": "應該觸發RAG檢索，提供機構資訊"
        },
        {
            "name": "😔 情緒支持",
            "message": "我好難過，沒人理解我",
            "expected": "不需要RAG，提供情緒支持"
        },
        {
            "name": "👋 日常問候",
            "message": "你好",
            "expected": "不需要RAG，簡單問候"
        },
        {
            "name": "💬 一般對話",
            "message": "今天天氣真好",
            "expected": "不需要RAG，一般回應"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n測試 {i}/{len(test_cases)}: {test_case['name']}")
        print(f"輸入: {test_case['message']}")
        print(f"預期: {test_case['expected']}")
        print("-" * 40)
        
        request = ChatRequest(
            user_id=f"test_logger_{i}",
            message=test_case['message']
        )
        
        try:
            response = await chat_service.process_message(request)
            print(f"回應: {response.reply}")
            print(f"成功 ✅")
        except Exception as e:
            print(f"錯誤 ❌: {str(e)}")
        
        # 等待一下讓日誌寫入
        await asyncio.sleep(0.5)
    
    # 顯示日誌文件位置
    today = datetime.now().strftime("%Y%m%d")
    log_file = f"logs/ultimate_workflow/ultimate_{today}.log"
    
    print("\n" + "="*80)
    print("測試完成")
    print(f"日誌文件: {log_file}")
    print("="*80)
    
    # 讀取並顯示最新的日誌內容
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        print("\n最新日誌內容（最後100行）:")
        print("="*80)
        for line in lines[-100:]:
            print(line, end='')
    except FileNotFoundError:
        print(f"\n日誌文件不存在: {log_file}")
    except Exception as e:
        print(f"\n讀取日誌錯誤: {str(e)}")


async def test_error_handling():
    """測試錯誤處理的日誌輸出"""
    
    print("\n" + "="*80)
    print("測試錯誤處理日誌")
    print("="*80)
    
    chat_service = ChatService()
    
    # 測試超長輸入（可能造成錯誤）
    request = ChatRequest(
        user_id="test_error",
        message="我" * 10000  # 超長文本
    )
    
    try:
        response = await chat_service.process_message(request)
        print(f"回應: {response.reply[:100]}...")
    except Exception as e:
        print(f"預期錯誤: {str(e)}")


async def main():
    """執行所有測試"""
    
    print("\n" + "="*80)
    print("UltimateLogger 測試套件")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 測試1: 基本場景
    await test_logger_output()
    
    # 測試2: 錯誤處理
    await test_error_handling()
    
    print("\n" + "="*80)
    print("所有測試完成")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())