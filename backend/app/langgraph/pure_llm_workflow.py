"""純LLM工作流 - 單次LLM調用完成所有任務"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from cachetools import TTLCache

from app.config import settings
from app.langgraph.state import WorkflowState
from app.services.rag_retriever import RAGRetriever
from app.utils.quality_logger import get_quality_logger

logger = logging.getLogger(__name__)


class PureLLMWorkflow:
    """純LLM工作流 - 一次調用處理所有"""
    
    UNIFIED_PROMPT = """你是「雄i聊」，高雄市毒品防制局的關懷AI助手。

# 你的任務（按順序執行）

## 步驟1：危機與意圖分析
仔細分析用戶訊息，識別：

### 危機等級判斷
- **高危(HIGH)**：
  * 自殺意念：想死、不想活、解脫、結束生命、沒有明天
  * 自傷行為：傷害自己、在頂樓、吃很多藥、割腕
  * 絕望情緒：活著好累、撐不下去、一切都沒意義
  
- **中危(MEDIUM)**：
  * 嚴重情緒困擾但無明確自殺意圖
  * 物質濫用傾向
  
- **低危(LOW)**：一般負面情緒
- **無危(NONE)**：正常對話

### 資訊需求判斷
需要機構資訊時標記need_info=true：
- 詢問電話、地址、機構
- 尋求戒毒、治療資源

## 步驟2：生成回應

### 回應原則
1. **危機優先**：高危必須提供1995專線
2. **簡潔有力**：30-50字為主
3. **溫暖真誠**：像朋友般自然
4. **實用資源**：提供可執行的幫助

### 字數限制
- 危機介入：最多50字（必含1995）
- 情緒支持：最多45字
- 資訊查詢：最多60字
- 一般對話：最多40字

### 官方資源（統一使用）
- 自殺防治專線：1995（24小時）
- 高雄市毒防局：07-713-4000
- 毒防局地址：前金區中正四路211號

# 輸出格式

請以下列格式回應：

##ANALYSIS##
{
  "risk_level": "HIGH/MEDIUM/LOW/NONE",
  "intent": "危機/求助/諮詢/情緒支持/一般對話",
  "need_info": true/false,
  "confidence": 0.0-1.0
}
##RESPONSE##
實際回應內容（遵守字數限制）

# 範例

輸入：「活著好累，想要解脫了」
##ANALYSIS##
{"risk_level": "HIGH", "intent": "危機", "need_info": false, "confidence": 0.95}
##RESPONSE##
聽起來很辛苦，要不要打1995聊聊？24小時都有人陪你。

輸入：「我覺得沒有明天了」
##ANALYSIS##
{"risk_level": "HIGH", "intent": "危機", "need_info": false, "confidence": 0.9}
##RESPONSE##
我在這裡陪你。1995專線24小時都可以打，會有人聽你說。

輸入：「毒防局在哪裡」
##ANALYSIS##
{"risk_level": "NONE", "intent": "諮詢", "need_info": true, "confidence": 0.95}
##RESPONSE##
高雄市毒防局在前金區中正四路211號，電話07-713-4000。

# 當前對話

用戶訊息：{user_message}
對話歷史：{memory}
當前時間：{current_time}

