#!/bin/bash

# 查看日誌腳本

# 顏色定義
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "================================================"
echo "         雄i聊服務日誌"
echo "================================================"
echo -e "${NC}"

# 選項菜單
echo "請選擇要查看的日誌："
echo "1) PostgreSQL 日誌"
echo "2) Redis 日誌"
echo "3) 所有 Docker 服務日誌"
echo "4) 即時追蹤所有日誌"
echo ""
read -p "請輸入選項 (1-4): " choice

case $choice in
    1)
        echo -e "${YELLOW}PostgreSQL 日誌：${NC}"
        docker-compose logs postgres
        ;;
    2)
        echo -e "${YELLOW}Redis 日誌：${NC}"
        docker-compose logs redis
        ;;
    3)
        echo -e "${YELLOW}所有服務日誌：${NC}"
        docker-compose logs
        ;;
    4)
        echo -e "${YELLOW}即時追蹤日誌 (Ctrl+C 停止)：${NC}"
        docker-compose logs -f
        ;;
    *)
        echo "無效的選項"
        exit 1
        ;;
esac