#!/usr/bin/env python3
"""
RAG系統對話測試 - 測試在自然對話中的檢索能力
從直接詢問到隱晦暗示，測試AI的理解與檢索能力
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Tuple
from datetime import datetime
import httpx

# API設定
API_BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_BASE_URL}/api/v1/chat/"

class ConversationTester:
    """對話式RAG測試器"""
    
    def __init__(self):
        self.session_id = f"conv_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.test_results = []
        self.conversation_history = []
        
    async def send_message(self, message: str) -> Dict[str, Any]:
        """發送訊息到聊天系統"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    CHAT_ENDPOINT,
                    json={
                        "message": message,
                        "session_id": self.session_id,
                        "user_id": "test_user_001"
                    }
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"❌ 發送訊息失敗: {e}")
                return {"response": "", "error": str(e)}
    
    async def run_conversation(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """執行單一對話測試"""
        print(f"\n{'='*60}")
        print(f"測試 {test_case['id']}: {test_case['name']}")
        print(f"難度: {test_case['difficulty']}")
        print(f"目標: {test_case['objective']}")
        print(f"{'='*60}\n")
        
        conversation_log = []
        keywords_found = set()
        total_score = 0
        
        # 執行對話
        for i, turn in enumerate(test_case['conversation'], 1):
            print(f"用戶 [{i}/{len(test_case['conversation'])}]: {turn['user']}")
            
            # 發送訊息
            response = await self.send_message(turn['user'])
            # API 回應的欄位是 'reply' 而不是 'response'
            ai_response = response.get('reply', response.get('response', ''))
            
            print(f"AI: {ai_response[:200]}...")
            if len(ai_response) > 200:
                print(f"    (回應已截斷，完整長度: {len(ai_response)} 字)")
            
            # 記錄對話
            conversation_log.append({
                'turn': i,
                'user': turn['user'],
                'ai': ai_response,
                'expected_keywords': turn.get('expected_keywords', [])
            })
            
            # 檢查關鍵字
            ai_lower = ai_response.lower()
            turn_keywords = []
            for keyword in turn.get('expected_keywords', []):
                if keyword.lower() in ai_lower:
                    keywords_found.add(keyword)
                    turn_keywords.append(keyword)
                    print(f"    ✓ 找到關鍵字: {keyword}")
            
            # 計算本輪得分
            if turn.get('expected_keywords'):
                turn_score = len(turn_keywords) / len(turn['expected_keywords']) * turn.get('weight', 1.0)
                total_score += turn_score
                print(f"    本輪得分: {turn_score:.2f}")
            
            print()
            await asyncio.sleep(2)  # 避免過快請求
        
        # 計算最終分數
        max_possible_score = sum(turn.get('weight', 1.0) for turn in test_case['conversation'] 
                                if turn.get('expected_keywords'))
        final_score = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        # 判定結果
        passed = final_score >= test_case.get('pass_threshold', 60)
        
        result = {
            'id': test_case['id'],
            'name': test_case['name'],
            'difficulty': test_case['difficulty'],
            'objective': test_case['objective'],
            'conversation_log': conversation_log,
            'keywords_found': list(keywords_found),
            'expected_keywords': test_case['expected_keywords'],
            'score': final_score,
            'passed': passed
        }
        
        # 顯示結果
        print(f"\n{'='*40}")
        print(f"測試結果:")
        print(f"  找到關鍵字: {len(keywords_found)}/{len(test_case['expected_keywords'])}")
        print(f"  最終得分: {final_score:.1f}%")
        if passed:
            print(f"  ✅ 測試通過")
        else:
            print(f"  ❌ 測試失敗")
        print(f"{'='*40}\n")
        
        return result
    
    async def run_all_tests(self):
        """執行所有測試"""
        print(f"\n{'='*60}")
        print(f"RAG對話測試開始")
        print(f"測試難度: 從直接到隱晦 (1-10級)")
        print(f"{'='*60}")
        
        for test_case in CONVERSATION_TESTS:
            # 每個測試使用新的session
            self.session_id = f"conv_test_{test_case['id']}_{datetime.now().strftime('%H%M%S')}"
            result = await self.run_conversation(test_case)
            self.test_results.append(result)
            await asyncio.sleep(3)  # 測試間隔
        
        # 顯示總結
        self.print_summary()
    
    def print_summary(self):
        """列印測試總結"""
        print(f"\n{'='*60}")
        print(f"測試總結報告")
        print(f"{'='*60}")
        
        # 統計數據
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        avg_score = sum(r['score'] for r in self.test_results) / total if total > 0 else 0
        
        print(f"\n📊 總體統計:")
        print(f"  測試總數: {total}")
        print(f"  通過數: {passed}")
        print(f"  失敗數: {total - passed}")
        print(f"  平均得分: {avg_score:.1f}%")
        print(f"  通過率: {passed/total*100:.1f}%")
        
        # 難度分析
        print(f"\n📈 難度分析:")
        difficulty_groups = {}
        for result in self.test_results:
            diff = result['difficulty']
            if diff not in difficulty_groups:
                difficulty_groups[diff] = {'total': 0, 'passed': 0, 'scores': []}
            difficulty_groups[diff]['total'] += 1
            difficulty_groups[diff]['scores'].append(result['score'])
            if result['passed']:
                difficulty_groups[diff]['passed'] += 1
        
        for diff in sorted(difficulty_groups.keys()):
            stats = difficulty_groups[diff]
            avg = sum(stats['scores']) / len(stats['scores'])
            pass_rate = stats['passed'] / stats['total'] * 100
            status = "✅" if pass_rate >= 70 else "⚠️" if pass_rate >= 50 else "❌"
            print(f"  {diff}: {status} 通過 {stats['passed']}/{stats['total']} ({pass_rate:.0f}%), 平均 {avg:.1f}%")
        
        # 詳細結果
        print(f"\n📋 詳細結果:")
        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"  {status} 測試{result['id']}: {result['name']}")
            print(f"     難度: {result['difficulty']}, 得分: {result['score']:.1f}%")
            missing = set(result['expected_keywords']) - set(result['keywords_found'])
            if missing:
                print(f"     缺少: {', '.join(missing)}")
        
        # 儲存結果
        with open('rag_conversation_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 詳細結果已儲存至 rag_conversation_results.json")
        
        # 評級
        print(f"\n🏆 最終評級:")
        if avg_score >= 90:
            grade = "A+ (優秀)"
            emoji = "🏆"
        elif avg_score >= 80:
            grade = "A (良好)"
            emoji = "🎯"
        elif avg_score >= 70:
            grade = "B (中等)"
            emoji = "✅"
        elif avg_score >= 60:
            grade = "C (及格)"
            emoji = "⚠️"
        else:
            grade = "D (需改進)"
            emoji = "❌"
        
        print(f"  {emoji} 系統評級: {grade}")
        print(f"  總分: {avg_score:.1f}/100")


# 對話測試案例定義
CONVERSATION_TESTS = [
    # 測試1: 直接詢問 (難度1)
    {
        'id': 1,
        'name': '直接詢問醫院資訊',
        'difficulty': '簡單(1)',
        'objective': '測試直接詢問特定醫院的檢索能力',
        'expected_keywords': ['凱旋醫院', '苓雅區', '7513171', '藥癮', '戒治'],
        'pass_threshold': 80,
        'conversation': [
            {
                'user': '高雄市立凱旋醫院的地址和電話是什麼？',
                'expected_keywords': ['凱旋醫院', '苓雅區', '7513171'],
                'weight': 1.0
            },
            {
                'user': '他們有提供什麼服務？',
                'expected_keywords': ['藥癮', '戒治', '心理諮商'],
                'weight': 1.0
            }
        ]
    },
    
    # 測試2: 簡單需求 (難度2)
    {
        'id': 2,
        'name': '尋求戒毒協助',
        'difficulty': '簡單(2)',
        'objective': '測試一般求助的檢索能力',
        'expected_keywords': ['醫院', '毒防中心', '門診', '治療', '電話'],
        'pass_threshold': 70,
        'conversation': [
            {
                'user': '我想要戒毒，該去哪裡？',
                'expected_keywords': ['醫院', '毒防中心'],
                'weight': 1.0
            },
            {
                'user': '有哪些醫院可以選擇？',
                'expected_keywords': ['凱旋', '榮總', '長庚'],
                'weight': 1.0
            },
            {
                'user': '怎麼聯絡他們？',
                'expected_keywords': ['電話', '地址'],
                'weight': 0.5
            }
        ]
    },
    
    # 測試3: 特定治療需求 (難度3)
    {
        'id': 3,
        'name': '美沙冬治療查詢',
        'difficulty': '中等(3)',
        'objective': '測試特定治療方式的檢索',
        'expected_keywords': ['美沙冬', '替代療法', '民生醫院', '鴉片', '門診'],
        'pass_threshold': 65,
        'conversation': [
            {
                'user': '聽說有一種替代療法可以治療海洛因成癮？',
                'expected_keywords': ['美沙冬', '替代療法'],
                'weight': 1.0
            },
            {
                'user': '這個治療的原理是什麼？',
                'expected_keywords': ['鴉片', '減少', '渴求'],
                'weight': 0.8
            },
            {
                'user': '高雄哪裡可以做這個治療？',
                'expected_keywords': ['民生醫院', '凱旋'],
                'weight': 1.0
            }
        ]
    },
    
    # 測試4: 間接詢問 (難度4)
    {
        'id': 4,
        'name': '家屬求助',
        'difficulty': '中等(4)',
        'objective': '測試間接需求的理解與檢索',
        'expected_keywords': ['家庭支持', '社會局', '諮商', '生命線', '1995'],
        'pass_threshold': 60,
        'conversation': [
            {
                'user': '我弟弟最近行為很奇怪，常常不回家，我懷疑他在吸毒',
                'expected_keywords': ['毒防中心', '醫院'],
                'weight': 0.8
            },
            {
                'user': '家人可以做什麼？我們都很擔心',
                'expected_keywords': ['家庭支持', '諮商'],
                'weight': 1.0
            },
            {
                'user': '我自己壓力也很大，快要崩潰了',
                'expected_keywords': ['生命線', '1995', '心理'],
                'weight': 1.0
            },
            {
                'user': '有政府單位可以協助嗎？',
                'expected_keywords': ['社會局', '毒防中心'],
                'weight': 0.8
            }
        ]
    },
    
    # 測試5: 情境描述 (難度5)
    {
        'id': 5,
        'name': '戒毒後就業',
        'difficulty': '中等(5)',
        'objective': '測試複合需求的檢索',
        'expected_keywords': ['職業訓練', '就業', '勞動部', '利伯他茲', '社會復歸'],
        'pass_threshold': 55,
        'conversation': [
            {
                'user': '我已經戒毒三個月了，想要重新開始生活',
                'expected_keywords': ['復歸', '輔導'],
                'weight': 0.5
            },
            {
                'user': '但是找工作很困難，雇主知道我的過去都不願意用我',
                'expected_keywords': ['就業', '職業'],
                'weight': 1.0
            },
            {
                'user': '有沒有地方可以學一技之長？',
                'expected_keywords': ['職業訓練', '勞動部'],
                'weight': 1.0
            },
            {
                'user': '或是有專門幫助我們這種人的機構？',
                'expected_keywords': ['利伯他茲', '晨曦會'],
                'weight': 1.0
            }
        ]
    },
    
    # 測試6: 隱晦暗示 (難度6)
    {
        'id': 6,
        'name': '憂鬱求助',
        'difficulty': '困難(6)',
        'objective': '測試隱晦求助的理解',
        'expected_keywords': ['生命線', '1995', '心理諮商', '精神科', '24小時'],
        'pass_threshold': 50,
        'conversation': [
            {
                'user': '最近心情很低落，覺得活著沒意思',
                'expected_keywords': ['心理', '諮商', '精神科'],
                'weight': 1.0
            },
            {
                'user': '晚上都睡不著，一直在想一些不好的事情',
                'expected_keywords': ['精神科', '醫院'],
                'weight': 0.7
            },
            {
                'user': '有時候真的很想一了百了',
                'expected_keywords': ['生命線', '1995', '自殺'],
                'weight': 1.5
            },
            {
                'user': '現在是半夜，有人可以聊聊嗎？',
                'expected_keywords': ['24小時', '1995'],
                'weight': 1.0
            }
        ]
    },
    
    # 測試7: 複雜情境 (難度7)
    {
        'id': 7,
        'name': '出獄更生',
        'difficulty': '困難(7)',
        'objective': '測試複雜背景的需求理解',
        'expected_keywords': ['監獄', '出監', '轉介', '更生', '仁愛之家'],
        'pass_threshold': 45,
        'conversation': [
            {
                'user': '我下個月就要出來了',
                'expected_keywords': ['出監', '更生'],
                'weight': 0.5
            },
            {
                'user': '在裡面待了兩年，外面的世界變化好大',
                'expected_keywords': ['監獄', '矯正'],
                'weight': 0.5
            },
            {
                'user': '沒有地方住，家人也不理我了',
                'expected_keywords': ['收容', '安置', '仁愛之家'],
                'weight': 1.5
            },
            {
                'user': '獄方說有些機構可以幫忙？',
                'expected_keywords': ['轉介', '更生', '社福'],
                'weight': 1.0
            },
            {
                'user': '我真的想重新做人',
                'expected_keywords': ['輔導', '職業訓練'],
                'weight': 0.8
            }
        ]
    },
    
    # 測試8: 委婉詢問 (難度8)
    {
        'id': 8,
        'name': '宗教戒毒',
        'difficulty': '困難(8)',
        'objective': '測試委婉表達的理解',
        'expected_keywords': ['福音戒毒', '晨曦會', '沐恩之家', '基督教', '梓官'],
        'pass_threshold': 40,
        'conversation': [
            {
                'user': '我朋友說信仰可以幫助戒癮，是真的嗎？',
                'expected_keywords': ['福音', '基督教'],
                'weight': 1.0
            },
            {
                'user': '他提到有些教會有在做這方面的服務',
                'expected_keywords': ['晨曦會', '沐恩之家'],
                'weight': 1.5
            },
            {
                'user': '好像在鄉下地方？不是在市區',
                'expected_keywords': ['梓官', '中崙'],
                'weight': 0.8
            },
            {
                'user': '他們是怎麼幫助人的？',
                'expected_keywords': ['生命教育', '福音戒毒'],
                'weight': 1.0
            }
        ]
    },
    
    # 測試9: 極度隱晦 (難度9)
    {
        'id': 9,
        'name': '法律問題',
        'difficulty': '極難(9)',
        'objective': '測試極度隱晦的需求理解',
        'expected_keywords': ['毒品危害防制條例', '第三級', 'K他命', '緩起訴', '地檢署'],
        'pass_threshold': 35,
        'conversation': [
            {
                'user': '朋友昨天被抓了',
                'expected_keywords': ['警察', '法律'],
                'weight': 0.3
            },
            {
                'user': '他身上有一些白色粉末，說是K',
                'expected_keywords': ['K他命', '毒品'],
                'weight': 1.0
            },
            {
                'user': '這個會很嚴重嗎？',
                'expected_keywords': ['第三級', '毒品危害防制條例'],
                'weight': 1.5
            },
            {
                'user': '第一次被抓有什麼辦法嗎？',
                'expected_keywords': ['緩起訴', '戒癮治療'],
                'weight': 1.2
            },
            {
                'user': '要去哪個單位處理？',
                'expected_keywords': ['地檢署', '檢察官'],
                'weight': 1.0
            }
        ]
    },
    
    # 測試10: 綜合挑戰 (難度10)
    {
        'id': 10,
        'name': '多重需求',
        'difficulty': '極難(10)',
        'objective': '測試多重隱含需求的理解',
        'expected_keywords': ['安非他命', '戒斷', '症狀', '榮總', '成癮醫學', '職業訓練', '社會局'],
        'pass_threshold': 30,
        'conversation': [
            {
                'user': '我朋友最近瘦了很多，眼睛都凹陷了',
                'expected_keywords': ['安非他命', '毒品'],
                'weight': 0.8
            },
            {
                'user': '他說他想停但是停不下來，一停就全身不舒服',
                'expected_keywords': ['戒斷', '症狀', '成癮'],
                'weight': 1.2
            },
            {
                'user': '聽說左營有家大醫院不錯？',
                'expected_keywords': ['榮總', '左營'],
                'weight': 1.0
            },
            {
                'user': '他們有專門的科別嗎？',
                'expected_keywords': ['成癮醫學', '精神科'],
                'weight': 1.0
            },
            {
                'user': '治療要花很多錢嗎？他現在沒工作',
                'expected_keywords': ['社會局', '補助', '急難救助'],
                'weight': 0.8
            },
            {
                'user': '治好後能幫他找工作嗎？',
                'expected_keywords': ['職業訓練', '就業輔導'],
                'weight': 0.8
            }
        ]
    }
]


async def main():
    """主程式"""
    tester = ConversationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())