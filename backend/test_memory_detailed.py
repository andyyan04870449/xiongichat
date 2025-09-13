"""詳細追蹤記憶流程的診斷腳本"""

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

# 打開 UltimateWorkflow 的詳細日誌
logging.getLogger("app.langgraph.ultimate_workflow").setLevel(logging.DEBUG)

async def test_memory_detailed():
    """詳細追蹤記憶系統的每個階段"""
    
    print("\n" + "="*80)
    print("記憶系統詳細診斷")
    print("="*80)
    
    chat_service = ChatService()
    memory_service = MemoryService()
    
    # 測試案例
    user_id = f"detailed_test_{datetime.now().strftime('%H%M%S')}"
    conversation_id = None
    
    # 建立多輪對話
    conversations = [
        "我叫張三，今年45歲",
        "我住在高雄市前鎮區",
        "我有三個小孩",
        "最大的18歲，讀大學",
        "你記得我的名字嗎？"
    ]
    
    for i, user_input in enumerate(conversations, 1):
        print(f"\n{'='*40} 第{i}輪對話 {'='*40}")
        print(f"User: {user_input}")
        
        request = ChatRequest(
            user_id=user_id,
            message=user_input,
            conversation_id=conversation_id
        )
        
        # 如果不是第一輪，先檢查記憶載入情況
        if conversation_id:
            print(f"\n--- 記憶載入檢查 (對話ID: {conversation_id}) ---")
            loaded_memory = await memory_service.load_conversation_memory(str(conversation_id))
            print(f"從資料庫載入了 {len(loaded_memory)} 條記憶")
            
            if loaded_memory:
                print("記憶內容預覽:")
                for j, mem in enumerate(loaded_memory[-4:], 1):  # 顯示最近4條
                    content_preview = mem['content'][:50] + "..." if len(mem['content']) > 50 else mem['content']
                    print(f"  {j}. [{mem['role']}]: {content_preview}")
        
        # 執行請求
        response = await chat_service.process_message(request)
        
        # 第一次請求後保存 conversation_id
        if conversation_id is None:
            conversation_id = response.conversation_id
            print(f"\n創建新對話 ID: {conversation_id}")
        
        print(f"AI: {response.reply}")
        
        # 等待資料寫入
        await asyncio.sleep(1)
        
        # 檢查資料庫狀態
        print(f"\n--- 資料庫狀態檢查 ---")
        async with get_db_context() as db:
            stmt = select(ConversationMessage).where(
                ConversationMessage.conversation_id == str(conversation_id)
            ).order_by(ConversationMessage.created_at)
            
            result = await db.execute(stmt)
            messages = result.scalars().all()
            print(f"資料庫中總共有 {len(messages)} 條消息")
    
    # 最終分析
    print("\n" + "="*80)
    print("最終分析")
    print("="*80)
    
    # 再次載入記憶，看看是否有完整內容
    final_memory = await memory_service.load_conversation_memory(str(conversation_id))
    print(f"\n最終記憶載入: {len(final_memory)} 條")
    
    # 檢查關鍵資訊是否被記住
    last_response = response.reply
    keywords = ["張三", "45", "四十五", "前鎮", "三個", "18", "大學"]
    found = [kw for kw in keywords if kw in last_response]
    
    if found:
        print(f"✅ AI 記住了: {', '.join(found)}")
    else:
        print("❌ AI 似乎沒有完整記住關鍵資訊")
        print(f"AI 的回應: {last_response}")
    
    # 顯示 MemoryService 的配置
    print(f"\n--- MemoryService 配置 ---")
    print(f"max_turns: {memory_service.max_turns}")
    print(f"實際最大載入量: {memory_service.max_turns * 2} 條訊息")
    
    print("\n" + "="*80)
    print("診斷完成")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_memory_detailed())