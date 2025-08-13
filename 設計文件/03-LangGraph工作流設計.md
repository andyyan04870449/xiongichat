# 03 - LangGraph 工作流設計文件

## 快速恢復指南
如果你忘記了這個模組，記住：這是系統的核心 AI 引擎，使用 LangGraph 構建工作流，包含 6 個節點：ProfileManager、Router、RAGRetriever、RiskDetector、ChatAgent、ConversationLogger。

## 核心技術棧
- LangGraph (工作流引擎)
- LangChain (LLM 整合)
- OpenAI GPT-4o (主要聊天模型)
- OpenAI GPT-4o-mini (工具模型)
- pgvector (向量檢索)

## LLM 模型選擇策略

### 模型分配原則
- **GPT-4o**: 用於主要聊天回應（ChatAgent），確保回覆品質
- **GPT-4o-mini**: 用於工具節點（Router、RiskDetector、RAGRetriever），降低成本

### 節點模型配置
| 節點 | 模型 | 原因 |
|-----|------|------|
| ChatAgent | gpt-4o | 需要高品質、同理心的回覆 |
| Router | gpt-4o-mini | 簡單分類任務 |
| RiskDetector | gpt-4o-mini | 規則為主，LLM輔助 |
| RAGRetriever | gpt-4o-mini | 僅用於重排序 |
| ProfileManager | 無需LLM | 資料庫CRUD操作 |
| ConversationLogger | 無需LLM | 資料庫儲存操作 |

## 專案結構
```
langgraph_workflow/
├── __init__.py
├── state.py            # 狀態定義
├── nodes/              # 各節點實作
│   ├── profile_manager.py
│   ├── router.py
│   ├── rag_retriever.py
│   ├── risk_detector.py
│   ├── chat_agent.py
│   └── conversation_logger.py
├── graph.py            # 工作流組裝
├── prompts/            # Prompt 模板
│   ├── router_prompt.py
│   ├── risk_prompt.py
│   └── chat_prompt.py
└── utils/
    ├── embeddings.py   # 向量嵌入
    └── memory.py       # 對話記憶管理
```

## 狀態定義

```python
# state.py
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class WorkflowState(TypedDict):
    # 輸入
    user_id: str
    conversation_id: Optional[UUID]
    input_text: str
    lang: str
    
    # 個案資料
    profile: Dict[str, Any]
    
    # 路由決策
    needs_rag: bool
    wants_profile_update: bool
    profile_patch: Dict[str, Any]
    
    # RAG 結果
    rag_context: List[Dict[str, Any]]
    
    # 風險評估
    risk: Dict[str, Any]
    
    # 生成回覆
    reply: str
    
    # 訊息 ID
    user_message_id: UUID
    assistant_message_id: UUID
    
    # 錯誤處理
    error: Optional[str]
    
    # 內部狀態
    _memory: Optional[List[Dict]]  # 對話歷史
    _timestamp: datetime
```

## Node 1: ProfileManager

```python
# nodes/profile_manager.py
from langchain.schema import BaseMessage
from typing import Dict, Any
import json

class ProfileManagerNode:
    """
    負責讀取和更新個案檔案
    """
    
    def __init__(self, db_helper):
        self.db = db_helper
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行節點邏輯"""
        try:
            # 讀取個案檔案
            profile = await self.db.get_user_profile(state["user_id"])
            
            if not profile:
                # 建立新個案
                profile = await self.db.create_user_profile(
                    user_id=state["user_id"],
                    lang=state.get("lang", "zh-TW")
                )
            
            state["profile"] = {
                "user_id": profile.user_id,
                "nickname": profile.nickname,
                "lang": profile.lang,
                "stage": profile.stage,
                "goals": profile.goals,
                "updated_at": profile.updated_at.isoformat()
            }
            
            # 如果需要更新檔案
            if state.get("wants_profile_update") and state.get("profile_patch"):
                await self._update_profile(
                    state["user_id"], 
                    state["profile_patch"]
                )
                # 更新 state 中的 profile
                state["profile"].update(state["profile_patch"])
            
        except Exception as e:
            state["error"] = f"ProfileManager error: {str(e)}"
            
        return state
    
    async def _update_profile(self, user_id: str, patch: Dict):
        """更新個案檔案"""
        allowed_fields = ["nickname", "lang", "stage", "goals"]
        
        update_data = {
            k: v for k, v in patch.items() 
            if k in allowed_fields
        }
        
        if update_data:
            await self.db.update_user_profile(user_id, update_data)
```

