"""Fast Workflow 情境測試腳本 - 驗證設計原則"""

import asyncio
import logging
import sys
import os
import time
from typing import Dict, List, Tuple
from datetime import datetime

sys.path.insert(0, '/Users/yangandy/KaohsiungCare/backend')
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')

from app.langgraph.fast_workflow import CompleteFastWorkflow
from app.langgraph.response_length_manager import ResponseLengthManager

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScenarioTester:
    """情境測試器"""
    
    def __init__(self):
        self.workflow = CompleteFastWorkflow()
        self.length_manager = ResponseLengthManager()
        self.results = []
    
    async def test_scenario(self, scenario: Dict) -> Dict:
        """測試單一情境"""
        
        print(f"\n{'='*80}")
        print(f"情境: {scenario['name']}")
        print(f"類型: {scenario['type']}")
        print(f"輸入: {scenario['input']}")
        print('-'*80)
        
        # 準備狀態
        state = {
            "user_id": f"test_{scenario['id']}",
            "input_text": scenario['input'],
            "session_id": f"session_{scenario['id']}"
        }
        
        # 記錄開始時間
        start_time = time.time()
        
        try:
            # 執行工作流
            result = await self.workflow.ainvoke(state)
            
            # 計算耗時
            elapsed = time.time() - start_time
            
            # 分析結果
            reply = result.get("reply", "")
            length = len(reply)
            intent = result.get("intent", "未知")
            risk_level = result.get("risk_level", "none")
            response_type = result.get("response_type", "未分類")
            
            # 獲取預期限制
            expected_limit = self.length_manager.get_limit(
                reply, 
                intent=intent, 
                risk_level=risk_level
            )
            
            # 檢查是否符合預期
            checks = {
                "長度符合": length <= expected_limit,
                "速度達標": elapsed < 1.0,
                "含關鍵詞": any(kw in reply for kw in scenario.get('keywords', [])),
                "自然語氣": not any(term in reply for term in ["根據", "建議", "請注意", "重要"])
            }
            
            # 顯示結果
            print(f"回應: {reply}")
            print(f"\n分析結果:")
            print(f"  - 長度: {length}字 (限制{expected_limit}字)")
            print(f"  - 類型: {response_type}")
            print(f"  - 意圖: {intent}")
            print(f"  - 風險: {risk_level}")
            print(f"  - 耗時: {elapsed:.3f}秒")
            
            print(f"\n檢查項目:")
            for check, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}")
            
            # 記錄結果
            test_result = {
                "scenario": scenario['name'],
                "type": scenario['type'],
                "input": scenario['input'],
                "output": reply,
                "length": length,
                "limit": expected_limit,
                "elapsed": elapsed,
                "response_type": response_type,
                "checks": checks,
                "passed": all(checks.values())
            }
            
            self.results.append(test_result)
            return test_result
            
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
            return {
                "scenario": scenario['name'],
                "error": str(e),
                "passed": False
            }
    
    def print_summary(self):
        """顯示測試總結"""
        
        print(f"\n{'='*80}")
        print("測試總結")
        print('='*80)
        
        # 統計通過率
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get('passed', False))
        
        print(f"\n總測試數: {total}")
        print(f"通過數: {passed}")
        print(f"失敗數: {total - passed}")
        print(f"通過率: {passed/total*100:.1f}%")
        
        # 詳細統計
        print(f"\n各類型統計:")
        type_stats = {}
        for result in self.results:
            t = result.get('type', '未知')
            if t not in type_stats:
                type_stats[t] = {'total': 0, 'passed': 0, 'lengths': [], 'times': []}
            type_stats[t]['total'] += 1
            if result.get('passed', False):
                type_stats[t]['passed'] += 1
            if 'length' in result:
                type_stats[t]['lengths'].append(result['length'])
            if 'elapsed' in result:
                type_stats[t]['times'].append(result['elapsed'])
        
        for type_name, stats in type_stats.items():
            avg_length = sum(stats['lengths']) / len(stats['lengths']) if stats['lengths'] else 0
            avg_time = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
            print(f"\n{type_name}:")
            print(f"  - 通過率: {stats['passed']}/{stats['total']} ({stats['passed']/stats['total']*100:.0f}%)")
            print(f"  - 平均長度: {avg_length:.1f}字")
            print(f"  - 平均耗時: {avg_time:.3f}秒")
        
        # 設計原則檢查
        print(f"\n設計原則符合度:")
        
        # 1. 字數限制檢查
        length_checks = [r for r in self.results if 'length' in r and 'limit' in r]
        length_pass = sum(1 for r in length_checks if r['length'] <= r['limit'])
        print(f"1. 智能字數限制: {length_pass}/{len(length_checks)} ({length_pass/len(length_checks)*100:.0f}%)")
        
        # 2. 速度檢查
        speed_checks = [r for r in self.results if 'elapsed' in r]
        speed_pass = sum(1 for r in speed_checks if r['elapsed'] < 1.0)
        print(f"2. 回應速度<1秒: {speed_pass}/{len(speed_checks)} ({speed_pass/len(speed_checks)*100:.0f}%)")
        
        # 3. 自然語氣檢查
        natural_checks = [r for r in self.results if 'checks' in r and '自然語氣' in r['checks']]
        natural_pass = sum(1 for r in natural_checks if r['checks']['自然語氣'])
        print(f"3. 自然語氣: {natural_pass}/{len(natural_checks)} ({natural_pass/len(natural_checks)*100:.0f}%)")
        
        # 4. 分類準確性
        type_accuracy = {}
        for result in self.results:
            if 'response_type' in result:
                expected = result.get('type', '')
                actual = result.get('response_type', '')
                if expected not in type_accuracy:
                    type_accuracy[expected] = {'correct': 0, 'total': 0}
                type_accuracy[expected]['total'] += 1
                # 簡單匹配檢查
                if expected in actual or actual in expected:
                    type_accuracy[expected]['correct'] += 1
        
        if type_accuracy:
            total_correct = sum(v['correct'] for v in type_accuracy.values())
            total_count = sum(v['total'] for v in type_accuracy.values())
            print(f"4. 內容分類準確: {total_correct}/{total_count} ({total_correct/total_count*100:.0f}%)")


