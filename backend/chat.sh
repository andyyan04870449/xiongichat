#!/bin/bash

# 聊天客戶端啟動腳本
set -e

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}     雄i聊 - 互動式聊天客戶端${NC}"
echo -e "${BLUE}========================================${NC}"

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 需要 Python 3${NC}"
    exit 1
fi

# 檢查服務是否運行
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${YELLOW}⚠️  服務未運行，正在啟動...${NC}"
    ./start.sh
    sleep 3
fi

# 啟動參數
USER_ID="${1:-user_001}"
API_URL="${2:-http://localhost:8000}"

echo -e "${GREEN}啟動聊天客戶端...${NC}"
echo -e "${GREEN}使用者: ${USER_ID}${NC}"
echo -e "${GREEN}伺服器: ${API_URL}${NC}"
echo ""

# 啟動 Python 客戶端
cd "$(dirname "$0")"  # 確保在腳本所在目錄執行
python3 chat.py --user "$USER_ID" --url "$API_URL"