# API 測試需求規格書

## 測試環境配置
- **測試資料庫**: xiongichat_test
- **測試用戶**: test_user_001 ~ test_user_100
- **API基礎路徑**: http://localhost:8000/api/v1

---

## 🔷 第一階段：基礎聊天 API

### API: POST /chat

#### TC001
- **測試名稱**: 新對話建立測試
- **目的**: 驗證系統能正確建立新對話並返回回覆
- **輸入**:
  ```json
  {
    "user_id": "test_user_001",
    "message": "你好，我是新用戶"
  }
  ```
- **預期輸出**:
  ```json
  {
    "conversation_id": "uuid格式",
    "user_message_id": "uuid格式",
    "assistant_message_id": "uuid格式",
    "reply": "包含歡迎詞的回覆內容"
  }
  ```

#### TC002
- **測試名稱**: 延續對話測試
- **目的**: 驗證系統能記住之前的對話內容
- **輸入**:
  ```json
  {
    "user_id": "test_user_001",
    "conversation_id": "{TC001返回的conversation_id}",
    "message": "我剛剛說了什麼？"
  }
  ```
- **預期輸出**:
  ```json
  {
    "conversation_id": "與輸入相同",
    "reply": "包含「新用戶」相關內容"
  }
  ```

#### TC003[暫緩實施]
- **測試名稱**: 長文本輸入測試
- **目的**: 驗證系統能處理超長輸入
- **輸入**:
  ```json
  {
    "user_id": "test_user_002",
    "message": "重複1000字的長文本..."
  }
  ```
- **預期輸出**:
  ```json
  {
    "reply": "正常回覆，不會因長度出錯"
  }
  ```

#### TC004
- **測試名稱**: 空訊息測試
- **目的**: 驗證輸入驗證機制
- **輸入**:
  ```json
  {
    "user_id": "test_user_003",
    "message": ""
  }
  ```
- **預期輸出**:
  ```json
  {
    "error": "訊息不能為空",
    "status_code": 400
  }
  ```

#### TC005
- **測試名稱**: 記憶窗口測試
- **目的**: 驗證只記住最近10輪對話
- **輸入**: 連續發送15輪對話，第16輪詢問第1輪內容
- **預期輸出**: 系統不記得第1輪的內容

### API: GET /conversations/{conversation_id}

#### TC006
- **測試名稱**: 取得對話歷史測試
- **目的**: 驗證能正確返回對話歷史
- **輸入**: 
  ```
  GET /conversations/{valid_conversation_id}
  ```
- **預期輸出**:
  ```json
  {
    "conversation_id": "匹配輸入",
    "started_at": "時間戳",
    "messages": [
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."}
    ]
  }
  ```

#### TC007
- **測試名稱**: 無效對話ID測試
- **目的**: 驗證錯誤處理
- **輸入**:
  ```
  GET /conversations/invalid-uuid
  ```
- **預期輸出**:
  ```json
  {
    "error": "對話不存在",
    "status_code": 404
  }
  ```

---

## 🔷 第二階段：RAG 檢索 API

### API: POST /knowledge/search

#### TC008
- **測試名稱**: 相關知識檢索測試
- **目的**: 驗證能檢索到相關毒防服務資訊
- **輸入**:
  ```json
  {
    "query": "高雄市毒防中心地址",
    "k": 5
  }
  ```
- **預期輸出**:
  ```json
  {
    "results": [
      {
        "content": "包含地址資訊",
        "relevance_score": "> 0.7",
        "source": "資料來源",
        "metadata": {}
      }
    ]
  }
  ```

#### TC009
- **測試名稱**: 無相關結果測試
- **目的**: 驗證無相關內容時的處理
- **輸入**:
  ```json
  {
    "query": "完全無關xyz123",
    "k": 5
  }
  ```
- **預期輸出**:
  ```json
  {
    "results": [],
    "message": "未找到相關資訊"
  }
  ```

#### TC010
- **測試名稱**: 多語言檢索測試
- **目的**: 驗證支援不同語言檢索
- **輸入**:
  ```json
  {
    "query": "methadone treatment",
    "k": 3,
    "lang": "en"
  }
  ```
- **預期輸出**: 返回英文相關內容

### API: POST /knowledge/upload

#### TC011
- **測試名稱**: PDF上傳測試
- **目的**: 驗證能正確處理PDF檔案
- **輸入**: 
  ```
  FormData: {
    file: "test_document.pdf",
    category: "medical"
  }
  ```
- **預期輸出**:
  ```json
  {
    "status": "success",
    "chunks_created": 10,
    "document_id": "uuid"
  }
  ```

#### TC012
- **測試名稱**: 檔案大小限制測試
- **目的**: 驗證檔案大小限制
- **輸入**: 超過10MB的檔案
- **預期輸出**:
  ```json
  {
    "error": "檔案大小超過限制",
    "max_size": "10MB",
    "status_code": 413
  }
  ```

---

## 🔷 第三階段：風險偵測與個案管理 API

### API: POST /chat (含風險偵測)

