# 雄i聊 API 串接文件

## 🌐 API 端點資訊

**Base URL**: `https://xiongichat.ngrok.io`  
**API Version**: v1  
**完整 API 路徑**: `https://xiongichat.ngrok.io/api/v1`

---

## 📋 API 端點說明

### 1️⃣ 聊天對話 API

**端點**: `POST https://xiongichat.ngrok.io/api/v1/chat/`

**功能**: 發送訊息給 AI 助手並取得回覆

**請求範例**:
```json
{
  "user_id": "user_001",        // 必填：使用者唯一識別碼
  "message": "你好，我想了解戒毒資源",  // 必填：使用者訊息
  "conversation_id": "7b44bdfa-253a-4d6f-81af-dd6ef598b56b"  // 選填：延續對話時使用
}
```

**回應範例**:
```json
{
  "conversation_id": "7b44bdfa-253a-4d6f-81af-dd6ef598b56b",
  "reply": "你好！我很樂意幫助你了解戒毒資源。高雄市有多個專業機構...",
  "user_message_id": "020e2d3c-56b6-46da-9833-148cef54527b",
  "assistant_message_id": "1a0bc376-40a1-4e25-9059-8f4de848804f"
}
```

---

### 2️⃣ 取得對話歷史

**端點**: `GET https://xiongichat.ngrok.io/api/v1/conversations/{conversation_id}`

**功能**: 查詢特定對話的完整歷史記錄

**回應範例**:
```json
{
  "id": "7b44bdfa-253a-4d6f-81af-dd6ef598b56b",
  "user_id": "user_001",
  "started_at": "2025-08-13T21:27:37",
  "messages": [
    {
      "role": "user",
      "content": "你好，我想了解戒毒資源",
      "created_at": "2025-08-13T21:27:37"
    },
    {
      "role": "assistant",
      "content": "你好！我很樂意幫助你...",
      "created_at": "2025-08-13T21:27:38"
    }
  ]
}
```

---

### 3️⃣ 健康檢查

**端點**: `GET https://xiongichat.ngrok.io/health`

**功能**: 檢查服務是否正常運行

**回應範例**:
```json
{
  "status": "healthy",
  "service": "XiongIChat",
  "version": "0.1.0"
}
```

---

## 💻 前端整合範例

### JavaScript (使用 fetch)
```javascript
// 設定 API 基礎 URL
const API_BASE = 'https://xiongichat.ngrok.io/api/v1';

// 發送聊天訊息
async function sendMessage(userId, message, conversationId = null) {
  try {
    const response = await fetch(`${API_BASE}/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        message: message,
        conversation_id: conversationId
      })
    });
    
    if (!response.ok) throw new Error('API request failed');
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// 使用範例
let conversationId = null;

// 第一次對話
const firstChat = await sendMessage('user_001', '你好');
conversationId = firstChat.conversation_id;
console.log('AI 回覆:', firstChat.reply);

// 延續對話
const secondChat = await sendMessage('user_001', '我想了解戒毒資源', conversationId);
console.log('AI 回覆:', secondChat.reply);
```

### React 範例
```jsx
import { useState } from 'react';

const API_BASE = 'https://xiongichat.ngrok.io/api/v1';

function ChatComponent() {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  const sendMessage = async () => {
    if (!input.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'user_001',
          message: input,
          conversation_id: conversationId
        })
      });
      
      const data = await response.json();
      
      // 更新對話 ID
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }
      
      // 更新訊息列表
      setMessages(prev => [
        ...prev,
        { role: 'user', content: input },
        { role: 'assistant', content: data.reply }
      ]);
      
      setInput('');
    } catch (error) {
      console.error('發送失敗:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      <div className="input-area">
        <input 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>
          {loading ? '發送中...' : '發送'}
        </button>
      </div>
    </div>
  );
}
```

---

## 🔧 測試工具

### 使用 curl 測試
```bash
# 測試健康檢查
curl https://xiongichat.ngrok.io/health

# 發送聊天訊息
curl -X POST https://xiongichat.ngrok.io/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "你好"
  }'
```

### 使用 Postman
1. 匯入以下 URL: `https://xiongichat.ngrok.io/api/v1/chat/`
2. 設定 Method 為 POST
3. Headers 加入: `Content-Type: application/json`
4. Body 選擇 raw JSON，輸入請求內容

---

## ⚠️ 注意事項

1. **CORS**: 已設定允許所有來源（開發階段），包含 `https://kunyou-poc-frontend.ngrok.io`
2. **結尾斜線**: API 端點需要結尾斜線 `/api/v1/chat/`（不是 `/api/v1/chat`）
3. **對話記憶**: 系統會自動維護最近 10 輪對話的記憶
4. **使用者識別**: `user_id` 可以是任何唯一字串，建議使用使用者的實際 ID

---

## 📖 API 文件

- **Swagger UI**: https://xiongichat.ngrok.io/docs
- **ReDoc**: https://xiongichat.ngrok.io/redoc

---

## 🐛 常見問題

### CORS 錯誤
確認請求來源已加入 CORS 允許清單，或聯繫後端更新設定

### 404 Not Found
確認 API 路徑正確，特別注意結尾的斜線

### 500 Internal Server Error
可能是後端服務問題，請聯繫後端工程師

---

## 📞 技術支援

如遇到問題，請提供：
1. 錯誤訊息截圖
2. 請求的完整 URL 和參數
3. 瀏覽器 Console 錯誤訊息