## Node 2: Router

```python
# nodes/router.py
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from prompts.router_prompt import ROUTER_SYSTEM_PROMPT

class RouterNode:
    """
    分析使用者意圖，決定工作流路徑
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # 使用較小模型進行路由判斷
            temperature=0.1,
            max_tokens=200
        )
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """判斷是否需要 RAG 或更新 Profile"""
        
        try:
            # 構建 prompt
            messages = [
                SystemMessage(content=ROUTER_SYSTEM_PROMPT),
                HumanMessage(content=f"""
使用者輸入: {state["input_text"]}
使用者語言: {state["profile"]["lang"]}
當前階段: {state["profile"]["stage"]}

請分析以下幾點:
1. 是否需要查詢知識庫 (毒防服務、法律、醫療資訊等)
2. 是否要更新個案檔案 (暱稱、語言、目標等)

回應格式:
{{
    "needs_rag": true/false,
    "wants_profile_update": true/false,
    "profile_patch": {{}},
    "reasoning": "簡短說明"
}}
                """)
            ]
            
            # 呼叫 LLM
            response = await self.llm.ainvoke(messages)
            result = json.loads(response.content)
            
            state["needs_rag"] = result.get("needs_rag", False)
            state["wants_profile_update"] = result.get("wants_profile_update", False)
            state["profile_patch"] = result.get("profile_patch", {})
            
        except Exception as e:
            # 預設不需要 RAG
            state["needs_rag"] = False
            state["wants_profile_update"] = False
            state["error"] = f"Router error: {str(e)}"
        
        return state
```

## Node 3: RAGRetriever

```python
# nodes/rag_retriever.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import PGVector
from typing import List, Dict

class RAGRetrieverNode:
    """
    向量檢索相關知識
    """
    
    def __init__(self, connection_string: str):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        
        self.vectorstore = PGVector(
            connection_string=connection_string,
            embedding_function=self.embeddings,
            collection_name="rag_documents",
            distance_strategy="cosine"
        )
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行檢索"""
        
        # 如果不需要 RAG，直接返回
        if not state.get("needs_rag", False):
            state["rag_context"] = []
            return state
        
        try:
            # 構建查詢
            query = self._build_query(state["input_text"], state["profile"])
            
            # 向量檢索
            docs = await self.vectorstore.asimilarity_search_with_score(
                query,
                k=5,
                filter={
                    "lang": state["profile"]["lang"]  # 語言過濾
                }
            )
            
            # 格式化結果
            rag_context = []
            for doc, score in docs:
                if score > 0.7:  # 相似度閾值
                    rag_context.append({
                        "title": doc.metadata.get("title", ""),
                        "content": self._truncate(doc.page_content, 500),
                        "source": doc.metadata.get("source", ""),
                        "date": doc.metadata.get("published_date", ""),
                        "score": float(score)
                    })
            
            state["rag_context"] = rag_context[:3]  # 最多 3 筆
            
        except Exception as e:
            state["rag_context"] = []
            state["error"] = f"RAG error: {str(e)}"
        
        return state
    
    def _build_query(self, input_text: str, profile: Dict) -> str:
        """增強查詢"""
        # 可根據個案階段調整查詢
        stage_keywords = {
            "assessment": "評估 初診 檢測",
            "treatment": "治療 戒治 復健",
            "recovery": "康復 追蹤 社會復歸"
        }
        
        keywords = stage_keywords.get(profile.get("stage", ""), "")
        return f"{input_text} {keywords}".strip()
    
    def _truncate(self, text: str, max_length: int) -> str:
        """截斷文字"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
```

## Node 4: RiskDetector

