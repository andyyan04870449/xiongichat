"""诊断意图分析JSON错误的简单测试"""

import asyncio
import logging
from app.langgraph.ultimate_workflow import IntentAnalyzer

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_intent_analysis():
    """测试意图分析器"""
    
    analyzer = IntentAnalyzer()
    
    # 测试简单输入
    test_inputs = [
        "你好",
        "我叫阿明，今年35歲",
        "我想戒毒",
        "我很難過"
    ]
    
    for i, text in enumerate(test_inputs, 1):
        print(f"\n=== 測試 {i}: {text} ===")
        
        try:
            result = await analyzer.analyze(text, None)
            print(f"✅ 成功: {result}")
        except Exception as e:
            print(f"❌ 失敗: {str(e)}")
            print(f"異常類型: {type(e).__name__}")
            import traceback
            print(f"詳細錯誤:\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_intent_analysis())