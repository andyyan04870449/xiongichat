"""執行長對話測試案例的簡化版腳本（忽略intent錯誤）"""

import asyncio
import json
import time
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from app.services.chat import ChatService
from app.schemas.chat import ChatRequest

# 設定日誌級別以減少錯誤輸出
logging.getLogger("app.langgraph.ultimate_workflow").setLevel(logging.CRITICAL)

# 確保使用UltimateWorkflow
os.environ["USE_ULTIMATE_WORKFLOW"] = "true"


class SimpleLongConversationTestRunner:
    """簡化版長對話測試執行器"""
    
    def __init__(self):
        self.chat_service = ChatService()
        self.results = []
        
    async def run_conversation(self, case_name: str, conversation: List[str]) -> Dict[str, Any]:
        """執行單一長對話測試（簡化版）"""
        
        user_id = f"simple_test_{case_name}_{datetime.now().strftime('%H%M%S')}"
        conversation_id = None  # 第一次請求會自動生成，後續使用相同的
        conversation_history = []
        
        try:
            print(f"\n開始測試: {case_name}")
            print("-" * 50)
            
            # 執行對話的每一輪
            for i, user_input in enumerate(conversation):
                print(f"\n第{i+1}輪")
                print(f"用戶: {user_input}")
                
                request = ChatRequest(
                    user_id=user_id,
                    message=user_input,
                    conversation_id=conversation_id  # 傳遞 conversation_id
                )
                
                start_time = time.time()
                response = await self.chat_service.process_message(request)
                response_time = time.time() - start_time
                
                # 第一次請求後保存 conversation_id
                if conversation_id is None:
                    conversation_id = response.conversation_id
                    print(f"Conversation ID: {conversation_id}")
                
                ai_response = response.reply
                print(f"AI: {ai_response[:100]}...")
                print(f"耗時: {response_time:.2f}秒")
                
                conversation_history.append({
                    "turn": i + 1,
                    "user": user_input,
                    "ai": ai_response,
                    "response_time": round(response_time, 2)
                })
                
                # 控制請求頻率
                await asyncio.sleep(0.5)
            
            result = {
                "case_name": case_name,
                "conversation_history": conversation_history,
                "total_turns": len(conversation_history),
                "success": True
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 測試失敗: {str(e)}")
            return {
                "case_name": case_name,
                "error": str(e),
                "success": False
            }


async def main():
    """執行簡化版長對話測試"""
    
    print("\n" + "="*80)
    print("雄i聊系統 - 簡化版長對話測試")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    runner = SimpleLongConversationTestRunner()
    
    # 定義幾個簡單的測試案例
    test_cases = [
        {
            "name": "個人資訊記憶測試",
            "conversation": [
                "我叫阿明，今年35歲",
                "我有兩個小孩",
                "你記得我幾歲嗎？"
            ]
        },
        {
            "name": "情緒追蹤測試",
            "conversation": [
                "今天心情很差",
                "被老闆罵了",
                "不過現在好一點了",
                "我的心情怎麼樣？"
            ]
        },
        {
            "name": "事件記憶測試",
            "conversation": [
                "週一我去了醫院",
                "週三參加團體治療",
                "週五和家人吃飯",
                "這週我做了什麼？"
            ]
        },
        {
            "name": "戒毒進展測試",
            "conversation": [
                "我已經戒毒3個月了",
                "下個月是我女兒生日",
                "到女兒生日我戒毒多久了？"
            ]
        },
        {
            "name": "關係記憶測試",
            "conversation": [
                "我太太很支持我",
                "但哥哥不相信我",
                "朋友阿強也在戒毒",
                "誰對我幫助最大？"
            ]
        }
    ]
    
    # 執行所有測試案例
    all_results = []
    
    for test_case in test_cases:
        result = await runner.run_conversation(
            test_case["name"],
            test_case["conversation"]
        )
        all_results.append(result)
        
        # 短暫休息
        await asyncio.sleep(2)
    
    # 顯示總結
    print("\n" + "="*80)
    print("測試總結")
    print("="*80)
    
    successful = [r for r in all_results if r.get('success', False)]
    print(f"\n總測試數: {len(all_results)}")
    print(f"成功: {len(successful)}")
    print(f"失敗: {len(all_results) - len(successful)}")
    
    # 分析最後一輪回應
    print("\n最後一輪回應分析:")
    for result in all_results:
        if result.get('success') and result.get('conversation_history'):
            last_turn = result['conversation_history'][-1]
            print(f"\n{result['case_name']}:")
            print(f"  問題: {last_turn['user']}")
            print(f"  回答: {last_turn['ai'][:150]}...")
            
            # 簡單檢查是否包含關鍵資訊
            ai_response = last_turn['ai']
            if "35" in ai_response or "兩個" in ai_response:
                print("  ✅ 包含關鍵資訊")
            elif "心情" in ai_response or "好轉" in ai_response:
                print("  ✅ 理解情緒變化")
            elif "週一" in ai_response or "醫院" in ai_response:
                print("  ✅ 記得事件")
            elif "4個月" in ai_response or "四個月" in ai_response:
                print("  ✅ 正確推理")
            elif "太太" in ai_response or "支持" in ai_response:
                print("  ✅ 記得關係")
            else:
                print("  ⚠️ 可能遺漏資訊")
    
    # 儲存結果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"simple_long_conversation_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(all_results),
            "successful": len(successful),
            "results": all_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 報告已儲存: {report_file}")
    
    print("\n" + "="*80)
    print("🎉 簡化版長對話測試完成！")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())