```python
# nodes/risk_detector.py
import re
from typing import Dict, List
from langchain.chat_models import ChatOpenAI
from prompts.risk_prompt import RISK_DETECTION_PROMPT

class RiskDetectorNode:
    """
    偵測風險訊號
    """
    
    # 風險關鍵字 (多語言)
    RISK_KEYWORDS = {
        "self_harm": {
            "zh-TW": ["自殺", "自殘", "結束生命", "不想活"],
            "en": ["suicide", "kill myself", "end my life"]
        },
        "drug_use": {
            "zh-TW": ["吸毒", "用藥", "海洛因", "安非他命"],
            "en": ["heroin", "meth", "cocaine", "using drugs"]
        },
        "violence": {
            "zh-TW": ["打人", "傷害", "報復", "殺"],
            "en": ["hurt", "kill", "revenge", "attack"]
        }
    }
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # 使用較小模型進行風險分類
            temperature=0,
            max_tokens=300
        )
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """執行風險偵測"""
        
        try:
            # 第一層：規則檢測
            rule_result = self._rule_based_detection(
                state["input_text"], 
                state["profile"]["lang"]
            )
            
            # 第二層：LLM 檢測
            llm_result = await self._llm_based_detection(
                state["input_text"],
                state["profile"]
            )
            
            # 合併結果 (取較高風險)
            final_level = self._get_higher_risk_level(
                rule_result["level"],
                llm_result["level"]
            )
            
            # 合併證據
            categories = list(set(
                rule_result["categories"] + llm_result["categories"]
            ))
            
            evidence = {
                "rule_based": rule_result.get("evidence", []),
                "llm_based": llm_result.get("evidence", {})
            }
            
            state["risk"] = {
                "level": final_level,
                "categories": categories,
                "evidence": evidence
            }
            
            # 高風險時記錄特殊事件
            if final_level in ["HIGH", "IMMINENT"]:
                await self._log_high_risk_event(state)
            
        except Exception as e:
            state["risk"] = {
                "level": "NONE",
                "categories": [],
                "evidence": {"error": str(e)}
            }
        
        return state
    
    def _rule_based_detection(self, text: str, lang: str) -> Dict:
        """基於規則的風險檢測"""
        detected_categories = []
        evidence = []
        
        for category, keywords_dict in self.RISK_KEYWORDS.items():
            keywords = keywords_dict.get(lang, keywords_dict.get("zh-TW", []))
            
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    detected_categories.append(category)
                    evidence.append(f"keyword:{keyword}")
                    break
        
        # 判斷風險等級
        if "self_harm" in detected_categories:
            level = "HIGH"
        elif detected_categories:
            level = "MEDIUM"
        else:
            level = "NONE"
        
        return {
            "level": level,
            "categories": detected_categories,
            "evidence": evidence
        }
    
    async def _llm_based_detection(self, text: str, profile: Dict) -> Dict:
        """基於 LLM 的風險檢測"""
        
        messages = [
            SystemMessage(content=RISK_DETECTION_PROMPT),
            HumanMessage(content=f"""
分析以下訊息的風險等級:

訊息: {text}
使用者階段: {profile.get('stage', 'unknown')}

請回應 JSON 格式:
{{
    "level": "NONE/LOW/MEDIUM/HIGH/IMMINENT",
    "categories": [],
    "confidence": 0.0-1.0,
    "reasoning": "簡短說明"
}}
            """)
        ]
        
        response = await self.llm.ainvoke(messages)
        result = json.loads(response.content)
        
        return {
            "level": result.get("level", "NONE"),
            "categories": result.get("categories", []),
            "evidence": {
                "confidence": result.get("confidence", 0),
                "reasoning": result.get("reasoning", "")
            }
        }
    
    def _get_higher_risk_level(self, level1: str, level2: str) -> str:
        """取較高風險等級"""
        levels = ["NONE", "LOW", "MEDIUM", "HIGH", "IMMINENT"]
        idx1 = levels.index(level1) if level1 in levels else 0
        idx2 = levels.index(level2) if level2 in levels else 0
        return levels[max(idx1, idx2)]
    
    async def _log_high_risk_event(self, state: WorkflowState):
        """記錄高風險事件"""
        # TODO: 寫入專門的高風險事件表
        pass
```

## Node 5: ChatAgent

