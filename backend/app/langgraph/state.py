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
    
    # 語意分析
    semantic_analysis: Optional[Dict[str, Any]]  # 語意理解結果
    mentioned_substances: Optional[List[str]]  # 提及的物質
    user_intent: Optional[str]  # 用戶意圖
    emotional_state: Optional[str]  # 情緒狀態
    
    # 安全檢查
    drug_info: Optional[Dict[str, Any]]  # 毒品相關資訊
    risk_level: Optional[str]  # 風險等級
    response_strategy: Optional[str]  # 回應策略
    
    # 意圖分類
    need_knowledge: Optional[bool]  # 是否需要查詢知識庫
    intent_category: Optional[str]  # 意圖類別
    
    # RAG 檢索
    retrieved_knowledge: Optional[List[Dict[str, Any]]]  # 檢索到的知識
    
    # 生成回覆
    reply: str
    
    # 訊息 ID
    user_message_id: Optional[str]
    assistant_message_id: Optional[str]
    
    # 錯誤處理
    error: Optional[str]
    
    # 時間戳
    timestamp: datetime