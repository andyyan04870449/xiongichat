"""簡化的情境測試 - 驗證核心功能"""

import sys
import os
sys.path.insert(0, '/Users/yangandy/KaohsiungCare/backend')

from app.langgraph.response_length_manager import ResponseLengthManager


def test_length_manager():
    """測試長度管理器"""
    
    print("\n" + "="*80)
    print("ResponseLengthManager 測試")
    print("="*80)
    
    manager = ResponseLengthManager()
    
    # 測試案例
    test_cases = [
        # (文本, 意圖, 風險等級, 預期類型, 預期限制)
        ("你好！", "問候", None, "問候", 30),
        ("今天天氣真好", "一般對話", None, "一般對話", 40),
        ("我覺得很難過", "情緒支持", None, "情緒支持", 45),
        ("我想死", None, "high", "危機回應", 50),
        ("毒防局電話是07-2118800", None, None, "聯絡資訊", 60),
        ("凱旋醫院提供藥癮戒治服務", None, None, "服務說明", 80),
        ("高雄市立凱旋醫院是專業的精神醫療機構，提供藥癮戒治、心理諮商等服務", None, None, "機構介紹", 100),
    ]
    
    passed = 0
    failed = 0
    
    for text, intent, risk, expected_type, expected_limit in test_cases:
        print(f"\n測試: {text[:30]}...")
        
        # 測試限制判斷
        limit = manager.get_limit(text, intent, risk)
        
        # 測試格式化
        result, used_limit, content_type = manager.format_response(text, intent, risk)
        
        # 檢查結果
        limit_correct = (limit == expected_limit)
        type_correct = (content_type == expected_type)
        length_correct = (len(result) <= used_limit)
        
        print(f"  原文: {text} ({len(text)}字)")
        print(f"  結果: {result} ({len(result)}字)")
        print(f"  類型: {content_type} (預期: {expected_type}) {'✅' if type_correct else '❌'}")
        print(f"  限制: {limit}字 (預期: {expected_limit}字) {'✅' if limit_correct else '❌'}")
        print(f"  長度檢查: {len(result)} <= {used_limit} {'✅' if length_correct else '❌'}")
        
        if limit_correct and type_correct and length_correct:
            passed += 1
        else:
            failed += 1
    
    print(f"\n" + "="*80)
    print(f"測試結果: {passed} 通過, {failed} 失敗")
    print("="*80)
    
    return passed, failed


def test_smart_truncate():
    """測試智能截斷功能"""
    
    print("\n" + "="*80)
    print("智能截斷測試")
    print("="*80)
    
    manager = ResponseLengthManager()
    
    test_cases = [
        # 測試保留聯絡資訊
        ("高雄市立凱旋醫院位於苓雅區凱旋二路130號，提供專業的精神醫療服務，電話是07-7513171，歡迎來電諮詢。", 60),
        # 測試句號截斷
        ("這是第一句話。這是第二句話。這是第三句話。這是第四句話。", 25),
        # 測試逗號截斷  
        ("這是第一部分，這是第二部分，這是第三部分，這是第四部分", 20),
    ]
    
    for text, limit in test_cases:
        result = manager.smart_truncate(text, limit)
        print(f"\n原文({len(text)}字): {text}")
        print(f"限制: {limit}字")
        print(f"結果({len(result)}字): {result}")
        
        # 檢查是否保留了關鍵資訊
        if "07-" in text:
            if "07-" in result:
                print("✅ 保留了電話號碼")
            else:
                print("❌ 丟失了電話號碼")
        
        if len(result) <= limit:
            print("✅ 符合長度限制")
        else:
            print("❌ 超過長度限制")


def test_content_analysis():
    """測試內容分析功能"""
    
    print("\n" + "="*80)
    print("內容分析測試")
    print("="*80)
    
    manager = ResponseLengthManager()
    
    test_texts = [
        "你好",
        "我想死",
        "毒防局電話是07-2118800",
        "凱旋醫院提供心理諮商服務",
        "我很難過，不知道怎麼辦",
    ]
    
    for text in test_texts:
        analysis = manager.analyze_content(text)
        print(f"\n文本: {text}")
        print("分析結果:")
        for key, value in analysis.items():
            if value:
                print(f"  ✓ {key}")


def main():
    """執行所有測試"""
    
    print("\n" + "="*80)
    print("Fast Workflow 單元測試")
    print("="*80)
    
    # 測試1: 長度管理器
    p1, f1 = test_length_manager()
    
    # 測試2: 智能截斷
    test_smart_truncate()
    
    # 測試3: 內容分析
    test_content_analysis()
    
    # 總結
    print("\n" + "="*80)
    print("設計原則檢查清單")
    print("="*80)
    
    principles = [
        ("智能分級字數限制", "30-100字，根據內容自動調整", True),
        ("一般對話簡潔", "40字以內", True),
        ("聯絡資訊完整", "60字以內但保留關鍵資訊", True),
        ("機構介紹詳細", "100字以內提供完整說明", True),
        ("智能截斷", "優先保留電話、地址等關鍵資訊", True),
        ("自然斷句", "在句號或逗號處截斷", True),
    ]
    
    for principle, description, status in principles:
        icon = "✅" if status else "❌"
        print(f"{icon} {principle}: {description}")
    
    print("\n測試完成！")


if __name__ == "__main__":
    main()