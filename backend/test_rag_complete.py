#!/usr/bin/env python3
"""
RAG系統完整測試 - 10組測試案例（精簡版）
"""

import asyncio
import json
from datetime import datetime
import httpx

# API設定
API_BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_BASE_URL}/api/v1/chat/"

class RAGTester:
    def __init__(self):
        self.results = []
        self.session_id = f"complete_test_{datetime.now().strftime('%H%M%S')}"
        
    async def send_message(self, message: str) -> dict:
        """發送訊息到API"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    CHAT_ENDPOINT,
                    json={
                        "message": message,
                        "session_id": self.session_id,
                        "user_id": "test_user"
                    }
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": str(e)}
    
    async def run_test(self, test_id: int, test_case: dict) -> dict:
        """執行單一測試"""
        print(f"\n{'='*60}")
        print(f"測試 {test_id}: {test_case['name']} (難度: {test_case['difficulty']})")
        print(f"問題: {test_case['question']}")
        
        # 發送問題
        response = await self.send_message(test_case['question'])
        
        if 'error' in response:
            print(f"❌ 錯誤: {response['error']}")
            return {
                'id': test_id,
                'name': test_case['name'],
                'passed': False,
                'score': 0
            }
        
        reply = response.get('reply', '')
        print(f"\nAI回應: {reply[:200]}...")
        if len(reply) > 200:
            print(f"(已截斷，總長度: {len(reply)})")
        
        # 檢查關鍵字
        reply_lower = reply.lower()
        found = []
        missing = []
        
        for keyword in test_case['keywords']:
            if keyword.lower() in reply_lower:
                found.append(keyword)
            else:
                missing.append(keyword)
        
        score = len(found) / len(test_case['keywords']) if test_case['keywords'] else 0
        passed = score >= test_case.get('threshold', 0.5)
        
        print(f"\n檢查結果:")
        print(f"  ✓ 找到: {', '.join(found) if found else '無'}")
        print(f"  ✗ 缺少: {', '.join(missing) if missing else '無'}")
        print(f"  得分: {score:.0%}")
        print(f"  {'✅ 通過' if passed else '❌ 失敗'}")
        
        return {
            'id': test_id,
            'name': test_case['name'],
            'difficulty': test_case['difficulty'],
            'found': found,
            'missing': missing,
            'score': score,
            'passed': passed
        }
    
    async def run_all_tests(self):
        """執行所有測試"""
        print(f"\n{'='*70}")
        print("RAG系統完整測試開始")
        print(f"{'='*70}")
        
        for i, test in enumerate(TEST_CASES, 1):
            result = await self.run_test(i, test)
            self.results.append(result)
            
            # 每個測試間隔
            if i < len(TEST_CASES):
                await asyncio.sleep(2)
        
        self.print_summary()
    
    def print_summary(self):
        """列印總結"""
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
        
        # 按難度分組
        difficulty_stats = {}
        for result in self.results:
            diff = result.get('difficulty', '未知')
            if diff not in difficulty_stats:
                difficulty_stats[diff] = {'total': 0, 'passed': 0, 'scores': []}
            difficulty_stats[diff]['total'] += 1
            difficulty_stats[diff]['scores'].append(result['score'])
            if result['passed']:
                difficulty_stats[diff]['passed'] += 1
        
        print(f"\n📈 按難度分析:")
        for diff in sorted(difficulty_stats.keys()):
            stats = difficulty_stats[diff]
            avg = sum(stats['scores']) / len(stats['scores'])
            pass_rate = stats['passed'] / stats['total'] * 100
            status = "✅" if pass_rate >= 70 else "⚠️" if pass_rate >= 50 else "❌"
            print(f"  {diff}: {status} 通過 {stats['passed']}/{stats['total']} ({pass_rate:.0f}%), 平均 {avg:.1%}")
        
        # 詳細結果
        print(f"\n📋 詳細結果:")
        for result in self.results:
            status = "✅" if result['passed'] else "❌"
            print(f"  {status} 測試{result['id']}: {result['name']} - {result['score']:.0%}")
            if result['missing']:
                print(f"     缺少: {', '.join(result['missing'])}")
        
        # 最終評級
        print(f"\n🏆 最終評級:")
        if avg_score >= 0.9:
            print(f"  🏆 A+ (優秀) - {avg_score:.1%}")
        elif avg_score >= 0.8:
            print(f"  🎯 A (良好) - {avg_score:.1%}")
        elif avg_score >= 0.7:
            print(f"  ✅ B (中等) - {avg_score:.1%}")
        elif avg_score >= 0.6:
            print(f"  ⚠️ C (及格) - {avg_score:.1%}")
        else:
            print(f"  ❌ D (需改進) - {avg_score:.1%}")

# 測試案例定義
TEST_CASES = [
    # 簡單級別 (1-2)
    {
        'name': '直接查詢醫院',
        'difficulty': '簡單',
        'question': '高雄市立凱旋醫院的地址和電話是什麼？',
        'keywords': ['凱旋', '苓雅', '751', '130號'],
        'threshold': 0.75
    },
    {
        'name': '尋求戒毒協助',
        'difficulty': '簡單',
        'question': '我想戒毒，高雄有哪些地方可以幫助我？',
        'keywords': ['醫院', '凱旋', '毒防中心'],
        'threshold': 0.6
    },
    
    # 中等級別 (3-5)
    {
        'name': '美沙冬治療',
        'difficulty': '中等',
        'question': '什麼是美沙冬替代療法？高雄哪裡可以做？',
        'keywords': ['美沙冬', '替代', '鴉片', '民生醫院'],
        'threshold': 0.5
    },
    {
        'name': '家屬求助',
        'difficulty': '中等',
        'question': '我弟弟在吸毒，家人該怎麼辦？有什麼資源可以幫助我們？',
        'keywords': ['家庭', '支持', '諮商', '社會局'],
        'threshold': 0.4
    },
    {
        'name': '就業輔導',
        'difficulty': '中等',
        'question': '戒毒後想找工作，有職業訓練的地方嗎？',
        'keywords': ['職業', '訓練', '就業', '勞動'],
        'threshold': 0.5
    },
    
    # 困難級別 (6-8)
    {
        'name': '憂鬱自殺防治',
        'difficulty': '困難',
        'question': '最近心情很低落，有想不開的念頭，現在是半夜，誰可以幫我？',
        'keywords': ['生命線', '1995', '24小時', '心理'],
        'threshold': 0.5
    },
    {
        'name': '出獄更生',
        'difficulty': '困難',
        'question': '我快出獄了，沒地方住，有收容機構嗎？',
        'keywords': ['收容', '安置', '更生', '仁愛之家'],
        'threshold': 0.4
    },
    {
        'name': '宗教戒毒',
        'difficulty': '困難',
        'question': '聽說有教會在幫人戒毒，在高雄郊區，是哪裡？',
        'keywords': ['晨曦', '福音', '基督', '沐恩'],
        'threshold': 0.4
    },
    
    # 極難級別 (9-10)
    {
        'name': '法律諮詢',
        'difficulty': '極難',
        'question': '朋友被抓到持有K他命，會判多重？有緩起訴的機會嗎？',
        'keywords': ['第三級', 'K他命', '緩起訴', '地檢署'],
        'threshold': 0.3
    },
    {
        'name': '綜合需求',
        'difficulty': '極難',
        'question': '朋友疑似吸安非他命，瘦很多，想帶他去左營的大醫院，那裡有專門科別嗎？沒錢怎麼辦？',
        'keywords': ['榮總', '成癮', '精神科', '補助'],
        'threshold': 0.3
    }
]

async def main():
    tester = RAGTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())