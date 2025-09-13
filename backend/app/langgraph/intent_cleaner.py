"""智能語意清理器 - 保留核心查詢意圖，去除口語噪音"""

import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from app.config import settings

logger = logging.getLogger(__name__)

class IntentCleaner:
    """語意清理器 - 將口語化表達轉換為清晰的查詢語句"""
    
    CLEANING_PROMPT = """你是語意清理專家。將用戶的口語表達轉換為清晰的查詢語句，用於知識庫檢索。

核心原則：
1. 保留所有資訊內容（人名、地名、機構、症狀、需求）
2. 保留查詢意圖（想要、需要、詢問、尋找）
3. 去除口語化填充（語氣詞、停頓詞、重複）
4. 修正語法但不改變意思
5. 保持自然的中文語句結構

處理策略：
- 填充詞：去除「嗯、啊、呃、那個、就是、一下、其實」等
- 重複：合併重複表達「很痛很痛」→「很痛」
- 口語化：「咧、啦、喔、欸」等語氣詞移除
- 不完整句：補充使其通順但不添加額外資訊
- 方言/俚語：轉為標準表達但保留原意

輸出要求：
- 保持原意不變
- 輸出自然通順的查詢語句
- 如果原句已經清晰，直接返回原句
- 長度適中（不要過度精簡）

用戶輸入：{message}

清理後的查詢語句："""

    def __init__(self):
        # 使用GPT-4o-mini快速處理
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=100,  # 清理後的語句不應太長
            api_key=settings.openai_api_key,
            timeout=3
        )
        logger.info("IntentCleaner initialized with GPT-4o-mini")
    
    async def clean_query(self, user_message: str) -> str:
        """清理用戶語句，返回適合RAG查詢的清晰語句"""
        
        # 極短語句不處理
        if len(user_message) < 5:
            return user_message
        
        # 已經很清晰的語句快速判斷
        if self._is_clean(user_message):
            logger.debug(f"[IntentCleaner] 語句已清晰，直接使用: {user_message}")
            return user_message
        
        try:
            # 使用LLM清理
            prompt = self.CLEANING_PROMPT.format(message=user_message)
            messages = [
                SystemMessage(content="你是語意清理專家，擅長將口語轉換為清晰查詢"),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            cleaned_text = response.content.strip()
            
            # 確保清理結果合理
            if cleaned_text and len(cleaned_text) > 2:
                logger.info(f"[IntentCleaner] 清理成功: '{user_message[:30]}...' → '{cleaned_text[:30]}...'")
                return cleaned_text
            else:
                logger.warning(f"[IntentCleaner] 清理結果異常，使用原文")
                return user_message
                
        except Exception as e:
            logger.warning(f"[IntentCleaner] LLM清理失敗: {str(e)}")
            # Fallback: 簡單規則清理
            return self._simple_clean(user_message)
    
    def _is_clean(self, text: str) -> bool:
        """快速判斷語句是否已經清晰"""
        # 常見噪音詞列表
        noise_words = [
            "嗯", "啊", "呃", "欸", "喔", "啦", "咧", "齁",
            "那個", "就是", "就是說", "然後", "其實", "一下",
            "那種", "這種", "什麼的", "之類的", "怎麼說"
        ]
        
        # 檢查是否包含噪音詞
        for word in noise_words:
            if word in text:
                return False
        
        # 檢查是否有過多省略號或問號
        if text.count("...") > 1 or text.count("？") > 2:
            return False
        
        # 檢查是否有重複字符（如：好好好、痛痛痛）
        import re
        if re.search(r'(.)\1{2,}', text):
            return False
        
        return True
    
    def _simple_clean(self, text: str) -> str:
        """簡單規則清理（備用方案）"""
        # 移除常見填充詞
        noise_patterns = [
            "嗯+", "啊+", "呃+", "欸+",  # 語氣詞
            "那個", "就是說?", "然後呢?", "其實",  # 填充詞
            "一下子?", "什麼的", "之類的",  # 模糊詞
            r"\.{3,}", r"。{2,}", r"！{2,}", r"？{2,}",  # 過多標點
            r"(.)\1{3,}",  # 重複字符（保留2個）
        ]
        
        import re
        cleaned = text
        for pattern in noise_patterns:
            cleaned = re.sub(pattern, "", cleaned)
        
        # 移除多餘空格
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # 如果清理後太短或為空，返回原文
        if len(cleaned) < 3:
            return text
        
        logger.debug(f"[IntentCleaner] 規則清理: '{text[:30]}' → '{cleaned[:30]}'")
        return cleaned
    
    def get_query_focus(self, cleaned_text: str) -> str:
        """提取查詢焦點（可選的額外優化）"""
        # 識別查詢焦點詞
        focus_patterns = {
            "location": ["在哪", "地址", "位置", "怎麼去", "路線"],
            "contact": ["電話", "聯絡", "預約", "掛號"],
            "service": ["服務", "治療", "看診", "門診"],
            "time": ["時間", "幾點", "營業", "開放"],
            "cost": ["費用", "價格", "收費", "多少錢"]
        }
        
        for focus_type, keywords in focus_patterns.items():
            for keyword in keywords:
                if keyword in cleaned_text:
                    logger.debug(f"[IntentCleaner] 查詢焦點: {focus_type}")
                    return focus_type
        
        return "general"
    
    async def contextualize_query(self, user_message: str, memory: list = None) -> str:
        """結合對話記憶理解當前查詢的完整語境
        
        這個方法解決了用戶在連續對話中使用代詞或省略主語的問題
        例如：
        - 用戶：「你知道凱旋醫院嗎？」
        - AI：「知道」
        - 用戶：「他們的電話是多少？」 <- 需要理解「他們」指凱旋醫院
        
        Args:
            user_message: 當前用戶訊息
            memory: 對話歷史記錄
            
        Returns:
            包含完整語境的查詢語句
        """
        
        # 如果沒有歷史記錄，直接清理當前訊息
        if not memory or len(memory) == 0:
            return await self.clean_query(user_message)
        
        # 檢查是否需要語境補充（包含代詞或缺少主語）
        needs_context = self._needs_context(user_message)
        
        if not needs_context:
            # 不需要語境，直接清理
            return await self.clean_query(user_message)
        
        try:
            # 構建語境理解提示
            context_prompt = """你是對話語境理解專家。基於對話歷史，將用戶的當前問題轉換為完整、清晰的查詢語句。

核心任務：
1. 識別代詞（他、她、它、他們、那裡、這個）指向的具體對象
2. 補充省略的主語或賓語
3. 保持查詢意圖不變
4. 輸出適合知識庫檢索的完整語句

對話歷史：
{history}

當前用戶問題：{current}

重要規則：
- 如果用戶問「電話」「地址」等，要包含是哪個機構的電話/地址
- 如果用戶說「那裡」「他們」，要替換為具體名稱
- 保持原始查詢意圖，只補充缺失的語境
- 不要添加無關資訊

輸出完整查詢語句："""
            
            # 格式化對話歷史
            history_str = self._format_memory_for_context(memory[-6:])  # 最近6條
            
            prompt = context_prompt.format(
                history=history_str,
                current=user_message
            )
            
            messages = [
                SystemMessage(content="你是語境理解專家，將對話中的問題轉換為完整查詢"),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            contextualized = response.content.strip()
            
            logger.info(f"[Context] 語境補充: '{user_message}' → '{contextualized}'")
            return contextualized
            
        except Exception as e:
            logger.warning(f"[Context] 語境理解失敗: {str(e)}")
            # 降級到簡單清理
            return await self.clean_query(user_message)
    
    def _needs_context(self, text: str) -> bool:
        """判斷是否需要語境補充"""
        
        # 代詞列表
        pronouns = [
            "他", "她", "它", "他們", "她們", "它們",
            "這", "那", "這個", "那個", "這裡", "那裡",
            "此", "該", "其"
        ]
        
        # 缺少主語的問句模式
        incomplete_patterns = [
            "的電話", "的地址", "在哪", "怎麼去",
            "什麼時間", "要多少錢", "有什麼服務"
        ]
        
        # 檢查是否包含代詞
        for pronoun in pronouns:
            if pronoun in text:
                return True
        
        # 檢查是否是不完整問句
        for pattern in incomplete_patterns:
            if pattern in text and len(text) < 15:  # 短句且包含模式
                return True
        
        return False
    
    def _format_memory_for_context(self, memory: list) -> str:
        """格式化記憶用於語境理解"""
        if not memory:
            return "無"
        
        formatted = []
        for msg in memory:
            role = "用戶" if msg.get("role") == "user" else "AI"
            content = msg.get("content", "")
            # 只保留關鍵內容，避免過長
            if len(content) > 100:
                content = content[:100] + "..."
            formatted.append(f"{role}：{content}")
        
        return "\n".join(formatted)