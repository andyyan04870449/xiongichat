"""毒品安全檢查節點 - 檢索毒品資訊並評估風險"""

from typing import Dict, Any, List, Optional
import logging

from app.langgraph.state import WorkflowState
from app.services.rag_retriever import RAGRetriever

logger = logging.getLogger(__name__)


class DrugSafetyCheckNode:
    """毒品安全檢查節點 - 檢索相關毒品資訊並評估回應策略"""
    
    def __init__(self):
        self.retriever = RAGRetriever()
        
        # 風險等級定義
        self.RISK_LEVELS = {
            "HIGH": "高風險",  # 明確違法意圖
            "MEDIUM": "中風險",  # 可能的不當使用
            "LOW": "低風險",  # 尋求幫助或資訊
            "SAFE": "安全"  # 無毒品相關
        }
        
        # 回應策略
        self.RESPONSE_STRATEGIES = {
            "REDIRECT_TO_HELP": "引導至專業協助",
            "EDUCATIONAL": "提供教育資訊",
            "SUPPORTIVE": "提供情緒支持",
            "PREVENTIVE": "預防性介入",
            "NORMAL": "一般回應"
        }
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行毒品安全檢查"""
        try:
            # 如果沒有提及物質，跳過檢查
            if not state.get("mentioned_substances"):
                logger.info("No substances mentioned, skipping drug safety check")
                state["drug_info"] = {}
                state["risk_level"] = "SAFE"
                state["response_strategy"] = "NORMAL"
                return state
            
            # 檢索毒品相關資訊
            drug_info = await self._retrieve_drug_information(
                state["mentioned_substances"]
            )
            
            # 評估風險等級
            risk_level = self._assess_risk_level(
                state["semantic_analysis"],
                drug_info
            )
            
            # 決定回應策略
            response_strategy = self._determine_response_strategy(
                risk_level,
                state["user_intent"],
                state["emotional_state"]
            )
            
            # 更新狀態
            state["drug_info"] = drug_info
            state["risk_level"] = risk_level
            state["response_strategy"] = response_strategy
            
            logger.info(f"Drug safety check: risk={risk_level}, strategy={response_strategy}")
            
        except Exception as e:
            logger.error(f"DrugSafetyCheck error: {str(e)}")
            # 錯誤時採用保守策略
            state["drug_info"] = {}
            state["risk_level"] = "MEDIUM"
            state["response_strategy"] = "REDIRECT_TO_HELP"
        
        return state
    
    async def _retrieve_drug_information(self, substances: List[str]) -> Dict[str, Any]:
        """檢索毒品相關資訊"""
        drug_info = {}
        
        for substance in substances:
            # 使用向量檢索找出相關毒品資訊
            results = await self.retriever.retrieve(
                query=f"{substance} 毒品 管制藥品 俗名",
                k=3,
                filters={"category": "drug_information"},
                similarity_threshold=0.6
            )
            
            if results:
                # 提取關鍵資訊
                drug_details = {
                    "formal_name": "",
                    "common_names": [],
                    "control_level": "",
                    "medical_use": "",
                    "risks": [],
                    "legal_status": ""
                }
                
                for result in results:
                    content = result.content
                    # 從內容中提取結構化資訊
                    if "級管制" in content or "級毒品" in content:
                        drug_details["control_level"] = self._extract_control_level(content)
                    if "俗名" in content or "俗稱" in content:
                        drug_details["common_names"].extend(self._extract_common_names(content))
                    if "醫療" in content or "治療" in content:
                        drug_details["medical_use"] = self._extract_medical_use(content)
                
                drug_info[substance] = drug_details
        
        return drug_info
    
    def _assess_risk_level(self, semantic_analysis: Dict, drug_info: Dict) -> str:
        """評估風險等級"""
        
        # 無毒品資訊為安全
        if not drug_info:
            return "SAFE"
        
        user_intent = semantic_analysis.get("user_intent", "")
        risk_indicators = semantic_analysis.get("risk_indicators", [])
        
        # 高風險：明確的獲取意圖或違法意圖
        if user_intent == "獲取物質" or "違法" in str(risk_indicators):
            return "HIGH"
        
        # 中風險：可能的不當使用或好奇
        if user_intent in ["詢問資訊", "其他"] and drug_info:
            # 檢查是否涉及高級別管制藥品
            for substance, info in drug_info.items():
                if "第一級" in info.get("control_level", "") or "第二級" in info.get("control_level", ""):
                    return "MEDIUM"
        
        # 低風險：尋求幫助
        if user_intent == "尋求幫助":
            return "LOW"
        
        return "LOW"
    
    def _determine_response_strategy(self, risk_level: str, user_intent: str, emotional_state: str) -> str:
        """決定回應策略"""
        
        # 高風險一律引導至專業協助
        if risk_level == "HIGH":
            return "REDIRECT_TO_HELP"
        
        # 中風險根據意圖決定
        if risk_level == "MEDIUM":
            if user_intent == "詢問資訊":
                return "EDUCATIONAL"
            else:
                return "PREVENTIVE"
        
        # 低風險提供支持
        if risk_level == "LOW":
            if emotional_state in ["負面", "焦慮", "憂鬱", "絕望"]:
                return "SUPPORTIVE"
            else:
                return "EDUCATIONAL"
        
        return "NORMAL"
    
    def _extract_control_level(self, content: str) -> str:
        """從內容提取管制等級"""
        levels = ["第一級", "第二級", "第三級", "第四級"]
        for level in levels:
            if level in content:
                return level
        return "未知"
    
    def _extract_common_names(self, content: str) -> List[str]:
        """從內容提取俗名"""
        # 簡化實作，實際應該用更複雜的提取邏輯
        common_names = []
        if "俗名" in content or "俗稱" in content:
            # 這裡應該解析內容提取俗名列表
            pass
        return common_names
    
    def _extract_medical_use(self, content: str) -> str:
        """從內容提取醫療用途"""
        if "醫療" in content:
            # 簡化實作
            return "可能有醫療用途"
        return ""