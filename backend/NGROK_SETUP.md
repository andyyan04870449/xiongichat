# ngrok 設定說明

## 🌐 部署架構

- **前端**: https://kunyou-poc-frontend.ngrok.io
- **後端**: 需要設定（見下方選項）

## 📋 設定選項

### 選項 1：使用新的固定域名（推薦）
需要在 ngrok 儀表板設定新的域名 `kunyou-poc-backend.ngrok.io`

```bash
# 啟動後端 ngrok
ngrok http 8000 --hostname=kunyou-poc-backend.ngrok.io
```

**前端串接 URL**: `https://kunyou-poc-backend.ngrok.io/api/v1`

### 選項 2：使用隨機 URL（免費測試）
```bash
# 啟動後端 ngrok（會產生隨機 URL）
ngrok http 8000
```

執行後會顯示類似：
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**前端串接 URL**: `https://abc123.ngrok.io/api/v1`（使用實際產生的 URL）

### 選項 3：使用 Edge + Traffic Policy（進階）
如果你的 ngrok 方案支援 Edge 功能，可以在同一個域名下設定路由規則：

1. 登入 ngrok Dashboard
2. 前往 Cloud Edge → Edges
3. 建立或編輯你的 Edge
4. 在 Traffic Policy 中加入路由規則：

```json
{
  "routes": [
    {
      "match": "/api/*",
      "actions": [
        {
          "type": "forward",
          "config": {
            "url": "http://localhost:8000"
          }
        }
      ]
    },
    {
      "match": "/*",
      "actions": [
        {
          "type": "forward",
          "config": {
            "url": "http://localhost:3000"
          }
        }
      ]
    }
  ]
}
```

這樣可以實現：
- `https://kunyou-poc-frontend.ngrok.io/api/*` → 後端
- `https://kunyou-poc-frontend.ngrok.io/*` → 前端

## 🚀 快速啟動步驟

1. **啟動後端服務**
```bash
cd backend
./start.sh
```

2. **啟動 ngrok**

選擇其中一種方式：

```bash
# 方式 A：固定域名（需要設定）
ngrok http 8000 --hostname=kunyou-poc-backend.ngrok.io

# 方式 B：隨機 URL（免費）
ngrok http 8000
```

3. **記錄 ngrok URL**

ngrok 啟動後會顯示：
```
Session Status    online
Web Interface     http://127.0.0.1:4040
Forwarding        https://[你的域名].ngrok.io -> http://localhost:8000
```

4. **測試 API**
```bash
# 測試健康檢查
curl https://[你的ngrok域名]/health

# 測試聊天 API
curl -X POST https://[你的ngrok域名]/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "你好"
  }'
```

## 🔧 前端設定

在前端專案中設定 API Base URL：

```javascript
// .env 或設定檔
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://kunyou-poc-backend.ngrok.io';

// API 呼叫
const response = await fetch(`${API_BASE_URL}/api/v1/chat/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: userId,
    message: userMessage,
    conversation_id: conversationId
  })
});
```

## 📝 注意事項

1. **CORS 已設定**: 後端已配置允許來自 `https://kunyou-poc-frontend.ngrok.io` 的請求
2. **HTTPS**: ngrok 自動提供 HTTPS，確保安全連線
3. **Session Timeout**: 免費版 ngrok 有 8 小時 session 限制
4. **Rate Limiting**: ngrok 有請求速率限制，生產環境建議使用付費方案

## 🛠️ 故障排除

### 問題：CORS 錯誤
確認後端 CORS 設定包含前端域名

### 問題：連線被拒絕
1. 確認後端服務正在運行（port 8000）
2. 確認 ngrok 正確轉發到 localhost:8000

### 問題：404 Not Found
確認 API 路徑正確：`/api/v1/chat/`（注意結尾的斜線）

## 📞 聯絡支援

如有問題，請提供：
1. ngrok 顯示的 Forwarding URL
2. 錯誤訊息截圖
3. 瀏覽器 Console 錯誤訊息