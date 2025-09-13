"""測試 FastWorkflow 整合到主系統"""

import asyncio
import time
import json
import sys
import os
sys.path.insert(0, '/Users/yangandy/KaohsiungCare/backend')

from app.services.chat import ChatService
from app.schemas.chat import ChatRequest


async def test_performance():
    """測試效能提升"""
    
    print("\n" + "="*80)
    print("測試 FastWorkflow 效能")
    print("="*80)
    
    # 初始化服務
    chat_service = ChatService()
    
    # 測試案例
    test_cases = [
        ("簡單問候", "你好"),
        ("一般對話", "今天天氣真好"),
        ("危機情況", "我想死了"),
        ("查詢資訊", "毒防局的電話是什麼"),
        ("複雜查詢", "有哪些地方提供戒毒服務"),
    ]
    
    total_time = 0
    results = []
    
    for name, message in test_cases:
        print(f"\n測試: {name}")
        print(f"輸入: {message}")
        
        # 準備請求
        request = ChatRequest(
            user_id=f"test_user_{name}",
            message=message
        )
        
        # 計時
        start = time.time()
        
        try:
            # 執行請求
            response = await chat_service.process_message(request)
            
            # 計算耗時
            elapsed = time.time() - start
            total_time += elapsed
            
            print(f"回應: {response.reply}")
            print(f"耗時: {elapsed:.2f}秒")
            
            # 檢查效能
            if elapsed < 1.0:
                print("✅ 符合 <1秒 目標")
            elif elapsed < 2.0:
                print("⚠️ 略慢 (1-2秒)")
            else:
                print(f"❌ 太慢 ({elapsed:.1f}秒)")
            
            results.append({
                "name": name,
                "time": elapsed,
                "response_length": len(response.reply)
            })
            
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
            results.append({
                "name": name,
                "error": str(e)
            })
    
    # 統計
    print("\n" + "="*80)
    print("效能統計")
    print("="*80)
    
    successful = [r for r in results if "error" not in r]
    if successful:
        avg_time = sum(r["time"] for r in successful) / len(successful)
        max_time = max(r["time"] for r in successful)
        min_time = min(r["time"] for r in successful)
        
        print(f"平均耗時: {avg_time:.2f}秒")
        print(f"最快: {min_time:.2f}秒")
        print(f"最慢: {max_time:.2f}秒")
        
        # 檢查是否達標
        if avg_time < 1.0:
            print("🎉 達成目標！平均 <1秒")
        else:
            print(f"⚠️ 未達標，需要進一步優化 (目標<1秒，實際{avg_time:.2f}秒)")
    
    return results


async def compare_workflows():
    """比較新舊工作流效能"""
    
    print("\n" + "="*80)
    print("比較工作流效能")
    print("="*80)
    
    test_message = "有哪些地方提供戒毒服務"
    
    # 測試 FastWorkflow
    print("\n1. FastWorkflow (USE_FAST_WORKFLOW=true):")
    os.environ["USE_FAST_WORKFLOW"] = "true"
    os.environ["USE_OPTIMIZED_WORKFLOW"] = "false"
    
    chat_service = ChatService()
    request = ChatRequest(user_id="compare_test", message=test_message)
    
    start = time.time()
    response = await chat_service.process_message(request)
    fast_time = time.time() - start
    
    print(f"   耗時: {fast_time:.2f}秒")
    print(f"   回應長度: {len(response.reply)}字")
    
    # 測試 OptimizedWorkflow
    print("\n2. OptimizedWorkflow (USE_OPTIMIZED_WORKFLOW=true):")
    os.environ["USE_FAST_WORKFLOW"] = "false"
    os.environ["USE_OPTIMIZED_WORKFLOW"] = "true"
    
    # 重新初始化以使用新設定
    chat_service = ChatService()
    
    start = time.time()
    response = await chat_service.process_message(request)
    optimized_time = time.time() - start
    
    print(f"   耗時: {optimized_time:.2f}秒")
    print(f"   回應長度: {len(response.reply)}字")
    
    # 比較結果
    print("\n" + "="*80)
    print("效能提升")
    print("="*80)
    
    if fast_time < optimized_time:
        improvement = (optimized_time - fast_time) / optimized_time * 100
        speedup = optimized_time / fast_time
        print(f"✅ FastWorkflow 快 {improvement:.1f}%")
        print(f"   速度提升: {speedup:.1f}x")
        print(f"   節省時間: {optimized_time - fast_time:.2f}秒")
    else:
        print("⚠️ FastWorkflow 沒有更快，需要檢查")
    
    # 恢復預設設定
    os.environ["USE_FAST_WORKFLOW"] = "true"
    os.environ["USE_OPTIMIZED_WORKFLOW"] = "false"


async def main():
    """執行所有測試"""
    
    print("\n" + "="*80)
    print("FastWorkflow 整合測試")
    print("="*80)
    
    # 確保使用 FastWorkflow
    os.environ["USE_FAST_WORKFLOW"] = "true"
    os.environ["USE_OPTIMIZED_WORKFLOW"] = "false"
    
    # 測試1: 效能測試
    await test_performance()
    
    # 測試2: 比較測試（選擇性）
    # await compare_workflows()
    
    print("\n測試完成！")


if __name__ == "__main__":
    asyncio.run(main())