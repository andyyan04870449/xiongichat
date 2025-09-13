#!/usr/bin/env python3
"""
RAG系統快速測試 - 測試前3個案例
"""

import asyncio
import json
from datetime import datetime
import httpx

# API設定
API_BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_BASE_URL}/api/v1/chat/"

async def test_rag():
    """快速測試RAG系統"""
    session_id = f"quick_test_{datetime.now().strftime('%H%M%S')}"
    
    # 測試案例
    test_cases = [
        {
            'name': '查詢凱旋醫院',
            'message': '高雄市立凱旋醫院在哪裡？電話多少？',
            'expected': ['凱旋', '苓雅', '751']
        },
        {
            'name': '查詢戒毒服務',
            'message': '我想要戒毒，高雄有哪些醫院可以幫助我？',
            'expected': ['醫院', '戒', '治療']
        },
        {
            'name': '查詢美沙冬',
            'message': '什麼是美沙冬替代療法？高雄哪裡可以接受這個治療？',
            'expected': ['美沙冬', '替代', '鴉片']
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, test in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"測試 {i}: {test['name']}")
            print(f"問題: {test['message']}")
            
            try:
                response = await client.post(
                    CHAT_ENDPOINT,
                    json={
                        "message": test['message'],
                        "session_id": session_id,
                        "user_id": "test_user"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                reply = data.get('reply', '')
                print(f"\n回應: {reply[:300]}...")
                if len(reply) > 300:
                    print(f"(已截斷，總長度: {len(reply)})")
                
                # 檢查關鍵字
                reply_lower = reply.lower()
                found = []
                missing = []
                
                for keyword in test['expected']:
                    if keyword.lower() in reply_lower:
                        found.append(keyword)
                    else:
                        missing.append(keyword)
                
                print(f"\n結果:")
                print(f"  ✓ 找到: {', '.join(found) if found else '無'}")
                print(f"  ✗ 缺少: {', '.join(missing) if missing else '無'}")
                
                success_rate = len(found) / len(test['expected']) if test['expected'] else 0
                if success_rate >= 0.5:
                    print(f"  ✅ 通過 ({success_rate:.0%})")
                else:
                    print(f"  ❌ 失敗 ({success_rate:.0%})")
                    
            except Exception as e:
                print(f"❌ 錯誤: {e}")
            
            await asyncio.sleep(2)  # 避免過快請求
    
    print(f"\n{'='*60}")
    print("測試完成")

if __name__ == "__main__":
    asyncio.run(test_rag())