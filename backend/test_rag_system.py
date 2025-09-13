#!/usr/bin/env python3
"""
RAG系統測試集 - 測試向量資料庫檢索能力
基於實際資料庫內容設計的測試案例
"""

import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime
import httpx
from colorama import init, Fore, Style

init(autoreset=True)

# API設定
API_BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_BASE_URL}/api/v1/chat"

class RAGSystemTester:
    """RAG系統測試器"""
    
    def __init__(self):
        self.session_id = f"rag_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.test_results = []
        
    async def send_message(self, message: str) -> Dict[str, Any]:
        """發送訊息到聊天系統"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    CHAT_ENDPOINT,
                    json={
                        "message": message,
                        "session_id": self.session_id
                    }
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"{Fore.RED}❌ 發送訊息失敗: {e}{Style.RESET_ALL}")
                return {"response": "", "error": str(e)}
    
    async def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """執行單一測試案例"""
        print(f"\n{Fore.CYAN}📝 測試案例: {test_case['name']}{Style.RESET_ALL}")
        print(f"   問題: {test_case['question']}")
        
        # 發送問題
        response = await self.send_message(test_case['question'])
        
        # 檢查預期的關鍵字
        response_text = response.get('response', '').lower()
        expected_keywords = [kw.lower() for kw in test_case['expected_keywords']]
        found_keywords = [kw for kw in expected_keywords if kw in response_text]
        missing_keywords = [kw for kw in expected_keywords if kw not in response_text]
        
        # 計算成功率
        success_rate = len(found_keywords) / len(expected_keywords) if expected_keywords else 0
        passed = success_rate >= test_case.get('pass_threshold', 0.5)
        
        # 結果
        result = {
            'name': test_case['name'],
            'category': test_case['category'],
            'question': test_case['question'],
            'response': response.get('response', ''),
            'expected_keywords': expected_keywords,
            'found_keywords': found_keywords,
            'missing_keywords': missing_keywords,
            'success_rate': success_rate,
            'passed': passed
        }
        
        # 顯示結果
        if passed:
            print(f"   {Fore.GREEN}✅ 通過 (成功率: {success_rate:.1%}){Style.RESET_ALL}")
        else:
            print(f"   {Fore.RED}❌ 失敗 (成功率: {success_rate:.1%}){Style.RESET_ALL}")
            print(f"   缺少關鍵字: {', '.join(missing_keywords)}")
        
        return result
    
    async def run_all_tests(self):
        """執行所有測試"""
        print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}RAG系統測試開始{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        
        for test_case in TEST_CASES:
            result = await self.run_test_case(test_case)
            self.test_results.append(result)
            await asyncio.sleep(2)  # 避免過快請求
        
        # 統計結果
        self.print_summary()
    
    def print_summary(self):
        """列印測試摘要"""
        print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}測試結果摘要{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        
        # 按類別統計
        categories = {}
        for result in self.test_results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            categories[cat]['total'] += 1
            if result['passed']:
                categories[cat]['passed'] += 1
        
        print(f"\n📊 總體結果:")
        print(f"   總測試數: {total}")
        print(f"   {Fore.GREEN}通過: {passed}{Style.RESET_ALL}")
        print(f"   {Fore.RED}失敗: {failed}{Style.RESET_ALL}")
        print(f"   成功率: {passed/total:.1%}")
        
        print(f"\n📈 分類結果:")
        for cat, stats in categories.items():
            rate = stats['passed'] / stats['total']
            color = Fore.GREEN if rate >= 0.7 else Fore.YELLOW if rate >= 0.5 else Fore.RED
            print(f"   {cat}: {color}{stats['passed']}/{stats['total']} ({rate:.1%}){Style.RESET_ALL}")
        
        # 失敗案例詳情
        if failed > 0:
            print(f"\n{Fore.RED}❌ 失敗案例詳情:{Style.RESET_ALL}")
            for result in self.test_results:
                if not result['passed']:
                    print(f"\n   案例: {result['name']}")
                    print(f"   問題: {result['question']}")
                    print(f"   缺少: {', '.join(result['missing_keywords'])}")
        
        # 儲存結果
        with open('rag_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 詳細結果已儲存至 rag_test_results.json")


# 測試案例定義
TEST_CASES = [
    # === 醫療院所查詢 ===
    {
        'name': '查詢戒毒醫院',
        'category': '醫療院所',
        'question': '我想找高雄可以戒毒的醫院',
        'expected_keywords': ['凱旋醫院', '戒癮', '美沙冬'],
        'pass_threshold': 0.6
    },
    {
        'name': '查詢精神科服務',
        'category': '醫療院所',
        'question': '高雄哪裡有精神科可以看診?',
        'expected_keywords': ['精神科', '醫院', '門診'],
        'pass_threshold': 0.7
    },
    {
        'name': '查詢美沙冬治療',
        'category': '醫療院所',
        'question': '哪裡可以接受美沙冬替代療法?',
        'expected_keywords': ['美沙冬', '替代', '民生醫院'],
        'pass_threshold': 0.6
    },
    {
        'name': '查詢榮總服務',
        'category': '醫療院所',
        'question': '高雄榮總有戒毒門診嗎?電話多少?',
        'expected_keywords': ['榮民總醫院', '成癮', '3422121'],
        'pass_threshold': 0.6
    },
    
    # === 政府機關查詢 ===
    {
        'name': '查詢毒防中心',
        'category': '政府機關',
        'question': '高雄毒品危害防制中心在哪裡?',
        'expected_keywords': ['毒品危害防制中心', '凱旋二路', '7134000'],
        'pass_threshold': 0.6
    },
    {
        'name': '查詢個案管理服務',
        'category': '政府機關',
        'question': '毒防中心有提供什麼服務?',
        'expected_keywords': ['個案管理', '轉介', '追蹤輔導'],
        'pass_threshold': 0.6
    },
    {
        'name': '查詢監獄服務',
        'category': '政府機關',
        'question': '高雄監獄有提供戒毒相關的訓練嗎?',
        'expected_keywords': ['監獄', '技能訓練', '矯正'],
        'pass_threshold': 0.5
    },
    
    # === 民間團體查詢 ===
    {
        'name': '查詢生命線',
        'category': '民間團體',
        'question': '我很憂鬱想自殺，有24小時專線嗎?',
        'expected_keywords': ['生命線', '1995', '24小時'],
        'pass_threshold': 0.6
    },
    {
        'name': '查詢晨曦會',
        'category': '民間團體',
        'question': '晨曦會在高雄有服務據點嗎?',
        'expected_keywords': ['晨曦會', '福音戒毒', '梓官'],
        'pass_threshold': 0.6
    },
    {
        'name': '查詢宗教戒毒',
        'category': '民間團體',
        'question': '有基督教的戒毒機構嗎?',
        'expected_keywords': ['基督教', '沐恩之家', '福音'],
        'pass_threshold': 0.5
    },
    
    # === 醫療知識查詢 ===
    {
        'name': '查詢毒品危害',
        'category': '醫療知識',
        'question': '安非他命對身體有什麼危害?',
        'expected_keywords': ['安非他命', '神經', '中風'],
        'pass_threshold': 0.6
    },
    {
        'name': '查詢戒斷症狀',
        'category': '醫療知識',
        'question': '海洛因戒斷會有什麼症狀?',
        'expected_keywords': ['海洛因', '戒斷', '症狀'],
        'pass_threshold': 0.6
    },
    {
        'name': '查詢美沙冬原理',
        'category': '醫療知識',
        'question': '美沙冬替代療法的原理是什麼?',
        'expected_keywords': ['美沙冬', '鴉片', '替代'],
        'pass_threshold': 0.6
    },
    
    # === 法律相關查詢 ===
    {
        'name': '查詢毒品分級',
        'category': '法律知識',
        'question': 'K他命是第幾級毒品?',
        'expected_keywords': ['K他命', '第三級'],
        'pass_threshold': 0.7
    },
    {
        'name': '查詢毒品法規',
        'category': '法律知識',
        'question': '毒品危害防制條例怎麼分類毒品?',
        'expected_keywords': ['毒品危害防制條例', '分類', '第一級'],
        'pass_threshold': 0.6
    },
    
    # === 綜合查詢 ===
    {
        'name': '急難求助',
        'category': '綜合查詢',
        'question': '我弟弟吸毒，現在很痛苦想戒，該打電話去哪裡求助?',
        'expected_keywords': ['醫院', '毒防中心', '電話'],
        'pass_threshold': 0.5
    },
    {
        'name': '就業輔導查詢',
        'category': '綜合查詢',
        'question': '戒毒後想找工作，有職業訓練的地方嗎?',
        'expected_keywords': ['職業訓練', '就業', '勞動部'],
        'pass_threshold': 0.5
    },
    {
        'name': '家屬求助',
        'category': '綜合查詢',
        'question': '我先生在吸毒，家人可以得到什麼協助?',
        'expected_keywords': ['家庭支持', '社會局', '諮商'],
        'pass_threshold': 0.5
    },
    
    # === 特定機構查詢 ===
    {
        'name': '查詢凱旋醫院',
        'category': '特定機構',
        'question': '高雄市立凱旋醫院的地址和電話是多少?',
        'expected_keywords': ['凱旋醫院', '苓雅區', '7513171'],
        'pass_threshold': 0.7
    },
    {
        'name': '查詢長庚醫院',
        'category': '特定機構',
        'question': '高雄長庚有成癮治療嗎?在哪裡?',
        'expected_keywords': ['長庚', '鳥松', '成癮'],
        'pass_threshold': 0.6
    }
]


async def main():
    """主程式"""
    tester = RAGSystemTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())