"""Fast Chat 工作流程 - 極簡高效版本
設計原則：40字限制、2-3步驟、<1秒回應
"""

import asyncio
import json
import logging
import re
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from cachetools import TTLCache

from app.config import settings
from app.langgraph.state import WorkflowState
from app.services.rag_retriever import RAGRetriever
from app.utils.ai_logger import get_ai_logger
from app.langgraph.response_length_manager import ResponseLengthManager

logger = logging.getLogger(__name__)


class QuickAnalyzerNode:
    """快速綜合分析節點 - 整合4個分析功能為1個
    
    整合功能：
    - 危機判斷（DrugSafetyCheckNode）
    - 意圖分析（IntentRouterNode）
    - 語意理解（SemanticAnalyzerNode）
    - 對話理解（ContextUnderstandingNode）
    """
    
    # 關鍵詞快速判斷（避免LLM調用）
    CRISIS_KEYWORDS = ["自殺", "想死", "死了", "不想活", "活不下去", "結束生命", "了結"]
    HELP_KEYWORDS = ["戒毒", "戒癮", "勒戒", "治療", "幫助", "求助", "協助"]
    INFO_KEYWORDS = ["地址", "電話", "怎麼去", "幾點", "在哪", "聯絡", "哪些地方", "哪裡"]
    GREETING_KEYWORDS = ["你好", "嗨", "哈囉", "早安", "午安", "晚安"]
    
    ANALYSIS_PROMPT = """你是專業的心理健康分析系統。請仔細分析用戶訊息，特別注意：
1. 危機信號：任何自殺、想死、結束生命的暗示都要標記為high risk
2. 求助需求：詢問戒毒、治療、機構資訊時要標記need_knowledge為true
3. 情緒狀態：識別負面情緒和求助意圖

返回JSON格式：
{{
  "risk_level": "none/low/high",
  "need_knowledge": true/false,
  "intent": "問候/詢問資訊/情緒支持/求助/危機介入/一般對話",
  "entities": [],
  "search_query": "簡潔的搜尋關鍵詞"
}}

用戶：{input_text}

分析要點：
- "想死"、"死了"、"不想活" -> risk_level: "high", intent: "危機介入"
- "戒毒"、"哪些地方"、"機構" -> need_knowledge: true, intent: "詢問資訊"
- 生成適合RAG檢索的search_query

只返回JSON。"""

    def __init__(self):
        # 使用最快的模型進行分析
        self.llm = ChatOpenAI(
            model=settings.openai_model_analysis,  # gpt-4o-mini
            temperature=0.1,
            max_tokens=150,
            api_key=settings.openai_api_key,
        )
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行快速分析"""
        try:
            text = state.get("input_text", "")
            
            # 初始化分析結果
            state["risk_level"] = "none"
            state["need_knowledge"] = False
            state["intent"] = "一般對話"
            state["entities"] = []
            state["search_query"] = ""
            
            # 步驟1: 危機關鍵詞快速判斷（最高優先級）
            if any(kw in text for kw in self.CRISIS_KEYWORDS):
                state["risk_level"] = "high"
                state["need_knowledge"] = True
                state["intent"] = "危機介入"
                state["search_query"] = "自殺防治 心理諮商 緊急專線"
                logger.info(f"Crisis detected via keywords: {text[:30]}")
                # 危機情況仍需要LLM深度分析
                result = await self._llm_analyze(text)
                if result:
                    # 保留危機標記，但更新其他資訊
                    state["risk_level"] = "high"  # 確保不被覆蓋
                    state.update({k: v for k, v in result.items() if k != "risk_level"})
                return state
            
            # 步驟2: 求助關鍵詞判斷
            if any(kw in text for kw in self.HELP_KEYWORDS):
                state["need_knowledge"] = True
                state["intent"] = "求助"
                state["search_query"] = text
                # 求助情況需要LLM分析具體需求
                result = await self._llm_analyze(text)
                if result:
                    state.update(result)
                return state
            
            # 步驟3: 資訊查詢關鍵詞判斷
            if any(kw in text for kw in self.INFO_KEYWORDS):
                state["need_knowledge"] = True
                state["intent"] = "詢問資訊"
                state["search_query"] = text
                
            # 步驟4: 問候關鍵詞判斷
            if any(kw in text for kw in self.GREETING_KEYWORDS):
                state["intent"] = "問候"
                if len(text) <= 10:  # 簡短問候不需要LLM
                    return state
            
            # 步驟5: 複雜情況或不確定時用LLM
            # 擴展觸發條件：問句、較長文本、包含情緒詞
            if ("?" in text or "嗎" in text or "呢" in text or 
                len(text) > 15 or  # 降低長度閾值
                any(word in text for word in ["難過", "痛苦", "絕望", "沒有希望"])):
                result = await self._llm_analyze(text)
                if result:
                    # 合併結果，優先保留已識別的危機標記
                    if state["risk_level"] == "high":
                        result["risk_level"] = "high"
                    state.update(result)
            
            return state
            
        except Exception as e:
            logger.error(f"QuickAnalyzer error: {str(e)}")
            # 發生錯誤時使用安全預設值
            state["risk_level"] = "none"
            state["need_knowledge"] = False
            return state
    
    async def _llm_analyze(self, text: str) -> Optional[Dict]:
        """使用LLM進行深度分析"""
        try:
            prompt = self.ANALYSIS_PROMPT.format(input_text=text)
            
            messages = [
                SystemMessage(content="你是一個對話分析系統，只返回JSON格式結果。"),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # 解析JSON
            result = json.loads(response.content)
            logger.debug(f"LLM analysis result: {result}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return None
        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
            return None


class SmartRAGNode:
    """智能知識檢索節點 - 條件式執行"""
    
    def __init__(self):
        self.retriever = RAGRetriever()
        self.cache = TTLCache(maxsize=50, ttl=300)  # 5分鐘快取
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行智能檢索"""
        try:
            # 條件判斷：是否需要檢索
            if not state.get("need_knowledge"):
                logger.debug("Skipping RAG - not needed")
                return state
            
            # 使用建議的查詢詞或原始輸入
            query = state.get("search_query") or state.get("input_text", "")
            
            # 根據意圖優化查詢
            intent = state.get("intent", "")
            if intent == "危機介入":
                # 危機情況優先搜尋緊急資源
                query = f"自殺防治 1995 心理諮商 緊急求助 {query}"
            elif intent == "求助" and "戒毒" in state.get("input_text", ""):
                # 戒毒求助優先搜尋戒毒機構
                query = f"戒毒 戒癮 治療機構 高雄 {query}"
            elif intent == "詢問資訊":
                # 資訊查詢加入地區限定
                query = f"高雄 {query}"
            
            # 檢查快取
            cache_key = f"rag:{query[:50]}"
            if cache_key in self.cache:
                logger.info(f"RAG cache hit for: {query[:30]}")
                state["knowledge"] = self.cache[cache_key]
                return state
            
            # 執行檢索，調整參數以獲得更好結果
            logger.info(f"Executing RAG search for: {query[:30]}")
            results = await self.retriever.retrieve(
                query=query,
                k=5,  # 增加檢索數量
                similarity_threshold=0.3  # 降低門檻以獲得更多結果
            )
            
            if results:
                # 提取關鍵資訊
                key_info = self._extract_key_info(results)
                state["knowledge"] = key_info
                # 加入快取
                self.cache[cache_key] = key_info
                logger.info(f"RAG found {len(results)} results: {key_info[:50]}")
            else:
                # 沒有結果時提供預設資源
                if intent == "危機介入":
                    state["knowledge"] = "自殺防治專線1995（24小時）、生命線1995、張老師1980"
                elif "戒毒" in query:
                    state["knowledge"] = "毒品危害防制中心0800-770-885、高雄市立凱旋醫院成癮防治科07-7513171"
                else:
                    state["knowledge"] = ""
                logger.info("RAG found no results, using default resources")
            
            return state
            
        except Exception as e:
            logger.error(f"SmartRAG error: {str(e)}")
            state["knowledge"] = ""
            return state
    
    def _extract_key_info(self, results: List) -> str:
        """提取關鍵資訊（電話、地址等）"""
        info_parts = []
        
        for result in results[:2]:
            content = result.content if hasattr(result, 'content') else str(result)
            
            # 提取電話號碼
            phones = re.findall(r'07-\d{7,8}|\d{4}|1\d{3}', content)
            for phone in phones[:1]:  # 只取第一個電話
                if phone not in info_parts:
                    info_parts.append(phone)
            
            # 提取簡短地址
            if "路" in content or "號" in content:
                # 嘗試提取地址
                addr_match = re.search(r'[^，。\s]{2,10}[路街][^，。\s]{0,10}號', content)
                if addr_match:
                    addr = addr_match.group()
                    if len(addr) <= 20 and addr not in info_parts:
                        info_parts.append(addr)
        
        # 組合資訊，確保不超過40字
        result = " ".join(info_parts)
        if len(result) > 40:
            result = result[:37] + "..."
        
        return result


