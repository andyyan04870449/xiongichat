"""診斷記憶系統問題的測試腳本"""

import asyncio
import logging
from datetime import datetime
from app.services.chat import ChatService
from app.schemas.chat import ChatRequest
from app.services.memory import MemoryService
from app.database import get_db_context
from app.models import ConversationMessage
from sqlalchemy import select

# 設定日誌級別以顯示所有資訊
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_memory_system():
    """測試記憶系統完整流程"""
    
    print("\n" + "="*80)
    print("記憶系統診斷測試")
    print("="*80)
    
    chat_service = ChatService()
    memory_service = MemoryService()
    
    # 測試案例
    user_id = f"memory_test_{datetime.now().strftime('%H%M%S')}"
    conversation_id = None
    
    print("\n1. 發送第一條消息")
    print("-" * 40)
    
    # 第一條消息
    request1 = ChatRequest(
        user_id=user_id,
        message="我叫阿明，今年35歲",
        conversation_id=conversation_id
    )
    
    response1 = await chat_service.process_message(request1)
    conversation_id = response1.conversation_id
    
    print(f"User: {request1.message}")
    print(f"AI: {response1.reply[:100]}...")
    print(f"Conversation ID: {conversation_id}")
    
    # 等待資料寫入
    await asyncio.sleep(1)
    
    print("\n2. 檢查資料庫中的記憶")
    print("-" * 40)
    
    # 直接從資料庫查詢
    async with get_db_context() as db:
        stmt = select(ConversationMessage).where(
            ConversationMessage.conversation_id == str(conversation_id)
        ).order_by(ConversationMessage.created_at)
        
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        print(f"資料庫中找到 {len(messages)} 條消息：")
        for msg in messages:
            print(f"  - {msg.role}: {msg.content[:50]}...")
    
    print("\n3. 測試記憶載入")
    print("-" * 40)
    
    # 載入記憶
    loaded_memory = await memory_service.load_conversation_memory(str(conversation_id))
    print(f"載入的記憶有 {len(loaded_memory)} 條：")
    for mem in loaded_memory:
        print(f"  - {mem['role']}: {mem['content'][:50]}...")
    
    print("\n4. 發送第二條消息（測試記憶）")
    print("-" * 40)
    
    # 第二條消息
    request2 = ChatRequest(
        user_id=user_id,
        message="你記得我幾歲嗎？",
        conversation_id=conversation_id
    )
    
    # 啟用更詳細的日誌
    logging.getLogger("app.services.chat").setLevel(logging.DEBUG)
    logging.getLogger("app.langgraph.ultimate_workflow").setLevel(logging.DEBUG)
    
    response2 = await chat_service.process_message(request2)
    
    print(f"User: {request2.message}")
    print(f"AI: {response2.reply}")
    
    # 分析回應
    print("\n5. 分析結果")
    print("-" * 40)
    
    if "35" in response2.reply or "三十五" in response2.reply:
        print("✅ AI 成功記住了年齡！")
    else:
        print("❌ AI 沒有記住年齡")
        
        # 進一步診斷
        print("\n診斷資訊：")
        print(f"- Conversation ID 一致性: {conversation_id == response2.conversation_id}")
        print(f"- 記憶載入數量: {len(loaded_memory)}")
        print(f"- 第一條消息是否包含年齡: {'35歲' in request1.message}")
        
    print("\n6. 檢查最終資料庫狀態")
    print("-" * 40)
    
    # 再次查詢資料庫
    async with get_db_context() as db:
        stmt = select(ConversationMessage).where(
            ConversationMessage.conversation_id == str(conversation_id)
        ).order_by(ConversationMessage.created_at)
        
        result = await db.execute(stmt)
        final_messages = result.scalars().all()
        
        print(f"最終資料庫中有 {len(final_messages)} 條消息")
        
        # 檢查是否包含所有對話
        expected_messages = [
            ("user", "我叫阿明，今年35歲"),
            ("assistant", response1.reply),
            ("user", "你記得我幾歲嗎？"),
            ("assistant", response2.reply)
        ]
        
        if len(final_messages) >= 4:
            print("✅ 所有對話都已儲存")
        else:
            print(f"⚠️ 預期4條消息，實際只有{len(final_messages)}條")
    
    print("\n" + "="*80)
    print("診斷完成")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_memory_system())