"""效能對比測試 - 分析不同複雜度的處理時間"""

import asyncio
import httpx
import json
import statistics
from datetime import datetime
from typing import List, Dict


async def run_performance_test():
    """執行效能測試"""
    
    base_url = "http://localhost:8000"
    
    # 不同複雜度的測試案例
    test_scenarios = {
        "simple": [
            {"message": "你好", "expected_time": 3.5},
            {"message": "你是誰", "expected_time": 5.0},
            {"message": "早安", "expected_time": 3.5},
        ],
        "moderate": [
            {"message": "最近壓力好大", "expected_time": 7.0},
            {"message": "我心情不好", "expected_time": 7.0},
            {"message": "睡不著", "expected_time": 7.0},
        ],
        "complex": [
            {"message": "毒防局在哪裡", "expected_time": 15.0},
            {"message": "戒毒有什麼方法", "expected_time": 15.0},
            {"message": "K他命是什麼", "expected_time": 15.0},
        ]
    }
    
    print("="*60)
    print("效能對比測試")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        results = {}
        
        for complexity, scenarios in test_scenarios.items():
            print(f"\n測試 {complexity.upper()} 複雜度場景")
            print("-"*40)
            
            times = []
            for scenario in scenarios:
                print(f"輸入: {scenario['message']}")
                
                # 執行3次取平均
                scenario_times = []
                for i in range(3):
                    import time
                    start = time.time()
                    
                    try:
                        response = await client.post(
                            f"{base_url}/api/v1/chat/",
                            json={
                                "user_id": f"perf_test_{complexity}",
                                "message": scenario['message']
                            }
                        )
                        
                        elapsed = time.time() - start
                        scenario_times.append(elapsed)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if i == 0:  # 只顯示第一次的回應
                                print(f"  回應: {data['reply'][:50]}...")
                        
                    except Exception as e:
                        print(f"  錯誤: {str(e)}")
                        scenario_times.append(30.0)  # 錯誤時的懲罰時間
                    
                    await asyncio.sleep(1)  # 避免過快請求
                
                avg_time = statistics.mean(scenario_times)
                times.append(avg_time)
                
                # 判斷是否符合預期
                status = "✅" if avg_time <= scenario['expected_time'] else "⚠️"
                print(f"  平均時間: {avg_time:.2f}s (預期: <{scenario['expected_time']}s) {status}")
            
            results[complexity] = {
                "times": times,
                "avg": statistics.mean(times),
                "min": min(times),
                "max": max(times),
                "std": statistics.stdev(times) if len(times) > 1 else 0
            }
    
    # 顯示總結
    print("\n" + "="*60)
    print("效能測試總結")
    print("="*60)
    
    for complexity, stats in results.items():
        print(f"\n{complexity.upper()} 複雜度:")
        print(f"  平均回應時間: {stats['avg']:.2f}s")
        print(f"  最快: {stats['min']:.2f}s")
        print(f"  最慢: {stats['max']:.2f}s")
        print(f"  標準差: {stats['std']:.2f}s")
    
    # 檢查是否符合重構目標
    print("\n" + "="*60)
    print("重構目標達成度")
    print("="*60)
    
    targets = {
        "simple": 3.5,   # 目標: <3.5秒
        "moderate": 7.0,  # 目標: <7秒  
        "complex": 15.0   # 目標: <15秒
    }
    
    for complexity, target in targets.items():
        actual = results[complexity]["avg"]
        if actual <= target:
            print(f"✅ {complexity}: {actual:.2f}s <= {target}s (達成)")
        else:
            print(f"❌ {complexity}: {actual:.2f}s > {target}s (未達成)")
    
    # 保存結果
    with open(f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


async def analyze_log_patterns():
    """分析日誌中的處理模式"""
    
    print("\n" + "="*60)
    print("日誌分析")
    print("="*60)
    
    log_file = "/Users/yangandy/KaohsiungCare/backend/logs/ai_analysis/ai_analysis_20250906.log"
    
    # 讀取最近的日誌
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()[-200:]  # 最近200行
    
    # 分析路由決策
    routing_decisions = {"simple": 0, "moderate": 0, "complex": 0}
    processing_times = []
    
    for line in lines:
        if "Routing Decision:" in line:
            if "simple" in line:
                routing_decisions["simple"] += 1
            elif "moderate" in line:
                routing_decisions["moderate"] += 1
            elif "complex" in line:
                routing_decisions["complex"] += 1
        
        if "處理時間:" in line:
            try:
                time_str = line.split("處理時間:")[1].split("秒")[0].strip()
                processing_times.append(float(time_str))
            except:
                pass
    
    print("\n路由決策分布:")
    total = sum(routing_decisions.values())
    if total > 0:
        for complexity, count in routing_decisions.items():
            percentage = (count / total) * 100
            print(f"  {complexity}: {count} ({percentage:.1f}%)")
    
    if processing_times:
        print("\n處理時間統計:")
        print(f"  平均: {statistics.mean(processing_times):.2f}秒")
        print(f"  中位數: {statistics.median(processing_times):.2f}秒")
        print(f"  最快: {min(processing_times):.2f}秒")
        print(f"  最慢: {max(processing_times):.2f}秒")


if __name__ == "__main__":
    # 執行效能測試
    asyncio.run(run_performance_test())
    
    # 分析日誌
    asyncio.run(analyze_log_patterns())