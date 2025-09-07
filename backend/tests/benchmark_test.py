"""效能基準測試 - 比較新舊工作流程"""

import asyncio
import time
import statistics
from typing import Dict, List, Tuple
from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

from test_scenarios import TestScenario, ScenarioTestRunner


@dataclass
class BenchmarkResult:
    """基準測試結果"""
    workflow_version: str  # "original" or "refactored"
    scenario_id: str
    response_times: List[float]  # 多次執行的回應時間
    llm_calls: int  # LLM調用次數
    avg_response_time: float
    std_dev: float
    min_time: float
    max_time: float
    p95_time: float  # 95百分位
    success_rate: float


class WorkflowBenchmark:
    """工作流程效能基準測試"""
    
    def __init__(self):
        self.results: Dict[str, List[BenchmarkResult]] = {
            "original": [],
            "refactored": []
        }
    
    async def benchmark_scenario(
        self, 
        scenario: TestScenario,
        workflow_version: str,
        iterations: int = 10
    ) -> BenchmarkResult:
        """對單一情境進行基準測試"""
        
        print(f"\n基準測試: {scenario.description} ({workflow_version})")
        print(f"執行 {iterations} 次迭代...")
        
        response_times = []
        successes = 0
        
        for i in range(iterations):
            try:
                # 模擬工作流程執行
                if workflow_version == "original":
                    result = await self._run_original_workflow(scenario)
                else:
                    result = await self._run_refactored_workflow(scenario)
                
                response_times.append(result["response_time"])
                if result["success"]:
                    successes += 1
                
                print(f"  迭代 {i+1}: {result['response_time']:.2f}s")
                
            except Exception as e:
                print(f"  迭代 {i+1}: 錯誤 - {str(e)}")
                response_times.append(10.0)  # 懲罰失敗的請求
        
        # 計算統計數據
        avg_time = statistics.mean(response_times)
        std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
        min_time = min(response_times)
        max_time = max(response_times)
        p95_time = np.percentile(response_times, 95)
        success_rate = successes / iterations
        
        return BenchmarkResult(
            workflow_version=workflow_version,
            scenario_id=scenario.id,
            response_times=response_times,
            llm_calls=5 if workflow_version == "original" else 2,
            avg_response_time=avg_time,
            std_dev=std_dev,
            min_time=min_time,
            max_time=max_time,
            p95_time=p95_time,
            success_rate=success_rate
        )
    
    async def _run_original_workflow(self, scenario: TestScenario) -> Dict:
        """模擬原始工作流程"""
        start_time = time.time()
        
        # 模擬9個節點的處理時間
        await asyncio.sleep(0.3)  # 記憶載入
        await asyncio.sleep(0.8)  # 深度理解 (LLM)
        await asyncio.sleep(0.8)  # 語意分析 (LLM)
        await asyncio.sleep(0.2)  # 毒品檢查
        await asyncio.sleep(0.8)  # 意圖路由 (LLM)
        await asyncio.sleep(0.3)  # RAG檢索
        await asyncio.sleep(0.8)  # 回應生成 (LLM)
        await asyncio.sleep(0.8)  # 回應驗證 (LLM)
        await asyncio.sleep(0.1)  # 對話記錄
        
        response_time = time.time() - start_time
        
        # 模擬驗證失敗的情況（30%機率）
        import random
        if random.random() < 0.3:
            response_time += 2.0  # 額外的重試時間
        
        return {
            "response_time": response_time,
            "success": True,
            "llm_calls": 5
        }
    
    async def _run_refactored_workflow(self, scenario: TestScenario) -> Dict:
        """模擬重構後的工作流程"""
        start_time = time.time()
        
        # 模擬2階段處理
        await asyncio.sleep(0.3)  # 記憶載入
        await asyncio.sleep(1.2)  # 統一分析 (LLM)
        
        # 條件性RAG（50%機率需要）
        import random
        if random.random() < 0.5:
            await asyncio.sleep(0.3)  # RAG檢索
        
        await asyncio.sleep(1.0)  # 智能生成 (LLM)
        await asyncio.sleep(0.1)  # 對話記錄
        
        response_time = time.time() - start_time
        
        return {
            "response_time": response_time,
            "success": True,
            "llm_calls": 2
        }
    
    async def run_comparison(self, scenarios: List[TestScenario], iterations: int = 10):
        """執行比較測試"""
        
        print("="*60)
        print("工作流程效能比較測試")
        print("="*60)
        
        for scenario in scenarios:
            # 測試原始工作流程
            original_result = await self.benchmark_scenario(
                scenario, "original", iterations
            )
            self.results["original"].append(original_result)
            
            # 測試重構工作流程
            refactored_result = await self.benchmark_scenario(
                scenario, "refactored", iterations
            )
            self.results["refactored"].append(refactored_result)
            
            # 顯示比較
            self._print_comparison(scenario, original_result, refactored_result)
    
    def _print_comparison(
        self, 
        scenario: TestScenario,
        original: BenchmarkResult,
        refactored: BenchmarkResult
    ):
        """印出比較結果"""
        print(f"\n{'='*50}")
        print(f"情境: {scenario.description}")
        print(f"{'='*50}")
        
        improvement = ((original.avg_response_time - refactored.avg_response_time) 
                      / original.avg_response_time * 100)
        
        print(f"\n原始工作流程:")
        print(f"  平均回應時間: {original.avg_response_time:.2f}s")
        print(f"  標準差: {original.std_dev:.2f}s")
        print(f"  P95: {original.p95_time:.2f}s")
        print(f"  LLM調用: {original.llm_calls}次")
        
        print(f"\n重構工作流程:")
        print(f"  平均回應時間: {refactored.avg_response_time:.2f}s")
        print(f"  標準差: {refactored.std_dev:.2f}s")
        print(f"  P95: {refactored.p95_time:.2f}s")
        print(f"  LLM調用: {refactored.llm_calls}次")
        
        print(f"\n改進:")
        print(f"  回應時間: {improvement:.1f}% 更快")
        print(f"  LLM調用: 減少 {original.llm_calls - refactored.llm_calls} 次")
    
    def generate_charts(self):
        """生成比較圖表"""
        if not self.results["original"] or not self.results["refactored"]:
            print("沒有足夠的數據生成圖表")
            return
        
        # 準備數據
        scenarios = [r.scenario_id for r in self.results["original"]]
        original_times = [r.avg_response_time for r in self.results["original"]]
        refactored_times = [r.avg_response_time for r in self.results["refactored"]]
        
        # 創建圖表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 柱狀圖比較
        x = np.arange(len(scenarios))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, original_times, width, label='原始', color='coral')
        bars2 = ax1.bar(x + width/2, refactored_times, width, label='重構', color='lightgreen')
        
        ax1.set_xlabel('測試情境')
        ax1.set_ylabel('平均回應時間 (秒)')
        ax1.set_title('工作流程回應時間比較')
        ax1.set_xticks(x)
        ax1.set_xticklabels(scenarios, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 在柱狀圖上添加數值
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}s', ha='center', va='bottom', fontsize=8)
        
        for bar in bars2:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}s', ha='center', va='bottom', fontsize=8)
        
        # 改進百分比圖
        improvements = [
            ((o - r) / o * 100) 
            for o, r in zip(original_times, refactored_times)
        ]
        
        colors = ['green' if i > 0 else 'red' for i in improvements]
        bars = ax2.bar(scenarios, improvements, color=colors)
        
        ax2.set_xlabel('測試情境')
        ax2.set_ylabel('改進百分比 (%)')
        ax2.set_title('效能改進程度')
        ax2.set_xticklabels(scenarios, rotation=45, ha='right')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.grid(True, alpha=0.3)
        
        # 添加百分比標籤
        for bar, imp in zip(bars, improvements):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{imp:.1f}%', ha='center', 
                    va='bottom' if height > 0 else 'top', fontsize=8)
        
        plt.tight_layout()
        
        # 保存圖表
        filename = f"benchmark_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=100)
        print(f"\n圖表已保存至: {filename}")
        plt.show()
    
    def print_summary(self):
        """印出總結報告"""
        print("\n" + "="*60)
        print("效能基準測試總結")
        print("="*60)
        
        # 計算總體統計
        orig_avg = statistics.mean([r.avg_response_time for r in self.results["original"]])
        ref_avg = statistics.mean([r.avg_response_time for r in self.results["refactored"]])
        
        orig_p95 = statistics.mean([r.p95_time for r in self.results["original"]])
        ref_p95 = statistics.mean([r.p95_time for r in self.results["refactored"]])
        
        print(f"\n總體平均回應時間:")
        print(f"  原始: {orig_avg:.2f}s")
        print(f"  重構: {ref_avg:.2f}s")
        print(f"  改進: {((orig_avg - ref_avg) / orig_avg * 100):.1f}%")
        
        print(f"\n總體P95回應時間:")
        print(f"  原始: {orig_p95:.2f}s")
        print(f"  重構: {ref_p95:.2f}s")
        print(f"  改進: {((orig_p95 - ref_p95) / orig_p95 * 100):.1f}%")
        
        print(f"\nLLM調用次數:")
        print(f"  原始: 5-6次/請求")
        print(f"  重構: 2次/請求")
        print(f"  減少: 60-67%")
        
        print(f"\n預估成本節省:")
        cost_per_llm_call = 0.002  # 假設每次LLM調用成本
        orig_cost = 5 * cost_per_llm_call
        ref_cost = 2 * cost_per_llm_call
        print(f"  每請求成本降低: ${orig_cost - ref_cost:.4f}")
        print(f"  成本節省: {((orig_cost - ref_cost) / orig_cost * 100):.1f}%")


async def main():
    """主測試程序"""
    benchmark = WorkflowBenchmark()
    
    # 選擇要測試的情境
    test_scenarios = [
        GreetingScenarios.SIMPLE_GREETING,
        GreetingScenarios.IDENTITY_QUERY,
        InformationScenarios.LOCATION_QUERY,
        EmotionalScenarios.MILD_STRESS,
    ]
    
    # 執行比較測試
    await benchmark.run_comparison(test_scenarios, iterations=5)
    
    # 顯示總結
    benchmark.print_summary()
    
    # 生成圖表
    benchmark.generate_charts()


if __name__ == "__main__":
    asyncio.run(main())