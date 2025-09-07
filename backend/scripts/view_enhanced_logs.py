"""查看增強日誌的腳本"""

import json
import sys
from datetime import datetime
from pathlib import Path


def analyze_log_file(log_file):
    """分析日誌檔案並顯示統計"""
    
    print(f"\n📊 分析日誌檔案: {log_file.name}")
    print("="*60)
    
    # 統計各階段出現次數和平均耗時
    stage_stats = {}
    workflow_times = []
    routing_stats = {"simple": 0, "moderate": 0, "complex": 0}
    crisis_levels = {"none": 0, "low": 0, "medium": 0, "high": 0}
    
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            if '階段耗時:' in line:
                # 找到一個完整的工作流程
                continue
                
            if '路由決策' in line and 'ms]' in line:
                # 提取路由決策
                if 'simple' in line:
                    routing_stats['simple'] += 1
                elif 'moderate' in line:
                    routing_stats['moderate'] += 1
                elif 'complex' in line:
                    routing_stats['complex'] += 1
                    
            if '危機評估' in line or '危機等級' in line:
                # 提取危機等級
                for level in crisis_levels.keys():
                    if level in line:
                        crisis_levels[level] += 1
                        break
                        
            if '總處理時間:' in line:
                # 提取總處理時間
                try:
                    time_str = line.split('總處理時間:')[1].split('秒')[0].strip()
                    workflow_times.append(float(time_str))
                except:
                    pass
    
    # 顯示統計結果
    print("\n🔀 路由決策分布:")
    total_routes = sum(routing_stats.values())
    for route, count in routing_stats.items():
        percentage = (count/total_routes*100) if total_routes > 0 else 0
        print(f"  {route}: {count} ({percentage:.1f}%)")
    
    print("\n🚨 危機等級分布:")
    total_crisis = sum(crisis_levels.values())
    for level, count in crisis_levels.items():
        percentage = (count/total_crisis*100) if total_crisis > 0 else 0
        icon = {"none": "✅", "low": "🟡", "medium": "🟠", "high": "🔴"}.get(level, "❓")
        print(f"  {icon} {level}: {count} ({percentage:.1f}%)")
    
    print("\n⏱️ 處理時間統計:")
    if workflow_times:
        print(f"  平均: {sum(workflow_times)/len(workflow_times):.2f}秒")
        print(f"  最快: {min(workflow_times):.2f}秒")
        print(f"  最慢: {max(workflow_times):.2f}秒")
        print(f"  總計: {len(workflow_times)} 個請求")


def show_recent_entries(log_file, n=5):
    """顯示最近的日誌條目"""
    
    print(f"\n📝 最近 {n} 個請求摘要:")
    print("="*60)
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找出請求開始的位置
    request_starts = []
    for i, line in enumerate(lines):
        if '🚀 新對話請求' in line:
            request_starts.append(i)
    
    # 顯示最近的請求
    for req_idx in request_starts[-n:]:
        if req_idx < len(lines):
            # 提取請求資訊
            print("\n" + lines[req_idx-1].strip())  # 分隔線
            for i in range(req_idx, min(req_idx + 50, len(lines))):
                line = lines[i]
                if '用戶:' in line or '訊息:' in line:
                    print(line.strip())
                elif '路由決策' in line:
                    print(line.strip())
                elif '危機' in line and '等級' in line:
                    print(line.strip())
                elif '最終回應' in line:
                    print(line.strip())
                    # 顯示回應內容（限制長度）
                    if i+1 < len(lines):
                        response = lines[i+1].strip()
                        if len(response) > 100:
                            response = response[:100] + "..."
                        print(f"  回應: {response}")
                elif '總處理時間' in line:
                    print(line.strip())
                    break


def analyze_jsonl_file(jsonl_file):
    """分析 JSONL 格式的詳細日誌"""
    
    print(f"\n📈 詳細數據分析: {jsonl_file.name}")
    print("="*60)
    
    stage_timings = {}
    llm_calls = 0
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                stage = data.get('stage', '')
                
                # 統計階段耗時
                if 'stage_time_ms' in data:
                    if stage not in stage_timings:
                        stage_timings[stage] = []
                    stage_timings[stage].append(data['stage_time_ms'])
                
                # 統計 LLM 調用
                if stage in ['ROUTING_DECISION', 'COMBINED_ANALYSIS', 'CONTEXT_UNDERSTANDING', 
                           'SEMANTIC_ANALYSIS', 'INTENT_ROUTING', 'RESPONSE_GENERATION']:
                    llm_calls += 1
                    
            except json.JSONDecodeError:
                continue
    
    print("\n⚙️ 各階段平均耗時:")
    for stage, times in sorted(stage_timings.items()):
        if times:
            avg_time = sum(times) / len(times)
            print(f"  {stage}: {avg_time:.0f}ms (n={len(times)})")
    
    print(f"\n🤖 LLM 調用次數: {llm_calls}")


def main():
    """主函數"""
    
    # 取得今天的日誌檔案
    log_dir = Path("logs/ai_analysis")
    today = datetime.now().strftime("%Y%m%d")
    
    log_file = log_dir / f"ai_analysis_{today}.log"
    jsonl_file = log_dir / f"ai_analysis_{today}.jsonl"
    
    if log_file.exists():
        analyze_log_file(log_file)
        show_recent_entries(log_file, n=3)
    else:
        print(f"❌ 找不到日誌檔案: {log_file}")
    
    if jsonl_file.exists():
        analyze_jsonl_file(jsonl_file)
    else:
        print(f"❌ 找不到 JSONL 檔案: {jsonl_file}")


if __name__ == "__main__":
    main()