class FastResponseNode:
    """快速回應生成節點 - 嚴格40字限制"""
    
    # 預設模板（減少LLM調用）
    TEMPLATES = {
        "high_risk": "聽起來很辛苦，要不要打1995聊聊？",
        "need_help": "我在這裡陪你，可以打1995專線。",
        "greeting": "你好！今天過得如何？",
        "morning": "早安！今天有什麼計畫嗎？",
        "evening": "晚安！今天還好嗎？",
        "support": "我在這裡陪你，想聊什麼嗎？",
        "unknown": "不好意思，我沒聽清楚。",
        "info_found": "我查到：{knowledge}",
        "no_info": "抱歉，我沒有這個資訊。"
    }
    
    # 極簡提示詞（智能彈性版本）
    CHAT_PROMPT = """你是朋友「雄i聊」，一個關懷陪伴的AI助手。

回應原則：
1. 一般對話≤40字
2. 聯絡資訊≤60字  
3. 機構介紹≤100字（包含服務說明）
4. 自然口語，像朋友
5. 資訊要完整但精簡

特殊情況處理：
- 危機狀況：立即提供求助資源（1995專線等）
- 求助需求：提供具體機構和聯絡方式
- 使用檢索到的知識時，整理成簡潔易懂的格式

{context}

用戶：{input_text}
直接回應："""

    def __init__(self):
        # 使用主要模型但合理限制token
        self.llm = ChatOpenAI(
            model=settings.openai_model_chat,  # gpt-4o
            temperature=0.3,  # 低溫度保持穩定
            max_tokens=60,  # 彈性限制（約90-120字中文）
            api_key=settings.openai_api_key,
        )
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """生成回應"""
        try:
            risk = state.get("risk_level", "none")
            intent = state.get("intent", "一般對話")
            knowledge = state.get("knowledge", "")
            
            # 策略1: 高風險優先處理（危機介入）
            if risk == "high" or intent == "危機介入":
                if knowledge:
                    # 有檢索結果時，組合關懷語和資源
                    reply = f"聽起來你很辛苦。{knowledge[:50]}"
                else:
                    reply = "聽起來很辛苦，要不要打1995聊聊？這是24小時專線。"
            
            # 策略2: 求助需求（包含戒毒等）
            elif intent == "求助":
                if knowledge:
                    reply = f"我找到一些資源：{knowledge}"
                else:
                    # 沒有檢索結果時用LLM生成
                    reply = await self._generate_response(state)
            
            # 策略3: 資訊查詢回應
            elif intent == "詢問資訊":
                if knowledge:
                    # 有檢索結果直接使用
                    reply = knowledge
                else:
                    # 沒有結果時說明情況
                    reply = "抱歉，我沒有找到相關資訊。建議你可以撥打毒防局諮詢專線。"
            
            # 策略4: 問候回應
            elif intent == "問候":
                # 根據時間選擇問候語
                hour = datetime.now().hour
                if 5 <= hour < 12:
                    reply = self.TEMPLATES["morning"]
                elif 18 <= hour < 23:
                    reply = self.TEMPLATES["evening"]
                else:
                    reply = self.TEMPLATES["greeting"]
            
            # 策略5: 情緒支持
            elif intent == "情緒支持":
                if knowledge:
                    reply = f"我在這裡陪你。{knowledge[:30]}"
                else:
                    reply = self.TEMPLATES["support"]
            
            # 策略6: LLM生成（最後手段）
            else:
                reply = await self._generate_response(state)
            
            # 使用 ResponseLengthManager 進行智能處理
            intent = state.get("intent", "一般對話")
            risk_level = state.get("risk_level", "none")
            
            # 保存原始回應
            original_reply = reply
            
            # 格式化回應
            reply, used_limit, content_type = ResponseLengthManager.format_response(
                reply, 
                intent=intent, 
                risk_level=risk_level
            )
            
            # 記錄字數管理（如果有截斷）
            ai_logger = get_ai_logger()
            if len(original_reply) > len(reply):
                ai_logger.log_length_management(
                    original_text=original_reply,
                    final_text=reply,
                    content_type=content_type,
                    limit=used_limit,
                    truncated=True
                )
            
            # 記錄處理結果
            logger.info(f"[{content_type}] Response: {len(reply)}字 (限制{used_limit}字)")
            state["response_type"] = content_type
            state["response_length"] = len(reply)
            state["response_length_limit"] = used_limit
            
            state["reply"] = reply
            logger.info(f"Generated response: {reply}")
            
            return state
            
        except Exception as e:
            logger.error(f"FastResponse error: {str(e)}")
            state["reply"] = self.TEMPLATES["unknown"]
            return state
    
    async def _generate_response(self, state: WorkflowState) -> str:
        """使用LLM生成回應（只在必要時）"""
        try:
            # 構建上下文
            context_parts = []
            
            # 加入記憶上下文
            if state.get("memory"):
                last_exchange = state["memory"][-1] if state["memory"] else None
                if last_exchange:
                    context_parts.append(f"剛才：{last_exchange.get('user', '')[:20]}")
            
            # 加入檢索到的知識
            if state.get("knowledge"):
                context_parts.append(f"相關資訊：{state['knowledge']}")
            
            # 加入意圖和風險資訊
            if state.get("intent"):
                context_parts.append(f"用戶意圖：{state['intent']}")
            
            if state.get("risk_level") and state["risk_level"] != "none":
                context_parts.append(f"風險等級：{state['risk_level']}")
            
            context = "\n".join(context_parts) if context_parts else ""
            
            prompt = self.CHAT_PROMPT.format(
                context=context,
                input_text=state.get("input_text", "")[:100]
            )
            
            messages = [SystemMessage(content=prompt)]
            
            response = await self.llm.ainvoke(messages)
            
            return response.content
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return self.TEMPLATES["unknown"]


