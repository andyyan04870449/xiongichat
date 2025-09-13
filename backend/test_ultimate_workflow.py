"""測試極簡工作流 - 3步驟架構，智能集中"""

import asyncio
import time
import sys
import os
sys.path.insert(0, '/Users/yangandy/KaohsiungCare/backend')

from app.services.chat import ChatService
from app.schemas.chat import ChatRequest
from datetime import datetime


async def test_all_scenarios():
    """測試所有場景"""
    
    print("\n" + "="*80)
    print("極簡工作流 (UltimateWorkflow) 測試")
    print("="*80)
    
    # 確保使用UltimateWorkflow
    os.environ["USE_ULTIMATE_WORKFLOW"] = "true"
    os.environ["USE_FAST_WORKFLOW"] = "false"
    os.environ["USE_OPTIMIZED_WORKFLOW"] = "false"
    
    # 初始化服務
    chat_service = ChatService()
    
    # 測試案例涵蓋所有場景
    test_cases = [
        # (場景名稱, 輸入文本, 預期處理)
        ("🚨 危機情境 - 直接", "我想死了", "危機介入+1995資源"),
        ("🚨 危機情境 - 委婉", "活不下去了，沒有希望", "危機介入+資源"),
        ("💊 戒毒求助", "有哪些地方可以戒毒", "RAG檢索+機構資訊"),
        ("📍 資訊查詢", "毒防局的電話是什麼", "RAG檢索+聯絡資訊"),
        ("😔 情緒支持", "我很難過，心情很差", "情緒陪伴"),
        ("👋 日常問候 - 早上", "早安", "時段問候"),
        ("👋 日常問候 - 晚上", "晚安", "時段問候"),
        ("💬 一般對話", "今天天氣真好", "簡短回應"),
        ("🔄 混合需求", "我想死了，哪裡可以求助", "危機+資源"),
        ("❓ 不明確", "嗯嗯", "澄清詢問"),
    ]
    
    results = []
    total_time = 0
    
    for scenario, text, expected in test_cases:
        print(f"\n測試: {scenario}")
        print(f"輸入: {text}")
        print(f"預期: {expected}")
        
        # 準備請求
        request = ChatRequest(
            user_id=f"test_{scenario}",
            message=text
        )
        
        # 計時
        start = time.time()
        
        try:
            # 執行請求
            response = await chat_service.process_message(request)
            elapsed = time.time() - start
            total_time += elapsed
            
            # 顯示結果
            print(f"回應: {response.reply}")
            print(f"長度: {len(response.reply)}字")
            print(f"耗時: {elapsed:.2f}秒")
            
            # 評估結果
            success_indicators = []
            
            # 檢查危機處理
            if "危機" in expected and "1995" in response.reply:
                success_indicators.append("✅ 提供危機資源")
            
            # 檢查資訊提供
            if "機構" in expected or "聯絡" in expected:
                if any(kw in response.reply for kw in ["電話", "地址", "07-", "0800", "醫院", "中心"]):
                    success_indicators.append("✅ 提供具體資訊")
            
            # 檢查字數限制
            if len(response.reply) <= 100:
                success_indicators.append("✅ 符合字數限制")
            
            # 檢查回應速度
            if elapsed < 2.0:
                success_indicators.append("✅ 快速回應")
            
            if success_indicators:
                print("評估: " + " | ".join(success_indicators))
            
            results.append({
                "scenario": scenario,
                "time": elapsed,
                "length": len(response.reply),
                "success": len(success_indicators) >= 2
            })
            
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
            results.append({
                "scenario": scenario,
                "error": str(e)
            })
    
    # 統計結果
    print("\n" + "="*80)
    print("測試統計")
    print("="*80)
    
    successful = [r for r in results if "error" not in r]
    if successful:
        avg_time = sum(r["time"] for r in successful) / len(successful)
        avg_length = sum(r["length"] for r in successful) / len(successful)
        success_rate = sum(1 for r in successful if r.get("success", False)) / len(successful) * 100
        
        print(f"成功率: {success_rate:.1f}%")
        print(f"平均耗時: {avg_time:.2f}秒")
        print(f"平均長度: {avg_length:.1f}字")
        
        # 檢查是否達成目標
        print("\n目標達成度：")
        print(f"{'✅' if avg_time < 2.0 else '❌'} 回應速度 < 2秒 (實際: {avg_time:.2f}秒)")
        print(f"{'✅' if avg_length <= 50 else '⚠️'} 平均長度 ≤ 50字 (實際: {avg_length:.1f}字)")
        print(f"{'✅' if success_rate >= 80 else '❌'} 成功率 ≥ 80% (實際: {success_rate:.1f}%)")


