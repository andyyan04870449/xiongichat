#!/usr/bin/env python3
"""
測試 OpenAI API 連接
"""
import os
import sys
from pathlib import Path

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import asyncio

# 載入環境變數
load_dotenv()

async def test_openai():
    """測試 OpenAI API"""
    
    # 檢查環境變數
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"1. API Key 設定: {'✅ 已設定' if api_key else '❌ 未設定'}")
    if api_key:
        print(f"   Key 前綴: {api_key[:20]}...")
    
    # 測試 OpenAI 連接
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=api_key)
        
        # 測試 Chat API
        print("\n2. 測試 Chat API...")
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "回覆OK"}],
            max_tokens=10
        )
        
        if response.choices:
            print(f"   ✅ Chat API 正常: {response.choices[0].message.content}")
        
        # 測試 Embeddings API
        print("\n3. 測試 Embeddings API...")
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input="測試文本"
        )
        
        if response.data:
            print(f"   ✅ Embeddings API 正常: 維度 {len(response.data[0].embedding)}")
        
        print("\n✅ OpenAI API 連接正常！")
        return True
        
    except Exception as e:
        print(f"\n❌ OpenAI API 錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_openai())