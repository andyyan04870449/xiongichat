# Docker 部署指南

## 🐳 Docker 容器化部署

本專案支援完整的 Docker 容器化部署，包含應用程式、PostgreSQL 資料庫和 Redis 快取。

## 📋 前置需求

- Docker 20.10+
- Docker Compose 2.0+ (或 docker compose 插件)
- 至少 4GB 可用記憶體

## 🚀 快速開始

### 1. 完整 Docker 部署（推薦）

使用 Docker 運行所有服務：

```bash
# 使用 Docker 啟動腳本
./docker-start.sh
```

這會自動：
- ✅ 檢查 Docker 環境
- ✅ 建立應用程式映像
- ✅ 啟動 PostgreSQL、Redis 和應用程式
- ✅ 設定網路連線
- ✅ 執行健康檢查

### 2. 停止服務

```bash
# 停止所有容器
./docker-stop.sh
```

可選擇：
- 清除資料庫資料
- 刪除 Docker 映像

## 📦 Docker 配置檔案

### 檔案說明

| 檔案 | 用途 | 說明 |
|------|------|------|
| `Dockerfile` | 開發映像 | 包含開發工具，支援熱重載 |
| `Dockerfile.prod` | 生產映像 | 優化大小，多階段建構 |
| `docker-compose.yml` | 基礎服務 | 只有 PostgreSQL 和 Redis |
| `docker-compose.full.yml` | 完整服務 | 包含應用程式 |

### 使用不同配置

```bash
# 開發環境（預設）
docker compose -f docker-compose.full.yml up

# 生產環境
docker build -f Dockerfile.prod -t xiongichat:prod .
docker run -p 8000:8000 --env-file .env xiongichat:prod

# 只啟動資料庫
docker compose up postgres redis
```

## 🔧 環境變數

Docker 容器會自動調整以下連線：

```env
# 容器內部連線（自動設定）
DATABASE_URL=postgresql+asyncpg://xiongichat:xiongichat123@postgres:5432/xiongichat
REDIS_URL=redis://redis:6379/0
```

## 🏗️ 架構說明

```
┌─────────────────────────────────────┐
│         Docker Network              │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │PostgreSQL│  │  Redis   │       │
│  │  :5432   │  │  :6379   │       │
│  └──────────┘  └──────────┘       │
│        ↑             ↑              │
│        └─────┬───────┘              │
│              │                      │
│       ┌──────────────┐              │
│       │  FastAPI App │              │
│       │    :8000     │              │
│       └──────────────┘              │
│              ↑                      │
└──────────────┼──────────────────────┘
               │
         Host :8000
```

## 📊 容器管理

### 查看狀態
```bash
# 查看運行中的容器
docker compose -f docker-compose.full.yml ps

# 查看日誌
docker compose -f docker-compose.full.yml logs

# 即時日誌
docker compose -f docker-compose.full.yml logs -f

# 特定服務日誌
docker compose -f docker-compose.full.yml logs app
```

### 執行命令
```bash
# 進入應用程式容器
docker compose -f docker-compose.full.yml exec app bash

# 進入 PostgreSQL
docker compose -f docker-compose.full.yml exec postgres psql -U xiongichat

# 進入 Redis
docker compose -f docker-compose.full.yml exec redis redis-cli
```

### 資料管理
```bash
# 備份資料庫
docker compose -f docker-compose.full.yml exec postgres \
  pg_dump -U xiongichat xiongichat > backup.sql

# 還原資料庫
docker compose -f docker-compose.full.yml exec -T postgres \
  psql -U xiongichat xiongichat < backup.sql
```

## 🔍 故障排除

### 容器無法啟動
```bash
# 檢查容器日誌
docker compose -f docker-compose.full.yml logs app

# 重新建立映像
docker compose -f docker-compose.full.yml build --no-cache

# 清理並重啟
docker compose -f docker-compose.full.yml down -v
docker compose -f docker-compose.full.yml up --build
```

### 網路連線問題
```bash
# 檢查網路
docker network ls
docker network inspect backend_xiongichat_network

# 重建網路
docker compose -f docker-compose.full.yml down
docker network prune
docker compose -f docker-compose.full.yml up
```

### 權限問題
```bash
# 修復檔案權限
sudo chown -R $USER:$USER .
chmod +x *.sh
```

## 🚢 生產部署

### 使用生產映像
```bash
# 建立生產映像
docker build -f Dockerfile.prod -t xiongichat:prod .

# 使用 Docker Swarm
docker swarm init
docker stack deploy -c docker-compose.prod.yml xiongichat

# 使用 Kubernetes
kubectl apply -f k8s/
```

### 效能優化
- 使用多階段建構減少映像大小
- 設定適當的資源限制
- 使用健康檢查確保服務可用
- 配置日誌輪替避免磁碟滿

## 📈 監控

### 資源使用
```bash
# 查看容器資源使用
docker stats

# 查看特定容器
docker stats xiongichat_app
```

### 健康檢查
```bash
# 檢查健康狀態
docker compose -f docker-compose.full.yml ps
curl http://localhost:8000/health
```

## 🔐 安全建議

1. **不要**在映像中包含敏感資料
2. 使用 `.dockerignore` 排除不必要檔案
3. 以非 root 使用者運行容器
4. 定期更新基礎映像
5. 使用環境變數管理設定

## 📚 相關資源

- [Docker 官方文件](https://docs.docker.com/)
- [Docker Compose 文件](https://docs.docker.com/compose/)
- [FastAPI Docker 部署](https://fastapi.tiangolo.com/deployment/docker/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Redis Docker](https://hub.docker.com/_/redis)