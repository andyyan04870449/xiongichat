"""簡單測試字數管理日誌"""

import sys
import os
sys.path.insert(0, '/Users/yangandy/KaohsiungCare/backend')

from app.langgraph.response_length_manager import ResponseLengthManager
from app.utils.ai_logger import get_ai_logger
from datetime import datetime


def test_direct_logging():
    """直接測試字數管理和日誌功能"""
    
    print("\n" + "="*80)
    print("直接測試字數管理日誌")
    print("="*80)
    
    # 初始化日誌器
    ai_logger = get_ai_logger(f"test_{datetime.now().strftime('%H%M%S')}")
    
    # 測試案例
    test_cases = [
        # (原始文本, 意圖, 風險等級)
        ("你好！很高興見到你，今天的天氣真的很不錯，希望你也有個美好的一天！", "問候", None),
        ("高雄市立凱旋醫院是南台灣最重要的精神醫療機構之一，提供完整的醫療團隊和多元化服務，地址位於高雄市苓雅區凱旋二路130號。", None, None),
        ("我覺得很難過很傷心很痛苦不知道該怎麼辦了，生活沒有希望", "情緒支持", None),
    ]
    
    for idx, (text, intent, risk) in enumerate(test_cases, 1):
        print(f"\n測試 {idx}:")
        print(f"原始文本 ({len(text)}字): {text}")
        
        # 使用 ResponseLengthManager 處理
        result, limit, content_type = ResponseLengthManager.format_response(
            text, intent, risk
        )
        
        print(f"內容類型: {content_type}")
        print(f"字數限制: {limit}")
        print(f"結果文本 ({len(result)}字): {result}")
        
        # 如果有截斷，記錄到日誌
        if len(text) > len(result):
            print("📏 發生截斷")
            ai_logger.log_length_management(
                original_text=text,
                final_text=result,
                content_type=content_type,
                limit=limit,
                truncated=True
            )
        else:
            print("✅ 未截斷")
        
        # 記錄回應生成
        ai_logger.log_response_generation(
            response=result,
            used_knowledge=False,
            response_type=content_type,
            length_limit=limit
        )
    
    print(f"\n查看日誌: logs/ai_analysis/ai_analysis_{datetime.now().strftime('%Y%m%d')}.log")


if __name__ == "__main__":
    test_direct_logging()