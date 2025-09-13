"""Fast Workflow 測試腳本"""

import asyncio
import logging
from app.langgraph.fast_workflow import create_fast_workflow
from app.langgraph.state import WorkflowState

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_fast_workflow():
    """測試快速工作流程"""
    
    # 創建工作流
    workflow = create_fast_workflow()
    
    # 測試案例
    test_cases = [
        # 1. 一般問候
        {
            "input": "你好",
            "expected_len": 40,
            "should_contain": ["好", "？"]
        },
        # 2. 危機偵測
        {
            "input": "我想死",
            "expected_len": 40,
            "should_contain": ["1995", "聊"]
        },
        # 3. 資訊查詢
        {
            "input": "毒防局電話多少",
            "expected_len": 40,
            "should_contain": ["07", "電話", "聯絡"]
        },
        # 4. 情緒支持
        {
            "input": "我很難過",
            "expected_len": 40,
            "should_contain": ["陪", "聊", "嗎"]
        },
        # 5. 長文本測試
        {
            "input": "我想要知道高雄市有哪些戒毒機構可以提供協助，最好是有電話可以聯絡的",
            "expected_len": 40,
            "should_contain": []  # 應該要被截斷
        },
        # 6. 早安問候
        {
            "input": "早安",
            "expected_len": 40,
            "should_contain": ["早", "今天"]
        },
        # 7. 毒品關鍵詞
        {
            "input": "有人要賣我安非他命",
            "expected_len": 40,
            "should_contain": ["1995", "專線", "聯絡"]
        },
        # 8. 一般對話
        {
            "input": "今天天氣不錯",
            "expected_len": 40,
            "should_contain": []
        }
    ]
    
    print("\n" + "="*60)
    print("Fast Workflow 測試開始")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n測試 {i}: {test['input'][:30]}")
        print("-" * 40)
        
        # 準備狀態
        state = WorkflowState(
            user_id=f"test_user_{i}",
            input_text=test["input"],
            session_id=f"test_session_{i}"
        )
        
        try:
            # 執行工作流
            result = await workflow.ainvoke(state)
            
            reply = result.get("reply", "")
            print(f"輸入: {test['input']}")
            print(f"回應: {reply}")
            print(f"長度: {len(reply)} 字")
            
            # 檢查長度
            if len(reply) <= test["expected_len"]:
                print(f"✅ 長度檢查通過 ({len(reply)} <= {test['expected_len']})")
                length_pass = True
            else:
                print(f"❌ 長度檢查失敗 ({len(reply)} > {test['expected_len']})")
                length_pass = False
            
            # 檢查關鍵詞
            keyword_pass = True
            for keyword in test.get("should_contain", []):
                if keyword in reply:
                    print(f"✅ 包含關鍵詞: {keyword}")
                else:
                    print(f"⚠️ 缺少關鍵詞: {keyword}")
                    keyword_pass = False
            
            # 檢查分析結果
            if result.get("risk_level"):
                print(f"風險等級: {result['risk_level']}")
            if result.get("intent"):
                print(f"意圖: {result['intent']}")
            if result.get("need_knowledge"):
                print(f"需要知識庫: {result['need_knowledge']}")
            
            if length_pass:
                passed += 1
                print("✅ 測試通過")
            else:
                failed += 1
                print("❌ 測試失敗")
                
        except Exception as e:
            print(f"❌ 執行錯誤: {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"測試結果: {passed} 通過, {failed} 失敗")
    print("="*60)
    
    # 測試快取
    print("\n測試快取功能...")
    state = WorkflowState(
        user_id="cache_test",
        input_text="你好",
        session_id="cache_session"
    )
    
    # 第一次調用
    import time
    start = time.time()
    result1 = await workflow.ainvoke(state)
    time1 = time.time() - start
    
    # 第二次調用（應該從快取）
    start = time.time()
    result2 = await workflow.ainvoke(state)
    time2 = time.time() - start
    
    print(f"第一次調用: {time1:.3f}秒 - {result1['reply']}")
    print(f"第二次調用: {time2:.3f}秒 - {result2['reply']}")
    
    if time2 < time1 * 0.5:
        print("✅ 快取功能正常")
    else:
        print("⚠️ 快取可能未生效")
    
    print("\n測試完成！")


if __name__ == "__main__":
    asyncio.run(test_fast_workflow())