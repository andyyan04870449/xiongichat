雄 i 聊 – LangGraph 工作流設計規格書（MVP + 對話留存）
版本：v1.0
日期：2025-08-12
狀態：開發用正式版（內部設計）

1. 設計目標
實現四大功能：

即時聊天與情緒支持

知識庫檢索（RAG）

高風險訊號偵測與通知

個案檔案管理（讀/寫）

對話全程留存（會話、訊息、風險資訊、知識庫來源、個案快照）

所有訊息與會話資料進入 PostgreSQL，供市府平台後續透過 Pull API 拉取

嚴格隔離外部推送（不直接 Push 至平台）

2. 系統邏輯架構
csharp
複製
編輯
[Web API /chat]
    ↓
[LangGraph 工作流引擎]
    ├── ProfileManager（讀取 / 更新個案檔案）
    ├── Router（判斷是否需知識庫檢索 / Profile 更新）
    ├── RAGRetriever（知識庫檢索與摘要）
    ├── RiskDetector（風險偵測與等級分類）
    ├── ChatAgent（生成回覆，含風險與RAG context）
    ├── ConversationLogger（落庫訊息 + 對話關聯）
    └── END
3. LangGraph 節點設計
3.1 ProfileManager
職責：讀取使用者 Profile（cases 表），並處理 Profile 更新

輸入：user_id, wants_profile_update, profile_patch

輸出：profile（dict）

資料存取：

GET cases WHERE user_id = :user_id

更新時：UPDATE cases SET ... WHERE user_id = :user_id

觸發條件：

每次聊天開頭必讀

wants_profile_update = true 時寫回

3.2 Router
職責：

分類使用者輸入意圖（聊天 / 查詢服務 / Profile 修改）

決定是否進行 RAG 檢索

規則：

needs_rag = True 若判斷屬於查詢毒防服務、法律、醫療等資訊

wants_profile_update = True 若判斷輸入涉及變更暱稱、語言、康復目標

輸入：input_text, profile

輸出：needs_rag, wants_profile_update

3.3 RAGRetriever
職責：檢索知識庫，返回摘要與來源

輸入：input_text, profile.lang

輸出：rag_context（List[dict]）

檢索邏輯：

向向量資料庫（PGVector / Faiss）檢索前 5 筆

根據語意分數與地區（profile.lang + 個案地區欄位）加權

壓縮成短段落，附 {title, source, date}

3.4 RiskDetector
職責：偵測風險訊號（自殺 / 暴力 / 用藥 / 犯罪等）

輸入：input_text, profile.lang

輸出：

json
複製
編輯
{
  "level": "NONE|LOW|MEDIUM|HIGH|IMMINENT",
  "categories": ["self_harm", "drug_use", ...],
  "evidence": ["keyword:...", "model:score=0.91"]
}
偵測方式：

第一層：規則 / 關鍵字匹配

第二層：LLM 分類器

最終等級：取較高者

3.5 ChatAgent
職責：生成回覆內容

輸入：input_text, profile, rag_context, risk

行為：

若 risk.level >= MEDIUM，在回覆中附安全引導與資源

若 needs_rag=True，融合 rag_context 內容

回覆語言根據 profile.lang

輸出：reply

3.6 ConversationLogger
職責：

寫入 conversation_messages 表（user/assistant 各一筆）

更新 conversations 表（last_message_at, updated_at）

輸入：

user_message（原文＋脫敏版）、assistant_reply（原文＋脫敏版）

risk、rag_sources、profile_snapshot

寫入：

若會話不存在 → 新增 conversations 記錄

寫入 user 訊息（含 risk / rag_sources）

寫入 assistant 訊息（含 rag_sources / profile_snapshot）

更新 conversations.last_message_at

4. 狀態結構（State）
python
複製
編輯
class State(TypedDict):
    user_id: str
    conversation_id: Optional[str]
    input_text: str
    profile: dict
    needs_rag: bool
    wants_profile_update: bool
    profile_patch: dict
    rag_context: List[dict]
    risk: dict
    reply: str
    error: Optional[str]
5. 節點流程（LangGraph 邊設計）
sql
複製
編輯
START → ProfileManager → Router
    ├── needs_rag=True → RAGRetriever → RiskDetector → ChatAgent → ConversationLogger → END
    └── needs_rag=False → RiskDetector → ChatAgent → ConversationLogger → END
6. 持久化與檢查點
Checkpointer：

SQLite / Postgres 版（建議 Postgres）

鍵：(user_id, conversation_id)

對話記憶策略：

Summary Memory：每 N 輪壓縮舊訊息

僅保留必要上下文給 ChatAgent，完整對話依賴 conversation_messages 表

7. 安全考量
PII 處理：

所有存入 content_redacted 欄位的資料需先經脫敏處理

原文 content 欄位可應用層加密（KMS）

權限隔離：

LangGraph 僅寫本系統資料庫，不直接呼叫市府平台 API

審計：

每次風險偵測結果 + 回覆存入 DB，方便日後對帳與稽核

8. 與 API 對接
LangGraph 執行完一輪後：

回覆即時回傳至 /chat API 呼叫方（Web 客戶端）

所有對話資料寫入 DB，供 §平台拉取規格書的 API 提供資料

對外 API（給 Web）：

POST /chat 接入點 → 呼叫 LangGraph → 回傳：

json
複製
編輯
{
  "conversation_id": "CONV-UUID",
  "user_message_id": "MSG-UUID-USER",
  "assistant_message_id": "MSG-UUID-AI",
  "reply": "我理解你最近壓力很大...",
  "risk": { "level": "LOW", "categories": [] }
}
9. 測試與驗收
功能測試：

RAG 檢索結果正確率（≥ 90% 主題相符）

風險偵測誤判率 ≤ 5%

Profile 更新正確落庫

性能測試：

單輪對話延遲 P95 ≤ 1.5 秒（含檢索與風險偵測）

資料驗證：

所有訊息正確關聯 conversation_id

content_redacted 無未遮罩敏感詞

