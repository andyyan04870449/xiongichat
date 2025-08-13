# 管理腳本說明

## 🚀 快速開始

### 基本操作
```bash
# 啟動所有服務
./start.sh

# 停止所有服務
./stop.sh

# 重新啟動
./restart.sh

# 開發模式（自動重載）
./dev.sh
```

### 測試與除錯
```bash
# 執行 API 測試
./test.sh

# 查看日誌
./logs.sh
```

## 📝 腳本說明

| 腳本 | 功能 | 說明 |
|------|------|------|
| `start.sh` | 正式啟動 | 啟動資料庫、Redis、應用程式 |
| `stop.sh` | 停止服務 | 停止所有 Docker 容器 |
| `restart.sh` | 重新啟動 | 停止後重新啟動 |
| `dev.sh` | 開發模式 | 啟用自動重載功能 |
| `test.sh` | API 測試 | 執行基本功能測試 |
| `logs.sh` | 查看日誌 | 查看各服務日誌 |

## 🔧 進階用法

### 清除所有資料
```bash
# 停止並清除資料庫
docker-compose down -v
```

### 僅啟動資料庫
```bash
docker-compose up -d postgres redis
```

### 查看即時日誌
```bash
docker-compose logs -f
```

### 進入資料庫
```bash
docker-compose exec postgres psql -U xiongichat -d xiongichat
```

### 進入 Redis
```bash
docker-compose exec redis redis-cli
```

## 🐛 故障排除

### 埠號被佔用
```bash
# 查看佔用 8000 埠的程序
lsof -i :8000

# 查看佔用 5432 埠的程序
lsof -i :5432
```

### 重置環境
```bash
# 完全清理並重建
docker-compose down -v
rm -rf venv
./start.sh
```