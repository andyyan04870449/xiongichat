#!/usr/bin/env python3
"""測試優化工作流程的效果"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List
import sys
import os

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.langgraph.simple_workflow import create_chat_workflow as create_simple_workflow
from app.langgraph.optimized_workflow import create_optimized_workflow
from app.langgraph.state import WorkflowState
from uuid import uuid4


class WorkflowTester:
    """工作流程測試器"""
    
    def __init__(self):
        self.simple_workflow = create_simple_workflow()
        self.optimized_workflow = create_optimized_workflow()
        self.test_cases = self._prepare_test_cases()
        self.results = []
    
    def _prepare_test_cases(self) -> List[Dict]:
        """準備測試案例"""
        return [
            # 簡單問候（應該走simple flow）
            {
                "name": "簡單問候",
                "input": "你好",
                "memory": [],
                "expected_complexity": "simple"
            },
            
            # 事實查詢（應該走simple或moderate flow）
            {
                "name": "服務查詢",
                "input": "美沙冬服務的地址在哪裡？",
                "memory": [],
                "expected_complexity": "simple"
            },
            
            # 有歷史的延續對話（應該走moderate flow）
            {
                "name": "延續對話",
                "input": "他說的那個地方遠嗎？",
                "memory": [
                    {"role": "user", "content": "我朋友想戒毒"},
                    {"role": "assistant", "content": "戒毒需要勇氣，有專業機構可以幫助。"},
                    {"role": "user", "content": "高雄有哪些地方"},
                    {"role": "assistant", "content": "高雄有毒防局提供協助。"}
                ],
                "expected_complexity": "moderate"
            },
            
            # 情緒累積（應該走complex flow）
            {
                "name": "情緒累積",
                "input": "我真的撐不下去了",
                "memory": [
                    {"role": "user", "content": "最近壓力很大"},
                    {"role": "assistant", "content": "壓力大要照顧自己。"},
                    {"role": "user", "content": "睡不著"},
                    {"role": "assistant", "content": "失眠很辛苦，要不要聊聊？"},
                    {"role": "user", "content": "每天都很痛苦"},
                    {"role": "assistant", "content": "聽起來你過得很辛苦。"}
                ],
                "expected_complexity": "complex"
            },
            
            # 毒品相關（必須走complex flow）
            {
                "name": "毒品相關",
                "input": "我朋友說有個東西可以讓人放鬆",
                "memory": [],
                "expected_complexity": "complex"
            },
            
            # 一般聊天（應該走moderate flow）
            {
                "name": "一般聊天",
                "input": "最近天氣真的很熱",
                "memory": [
                    {"role": "user", "content": "你好"},
                    {"role": "assistant", "content": "你好！有什麼可以幫你的嗎？"}
                ],
                "expected_complexity": "moderate"
            }
        ]
    
    async def test_single_case(self, test_case: Dict, use_optimized: bool) -> Dict:
        """測試單個案例"""
        workflow = self.optimized_workflow if use_optimized else self.simple_workflow
        workflow_name = "優化版" if use_optimized else "原始版"
        
        # 準備狀態
        state = WorkflowState(
            user_id="test_user",
            conversation_id=str(uuid4()),
            input_text=test_case["input"],
            memory=test_case["memory"],
            semantic_analysis=None,
            mentioned_substances=None,
            user_intent=None,
            emotional_state=None,
            drug_info=None,
            risk_level=None,
            response_strategy=None,
            need_knowledge=None,
            intent_category=None,
            retrieved_knowledge=None,
            reply="",
            user_message_id=None,
            assistant_message_id=None,
            error=None,
            timestamp=datetime.utcnow()
        )
        
        # 執行並計時
        start_time = time.time()
        try:
            result_state = await workflow.ainvoke(state)
            processing_time = time.time() - start_time
            
            # 提取結果
            result = {
                "workflow": workflow_name,
                "test_case": test_case["name"],
                "input": test_case["input"],
                "memory_length": len(test_case["memory"]),
                "complexity": result_state.get("complexity", "N/A"),
                "expected_complexity": test_case["expected_complexity"],
                "reply": result_state.get("reply", ""),
                "reply_length": len(result_state.get("reply", "")),
                "processing_time": processing_time,
                "error": result_state.get("error"),
                "routing_info": result_state.get("routing_info", {})
            }
            
            return result
            
        except Exception as e:
            return {
                "workflow": workflow_name,
                "test_case": test_case["name"],
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def run_comparison_tests(self):
        """執行對比測試"""
        print("=" * 80)
        print("工作流程優化效果測試")
        print("=" * 80)
        
        for test_case in self.test_cases:
            print(f"\n測試案例：{test_case['name']}")
            print(f"輸入：{test_case['input']}")
            print(f"記憶長度：{len(test_case['memory'])}")
            print("-" * 40)
            
            # 測試優化版本
            print("執行優化版本...")
            optimized_result = await self.test_single_case(test_case, use_optimized=True)
            
            # 測試原始版本
            print("執行原始版本...")
            original_result = await self.test_single_case(test_case, use_optimized=False)
            
            # 顯示結果
            self._display_comparison(optimized_result, original_result)
            
            # 保存結果
            self.results.append({
                "test_case": test_case["name"],
                "optimized": optimized_result,
                "original": original_result
            })
        
        # 顯示總結
        self._display_summary()
    
    def _display_comparison(self, optimized: Dict, original: Dict):
        """顯示對比結果"""
        print("\n【對比結果】")
        
        # 複雜度判斷
        if "complexity" in optimized:
            print(f"複雜度判斷：{optimized['complexity']} (預期：{optimized['expected_complexity']})")
            if optimized['complexity'] == optimized['expected_complexity']:
                print("✅ 複雜度判斷正確")
            else:
                print("⚠️ 複雜度判斷與預期不符")
        
        # 處理時間對比
        opt_time = optimized.get("processing_time", 0)
        org_time = original.get("processing_time", 0)
        
        print(f"\n處理時間：")
        print(f"  優化版：{opt_time:.2f} 秒")
        print(f"  原始版：{org_time:.2f} 秒")
        
        if org_time > 0:
            improvement = ((org_time - opt_time) / org_time) * 100
            print(f"  改善：{improvement:.1f}%")
        
        # 回應對比
        print(f"\n回應內容：")
        print(f"  優化版（{len(optimized.get('reply', ''))}字）：{optimized.get('reply', '')[:50]}...")
        print(f"  原始版（{len(original.get('reply', ''))}字）：{original.get('reply', '')[:50]}...")
        
        # 錯誤檢查
        if optimized.get("error"):
            print(f"❌ 優化版錯誤：{optimized['error']}")
        if original.get("error"):
            print(f"❌ 原始版錯誤：{original['error']}")
    
    def _display_summary(self):
        """顯示測試總結"""
        print("\n" + "=" * 80)
        print("測試總結")
        print("=" * 80)
        
        # 計算平均時間
        opt_times = [r["optimized"]["processing_time"] for r in self.results 
                    if "processing_time" in r["optimized"]]
        org_times = [r["original"]["processing_time"] for r in self.results 
                    if "processing_time" in r["original"]]
        
        if opt_times and org_times:
            avg_opt = sum(opt_times) / len(opt_times)
            avg_org = sum(org_times) / len(org_times)
            
            print(f"\n平均處理時間：")
            print(f"  優化版：{avg_opt:.2f} 秒")
            print(f"  原始版：{avg_org:.2f} 秒")
            print(f"  平均改善：{((avg_org - avg_opt) / avg_org * 100):.1f}%")
        
        # 複雜度分布
        complexity_dist = {}
        for r in self.results:
            complexity = r["optimized"].get("complexity", "unknown")
            complexity_dist[complexity] = complexity_dist.get(complexity, 0) + 1
        
        print(f"\n複雜度分布：")
        for comp, count in complexity_dist.items():
            percentage = (count / len(self.results)) * 100
            print(f"  {comp}: {count} ({percentage:.1f}%)")
        
        # 保存詳細結果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"test_results_{timestamp}.json"
        
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n詳細結果已保存到：{result_file}")


async def main():
    """主函數"""
    print("開始測試優化工作流程...")
    print("注意：需要配置 OPENAI_API_KEY 環境變數")
    
    # 檢查環境變數
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 錯誤：未設置 OPENAI_API_KEY 環境變數")
        return
    
    tester = WorkflowTester()
    await tester.run_comparison_tests()


if __name__ == "__main__":
    asyncio.run(main())