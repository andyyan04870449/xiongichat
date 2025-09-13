#!/usr/bin/env python3
"""
測試語境感知RAG改善 - 驗證多輪對話中的語境理解
"""

import asyncio
import json
from datetime import datetime
import httpx

# API設定
API_BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_BASE_URL}/api/v1/chat/"

class ContextAwareRAGTester:
    def __init__(self):
        self.results = []
        self.session_id = f"context_test_{datetime.now().strftime('%H%M%S')}"
        
    async def send_message(self, message: str, conversation_id: str = None) -> dict:
        """發送訊息到API"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                payload = {
                    "message": message,
                    "session_id": self.session_id,
                    "user_id": "test_user"
                }
                
                if conversation_id:
                    payload["conversation_id"] = conversation_id
                    
                response = await client.post(CHAT_ENDPOINT, json=payload)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": str(e)}
    
    async def run_conversation_test(self, test_name: str, conversation: list, expected_keywords: list) -> dict:
        """執行多輪對話測試"""
        print(f"\n{'='*70}")
        print(f"測試: {test_name}")
        print(f"{'='*70}")
        
        conversation_id = None
        all_responses = []
        
        # 執行對話
        for i, msg in enumerate(conversation, 1):
            print(f"\n輪次 {i}:")
            print(f"用戶: {msg}")
            
            response = await self.send_message(msg, conversation_id)
            
            if 'error' in response:
                print(f"❌ 錯誤: {response['error']}")
                return {
                    'name': test_name,
                    'passed': False,
                    'error': response['error']
                }
            
            # 保存conversation_id用於後續對話
            if not conversation_id and response.get('conversation_id'):
                conversation_id = response.get('conversation_id')
            
            reply = response.get('reply', '')
            all_responses.append(reply)
            print(f"AI: {reply[:200]}...")
            
            await asyncio.sleep(1)  # 避免過快請求
        
        # 檢查最後一個回應是否包含預期關鍵字
        final_response = all_responses[-1] if all_responses else ""
        final_response_lower = final_response.lower()
        
        found = []
        missing = []
        
        for keyword in expected_keywords:
            if keyword.lower() in final_response_lower:
                found.append(keyword)
            else:
                missing.append(keyword)
        
        score = len(found) / len(expected_keywords) if expected_keywords else 0
        passed = score >= 0.5  # 50%以上關鍵字即通過
        
        print(f"\n最終檢查:")
        print(f"  ✓ 找到: {', '.join(found) if found else '無'}")
        print(f"  ✗ 缺少: {', '.join(missing) if missing else '無'}")
        print(f"  得分: {score:.0%}")
        print(f"  {'✅ 通過' if passed else '❌ 失敗'}")
        
        return {
            'name': test_name,
            'conversation': conversation,
            'responses': all_responses,
            'found': found,
            'missing': missing,
            'score': score,
            'passed': passed
        }
    
    async def run_all_tests(self):
        """執行所有測試"""
        print(f"\n{'='*70}")
        print("語境感知RAG測試開始")
        print(f"{'='*70}")
        
        test_cases = [
            {
                'name': '基礎語境理解 - 凱旋醫院',
                'conversation': [
                    "你知道凱旋醫院嗎？",
                    "他們的電話是多少？"
                ],
                'expected': ['751', '07']  # 凱旋醫院電話
            },
            {
                'name': '代詞理解 - 那裡',
                'conversation': [
                    "高雄市毒防中心在哪裡？",
                    "那裡的電話號碼是什麼？"
                ],
                'expected': ['713', '07', '4000']  # 毒防中心電話
            },
            {
                'name': '省略主語 - 地址查詢',
                'conversation': [
                    "我想知道高雄榮總的資訊",
                    "地址在哪？"
                ],
                'expected': ['左營', '大中']  # 榮總地址關鍵字
            },
            {
                'name': '複雜語境 - 美沙冬治療',
                'conversation': [
                    "什麼是美沙冬替代療法？",
                    "高雄有哪些醫院可以做？",
                    "最近的在哪裡？電話多少？"
                ],
                'expected': ['電話', '地址', '醫院']
            },
            {
                'name': '連續追問 - 戒毒資源',
                'conversation': [
                    "我想戒毒",
                    "有哪些機構可以幫助我？",
                    "你剛說的第一個機構電話是多少？"
                ],
                'expected': ['07', '電話']
            },
            {
                'name': '混合語境 - 家屬諮詢',
                'conversation': [
                    "我弟弟在吸毒，我該怎麼辦？",
                    "有家屬支持團體嗎？",
                    "他們什麼時候有活動？怎麼聯絡？"
                ],
                'expected': ['聯絡', '電話', '時間']
            }
        ]
        
        for test_case in test_cases:
            result = await self.run_conversation_test(
                test_case['name'],
                test_case['conversation'],
                test_case['expected']
            )
            self.results.append(result)
            await asyncio.sleep(2)
        
        self.print_summary()
    
    def print_summary(self):
        """列印測試總結"""
        print(f"\n{'='*70}")
        print("測試總結")
        print(f"{'='*70}")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        avg_score = sum(r['score'] for r in self.results) / total if total > 0 else 0
        
        print(f"\n📊 總體統計:")
        print(f"  測試總數: {total}")
        print(f"  通過: {passed}")
        print(f"  失敗: {total - passed}")
        print(f"  平均得分: {avg_score:.1%}")
        print(f"  通過率: {passed/total*100:.1%}")
        
        print(f"\n📋 詳細結果:")
        for result in self.results:
            status = "✅" if result['passed'] else "❌"
            print(f"  {status} {result['name']}: {result['score']:.0%}")
            if result['missing']:
                print(f"     缺少: {', '.join(result['missing'])}")
        
        # 評級
        print(f"\n🏆 最終評級:")
        if avg_score >= 0.8:
            print(f"  🎯 優秀 - 語境理解能力強 ({avg_score:.1%})")
        elif avg_score >= 0.6:
            print(f"  ✅ 良好 - 基本語境理解正常 ({avg_score:.1%})")
        elif avg_score >= 0.4:
            print(f"  ⚠️ 中等 - 部分語境理解有效 ({avg_score:.1%})")
        else:
            print(f"  ❌ 需改進 - 語境理解能力不足 ({avg_score:.1%})")
        
        # 改善建議
        if avg_score < 0.8:
            print(f"\n💡 改善建議:")
            print("  1. 檢查 contextualize_query 方法是否正確調用")
            print("  2. 確認記憶是否正確傳遞到 RAG 查詢")
            print("  3. 驗證 LLM 提示詞是否清晰明確")
            print("  4. 考慮增加更多語境識別規則")

async def main():
    tester = ContextAwareRAGTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    print("\n🚀 開始語境感知RAG測試...")
    print("確保後端服務正在運行: http://localhost:8000")
    asyncio.run(main())