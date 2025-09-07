"""查詢構建器 - 根據理解結果構建最優查詢"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class QueryBuilder:
    """根據理解結果構建最優查詢"""
    
    def build_query(self, understanding: Dict, fallback_text: str) -> str:
        """構建查詢，支援多種場景"""
        
        # 優先使用 AI 推薦的查詢
        search_strategy = understanding.get("search_strategy", {})
        if search_strategy.get("search_query"):
            logger.info(f"Using AI-recommended query: {search_strategy['search_query']}")
            return search_strategy["search_query"]
        
        # 次選：組合實體和意圖
        entities = understanding.get("entities", {})
        intent = understanding.get("user_intent", {})
        
        main_entity = entities.get("主要實體", {}).get("name", "")
        underlying_intent = intent.get("underlying", "")
        
        if main_entity and underlying_intent:
            combined_query = f"{main_entity} {underlying_intent}"
            logger.info(f"Using entity-intent query: {combined_query}")
            return combined_query
        
        # 第三選：只使用主要實體
        if main_entity:
            logger.info(f"Using entity-only query: {main_entity}")
            return main_entity
        
        # 最後：使用原始輸入
        logger.info(f"Using fallback query: {fallback_text}")
        return fallback_text
    
    def get_search_parameters(self, understanding: Dict) -> Dict:
        """根據理解結果調整搜索參數"""
        
        confidence = understanding.get("confidence_score", 0.5)
        search_scope = understanding.get("search_strategy", {}).get("search_scope", "相關")
        
        logger.info(f"Search parameters - confidence: {confidence}, scope: {search_scope}")
        
        # 動態調整參數
        if search_scope == "精確" and confidence > 0.8:
            return {
                "k": 3,
                "similarity_threshold": 0.5,
                "use_rerank": True
            }
        elif search_scope == "廣泛" or confidence < 0.5:
            return {
                "k": 10,
                "similarity_threshold": 0.2,
                "use_keywords": True
            }
        else:  # 相關
            return {
                "k": 5,
                "similarity_threshold": 0.3,
                "use_rerank": False
            }
    
    def get_filters(self, understanding: Dict) -> Optional[Dict]:
        """根據理解結果構建過濾條件"""
        
        filters = {}
        
        # 根據意圖類別設定過濾
        intent_category = understanding.get("user_intent", {}).get("category", "")
        
        category_mapping = {
            "資訊查詢": ["contacts", "services", "faq"],
            "尋求幫助": ["medical", "services"],
            "情感支持": None,
            "閒聊": None,
            "任務執行": ["services", "legal"]
        }
        
        categories = category_mapping.get(intent_category)
        if categories:
            # 如果有多個類別，不設定過濾（讓檢索更廣泛）
            if len(categories) == 1:
                filters["category"] = categories[0]
        
        # 總是設定語言
        filters["lang"] = "zh-TW"
        
        return filters if filters else None
    
    def get_fallback_queries(self, understanding: Dict) -> List[str]:
        """獲取備選查詢列表"""
        
        fallback_queries = understanding.get("search_strategy", {}).get("fallback_queries", [])
        
        # 如果沒有備選查詢，根據實體生成
        if not fallback_queries:
            entities = understanding.get("entities", {})
            main_entity = entities.get("主要實體", {}).get("name", "")
            
            if main_entity:
                fallback_queries = [
                    main_entity,
                    f"{main_entity} 聯絡",
                    f"{main_entity} 資訊",
                    f"{main_entity} 服務"
                ]
        
        return fallback_queries
    
    def should_use_keywords(self, understanding: Dict) -> bool:
        """判斷是否應該使用關鍵字搜索"""
        
        confidence = understanding.get("confidence_score", 0.5)
        search_scope = understanding.get("search_strategy", {}).get("search_scope", "")
        
        # 低置信度或廣泛搜索時使用關鍵字
        return confidence < 0.4 or search_scope == "廣泛"
    
    def extract_keywords(self, understanding: Dict, input_text: str) -> List[str]:
        """提取關鍵字用於搜索"""
        
        keywords = []
        
        # 從實體中提取
        entities = understanding.get("entities", {})
        main_entity = entities.get("主要實體", {}).get("name", "")
        if main_entity:
            keywords.append(main_entity)
        
        # 從次要實體中提取
        secondary_entities = entities.get("次要實體", [])
        for entity in secondary_entities[:2]:  # 最多取2個次要實體
            if isinstance(entity, dict):
                keywords.append(entity.get("name", ""))
            elif isinstance(entity, str):
                keywords.append(entity)
        
        # 如果沒有實體，從原始輸入提取
        if not keywords:
            # 簡單的關鍵字提取（可以改進）
            words = input_text.split()
            keywords = [w for w in words if len(w) > 2][:3]
        
        return [k for k in keywords if k]  # 過濾空值