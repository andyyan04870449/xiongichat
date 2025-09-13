"""測試記憶流程的詳細診斷腳本"""

import asyncio
import logging
from datetime import datetime
from app.services.chat import ChatService
from app.schemas.chat import ChatRequest
from app.services.memory import MemoryService
from app.database import get_db_context
from app.models import ConversationMessage
from sqlalchemy import select
import json

# 設定詳細日誌
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_memory_flow():
    """測試記憶系統的完整流程"""
    
    print("\n" + "="*80)
    print("記憶流程詳細診斷")
    print("="*80)
    
    chat_service = ChatService()
    memory_service = MemoryService()
    
    # 測試案例
    user_id = f"flow_test_{datetime.now().strftime('%H%M%S')}"
    conversation_id = None
    
    print("\n========== 第一輪對話 ==========")
    
    # 第一條消息
    request1 = ChatRequest(
        user_id=user_id,
        message="我叫阿明，今年35歲，住在高雄",
        conversation_id=conversation_id
    )
    
    print(f"User ID: {user_id}")
    print(f"User: {request1.message}")
    
    response1 = await chat_service.process_message(request1)
    conversation_id = response1.conversation_id
    
    print(f"Conversation ID: {conversation_id}")
    print(f"AI: {response1.reply[:100]}...")
    
    # 等待資料寫入
    await asyncio.sleep(2)
    
    print("\n========== 檢查資料庫儲存 ==========")
    
    # 檢查資料庫
    async with get_db_context() as db:
        stmt = select(ConversationMessage).where(
            ConversationMessage.conversation_id == str(conversation_id)
        ).order_by(ConversationMessage.created_at)
        
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        print(f"資料庫中有 {len(messages)} 條消息")
        for i, msg in enumerate(messages, 1):
            print(f"  {i}. [{msg.role}]: {msg.content[:50]}...")
    
    print("\n========== 第二輪對話（測試記憶載入）==========")
    
    # 載入記憶
    loaded_memory = await memory_service.load_conversation_memory(str(conversation_id))
    print(f"載入了 {len(loaded_memory)} 條記憶")
    for mem in loaded_memory:
        print(f"  - {mem['role']}: {mem['content'][:50]}...")
    
    # 第二條消息
    request2 = ChatRequest(
        user_id=user_id,
        message="你記得我叫什麼名字嗎？幾歲？",
        conversation_id=conversation_id
    )
    
    print(f"\nUser: {request2.message}")
    
    # 追蹤記憶傳遞
    print("\n檢查 ChatService 的記憶載入...")
    
    # 手動測試記憶載入流程
    from app.langgraph import WorkflowState
    
    # 模擬 ChatService 的流程
    memory = await memory_service.load_conversation_memory(str(conversation_id))
    print(f"ChatService 載入的記憶: {len(memory)} 條")
    
    state = WorkflowState(
        user_id=user_id,
        conversation_id=str(conversation_id),
        input_text=request2.message,
        memory=memory,
        semantic_analysis=None,
        mentioned_substances=None,
        user_intent=None,
        emotional_state=None,
        drug_info=None,
        risk_level=None,
        response_strategy=None,
        need_knowledge=None,
        intent_category=None,
        retrieved_knowledge=None,
        reply="",
        user_message_id=None,
        assistant_message_id=None,
        error=None,
        timestamp=datetime.utcnow()
    )
    
    print(f"WorkflowState 中的記憶: {len(state['memory'])} 條")
    
    # 執行第二次請求
    response2 = await chat_service.process_message(request2)
    
    print(f"AI: {response2.reply}")
    
    # 分析回應
    print("\n========== 結果分析 ==========")
    
    keywords = ["阿明", "35", "三十五", "高雄"]
    found_keywords = [kw for kw in keywords if kw in response2.reply]
    
    if found_keywords:
        print(f"✅ AI 記住了: {', '.join(found_keywords)}")
    else:
        print("❌ AI 沒有記住關鍵資訊")
        
        # 詳細診斷
        print("\n診斷資訊：")
        print(f"1. Conversation ID 一致: {conversation_id == response2.conversation_id}")
        print(f"2. 資料庫有記錄: {len(messages)} 條")
        print(f"3. 記憶成功載入: {len(loaded_memory)} 條")
        
    # 等待並檢查最終狀態
    await asyncio.sleep(2)
    
    print("\n========== 最終資料庫狀態 ==========")
    
    async with get_db_context() as db:
        stmt = select(ConversationMessage).where(
            ConversationMessage.conversation_id == str(conversation_id)
        ).order_by(ConversationMessage.created_at)
        
        result = await db.execute(stmt)
        final_messages = result.scalars().all()
        
        print(f"總共 {len(final_messages)} 條消息")
        for i, msg in enumerate(final_messages, 1):
            print(f"  {i}. [{msg.role}]: {msg.content[:80]}...")
    
    print("\n" + "="*80)
    print("診斷完成")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_memory_flow())