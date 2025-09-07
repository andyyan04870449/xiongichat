"""重構的工作流狀態定義 - 簡化版本"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class RefactoredWorkflowState(TypedDict):
    """簡化的工作流狀態 - 只保留必要欄位"""
    
    # ========== 核心輸入 ==========
    user_id: str
    conversation_id: Optional[str]
    input_text: str
    session_id: Optional[str]
    
    # ========== 記憶管理 ==========
    memory: List[Dict[str, str]]  # 對話歷史
    
    # ========== 統一分析結果 ==========
    unified_analysis: Optional[Dict[str, Any]]  # 完整分析結果
    
    # 關鍵提取（為了兼容性和快速訪問）
    user_intent: Optional[str]  # 用戶意圖
    emotional_state: Optional[str]  # 情緒狀態
    risk_level: Optional[str]  # 風險等級
    response_strategy: Optional[str]  # 回應策略
    
    # ========== 知識檢索 ==========
    need_knowledge: Optional[bool]  # 是否需要檢索
    enhanced_query: Optional[str]  # 增強的搜索查詢
    retrieved_knowledge: Optional[List[Dict[str, Any]]]  # 檢索結果
    
    # ========== 風險檢測 ==========
    detected_drug_keywords: Optional[List[str]]  # 快速檢測的毒品關鍵詞
    mentioned_substances: Optional[List[str]]  # 分析出的物質
    
    # ========== 輸出 ==========
    reply: str  # 最終回應
    
    # ========== 訊息追蹤 ==========
    user_message_id: Optional[str]
    assistant_message_id: Optional[str]
    
    # ========== 元數據 ==========
    timestamp: datetime
    error: Optional[str]
    processing_time: Optional[float]


class SimplifiedState(TypedDict):
    """極簡狀態 - 用於快速處理"""
    
    # 必要欄位
    user_id: str
    input_text: str
    memory: List[Dict[str, str]]
    reply: str
    
    # 可選欄位
    conversation_id: Optional[str]
    analysis: Optional[Dict[str, Any]]
    knowledge: Optional[List[Dict[str, Any]]]


# 狀態轉換工具
class StateConverter:
    """狀態格式轉換工具"""
    
    @staticmethod
    def from_legacy_state(legacy_state: Dict) -> RefactoredWorkflowState:
        """從舊版狀態轉換到新版"""
        refactored = RefactoredWorkflowState(
            # 核心欄位
            user_id=legacy_state.get("user_id", ""),
            conversation_id=legacy_state.get("conversation_id"),
            input_text=legacy_state.get("input_text", ""),
            session_id=legacy_state.get("session_id"),
            
            # 記憶
            memory=legacy_state.get("memory", []),
            
            # 分析結果（整合多個舊節點的結果）
            unified_analysis={
                "context": legacy_state.get("context_understanding", {}),
                "semantic": legacy_state.get("semantic_analysis", {}),
                "intent": {"category": legacy_state.get("user_intent")},
                "emotional": {"current_state": legacy_state.get("emotional_state")},
                "risk": {"level": legacy_state.get("risk_level")}
            },
            
            # 關鍵信息
            user_intent=legacy_state.get("user_intent"),
            emotional_state=legacy_state.get("emotional_state"),
            risk_level=legacy_state.get("risk_level"),
            response_strategy=legacy_state.get("response_strategy"),
            
            # 知識檢索
            need_knowledge=legacy_state.get("need_knowledge"),
            enhanced_query=legacy_state.get("enhanced_query"),
            retrieved_knowledge=legacy_state.get("retrieved_knowledge"),
            
            # 風險
            mentioned_substances=legacy_state.get("mentioned_substances"),
            
            # 輸出
            reply=legacy_state.get("reply", ""),
            
            # 元數據
            timestamp=legacy_state.get("timestamp", datetime.now()),
            error=legacy_state.get("error")
        )
        
        return refactored
    
    @staticmethod
    def to_legacy_state(refactored_state: RefactoredWorkflowState) -> Dict:
        """從新版狀態轉換到舊版（為了兼容性）"""
        analysis = refactored_state.get("unified_analysis", {})
        
        legacy = {
            # 基礎欄位
            "user_id": refactored_state["user_id"],
            "conversation_id": refactored_state.get("conversation_id"),
            "input_text": refactored_state["input_text"],
            "memory": refactored_state.get("memory", []),
            
            # 分散的分析結果（模擬舊版多節點）
            "context_understanding": analysis.get("context", {}),
            "semantic_analysis": analysis.get("semantic", {}),
            "user_intent": refactored_state.get("user_intent"),
            "emotional_state": refactored_state.get("emotional_state"),
            "risk_level": refactored_state.get("risk_level"),
            "response_strategy": refactored_state.get("response_strategy"),
            
            # 知識檢索
            "need_knowledge": refactored_state.get("need_knowledge"),
            "enhanced_query": refactored_state.get("enhanced_query"),
            "retrieved_knowledge": refactored_state.get("retrieved_knowledge"),
            
            # 物質相關
            "mentioned_substances": refactored_state.get("mentioned_substances"),
            "drug_info": {"keywords": refactored_state.get("detected_drug_keywords", [])},
            
            # 輸出
            "reply": refactored_state["reply"],
            
            # 元數據
            "timestamp": refactored_state.get("timestamp"),
            "error": refactored_state.get("error")
        }
        
        return legacy