```python
# nodes/chat_agent.py
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.memory import ConversationSummaryBufferMemory
from prompts.chat_prompt import get_chat_prompt

class ChatAgentNode:
    """
    生成聊天回覆
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",  # 使用最佳模型生成高品質回覆
            temperature=0.7,
            max_tokens=800
        )
        
        # 對話記憶管理
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=2000,
            return_messages=True
        )
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """生成回覆"""
        
        try:
            # 取得對話歷史
            memory_messages = await self._get_conversation_memory(
                state["conversation_id"]
            )
            
            # 構建系統 prompt
            system_prompt = get_chat_prompt(
                profile=state["profile"],
                risk_level=state["risk"]["level"],
                has_rag=bool(state.get("rag_context"))
            )
            
            # 構建訊息
            messages = [SystemMessage(content=system_prompt)]
            
            # 加入對話歷史 (最近 5 輪)
            messages.extend(memory_messages[-10:])
            
            # 構建當前輸入
            user_content = self._build_user_message(state)
            messages.append(HumanMessage(content=user_content))
            
            # 呼叫 LLM
            response = await self.llm.ainvoke(messages)
            
            # 處理高風險情況
            if state["risk"]["level"] in ["HIGH", "IMMINENT"]:
                response.content = self._add_crisis_resources(
                    response.content,
                    state["profile"]["lang"]
                )
            
            state["reply"] = response.content
            
            # 更新記憶
            await self._update_memory(
                state["conversation_id"],
                user_content,
                response.content
            )
            
        except Exception as e:
            state["reply"] = self._get_fallback_reply(
                state["profile"]["lang"]
            )
            state["error"] = f"ChatAgent error: {str(e)}"
        
        return state
    
    def _build_user_message(self, state: WorkflowState) -> str:
        """構建使用者訊息 (含 RAG context)"""
        
        message = state["input_text"]
        
        # 加入 RAG 結果
        if state.get("rag_context"):
            context_str = "\n\n相關資訊:\n"
            for ctx in state["rag_context"]:
                context_str += f"- {ctx['title']}: {ctx['content'][:200]}...\n"
                context_str += f"  來源: {ctx['source']}\n"
            
            message = f"{message}\n{context_str}"
        
        return message
    
    def _add_crisis_resources(self, reply: str, lang: str) -> str:
        """加入危機資源"""
        
        resources = {
            "zh-TW": """

💚 如果您需要立即協助：
- 生命線協談專線：1995
- 張老師專線：1980
- 安心專線：1925
- 緊急就醫：119

我們關心您，請記得您並不孤單。
            """,
            "en": """

💚 If you need immediate help:
- Lifeline: 1995
- Teacher Zhang Hotline: 1980
- Mental Health Hotline: 1925
- Emergency: 119

We care about you. Remember, you're not alone.
            """
        }
        
        return reply + resources.get(lang, resources["zh-TW"])
    
    def _get_fallback_reply(self, lang: str) -> str:
        """錯誤時的預設回覆"""
        
        fallbacks = {
            "zh-TW": "抱歉，我現在無法處理您的訊息。請稍後再試，或聯繫我們的服務人員。",
            "en": "Sorry, I cannot process your message right now. Please try again later or contact our support."
        }
        
        return fallbacks.get(lang, fallbacks["zh-TW"])
    
    async def _get_conversation_memory(self, conversation_id: UUID) -> List:
        """取得對話記憶"""
        # TODO: 從資料庫載入對話歷史
        return []
    
    async def _update_memory(self, conversation_id: UUID, user_msg: str, ai_msg: str):
        """更新對話記憶"""
        # TODO: 儲存到快取或資料庫
        pass
```

## Node 6: ConversationLogger

```python
# nodes/conversation_logger.py
from uuid import uuid4
from datetime import datetime

class ConversationLoggerNode:
    """
    儲存對話到資料庫
    """
    
    def __init__(self, db_helper):
        self.db = db_helper
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """儲存訊息"""
        
        try:
            # 產生訊息 ID
            state["user_message_id"] = uuid4()
            state["assistant_message_id"] = uuid4()
            
            # 儲存到資料庫
            await self.db.save_message_pair(
                conversation_id=state["conversation_id"],
                user_content=state["input_text"],
                assistant_content=state["reply"],
                risk_info=state["risk"],
                rag_sources=state.get("rag_context", []),
                profile_snapshot=state["profile"]
            )
            
            # 更新會話時間
            await self.db.update_conversation_timestamp(
                state["conversation_id"]
            )
            
        except Exception as e:
            state["error"] = f"Logger error: {str(e)}"
            # 即使儲存失敗也不影響回覆
        
        return state
```

## 工作流組裝

