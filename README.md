# 雄i聊 (XiongIChat)

> 高雄市毒品防制局個案關懷聊天AI系統

## 🌟 專案簡介

雄i聊是專為高雄市毒品防制局設計的關懷聊天機器人，提供溫暖、專業的陪伴服務，協助個案在回歸社會過程中獲得情感支持和實用建議。

### 核心特色

- 🤖 **智能對話**: 基於 LangGraph 和 OpenAI GPT 的自然語言處理
- 💝 **關懷導向**: 專業諮商技巧結合台灣本土化語言風格
- 🔒 **隱私保護**: 完整的資料脫敏和隱私保護機制
- 📊 **風險監測**: 即時風險評估和預警系統
- 🎯 **精準回應**: 嚴格的字數限制確保簡潔有效的溝通

## 🏗️ 技術架構

### 後端技術棧
- **框架**: FastAPI + Python 3.11
- **AI引擎**: LangGraph + OpenAI GPT
- **資料庫**: PostgreSQL + Redis
- **部署**: Docker + Ngrok

### 核心功能
- 智能對話系統
- 對話記憶管理
- 風險偵測機制
- 資料脫敏處理
- 健康檢查監控

## 🚀 快速開始

### 前置需求
- Python 3.11+
- Docker Desktop
- Git

### 本地開發環境設置

1. **克隆專案**
   ```bash
   git clone https://github.com/andyyan04870449/xiongichat.git
   cd xiongichat
   ```

2. **設置環境變數**
   ```bash
   cd backend
   cp .env.example .env
   # 編輯 .env 文件，設置 OPENAI_API_KEY 等必要參數
   ```

3. **一鍵啟動服務**
   ```bash
   ./backend/start-ngrok-xiongichat.sh
   ```

   這個腳本會自動：
   - 🔧 清理舊進程
   - ⚡ 啟動雄i聊服務
   - 🗄️ 啟動資料庫服務
   - 🌐 啟動 ngrok 通道

4. **測試服務**
   ```bash
   ./backend/test.sh
   ```

### 服務端點

- **本地服務**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs
- **健康檢查**: http://localhost:8000/health
- **Ngrok 通道**: https://xiongichat.ngrok.io

## 📖 使用指南

### 互動式聊天
```bash
cd backend
./chat.sh
```

### API 使用範例
```bash
# 開始新對話
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "message": "你好，我想聊聊最近的煩惱"
  }'

# 查詢對話歷史
curl "http://localhost:8000/api/v1/conversations/user/user_001"
```

## 🔧 開發指南

### 專案結構
```
xiongichat/
├── backend/                 # 後端應用
│   ├── app/                # 核心應用代碼
│   │   ├── api/           # API 路由
│   │   ├── langgraph/     # LangGraph 工作流
│   │   ├── models/        # 資料模型
│   │   ├── schemas/       # Pydantic 模式
│   │   └── services/      # 業務邏輯
│   ├── docker-compose.yml # Docker 服務配置
│   ├── requirements.txt   # Python 依賴
│   └── start-ngrok-xiongichat.sh  # 一鍵啟動腳本
└── 設計文件/              # 系統設計文檔
```

### 管理腳本
- `start-ngrok-xiongichat.sh`: 一鍵啟動所有服務
- `stop-xiongichat.sh`: 停止所有服務
- `test.sh`: API 功能測試
- `chat.sh`: 互動式聊天客戶端

## 🔒 安全機制

- **資料脫敏**: 自動識別並脫敏敏感資訊
- **風險監測**: 即時評估對話風險等級
- **隱私保護**: 嚴格的個資保護機制
- **稽核日誌**: 完整的操作記錄

## 📊 監控與日誌

- 應用日誌: `backend/xiongichat.log`
- Ngrok 日誌: `backend/ngrok.log`
- 健康檢查: `/health` 端點

## 🤝 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📝 授權條款

本專案採用 MIT 授權條款。詳見 [LICENSE](LICENSE) 文件。

## 📞 聯絡資訊

- **專案維護者**: Andy Yan
- **專案連結**: [https://github.com/andyyan04870449/xiongichat](https://github.com/andyyan04870449/xiongichat)

---

**雄i聊** - 用科技傳遞溫暖，用AI陪伴成長 ❤️