請分析並回應："""

    def __init__(self):
        # 使用GPT-4o確保準確性
        self.llm = ChatOpenAI(
            model="gpt-4o",  # 用最好的模型確保安全
            temperature=0.3,
            max_tokens=200,
            api_key=settings.openai_api_key,
        )
        
        # 選擇性的RAG（僅在need_info時使用）
        self.retriever = RAGRetriever()
        
        # 快取
        self.cache = TTLCache(maxsize=100, ttl=300)
        self.memory_cache = {}
        
        logger.info("PureLLMWorkflow initialized - Single LLM architecture")
    
    async def ainvoke(self, state: WorkflowState) -> WorkflowState:
        """執行純LLM工作流"""
        start_time = time.time()
        
        # 設置UUID
        if not state.get("conversation_id"):
            state["conversation_id"] = str(uuid.uuid4())
        
        try:
            user_message = state.get("input_text", "")
            user_id = state.get("user_id", "default")
            
            # 檢查快取
            cache_key = f"{user_id}:{user_message[:50]}"
            if cache_key in self.cache:
                logger.info("Cache hit")
                state["reply"] = self.cache[cache_key]["response"]
                state["risk_level"] = self.cache[cache_key]["risk_level"]
                return state
            
            # 準備記憶
            memory = self._load_memory(user_id)
            memory_str = self._format_memory(memory) if memory else "無"
            
            # 構建提示
            prompt = self.UNIFIED_PROMPT.format(
                user_message=user_message,
                memory=memory_str,
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # 單次LLM調用
            llm_start = time.time()
            messages = [SystemMessage(content=prompt)]
            response = await self.llm.ainvoke(messages)
            llm_duration = (time.time() - llm_start) * 1000
            
            # 解析回應
            content = response.content
            analysis, reply = self._parse_response(content)
            
            # 如果需要RAG資訊
            if analysis.get("need_info") and analysis.get("intent") in ["諮詢", "求助"]:
                # 快速RAG查詢
                rag_info = await self._quick_rag(user_message)
                if rag_info:
                    # 將RAG資訊整合到回應中
                    reply = self._integrate_rag_info(reply, rag_info)
            
            # 更新狀態
            state["reply"] = reply
            state["risk_level"] = analysis.get("risk_level", "NONE").lower()
            state["intent"] = analysis.get("intent", "一般對話")
            state["analysis"] = analysis
            
            # 儲存快取和記憶
            self.cache[cache_key] = {
                "response": reply,
                "risk_level": state["risk_level"],
                "analysis": analysis
            }
            self._save_memory(user_id, user_message, reply)
            
            # 記錄品質
            quality_logger = get_quality_logger()
            quality_logger.log_conversation(
                conversation_id=state.get("conversation_id"),
                user_input=user_message,
                bot_output=reply,
                user_id=user_id,
                intent=analysis.get("intent", "一般對話"),
                risk_level=analysis.get("risk_level", "NONE").lower()
            )
            
            elapsed = time.time() - start_time
            logger.info(f"Pure LLM completed in {elapsed:.2f}s (LLM: {llm_duration:.0f}ms)")
            logger.info(f"Risk: {analysis.get('risk_level')}, Confidence: {analysis.get('confidence')}")
            
            return state
            
        except Exception as e:
            logger.error(f"Pure LLM error: {str(e)}")
            
            # 緊急fallback - 簡單關鍵字檢測
            if any(word in state.get("input_text", "") for word in ["死", "自殺", "解脫", "結束"]):
                state["reply"] = "聽起來很辛苦，要不要打1995聊聊？24小時都有人陪你。"
                state["risk_level"] = "high"
            else:
                state["reply"] = "不好意思，我需要想一下。能再說一次嗎？"
                state["risk_level"] = "none"
            
            return state
    
    def _parse_response(self, content: str) -> tuple:
        """解析LLM回應"""
        try:
            # 分離分析和回應
            if "##ANALYSIS##" in content and "##RESPONSE##" in content:
                parts = content.split("##ANALYSIS##")[1].split("##RESPONSE##")
                analysis_str = parts[0].strip()
                response_str = parts[1].strip()
                
                # 解析JSON
                analysis = json.loads(analysis_str)
                return analysis, response_str
            else:
                # 如果格式不對，嘗試直接使用
                logger.warning("Response format incorrect, using as-is")
                return {"risk_level": "NONE", "intent": "一般對話"}, content
                
        except Exception as e:
            logger.error(f"Parse error: {str(e)}")
            return {"risk_level": "NONE", "intent": "一般對話"}, content
    
    async def _quick_rag(self, query: str) -> str:
        """快速RAG查詢"""
        try:
            results = await self.retriever.retrieve(
                query=query,
                k=3,
                similarity_threshold=0.4
            )
            if results:
                # 提取關鍵資訊
                info_parts = []
                for r in results[:2]:
                    content = r.content if hasattr(r, 'content') else str(r)
                    if "07-" in content or "地址" in content:
                        info_parts.append(content[:50])
                return "；".join(info_parts) if info_parts else ""
        except:
            return ""
    
    def _integrate_rag_info(self, reply: str, rag_info: str) -> str:
        """整合RAG資訊到回應"""
        # 如果回應中沒有具體資訊，加入RAG資訊
        if "電話" not in reply and "07-" in rag_info:
            # 提取電話
            import re
            phone = re.search(r'07-[\d-]+', rag_info)
            if phone:
                reply += f"，電話{phone.group(0)}"
        return reply[:600]  # 確保不超過長度限制
    
    def _load_memory(self, user_id: str) -> List[Dict]:
        """載入記憶"""
        return self.memory_cache.get(user_id, [])[-3:]
    
    def _save_memory(self, user_id: str, user_msg: str, bot_reply: str):
        """儲存記憶"""
        if user_id not in self.memory_cache:
            self.memory_cache[user_id] = []
        
        self.memory_cache[user_id].extend([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": bot_reply}
        ])
        
        # 限制大小
        if len(self.memory_cache[user_id]) > 10:
            self.memory_cache[user_id] = self.memory_cache[user_id][-10:]
    
    def _format_memory(self, memory: List[Dict]) -> str:
        """格式化記憶"""
        formatted = []
        for msg in memory:
            role = "用戶" if msg.get("role") == "user" else "助理"
            formatted.append(f"{role}：{msg.get('content', '')}")
        return "\n".join(formatted)


def create_pure_llm_workflow():
    """建立純LLM工作流"""
    return PureLLMWorkflow()