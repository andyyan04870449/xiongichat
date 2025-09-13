"""Fast Workflow 獨立測試腳本"""

import asyncio
import logging
import sys
import os

# 添加路徑
sys.path.insert(0, '/Users/yangandy/KaohsiungCare/backend')

# 設定環境變數
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_fast_workflow():
    """測試快速工作流程"""
    
    # 直接導入需要的模組
    from app.langgraph.fast_workflow import CompleteFastWorkflow
    
    # 創建工作流
    workflow = CompleteFastWorkflow()
    
    # 測試案例
    test_cases = [
        # 1. 一般問候
        {
            "input": "你好",
            "description": "一般問候"
        },
        # 2. 危機偵測
        {
            "input": "我想死",
            "description": "危機偵測"
        },
        # 3. 資訊查詢
        {
            "input": "毒防局電話多少",
            "description": "資訊查詢"
        },
        # 4. 情緒支持
        {
            "input": "我很難過",
            "description": "情緒支持"
        },
        # 5. 長文本測試（應該被截斷到40字）
        {
            "input": "我想要知道高雄市有哪些戒毒機構可以提供協助，最好是有電話可以聯絡的，請詳細告訴我",
            "description": "長文本測試"
        },
        # 6. 毒品關鍵詞
        {
            "input": "有人要賣我安非他命",
            "description": "毒品關鍵詞"
        }
    ]
    
    print("\n" + "="*60)
    print("Fast Workflow 40字限制測試")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n測試 {i}: {test['description']}")
        print("-" * 40)
        
        # 準備狀態
        state = {
            "user_id": f"test_user_{i}",
            "input_text": test["input"],
            "session_id": f"test_session_{i}"
        }
        
        try:
            # 執行工作流
            import time
            start_time = time.time()
            result = await workflow.ainvoke(state)
            elapsed = time.time() - start_time
            
            reply = result.get("reply", "")
            print(f"輸入: {test['input']}")
            print(f"回應: {reply}")
            print(f"長度: {len(reply)} 字")
            print(f"耗時: {elapsed:.3f} 秒")
            
            # 40字檢查
            if len(reply) <= 40:
                print(f"✅ 通過40字限制 ({len(reply)} <= 40)")
                passed += 1
            else:
                print(f"❌ 違反40字限制 ({len(reply)} > 40)")
                failed += 1
            
            # 顯示分析結果
            if result.get("risk_level"):
                print(f"風險等級: {result['risk_level']}")
            if result.get("intent"):
                print(f"意圖: {result['intent']}")
            if result.get("need_knowledge"):
                print(f"需要知識庫: {result['need_knowledge']}")
                
        except Exception as e:
            print(f"❌ 執行錯誤: {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"測試結果總結")
    print(f"通過: {passed} 個")
    print(f"失敗: {failed} 個")
    print(f"成功率: {passed/(passed+failed)*100:.1f}%")
    print("="*60)
    
    # 測試快取
    print("\n測試快取功能...")
    state = {
        "user_id": "cache_test",
        "input_text": "你好",
        "session_id": "cache_session"
    }
    
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
        print("✅ 快取功能正常（第二次調用速度提升 {:.1f}%）".format((1 - time2/time1) * 100))
    else:
        print("⚠️ 快取可能未生效")
    
    # 性能統計
    print("\n" + "="*60)
    print("設計目標對照")
    print("-" * 40)
    print(f"{'指標':<20} {'目標':<15} {'實際':<15} {'狀態'}")
    print("-" * 40)
    
    avg_time = sum([time1, time2]) / 2
    print(f"{'平均回應時間':<20} {'<1秒':<15} {f'{avg_time:.3f}秒':<15} {'✅' if avg_time < 1 else '❌'}")
    print(f"{'40字符合率':<20} {'100%':<15} {f'{passed/(passed+failed)*100:.1f}%':<15} {'✅' if passed == len(test_cases) else '⚠️'}")
    print(f"{'快取功能':<20} {'啟用':<15} {'啟用':<15} {'✅' if time2 < time1 * 0.5 else '❌'}")
    
    print("="*60)
    print("\n測試完成！")


if __name__ == "__main__":
    # 檢查API Key
    if not os.getenv('OPENAI_API_KEY'):
        print("警告: OPENAI_API_KEY 未設定，某些功能可能無法正常運作")
    
    asyncio.run(test_fast_workflow())