# 雄i聊 API 前端對接文檔

## 基礎資訊

- **Base URL**: `http://localhost:8000/api/v1`
- **Content-Type**: `application/json`
- **編碼**: `UTF-8`

## 1. 聊天 API

### 1.1 發送訊息

**端點**: `POST /chat/`

**功能**: 發送訊息給AI助手並取得回覆

#### 請求格式 (Request)

```json
{
  "user_id": "string",           // 必填，使用者唯一識別碼 (1-100字元)
  "message": "string",           // 必填，訊息內容 (1-2000字元)
  "conversation_id": "uuid|null" // 選填，對話ID (延續對話時提供)
}
```

#### 回應格式 (Response)

**成功 (200 OK)**
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",     // UUID，對話ID
  "user_message_id": "123e4567-e89b-12d3-a456-426614174001",     // UUID，使用者訊息ID
  "assistant_message_id": "123e4567-e89b-12d3-a456-426614174002", // UUID，助手訊息ID
  "reply": "你好！有什麼可以幫你的嗎？",                          // 字串，AI回覆內容(最多40字)
  "timestamp": "2024-01-15T10:30:00Z"                            // ISO 8601時間戳
}
```

**錯誤回應 (400/500)**
```json
{
  "detail": "錯誤訊息說明"
}
```

#### 使用範例

**首次對話**
```javascript
// 請求
const response = await fetch('http://localhost:8000/api/v1/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 'user_001',
    message: '你好'
    // 不需要 conversation_id
  })
});

// 回應
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_message_id": "550e8400-e29b-41d4-a716-446655440001",
  "assistant_message_id": "550e8400-e29b-41d4-a716-446655440002",
  "reply": "你好！最近怎麼樣？",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**延續對話**
```javascript
// 請求 - 使用上一次回應的 conversation_id
const response = await fetch('http://localhost:8000/api/v1/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 'user_001',
    message: '我最近壓力很大',
    conversation_id: '550e8400-e29b-41d4-a716-446655440000' // 延續對話
  })
});

// 回應
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000", // 相同的對話ID
  "user_message_id": "550e8400-e29b-41d4-a716-446655440003",
  "assistant_message_id": "550e8400-e29b-41d4-a716-446655440004",
  "reply": "壓力大要照顧自己。想聊聊嗎？",
  "timestamp": "2024-01-15T10:31:00Z"
}
```

## 2. 對話歷史 API

### 2.1 獲取對話列表

**端點**: `GET /conversations/`

**功能**: 獲取使用者的對話列表

#### 請求參數

- `user_id` (string, required): 使用者ID
- `limit` (integer, optional): 返回數量限制，預設20
- `offset` (integer, optional): 分頁偏移量，預設0

#### 回應格式

```json
{
  "conversations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user_001",
      "started_at": "2024-01-15T10:00:00Z",
      "ended_at": null,
      "last_message_at": "2024-01-15T10:30:00Z",
      "message_count": 5
    }
  ],
  "total": 10,
  "limit": 20,
  "offset": 0
}
```

### 2.2 獲取對話詳情

**端點**: `GET /conversations/{conversation_id}`

**功能**: 獲取特定對話的完整訊息歷史

#### 回應格式

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_001",
  "started_at": "2024-01-15T10:00:00Z",
  "ended_at": null,
  "last_message_at": "2024-01-15T10:30:00Z",
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "role": "user",
      "content": "你好",
      "created_at": "2024-01-15T10:00:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "role": "assistant",
      "content": "你好！最近怎麼樣？",
      "created_at": "2024-01-15T10:00:01Z"
    }
  ]
}
```

## 3. 回應格式特點

### 3.1 AI回覆內容格式 (`reply` 欄位)

AI的回覆會遵循以下格式規則：

1. **字數限制**: 最多40個中文字（2句話以內）
2. **段落格式**: 使用 `\n\n` 分隔段落（通常不會有多段落）
3. **條列格式**: 使用 `•` 或數字標記 (1. 2. 3.)
4. **強調文字**: 使用 `**文字**` 表示粗體
5. **不會包含**: HTML標籤、圖片、連結

#### 格式範例

```json
{
  "reply": "你好！有什麼可以幫你的嗎？"                    // 簡單回應
}

{
  "reply": "壓力大要照顧自己。\n\n想聊聊嗎？"              // 有換行的回應
}

{
  "reply": "建議你：\n• 充足睡眠\n• 適度運動"              // 條列式回應
}

