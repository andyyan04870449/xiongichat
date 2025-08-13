#!/bin/bash

# 開發模式啟動腳本 (含自動重載)
set -e

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "================================================"
echo "         雄i聊 - 開發模式"
echo "================================================"
echo -e "${NC}"

# 檢查 .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}請編輯 .env 檔案設定 OPENAI_API_KEY${NC}"
    exit 1
fi

# 啟動 Docker 服務
echo -e "${YELLOW}啟動資料庫服務...${NC}"
docker-compose up -d

# 等待服務就緒
sleep 3

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}建立虛擬環境...${NC}"
    python3 -m venv venv
fi

# 啟用虛擬環境
source venv/bin/activate

# 安裝套件
pip install -q -r requirements.txt

echo -e "${GREEN}"
echo "================================================"
echo "     開發模式啟動成功 (自動重載已啟用)"
echo "================================================"
echo -e "${NC}"
echo -e "📍 API 文件: ${BLUE}http://localhost:8000/docs${NC}"
echo -e "📍 檔案變更將自動重載${NC}"
echo ""

# 使用 uvicorn 的 reload 模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info