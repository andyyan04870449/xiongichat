"""測試增強日誌功能"""

import asyncio
import httpx
from datetime import datetime


async def test_simple_query():
    """測試簡單查詢的日誌輸出"""
    
    base_url = "http://localhost:8000"
    
    print("測試簡單查詢...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/api/v1/chat/",
            json={
                "user_id": "log_test_simple",
                "message": "你好",
                "conversation_id": None
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 簡單查詢成功")
            print(f"回應: {data.get('reply', '')[:100]}...")
        else:
            print(f"❌ API錯誤: {response.status_code}")


async def test_crisis_query():
    """測試危機查詢的日誌輸出"""
    
    base_url = "http://localhost:8000"
    
    print("\n測試危機查詢...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/api/v1/chat/",
            json={
                "user_id": "log_test_crisis",
                "message": "我真的不想活了，覺得沒有希望",
                "conversation_id": None
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 危機查詢成功")
            print(f"回應: {data.get('reply', '')[:100]}...")
        else:
            print(f"❌ API錯誤: {response.status_code}")


async def test_knowledge_query():
    """測試知識查詢的日誌輸出"""
    
    base_url = "http://localhost:8000"
    
    print("\n測試知識查詢...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/api/v1/chat/",
            json={
                "user_id": "log_test_knowledge",
                "message": "請問毒防局的電話是多少？",
                "conversation_id": None
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 知識查詢成功")
            print(f"回應: {data.get('reply', '')[:100]}...")
        else:
            print(f"❌ API錯誤: {response.status_code}")


async def test_multi_turn_conversation():
    """測試多輪對話的日誌輸出"""
    
    messages = [
        "最近壓力很大",
        "工作一直出錯",
        "有時候會想要放棄"
    ]
    
    base_url = "http://localhost:8000"
    
    print("\n測試多輪對話...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        conv_id = None
        
        for idx, message in enumerate(messages, 1):
            print(f"\n第{idx}輪: {message}")
            
            response = await client.post(
                f"{base_url}/api/v1/chat/",
                json={
                    "user_id": "log_test_multi",
                    "message": message,
                    "conversation_id": conv_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                conv_id = data.get("conversation_id")
                print(f"✅ 第{idx}輪成功")
                print(f"回應: {data.get('reply', '')[:100]}...")
            else:
                print(f"❌ API錯誤: {response.status_code}")
                break
            
            await asyncio.sleep(1)


async def main():
    """執行所有測試"""
    
    print("="*60)
    print(f"增強日誌功能測試")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 執行各種測試
    await test_simple_query()
    await asyncio.sleep(2)
    
    await test_crisis_query()
    await asyncio.sleep(2)
    
    await test_knowledge_query()
    await asyncio.sleep(2)
    
    await test_multi_turn_conversation()
    
    print("\n" + "="*60)
    print("測試完成！")
    print("請檢查 logs/ai_analysis/ai_analysis_*.log 查看詳細日誌")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())