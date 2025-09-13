"""測試增強版 AI 分析日誌系統"""

import asyncio
import sys
import os
sys.path.insert(0, '/Users/yangandy/KaohsiungCare/backend')

from app.langgraph.fast_workflow import CompleteFastWorkflow
from app.langgraph.state import WorkflowState
from app.utils.ai_logger import get_ai_logger
from datetime import datetime


async def test_enhanced_logging():
    """測試增強版日誌功能"""
    
    print("\n" + "="*80)
    print("測試增強版 AI 分析日誌系統")
    print("="*80)
    
    # 創建工作流
    workflow = CompleteFastWorkflow()
    
    # 測試案例 - 涵蓋所有內容類型
    test_cases = [
        # (名稱, 輸入文本, 預期類型)
        ("簡單問候", "你好", "問候"),
        ("日常對話", "今天天氣真好", "一般對話"),
        ("情緒支持", "我覺得很難過，心情不好", "情緒支持"),
        ("危機狀況", "我想死了", "危機回應"),
        ("查詢電話", "毒防局的電話是什麼", "聯絡資訊"),
        ("服務詢問", "凱旋醫院提供什麼服務", "服務說明"),
        ("機構資訊", "介紹一下凱旋醫院的功能和服務", "機構介紹"),
        ("超長輸入", "我想要知道高雄市所有的戒毒機構包括他們的地址電話服務時間收費標準還有交通方式最好能告訴我哪一家最好", "一般對話"),
    ]
    
    print("\n開始測試各種情境...")
    
    for idx, (name, text, expected_type) in enumerate(test_cases, 1):
        print(f"\n--- 測試 {idx}: {name} ---")
        print(f"輸入: {text}")
        
        # 創建獨立的 session
        session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}"
        
        # 準備狀態
        state = WorkflowState(
            input_text=text,
            user_id=f"test_user_{idx}",
            session_id=session_id,
            conversation_id=f"conv_{idx}"
        )
        
        try:
            # 執行工作流
            result = await workflow.ainvoke(state)
            
            # 顯示結果
            print(f"回應: {result.get('reply', '無回應')}")
            print(f"類型: {result.get('response_type', '未知')} (預期: {expected_type})")
            print(f"長度: {result.get('response_length', 0)}字 / 限制: {result.get('response_length_limit', 40)}字")
            
            # 檢查是否符合預期
            if result.get('response_type') == expected_type:
                print("✅ 類型符合預期")
            else:
                print(f"⚠️ 類型不符 (實際: {result.get('response_type')})")
            
            if result.get('response_length', 0) <= result.get('response_length_limit', 40):
                print("✅ 長度符合限制")
            else:
                print("⚠️ 超過長度限制")
                
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
    
    print("\n" + "="*80)
    print("日誌測試完成！")
    print("請檢查以下檔案查看詳細日誌：")
    print(f"  - logs/ai_analysis/ai_analysis_{datetime.now().strftime('%Y%m%d')}.log")
    print(f"  - logs/ai_analysis/ai_analysis_{datetime.now().strftime('%Y%m%d')}.jsonl")
    print("="*80)


async def test_truncation_logging():
    """專門測試字數截斷的日誌記錄"""
    
    print("\n" + "="*80)
    print("測試字數截斷日誌功能")
    print("="*80)
    
    workflow = CompleteFastWorkflow()
    
    # 模擬會被截斷的長文本
    long_texts = [
        ("長問候", "你好！很高興見到你，今天的天氣真的很不錯，希望你也有個美好的一天，有什麼我可以幫助你的嗎？", "問候"),
        ("長機構介紹", "高雄市立凱旋醫院是南台灣最重要的精神醫療機構之一，擁有完整的醫療團隊包括精神科醫師心理師社工師職能治療師等，提供門診住院日間留院等多元化服務，並設有藥癮戒治中心協助藥物成癮者重返社會，地址位於高雄市苓雅區凱旋二路130號，服務時間為週一至週五上午8點到下午5點。", "機構介紹"),
    ]
    
    for name, text, expected_type in long_texts:
        print(f"\n測試: {name}")
        print(f"原始長度: {len(text)}字")
        
        state = WorkflowState(
            input_text="告訴我" + text,  # 模擬回應會是長文本
            user_id="truncation_test",
            session_id=f"trunc_{datetime.now().strftime('%H%M%S')}"
        )
        
        result = await workflow.ainvoke(state)
        
        print(f"最終長度: {result.get('response_length', 0)}字")
        print(f"限制: {result.get('response_length_limit', 40)}字")
        print(f"回應: {result.get('reply', '')}")
        
        # 檢查日誌中是否記錄了截斷操作
        if result.get('response_length', 0) < len(text):
            print("✅ 已截斷並記錄")
        else:
            print("ℹ️ 未截斷")


async def main():
    """執行所有測試"""
    
    print("\n" + "="*80)
    print("AI 分析日誌系統 - 增強版測試")
    print("="*80)
    
    # 測試1: 完整情境測試
    await test_enhanced_logging()
    
    # 測試2: 截斷功能測試
    await test_truncation_logging()
    
    print("\n測試完成！")


if __name__ == "__main__":
    asyncio.run(main())