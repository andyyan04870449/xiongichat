#!/bin/bash

# Docker 停止腳本
set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "================================================"
echo "         停止 Docker 容器"
echo "================================================"
echo -e "${NC}"

# 檢查 Docker Compose 命令
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# 停止容器
echo -e "${YELLOW}停止所有容器...${NC}"
$COMPOSE_CMD -f docker-compose.full.yml down

echo -e "${GREEN}✓ 容器已停止${NC}"

# 詢問是否清除資料
echo ""
read -p "是否清除資料庫資料？(y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}清除資料卷...${NC}"
    $COMPOSE_CMD -f docker-compose.full.yml down -v
    echo -e "${GREEN}✓ 資料已清除${NC}"
fi

# 詢問是否刪除映像
echo ""
read -p "是否刪除 Docker 映像？(y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}刪除映像...${NC}"
    docker rmi xiongichat:latest 2>/dev/null || true
    echo -e "${GREEN}✓ 映像已刪除${NC}"
fi

echo ""
echo -e "${GREEN}Docker 服務已完全停止${NC}"