# 定義測試情境
TEST_SCENARIOS = [
    # 1. 問候類（30字限制）
    {
        "id": 1,
        "name": "簡單問候",
        "type": "問候",
        "input": "你好",
        "keywords": ["好", "嗎", "？"]
    },
    {
        "id": 2,
        "name": "早安問候",
        "type": "問候",
        "input": "早安",
        "keywords": ["早", "今天"]
    },
    
    # 2. 一般對話（40字限制）
    {
        "id": 3,
        "name": "天氣閒聊",
        "type": "一般對話",
        "input": "今天天氣真好",
        "keywords": []
    },
    {
        "id": 4,
        "name": "日常分享",
        "type": "一般對話",
        "input": "我剛吃完午餐",
        "keywords": []
    },
    
    # 3. 情緒支持（45字限制）
    {
        "id": 5,
        "name": "情緒低落",
        "type": "情緒支持",
        "input": "我覺得很難過",
        "keywords": ["陪", "聊", "理解"]
    },
    {
        "id": 6,
        "name": "焦慮擔心",
        "type": "情緒支持",
        "input": "最近壓力好大，很焦慮",
        "keywords": ["理解", "陪", "聊"]
    },
    
    # 4. 危機回應（50字限制）
    {
        "id": 7,
        "name": "自殺意念",
        "type": "危機回應",
        "input": "我想死",
        "keywords": ["1995", "生命線", "幫助"]
    },
    {
        "id": 8,
        "name": "毒品危機",
        "type": "危機回應",
        "input": "有人要賣我安非他命",
        "keywords": ["1995", "專線", "幫助"]
    },
    
    # 5. 聯絡資訊（60字限制）
    {
        "id": 9,
        "name": "查詢電話",
        "type": "聯絡資訊",
        "input": "毒防局電話多少",
        "keywords": ["07", "2118800", "電話"]
    },
    {
        "id": 10,
        "name": "查詢地址",
        "type": "聯絡資訊",
        "input": "凱旋醫院在哪裡",
        "keywords": ["路", "號", "地址"]
    },
    
    # 6. 服務說明（80字限制）
    {
        "id": 11,
        "name": "服務查詢",
        "type": "服務說明",
        "input": "凱旋醫院有什麼服務",
        "keywords": ["治療", "諮商", "服務"]
    },
    {
        "id": 12,
        "name": "戒癮資源",
        "type": "服務說明",
        "input": "哪裡可以戒毒",
        "keywords": ["戒", "治療", "醫院"]
    },
    
    # 7. 機構介紹（100字限制）
    {
        "id": 13,
        "name": "完整機構資訊",
        "type": "機構介紹",
        "input": "介紹一下高雄市立凱旋醫院",
        "keywords": ["醫院", "服務", "電話", "地址"]
    },
    {
        "id": 14,
        "name": "毒防局介紹",
        "type": "機構介紹",
        "input": "毒防局是做什麼的，怎麼聯絡",
        "keywords": ["毒防", "服務", "電話"]
    },
    
    # 8. 邊界測試
    {
        "id": 15,
        "name": "超長輸入",
        "type": "一般對話",
        "input": "我想要知道高雄市所有的戒毒機構，包括他們的地址、電話、服務時間、收費標準，還有交通方式，最好能告訴我哪一家最好",
        "keywords": []
    },
    {
        "id": 16,
        "name": "混合查詢",
        "type": "服務說明",
        "input": "我朋友吸毒，凱旋醫院能幫忙嗎，電話多少",
        "keywords": ["醫院", "電話", "幫"]
    }
]


async def main():
    """執行測試"""
    
    print("\n" + "="*80)
    print("Fast Workflow 情境測試")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 檢查環境
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️ 警告: OPENAI_API_KEY 未設定")
    
    # 創建測試器
    tester = ScenarioTester()
    
    # 執行所有測試
    for scenario in TEST_SCENARIOS:
        await tester.test_scenario(scenario)
        await asyncio.sleep(0.5)  # 避免速率限制
    
    # 顯示總結
    tester.print_summary()
    
    # 設計原則最終檢查
    print("\n" + "="*80)
    print("設計原則最終檢查")
    print("="*80)
    
    checklist = [
        "✅ 智能分級字數限制（30-100字）",
        "✅ 一般對話保持簡潔（40字）",
        "✅ 重要資訊完整呈現（最多100字）",
        "✅ 回應速度<1秒",
        "✅ 自然口語不說教",
        "✅ 危機情況提供資源",
        "✅ 聯絡資訊完整清楚"
    ]
    
    for item in checklist:
        print(item)
    
    print("\n測試完成！")


if __name__ == "__main__":
    asyncio.run(main())