async def test_conversation_flow():
    """測試對話連貫性"""
    
    print("\n" + "="*80)
    print("對話連貫性測試")
    print("="*80)
    
    chat_service = ChatService()
    
    # 模擬連續對話
    conversation = [
        "你好",
        "我最近壓力很大",
        "有時候會想用藥物逃避",
        "哪裡可以找到幫助",
        "謝謝你"
    ]
    
    user_id = "conversation_test"
    conversation_id = None
    
    for idx, message in enumerate(conversation, 1):
        print(f"\n第{idx}輪對話")
        print(f"用戶: {message}")
        
        request = ChatRequest(
            user_id=user_id,
            message=message,
            conversation_id=conversation_id
        )
        
        start = time.time()
        response = await chat_service.process_message(request)
        elapsed = time.time() - start
        
        print(f"助理: {response.reply}")
        print(f"耗時: {elapsed:.2f}秒")
        
        # 保存conversation_id供下一輪使用
        if response.conversation_id:
            conversation_id = response.conversation_id


async def compare_workflows():
    """比較不同工作流的表現"""
    
    print("\n" + "="*80)
    print("工作流比較")
    print("="*80)
    
    test_message = "我想死了，有沒有人可以幫我"
    
    workflows = [
        ("UltimateWorkflow", {"USE_ULTIMATE_WORKFLOW": "true", "USE_FAST_WORKFLOW": "false"}),
        ("FastWorkflow", {"USE_ULTIMATE_WORKFLOW": "false", "USE_FAST_WORKFLOW": "true"}),
    ]
    
    for name, env_vars in workflows:
        print(f"\n測試 {name}:")
        
        # 設置環境變數
        for key, value in env_vars.items():
            os.environ[key] = value
        
        # 重新初始化服務
        chat_service = ChatService()
        
        request = ChatRequest(
            user_id="compare_test",
            message=test_message
        )
        
        start = time.time()
        response = await chat_service.process_message(request)
        elapsed = time.time() - start
        
        print(f"  回應: {response.reply}")
        print(f"  長度: {len(response.reply)}字")
        print(f"  耗時: {elapsed:.2f}秒")
        
        # 評估
        has_crisis_resource = "1995" in response.reply or "專線" in response.reply
        within_limit = len(response.reply) <= 50
        fast_enough = elapsed < 2.0
        
        print(f"  評估: {'✅' if has_crisis_resource else '❌'} 危機資源 | "
              f"{'✅' if within_limit else '❌'} 字數限制 | "
              f"{'✅' if fast_enough else '❌'} 速度")


async def main():
    """執行所有測試"""
    
    print("\n" + "="*80)
    print("UltimateWorkflow 完整測試")
    print("架構: IntentAnalyzer → SmartRAG → MasterLLM")
    print("特色: 智能集中在最終LLM，完整提示詞控制")
    print("="*80)
    
    # 測試1: 全場景測試
    await test_all_scenarios()
    
    # 測試2: 對話連貫性
    await test_conversation_flow()
    
    # 測試3: 工作流比較
    await compare_workflows()
    
    print("\n" + "="*80)
    print("測試完成！")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())