{
  "reply": "請聯繫**高雄市毒防局**尋求協助。"              // 有強調的回應
}
```

### 3.2 特殊場景回應

| 場景 | 回應特徵 | 範例 |
|------|---------|------|
| 問候 | 簡短友善 | "你好！最近怎麼樣？" |
| 情緒支持 | 關懷詢問 | "聽起來你很辛苦，想聊聊嗎？" |
| 毒品相關 | 謹慎教育 | "這會影響身心健康，需要幫助嗎？" |
| 求助訊號 | 鼓勵支持 | "願意求助需要勇氣！我可以提供資源。" |
| 危機情況 | 立即關懷 | "我很關心你。請撥打119尋求協助。" |
| 事實查詢 | 不編造 | "抱歉，我沒有相關資訊。" |

## 4. 錯誤處理

### 4.1 錯誤碼

| HTTP Status | 錯誤類型 | 說明 |
|-------------|---------|------|
| 400 | Bad Request | 請求參數錯誤 |
| 404 | Not Found | 資源不存在 |
| 422 | Validation Error | 參數驗證失敗 |
| 500 | Internal Server Error | 伺服器內部錯誤 |

### 4.2 錯誤回應格式

```json
{
  "detail": "訊息不能為空"  // 400 錯誤
}

{
  "detail": "處理訊息時發生錯誤，請稍後再試"  // 500 錯誤
}

{
  "detail": [              // 422 驗證錯誤
    {
      "loc": ["body", "message"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

## 5. 前端實作建議

### 5.1 對話管理

```javascript
class ChatManager {
  constructor() {
    this.conversationId = null;
    this.userId = this.getUserId();
  }
  
  async sendMessage(message) {
    const payload = {
      user_id: this.userId,
      message: message
    };
    
    // 如果有對話ID，加入請求
    if (this.conversationId) {
      payload.conversation_id = this.conversationId;
    }
    
    const response = await fetch('/api/v1/chat/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    
    const data = await response.json();
    
    // 保存對話ID供下次使用
    this.conversationId = data.conversation_id;
    
    return data;
  }
  
  newConversation() {
    this.conversationId = null;
  }
}
```

### 5.2 顯示格式處理

```javascript
function formatReply(reply) {
  // 處理換行
  let formatted = reply.replace(/\n\n/g, '<br><br>');
  
  // 處理粗體
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // 處理條列
  formatted = formatted.replace(/^• /gm, '<li>');
  if (formatted.includes('<li>')) {
    formatted = '<ul>' + formatted + '</ul>';
  }
  
  return formatted;
}
```

### 5.3 錯誤處理

```javascript
async function sendChatMessage(message) {
  try {
    const response = await fetch('/api/v1/chat/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        user_id: getUserId(),
        message: message,
        conversation_id: getCurrentConversationId()
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      
      if (response.status === 400) {
        // 顯示驗證錯誤
        showError('輸入錯誤：' + error.detail);
      } else if (response.status === 500) {
        // 系統錯誤
        showError('系統暫時無法使用，請稍後再試');
      }
      return null;
    }
    
    return await response.json();
    
  } catch (error) {
    // 網路錯誤
    showError('網路連線錯誤，請檢查網路');
    return null;
  }
}
```

## 6. 注意事項

1. **對話ID管理**
   - 首次對話不需要提供 `conversation_id`
   - 系統會在首次回應中返回新的 `conversation_id`
   - 延續對話時使用相同的 `conversation_id`
   - 開始新對話時不要帶 `conversation_id`

2. **字數限制**
   - AI回覆最多40個中文字
   - 使用者輸入最多2000字元

3. **使用者ID**
   - 需要前端自行管理使用者ID
   - 可使用裝置ID、隨機UUID或登入帳號

4. **時區處理**
   - 所有時間戳使用UTC時區
   - 前端需轉換為本地時間顯示

5. **特殊字元**
   - 回覆可能包含 `**` (粗體標記)
   - 回覆可能包含 `\n\n` (段落分隔)
   - 不會包含HTML或其他標記語言

## 7. 測試範例

### 使用 cURL 測試

```bash
# 首次對話
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "你好"
  }'

# 延續對話
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "我想了解戒毒資訊",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### 使用 Postman 測試

1. 設定 URL: `http://localhost:8000/api/v1/chat/`
2. 方法: POST
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "user_id": "test_user",
  "message": "你好"
}
```

## 8. 常見問題

**Q: 如何開始新對話？**
A: 發送訊息時不要包含 `conversation_id` 參數

**Q: 對話會保存多久？**
A: 對話永久保存在資料庫中

**Q: 可以同時有多個對話嗎？**
A: 可以，每個對話有獨立的 `conversation_id`

**Q: AI回覆超過40字怎麼辦？**
A: 系統設計確保不超過40字，偶爾超標會在下個版本修正

**Q: 如何處理網路斷線？**
A: 實作重試機制，保存 `conversation_id` 以便恢復對話