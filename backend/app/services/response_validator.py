"""回應驗證器 - 驗證並修復不符預期的回應"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import logging

from app.config import settings
from app.services.rag_retriever import RAGRetriever, RetrievalResult

logger = logging.getLogger(__name__)


class ResponseValidator:
    """驗證並修復不符預期的回應"""
    
    def __init__(self):
        # 驗證用mini模型（結構化輸出）
        self.validation_llm = ChatOpenAI(
            model=settings.openai_model_analysis,
            temperature=0.1,
            api_key=settings.openai_api_key,
            model_kwargs={
                "response_format": {"type": "json_object"}
            }
        )
        # 生成用4o模型（創意改寫）
        self.generation_llm = ChatOpenAI(
            model=settings.openai_model_chat,
            temperature=0.7,
            api_key=settings.openai_api_key
        )
        self.retriever = RAGRetriever()
    
    async def validate_and_fix(self, state: Dict, response: str) -> str:
        """驗證回應，失敗時自動修復"""
        
        understanding = state.get("context_understanding", {})
        
        # 如果沒有理解結果，直接返回原始回應
        if not understanding:
            return response
        
        # 驗證回應是否滿足用戶需求
        validation_prompt = f"""
分析系統回應是否滿足用戶需求：

用戶意圖：{json.dumps(understanding.get("user_intent", {}), ensure_ascii=False)}
資訊需求：{json.dumps(understanding.get("information_needs", {}), ensure_ascii=False)}
系統回應：{response}

返回 JSON：
{{
    "is_satisfactory": true/false,
    "missing_elements": ["缺少的要素"],
    "improvement_suggestions": ["改進建議"],
    "severity": "完全失敗/部分滿足/基本滿足/完全滿足"
}}

必須返回有效的 JSON 格式。
"""
        
        try:
            messages = [
                SystemMessage(content="你是一個回應品質評估系統"),
                HumanMessage(content=validation_prompt)
            ]
            
            validation_response = await self.validation_llm.ainvoke(messages)
            result = json.loads(validation_response.content)
            
            logger.info(f"Validation result: {result.get('severity')}")
            
            if not result.get("is_satisfactory", False):
                return await self._handle_validation_failure(state, response, result)
            
            return response
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            # 驗證失敗時返回原始回應
            return response
    
    async def _handle_validation_failure(
        self, 
        state: Dict, 
        original_response: str,
        validation_result: Dict
    ) -> str:
        """處理驗證失敗的情況"""
        
        severity = validation_result.get("severity", "部分滿足")
        
        if severity == "完全失敗":
            # 策略1：使用備選查詢重新檢索
            logger.info("Response completely failed validation, retrying with fallback queries")
            return await self._retry_with_fallback_queries(state)
            
        elif severity == "部分滿足":
            # 策略2：補充缺失資訊
            logger.info("Response partially satisfactory, supplementing missing info")
            return await self._supplement_missing_info(
                state, 
                original_response,
                validation_result.get("missing_elements", [])
            )
            
        else:
            # 策略3：優化現有回應
            logger.info("Response basically satisfactory, enhancing")
            return await self._enhance_response(
                state,
                original_response,
                validation_result.get("improvement_suggestions", [])
            )
    
    async def _retry_with_fallback_queries(self, state: Dict) -> str:
        """使用備選查詢重試"""
        
        understanding = state.get("context_understanding", {})
        fallback_queries = understanding.get("search_strategy", {}).get("fallback_queries", [])
        
        # 如果沒有備選查詢，生成一些
        if not fallback_queries:
            entities = understanding.get("entities", {})
            main_entity = entities.get("主要實體", {}).get("name", "")
            if main_entity:
                fallback_queries = [
                    main_entity,
                    f"{main_entity} 聯絡資訊",
                    f"{main_entity} 電話 地址"
                ]
        
        for query in fallback_queries:
            logger.info(f"Retrying with fallback query: {query}")
            
            # 重新檢索
            results = await self.retriever.retrieve(
                query=query,
                k=5,
                similarity_threshold=0.25
            )
            
            if results:
                # 生成新回應
                new_response = await self._generate_response_from_results(state, results)
                
                # 快速驗證
                if await self._quick_validate(state, new_response):
                    return new_response
        
        # 所有重試都失敗，返回道歉訊息
        return self._generate_apology_response(state)
    
    async def _supplement_missing_info(
        self, 
        state: Dict,
        original_response: str,
        missing_elements: List[str]
    ) -> str:
        """補充缺失的資訊"""
        
        supplement_prompt = f"""
原始回應：{original_response}

缺少以下要素：{', '.join(missing_elements)}

請補充這些資訊。如果無法從已有資訊中獲得，請明確說明並提供替代建議。
保持簡潔，符合原有的回應格式和語氣。
字數限制：40字以內。
"""
        
        messages = [
            SystemMessage(content="你是一個回應補充系統，幫助完善不完整的回應"),
            HumanMessage(content=supplement_prompt)
        ]
        
        supplemented_response = await self.generation_llm.ainvoke(messages)
        return supplemented_response.content
    
    async def _enhance_response(
        self,
        state: Dict,
        original_response: str,
        suggestions: List[str]
    ) -> str:
        """根據建議優化回應"""
        
        enhance_prompt = f"""
優化以下回應：
{original_response}

改進建議：
{chr(10).join(f"- {s}" for s in suggestions)}

請根據建議優化回應，保持原有資訊的同時改進表達方式。
保持簡潔自然的語氣，字數限制40字以內。
"""
        
        messages = [
            SystemMessage(content="你是一個回應優化系統"),
            HumanMessage(content=enhance_prompt)
        ]
        
        enhanced_response = await self.generation_llm.ainvoke(messages)
        return enhanced_response.content
    
    async def _generate_response_from_results(
        self, 
        state: Dict, 
        results: List[RetrievalResult]
    ) -> str:
        """從檢索結果生成回應"""
        
        if not results:
            return self._generate_apology_response(state)
        
        # 提取最相關的資訊
        top_result = results[0]
        
        generation_prompt = f"""
根據以下資訊回答用戶問題：

用戶問題：{state.get('input_text', '')}
相關資訊：
標題：{top_result.title}
內容：{top_result.content[:500]}

請提供簡潔準確的回應，包含用戶需要的具體資訊。
字數限制：40字以內，最多2句話。
"""
        
        messages = [
            SystemMessage(content="你是一個資訊整理助手"),
            HumanMessage(content=generation_prompt)
        ]
        
        response = await self.generation_llm.ainvoke(messages)
        return response.content
    
    async def _quick_validate(self, state: Dict, response: str) -> bool:
        """快速驗證回應是否基本滿足需求"""
        
        understanding = state.get("context_understanding", {})
        priority_need = understanding.get("information_needs", {}).get("priority", "")
        
        # 簡單檢查：回應中是否包含關鍵資訊
        if priority_need:
            # 檢查是否包含電話、地址等關鍵詞
            key_indicators = ["電話", "地址", "聯絡", "mail", "@", "號"]
            return any(indicator in response for indicator in key_indicators)
        
        # 預設通過
        return True
    
    def _generate_apology_response(self, state: Dict) -> str:
        """生成道歉回應"""
        
        understanding = state.get("context_understanding", {})
        intent = understanding.get("user_intent", {}).get("underlying", "")
        entity = understanding.get("entities", {}).get("主要實體", {}).get("name", "")
        
        if entity:
            return f"抱歉，我目前沒有{entity}的詳細資訊。建議您可以上網搜尋或直接聯繫詢問。"
        else:
            return "抱歉，我無法提供您需要的資訊。建議試試其他查詢方式。"