class MemoryManager:
    """輕量級記憶管理器"""
    
    def __init__(self):
        self.short_term = {}  # 短期記憶
        self.max_memory = 10  # 最多記10輪
    
    async def load(self, user_id: str) -> List[Dict]:
        """載入用戶記憶"""
        if user_id in self.short_term:
            return self.short_term[user_id][-5:]  # 返回最近5輪
        return []
    
    async def save(self, user_id: str, exchange: Dict):
        """儲存對話"""
        if user_id not in self.short_term:
            self.short_term[user_id] = []
        
        self.short_term[user_id].append(exchange)
        
        # 限制記憶大小
        if len(self.short_term[user_id]) > self.max_memory:
            self.short_term[user_id] = self.short_term[user_id][-self.max_memory:]


class CompleteFastWorkflow:
    """完整但快速的工作流 - 嚴格遵守40字原則"""
    
    def __init__(self):
        # 核心節點（只有3個）
        self.analyzer = QuickAnalyzerNode()
        self.rag = SmartRAGNode()
        self.generator = FastResponseNode()
        
        # 輔助功能
        self.memory = MemoryManager()
        self.response_cache = TTLCache(maxsize=100, ttl=300)
        
        logger.info("CompleteFastWorkflow initialized")
    
    async def ainvoke(self, state: WorkflowState) -> WorkflowState:
        """執行工作流程"""
        start_time = time.time()
        ai_logger = get_ai_logger(state.get("session_id"))
        
        try:
            import uuid
            
            user_id = state.get("user_id", "default")
            input_text = state.get("input_text", "")
            
            # 設置必要的 UUID
            if not state.get("conversation_id"):
                state["conversation_id"] = str(uuid.uuid4())
            if not state.get("user_message_id"):
                state["user_message_id"] = str(uuid.uuid4())
            if not state.get("assistant_message_id"):
                state["assistant_message_id"] = str(uuid.uuid4())
            
            # 記錄開始
            ai_logger.log_request_start(
                user_id=user_id,
                message=input_text,
                conversation_id=state.get("conversation_id")
            )
            
            # 0. 快取檢查（<10ms）
            cache_key = f"{user_id}:{input_text[:50]}"
            if cache_key in self.response_cache:
                logger.info(f"Cache hit for: {input_text[:30]}")
                state["reply"] = self.response_cache[cache_key]
                return state
            
            # 1. 載入記憶（<20ms）
            state["memory"] = await self.memory.load(user_id)
            
            # 2. 快速分析（<100ms）
            state = await self.analyzer(state)
            ai_logger.log_semantic_analysis({
                "risk_level": state.get("risk_level"),
                "intent": state.get("intent"),
                "need_knowledge": state.get("need_knowledge")
            })
            
            # 3. 條件式RAG（0-200ms）
            if state.get("need_knowledge"):
                state = await self.rag(state)
                if state.get("knowledge"):
                    ai_logger.log_retrieved_knowledge([{
                        "content": state["knowledge"],
                        "score": 1.0
                    }])
            
            # 4. 生成回應（<300ms）
            state = await self.generator(state)
            
            # 記錄回應生成（增強版）
            ai_logger.log_response_generation(
                response=state["reply"],
                used_knowledge=bool(state.get("knowledge")),
                response_type=state.get("response_type", "一般對話"),
                length_limit=state.get("response_length_limit", 40)
            )
            
            # 5. 後處理（異步）
            asyncio.create_task(self._post_process(state, user_id, input_text))
            
            # 快取結果
            self.response_cache[cache_key] = state["reply"]
            
            # 效能檢查
            elapsed = time.time() - start_time
            if elapsed > 1.0:
                logger.warning(f"Slow response: {elapsed:.2f}s for '{input_text[:30]}'")
            
            # 記錄完成（增強版：包含字數限制資訊）
            ai_logger.log_final_response(
                final_response=state["reply"],
                processing_time=elapsed,
                response_type=state.get("response_type", "一般對話"),
                length_limit=state.get("response_length_limit", 40)
            )
            
            logger.info(f"Workflow completed in {elapsed:.2f}s: {input_text[:20]} -> {state['reply']}")
            
            return state
            
        except Exception as e:
            logger.error(f"Workflow error: {str(e)}")
            ai_logger.log_error("WORKFLOW", e)
            state["reply"] = "不好意思，我沒聽清楚。"
            state["error"] = str(e)
            return state
    
    async def _post_process(self, state: Dict, user_id: str, input_text: str):
        """異步後處理（不影響回應速度）"""
        try:
            # 儲存記憶
            await self.memory.save(user_id, {
                "user": input_text,
                "bot": state.get("reply", ""),
                "timestamp": datetime.now().isoformat()
            })
            
            # 記錄對話
            logger.info(f"Dialog saved - User: {input_text[:30]}, Bot: {state.get('reply', '')}")
            
        except Exception as e:
            logger.error(f"Post-process error: {e}")


def create_fast_workflow():
    """建立快速工作流程"""
    return CompleteFastWorkflow()