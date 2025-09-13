"""智能關鍵詞提取器 - 使用GPT-4o-mini快速提取查詢關鍵詞"""

import logging
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from app.config import settings

logger = logging.getLogger(__name__)

class KeywordExtractor:
    """使用GPT-4o-mini快速提取RAG查詢關鍵詞"""
    
    EXTRACTION_PROMPT = """你是關鍵詞提取專家，從用戶訊息中提取用於知識庫查詢的關鍵詞。

提取規則：
1. 機構名稱：醫院、中心、診所、協會等
2. 地名地標：凱旋、民生、前金、苓雅等
3. 服務項目：戒毒、諮商、治療、美沙冬等
4. 查詢意圖：電話、地址、時間、服務等
5. 人名職稱：醫師、社工、個管師等

特殊處理：
- 「不想活」→ 提取「自殺防治、危機處理」
- 「毒品」→ 提取「戒毒、藥癮、毒防」
- 「心理問題」→ 提取「心理諮商、精神科」

輸出格式：
直接返回關鍵詞，用空格分隔，最多5個詞
例如：凱旋醫院 電話 地址 精神科 藥癮

用戶訊息：{message}

關鍵詞："""

    def __init__(self):
        # 使用4o-mini以節省成本和提高速度
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,  # 確保穩定輸出
            max_tokens=50,  # 只需要關鍵詞
            api_key=settings.openai_api_key,
            timeout=3  # 快速超時
        )
        logger.info("KeywordExtractor initialized with GPT-4o-mini")
    
    async def extract_keywords(self, user_message: str) -> List[str]:
        """從用戶訊息提取關鍵詞"""
        try:
            # 快速關鍵詞提取
            prompt = self.EXTRACTION_PROMPT.format(message=user_message)
            messages = [
                SystemMessage(content="你是關鍵詞提取專家"),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            keywords_text = response.content.strip()
            
            # 解析關鍵詞
            keywords = keywords_text.split()[:5]  # 最多5個
            
            # 如果沒有提取到關鍵詞，使用原始訊息的前幾個詞
            if not keywords:
                keywords = user_message.split()[:3]
            
            logger.info(f"[Keyword] 提取關鍵詞: {keywords} from '{user_message[:50]}'")
            return keywords
            
        except Exception as e:
            logger.warning(f"[Keyword] 提取失敗，使用fallback: {str(e)}")
            # Fallback: 簡單分詞
            return self._fallback_extract(user_message)
    
    def _fallback_extract(self, message: str) -> List[str]:
        """備用提取方法 - 簡單規則"""
        keywords = []
        
        # 關鍵詞庫
        institution_keywords = ["醫院", "中心", "診所", "協會", "機構"]
        service_keywords = ["電話", "地址", "服務", "時間", "聯絡"]
        location_keywords = ["凱旋", "民生", "前金", "苓雅", "小港"]
        
        # 掃描訊息
        for word in institution_keywords:
            if word in message:
                keywords.append(word)
        
        for word in service_keywords:
            if word in message:
                keywords.append(word)
                
        for word in location_keywords:
            if word in message:
                keywords.append(word)
        
        # 如果沒有找到，返回前幾個詞
        if not keywords:
            keywords = message.split()[:3]
        
        return keywords[:5]  # 最多5個

    def build_rag_query(self, keywords: List[str]) -> str:
        """構建RAG查詢字串"""
        # 智能組合關鍵詞
        if len(keywords) == 0:
            return ""
        
        # 如果有機構名+查詢意圖，優先組合
        query_parts = []
        
        # 檢查是否有機構名稱
        institutions = [k for k in keywords if any(
            inst in k for inst in ["醫院", "中心", "診所", "協會"]
        )]
        
        # 檢查是否有查詢意圖
        intents = [k for k in keywords if any(
            intent in k for intent in ["電話", "地址", "服務", "時間"]
        )]
        
        # 組合查詢
        if institutions and intents:
            # 機構+意圖
            query = f"{institutions[0]} {intents[0]}"
        elif institutions:
            # 只有機構
            query = " ".join(institutions)
        elif intents:
            # 只有意圖，加上所有關鍵詞
            query = " ".join(keywords)
        else:
            # 預設組合
            query = " ".join(keywords)
        
        logger.debug(f"[Keyword] RAG查詢: {query}")
        return query