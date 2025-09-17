"""測試 Google Places API 整合"""

import asyncio
import logging
from app.langgraph.ultimate_workflow import UltimateWorkflow
from app.langgraph.state import WorkflowState

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_places_query():
    """測試地點查詢功能"""

    workflow = UltimateWorkflow()

    # 測試案例
    test_cases = [
        {
            "input": "高雄市毒品防制局的電話是多少？",
            "description": "查詢毒防局電話"
        },
        {
            "input": "高雄市政府衛生局在哪裡？",
            "description": "查詢衛生局地址"
        },
        {
            "input": "凱旋醫院的地址和電話",
            "description": "查詢醫院完整資訊"
        },
        {
            "input": "高雄長庚醫院營業時間",
            "description": "查詢醫院營業時間"
        },
        {
            "input": "我想知道高雄市立大同醫院怎麼去",
            "description": "查詢醫院位置"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"測試 {i}: {test_case['description']}")
        print(f"用戶輸入: {test_case['input']}")
        print(f"{'='*60}")

        # 建立狀態
        state = WorkflowState(
            input_text=test_case["input"],
            user_id="test_user",
            session_id=f"test_session_{i}",
            conversation_id=f"test_conv_{i}"
        )

        try:
            # 執行工作流
            result = await workflow.ainvoke(state)

            print(f"\n意圖分析結果:")
            if result.get("intent_analysis"):
                intent = result["intent_analysis"]
                print(f"  - 意圖: {intent.get('intent')}")
                print(f"  - 需要Places API: {intent.get('need_places_api')}")
                if intent.get('place_query_info'):
                    pqi = intent['place_query_info']
                    print(f"  - 查詢類型: {pqi.get('query_type')}")
                    print(f"  - 地點名稱: {pqi.get('place_name')}")
                    print(f"  - 信心分數: {pqi.get('confidence')}")

            print(f"\nAI回應:")
            print(f"{result.get('reply', '無回應')}")

            if result.get("knowledge"):
                print(f"\n檢索到的知識:")
                print(f"{result.get('knowledge')[:200]}...")

        except Exception as e:
            print(f"錯誤: {str(e)}")
            import traceback
            traceback.print_exc()

        # 等待一下避免太快
        await asyncio.sleep(2)

async def test_single_query():
    """測試單一查詢（互動式）"""

    workflow = UltimateWorkflow()

    print("\n" + "="*60)
    print("Google Places API 測試 - 互動模式")
    print("="*60)
    print("範例輸入:")
    print("  - 高雄市毒品防制局的電話")
    print("  - 凱旋醫院在哪裡")
    print("  - 高雄長庚醫院營業時間")
    print("\n輸入 'quit' 結束測試")
    print("="*60)

    conversation_id = "interactive_test"

    while True:
        user_input = input("\n請輸入查詢: ").strip()

        if user_input.lower() == 'quit':
            print("結束測試")
            break

        if not user_input:
            continue

        # 建立狀態
        state = WorkflowState(
            input_text=user_input,
            user_id="test_user",
            session_id="interactive_session",
            conversation_id=conversation_id
        )

        try:
            print("\n處理中...")

            # 執行工作流
            result = await workflow.ainvoke(state)

            # 顯示分析結果
            print(f"\n{'='*40}")
            print("分析結果:")
            if result.get("intent_analysis"):
                intent = result["intent_analysis"]
                print(f"  意圖: {intent.get('intent')}")
                print(f"  需要Places API: {intent.get('need_places_api')}")
                if intent.get('need_places_api') and intent.get('place_query_info'):
                    pqi = intent['place_query_info']
                    print(f"  查詢類型: {pqi.get('query_type')}")
                    print(f"  地點名稱: {pqi.get('place_name')}")
                    print(f"  信心分數: {pqi.get('confidence')}")

            print(f"\n{'='*40}")
            print("AI回應:")
            print(result.get('reply', '無回應'))
            print(f"{'='*40}")

        except Exception as e:
            print(f"\n錯誤: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("選擇測試模式:")
    print("1. 自動測試多個案例")
    print("2. 互動式測試")

    choice = input("\n請選擇 (1 或 2): ").strip()

    if choice == "1":
        asyncio.run(test_places_query())
    elif choice == "2":
        asyncio.run(test_single_query())
    else:
        print("無效選擇")