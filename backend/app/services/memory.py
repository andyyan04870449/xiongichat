"""記憶管理服務"""

from typing import List, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models import ConversationMessage
from app.database import get_db_context

logger = logging.getLogger(__name__)


class MemoryService:
    """對話記憶管理服務"""
    
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
    
    async def load_conversation_memory(self, conversation_id: str) -> List[Dict[str, str]]:
        """載入對話記憶"""
        try:
            async with get_db_context() as db:
                # 查詢最近的訊息
                stmt = select(ConversationMessage).where(
                    ConversationMessage.conversation_id == conversation_id
                ).order_by(
                    ConversationMessage.created_at.desc()
                ).limit(self.max_turns * 2)  # *2 因為包含 user 和 assistant
                
                result = await db.execute(stmt)
                messages = result.scalars().all()
                
                # 反轉順序（從舊到新）
                messages = list(reversed(messages))
                
                # 轉換為記憶格式
                memory = []
                for msg in messages:
                    memory.append({
                        "role": msg.role,
                        "content": msg.content
                    })
                
                logger.info(f"Loaded {len(memory)} messages for conversation {conversation_id}")
                return memory
                
        except Exception as e:
            logger.error(f"Error loading memory: {str(e)}")
            return []
    
    async def save_conversation_memory(
        self, 
        conversation_id: str, 
        memory: List[Dict[str, str]]
    ) -> bool:
        """儲存對話記憶（如果需要的話）"""
        # 在目前的實作中，記憶直接從資料庫讀取
        # 這個方法保留給未來可能的快取實作
        return True
    
    def truncate_memory(self, memory: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """截斷記憶到最大輪數"""
        if len(memory) > self.max_turns * 2:
            return memory[-(self.max_turns * 2):]
        return memory