#### TC013
- **測試名稱**: 高風險內容偵測測試
- **目的**: 驗證能識別自殺相關內容
- **輸入**:
  ```json
  {
    "user_id": "test_user_004",
    "message": "我想要結束生命"
  }
  ```
- **預期輸出**:
  ```json
  {
    "reply": "包含關懷和求助資源",
    "risk": {
      "level": "HIGH",
      "categories": ["self_harm"]
    }
  }
  ```

#### TC014
- **測試名稱**: 藥物使用風險測試
- **目的**: 驗證能識別藥物相關風險
- **輸入**:
  ```json
  {
    "user_id": "test_user_005",
    "message": "我想再用一次海洛因"
  }
  ```
- **預期輸出**:
  ```json
  {
    "risk": {
      "level": "MEDIUM",
      "categories": ["drug_use"]
    }
  }
  ```

#### TC015
- **測試名稱**: 多重風險測試
- **目的**: 驗證能同時識別多種風險
- **輸入**:
  ```json
  {
    "message": "吸毒後想去打人"
  }
  ```
- **預期輸出**:
  ```json
  {
    "risk": {
      "categories": ["drug_use", "violence"]
    }
  }
  ```

### API: GET /cases/{user_id}

#### TC016
- **測試名稱**: 個案檔案查詢測試
- **目的**: 驗證能取得個案資料
- **輸入**:
  ```
  GET /cases/test_user_001
  ```
- **預期輸出**:
  ```json
  {
    "user_id": "test_user_001",
    "nickname": "測試用戶",
    "lang": "zh-TW",
    "stage": "assessment",
    "goals": ["維持清醒", "求職"]
  }
  ```

### API: PUT /cases/{user_id}

#### TC017
- **測試名稱**: 個案資料更新測試
- **目的**: 驗證能更新個案狀態
- **輸入**:
  ```json
  {
    "stage": "treatment",
    "goals": ["維持清醒", "家庭和諧"]
  }
  ```
- **預期輸出**:
  ```json
  {
    "status": "updated",
    "user_id": "test_user_001"
  }
  ```

### API: GET /risk-events

#### TC018
- **測試名稱**: 風險事件查詢測試
- **目的**: 驗證能查詢風險事件記錄
- **輸入**:
  ```
  GET /risk-events?level=HIGH&date_from=2024-01-01
  ```
- **預期輸出**:
  ```json
  {
    "events": [
      {
        "id": "uuid",
        "user_id": "匿名化ID",
        "risk_level": "HIGH",
        "detected_at": "時間戳",
        "categories": ["self_harm"]
      }
    ],
    "total": 5
  }
  ```

---

## 🔷 第四階段：安全與同步 API

### API: POST /auth/token

#### TC019
- **測試名稱**: Token生成測試
- **目的**: 驗證能生成有效JWT
- **輸入**:
  ```json
  {
    "client_id": "kao-platform",
    "client_secret": "test-secret",
    "scopes": ["messages.read"]
  }
  ```
- **預期輸出**:
  ```json
  {
    "access_token": "JWT格式",
    "token_type": "Bearer",
    "expires_in": 3600
  }
  ```

#### TC020
- **測試名稱**: 無效憑證測試
- **目的**: 驗證錯誤憑證被拒絕
- **輸入**:
  ```json
  {
    "client_id": "invalid",
    "client_secret": "wrong"
  }
  ```
- **預期輸出**:
  ```json
  {
    "error": "invalid_client",
    "status_code": 401
  }
  ```

### API: GET /api/v1/conversations (Pull API)

#### TC021
- **測試名稱**: 增量同步測試
- **目的**: 驗證能取得更新後的對話
- **輸入**:
  ```
  GET /api/v1/conversations?updated_after=2024-01-01T00:00:00Z
  Headers: Authorization: Bearer {token}
  ```
- **預期輸出**:
  ```json
  {
    "items": [
      {
        "id": "uuid",
        "user_id": "user_id",
        "updated_at": "> 輸入時間"
      }
    ],
    "next_cursor": "opaque_string"
  }
  ```

#### TC022
- **測試名稱**: 分頁測試
- **目的**: 驗證分頁機制正常
- **輸入**:
  ```
  GET /api/v1/conversations?page_size=10&cursor={from_TC021}
  ```
- **預期輸出**: 返回下一頁資料

#### TC023
- **測試名稱**: 權限範圍測試
- **目的**: 驗證不同scope的存取限制
- **輸入**: 
  ```
  Token with scope: messages.read
  GET /api/v1/messages/123?include=content
  ```
- **預期輸出**:
  ```json
  {
    "error": "forbidden_scope",
    "required_scope": "messages.read_full",
    "status_code": 403
  }
  ```

### API: GET /api/v1/messages

#### TC024
- **測試名稱**: 訊息批次取得測試
- **目的**: 驗證能批次取得訊息
- **輸入**:
  ```
  GET /api/v1/messages?updated_after=2024-01-01&risk_min=MEDIUM
  ```
- **預期輸出**:
  ```json
  {
    "items": [
      {
        "content_redacted": "脫敏內容",
        "risk": {"level": ">= MEDIUM"}
      }
    ]
  }
  ```

