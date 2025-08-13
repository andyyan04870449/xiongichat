"""工作流狀態定義"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class WorkflowState(TypedDict):
    """工作流狀態"""
    # 輸入
    user_id: str
    conversation_id: Optional[str]  # UUID as string
    input_text: str
    
    # 記憶管理
    memory: List[Dict[str, str]]  # 對話歷史
    
    # 生成回覆
    reply: str
    
    # 訊息 ID
    user_message_id: Optional[str]
    assistant_message_id: Optional[str]
    
    # 錯誤處理
    error: Optional[str]
    
    # 時間戳
    timestamp: datetime