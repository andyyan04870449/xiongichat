# 雄i聊後端系統

高雄市毒防局個案聊天AI系統後端

## 🚀 快速開始

### 1. 環境需求
- Python 3.10+
- PostgreSQL 15+
- Redis 7+

### 2. 安裝步驟

#### 使用 Docker Compose（推薦）
```bash
# 啟動資料庫和 Redis
docker-compose up -d

# 安裝 Python 套件
pip install -r requirements.txt

# 複製環境設定
cp .env.example .env

# 編輯 .env 檔案，設定 OPENAI_API_KEY
```

#### 手動安裝
```bash
# 安裝 PostgreSQL 和 Redis
# macOS
brew install postgresql@15 redis
brew services start postgresql@15
brew services start redis

# Ubuntu
sudo apt update
sudo apt install postgresql-15 redis-server

# 建立資料庫
psql -U postgres
CREATE DATABASE xiongichat;
CREATE USER xiongichat WITH PASSWORD 'xiongichat123';
GRANT ALL PRIVILEGES ON DATABASE xiongichat TO xiongichat;
\q

# 執行初始化 SQL
psql -U xiongichat -d xiongichat -f init.sql
```

### 3. 環境設定
編輯 `.env` 檔案：
```env
# 必要設定
OPENAI_API_KEY=your-openai-api-key-here

# 資料庫（使用 Docker 預設值）
DATABASE_URL=postgresql+asyncpg://xiongichat:xiongichat123@localhost:5432/xiongichat
```

### 4. 啟動服務
```bash
# 開發模式
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API 文件

啟動後訪問：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 主要功能

### 第一階段功能（已實作）
- ✅ 基礎聊天功能
- ✅ 短期記憶管理（10輪對話）
- ✅ 對話持久化儲存
- ✅ LangGraph 工作流

### API 端點
- `POST /api/v1/chat` - 發送聊天訊息
- `GET /api/v1/conversations/{id}` - 取得對話歷史
- `GET /api/v1/conversations/user/{user_id}` - 取得使用者對話列表

## 🧪 測試

```bash
# 測試聊天功能
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "你好"
  }'

# 延續對話
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "conversation_id": "從上一個回應取得的ID",
    "message": "我剛剛說了什麼？"
  }'
```

## 📁 專案結構

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   └── v1/
│   │       ├── chat.py
│   │       └── conversations.py
│   ├── langgraph/        # LangGraph 工作流
│   │   ├── nodes/        # 工作流節點
│   │   ├── state.py      # 狀態定義
│   │   └── workflow.py   # 工作流組裝
│   ├── models/           # 資料模型
│   ├── schemas/          # Pydantic 結構
│   ├── services/         # 業務邏輯
│   ├── config.py         # 配置管理
│   ├── database.py       # 資料庫連線
│   └── main.py           # 主程式
├── docker-compose.yml    # Docker 配置
├── init.sql             # 資料庫初始化
├── requirements.txt     # Python 套件
└── .env.example         # 環境變數範例
```

## 🔍 故障排除

### 資料庫連線失敗
```bash
# 檢查 PostgreSQL 是否運行
docker ps | grep postgres
# 或
pg_isready -h localhost -p 5432

# 檢查連線
psql -U xiongichat -h localhost -d xiongichat
```

### OpenAI API 錯誤
- 確認 `.env` 中的 `OPENAI_API_KEY` 設定正確
- 檢查 API 額度是否充足

### Redis 連線失敗
```bash
# 檢查 Redis 是否運行
redis-cli ping
# 應回應 PONG
```

## 🚧 開發計畫

- [ ] 第二階段：RAG 知識庫檢索
- [ ] 第三階段：風險偵測與通知
- [ ] 第四階段：安全機制
- [ ] 第五階段：脫敏機制

## 📝 授權

內部使用