### API: GET /audit-logs

#### TC025
- **測試名稱**: 審計日誌查詢測試
- **目的**: 驗證審計記錄完整性
- **輸入**:
  ```
  GET /audit-logs?action=full_content_access
  ```
- **預期輸出**:
  ```json
  {
    "logs": [
      {
        "timestamp": "時間戳",
        "client_id": "客戶端ID",
        "action": "full_content_access",
        "resource": "message:uuid"
      }
    ]
  }
  ```

---

## 🔷 第五階段：脫敏 API

### API: GET /messages/{id} (with redaction)

#### TC026
- **測試名稱**: 自動脫敏測試
- **目的**: 驗證預設返回脫敏內容
- **輸入**:
  ```
  GET /messages/{id}
  Token scope: messages.read
  ```
- **預期輸出**:
  ```json
  {
    "content": "我是王○○，電話09XX-XXX-XXX",
    "original_available": false
  }
  ```

#### TC027
- **測試名稱**: 完整內容存取測試
- **目的**: 驗證特殊權限可取得原文
- **輸入**:
  ```
  GET /messages/{id}?include=content
  Token scope: messages.read_full
  ```
- **預期輸出**:
  ```json
  {
    "content": "我是王大明，電話0912345678",
    "access_logged": true
  }
  ```

### API: POST /redaction/preview

#### TC028
- **測試名稱**: 脫敏預覽測試
- **目的**: 驗證脫敏效果預覽
- **輸入**:
  ```json
  {
    "text": "身分證A123456789，信箱test@example.com"
  }
  ```
- **預期輸出**:
  ```json
  {
    "original": "身分證A123456789，信箱test@example.com",
    "redacted": "身分證[身分證]，信箱[email]",
    "found_items": [
      {"type": "tw_id", "position": [3, 13]},
      {"type": "email", "position": [16, 32]}
    ]
  }
  ```

### API: PUT /redaction/rules

#### TC029
- **測試名稱**: 脫敏規則更新測試
- **目的**: 驗證能動態更新脫敏規則
- **輸入**:
  ```json
  {
    "rule_name": "custom_pattern",
    "pattern": "TEST\\d{4}",
    "replacement": "[TEST_ID]"
  }
  ```
- **預期輸出**:
  ```json
  {
    "status": "rule_updated",
    "active_rules": 25
  }
  ```

---

## 🔷 性能測試需求

### API: POST /chat

#### PT001
- **測試名稱**: 回應時間測試
- **目的**: 驗證回應時間符合SLA
- **輸入**: 100個並發請求
- **預期輸出**: P95 < 2秒，P99 < 3秒

### API: POST /knowledge/search

#### PT002
- **測試名稱**: 檢索速度測試
- **目的**: 驗證檢索效能
- **輸入**: 50個並發檢索請求
- **預期輸出**: P95 < 500ms

### API: GET /api/v1/conversations

#### PT003
- **測試名稱**: 大量資料同步測試
- **目的**: 驗證能處理大量資料
- **輸入**: 請求10000筆記錄
- **預期輸出**: 單頁(1000筆) < 800ms

---

## 🔷 錯誤處理測試

### 通用錯誤測試

#### ERR001
- **測試名稱**: 網路逾時測試
- **目的**: 驗證逾時處理
- **輸入**: 延遲30秒的請求
- **預期輸出**: 
  ```json
  {
    "error": "request_timeout",
    "status_code": 504
  }
  ```

#### ERR002
- **測試名稱**: 限流測試
- **目的**: 驗證限流機制
- **輸入**: 超過5 req/sec的請求
- **預期輸出**:
  ```json
  {
    "error": "rate_limited",
    "retry_after": 15,
    "status_code": 429
  }
  ```

#### ERR003
- **測試名稱**: 資料庫連線失敗測試
- **目的**: 驗證資料庫錯誤處理
- **輸入**: 資料庫離線時的請求
- **預期輸出**:
  ```json
  {
    "error": "service_unavailable",
    "status_code": 503
  }
  ```

---

## 📊 測試資料集

### 基礎測試資料
- **用戶ID**: test_user_001 ~ test_user_100
- **對話ID**: test_conv_001 ~ test_conv_100
- **訊息內容**: 
  - 一般對話: 50條
  - 風險內容: 20條
  - 知識查詢: 30條

### 知識庫測試資料
- **毒防服務**: 100筆
- **法律條文**: 50筆
- **醫療資源**: 80筆
- **常見問題**: 200筆

### 風險測試案例
- **NONE級**: 一般問候、天氣討論
- **LOW級**: 輕微負面情緒
- **MEDIUM級**: 提及藥物、輕微暴力
- **HIGH級**: 自殺意念、嚴重暴力
- **IMMINENT級**: 立即危險

---

## ✅ 測試通過標準

1. **功能正確性**: 100%測試案例通過
2. **效能指標**: 符合各API的SLA要求
3. **錯誤處理**: 所有錯誤都有適當回應
4. **安全性**: 無未授權存取
5. **資料完整性**: 無資料遺失或損壞

---

*每個API變更都需要更新對應的測試案例*