```python
# graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from nodes import *

def create_workflow(db_helper, connection_string):
    """建立 LangGraph 工作流"""
    
    # 初始化節點
    profile_manager = ProfileManagerNode(db_helper)
    router = RouterNode()
    rag_retriever = RAGRetrieverNode(connection_string)
    risk_detector = RiskDetectorNode()
    chat_agent = ChatAgentNode()
    conversation_logger = ConversationLoggerNode(db_helper)
    
    # 建立工作流
    workflow = StateGraph(WorkflowState)
    
    # 加入節點
    workflow.add_node("profile_manager", profile_manager)
    workflow.add_node("router", router)
    workflow.add_node("rag_retriever", rag_retriever)
    workflow.add_node("risk_detector", risk_detector)
    workflow.add_node("chat_agent", chat_agent)
    workflow.add_node("conversation_logger", conversation_logger)
    
    # 定義邊 (流程)
    workflow.set_entry_point("profile_manager")
    
    workflow.add_edge("profile_manager", "router")
    
    # 條件路由
    workflow.add_conditional_edges(
        "router",
        lambda x: "rag_retriever" if x["needs_rag"] else "risk_detector",
        {
            "rag_retriever": "rag_retriever",
            "risk_detector": "risk_detector"
        }
    )
    
    workflow.add_edge("rag_retriever", "risk_detector")
    workflow.add_edge("risk_detector", "chat_agent")
    workflow.add_edge("chat_agent", "conversation_logger")
    workflow.add_edge("conversation_logger", END)
    
    # 設定檢查點 (用於狀態持久化)
    checkpointer = PostgresSaver.from_conn_string(connection_string)
    
    # 編譯工作流
    app = workflow.compile(checkpointer=checkpointer)
    
    return app

# 主要入口
async def process_chat(
    user_id: str,
    conversation_id: str,
    input_text: str,
    lang: str = "zh-TW"
) -> dict:
    """處理聊天請求"""
    
    # 初始化工作流
    app = create_workflow(db_helper, connection_string)
    
    # 準備初始狀態
    initial_state = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "input_text": input_text,
        "lang": lang,
        "_timestamp": datetime.utcnow()
    }
    
    # 執行工作流
    config = {
        "configurable": {
            "thread_id": f"{user_id}:{conversation_id}"
        }
    }
    
    result = await app.ainvoke(initial_state, config)
    
    # 返回結果
    return {
        "conversation_id": result["conversation_id"],
        "user_message_id": result["user_message_id"],
        "assistant_message_id": result["assistant_message_id"],
        "reply": result["reply"],
        "risk": result["risk"],
        "rag_sources": result.get("rag_context", []),
        "profile_snapshot": result["profile"]
    }
```

## Prompt 模板

```python
# prompts/chat_prompt.py

def get_chat_prompt(profile: dict, risk_level: str, has_rag: bool) -> str:
    """取得聊天系統 prompt"""
    
    base_prompt = f"""你是「雄i聊」，高雄市毒品防制局的 AI 助理。
你的任務是提供溫暖、專業、不批判的支持給正在康復路上的個案。

個案資訊：
- 暱稱：{profile.get('nickname', '朋友')}
- 語言：{profile.get('lang', 'zh-TW')}
- 階段：{profile.get('stage', 'unknown')}
- 目標：{', '.join(profile.get('goals', []))}

對話原則：
1. 使用溫暖、同理心的語氣
2. 不批判、不說教
3. 提供實用的建議和資源
4. 鼓勵正向行為
5. 適時關心個案狀況
"""
    
    # 根據風險等級調整
    if risk_level in ["HIGH", "IMMINENT"]:
        base_prompt += """

⚠️ 偵測到高風險訊號 ⚠️
- 優先確保個案安全
- 提供緊急資源連結
- 使用穩定、冷靜的語氣
- 避免刺激性言語
"""
    
    # 如果有 RAG 結果
    if has_rag:
        base_prompt += """

請參考提供的相關資訊回答，但要用自己的話重新組織，
不要直接複製貼上。確保資訊的準確性和時效性。
"""
    
    return base_prompt
```

## 關鍵記憶點
1. **必須**為每個節點加入錯誤處理，單一節點失敗不影響整體
2. **記得** LangGraph 使用 thread_id 管理對話狀態
3. **注意**高風險訊息需要特殊處理和記錄
4. **重要** RAG 檢索要考慮語言和個案階段