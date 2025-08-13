#!/bin/bash

# Docker 完整啟動腳本
set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}"
echo "================================================"
echo "     雄i聊 - Docker 容器化啟動"
echo "================================================"
echo -e "${NC}"

# 檢查 Docker
echo -e "${YELLOW}[1/5] 檢查 Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安裝${NC}"
    echo "請先安裝 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker 服務未運行${NC}"
    echo "請啟動 Docker Desktop 或 Docker 服務"
    exit 1
fi
echo -e "${GREEN}✓ Docker 運行中${NC}"

# 檢查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}使用 docker compose（新版）${NC}"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# 檢查 .env
echo -e "${YELLOW}[2/5] 檢查環境設定...${NC}"
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠ 已從範本建立 .env，請設定 OPENAI_API_KEY${NC}"
        exit 1
    else
        echo -e "${RED}❌ 找不到 .env.example${NC}"
        exit 1
    fi
fi

# 檢查 API Key
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo -e "${RED}❌ 請在 .env 中設定有效的 OPENAI_API_KEY${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 環境設定完成${NC}"

# 建立映像
echo -e "${YELLOW}[3/5] 建立 Docker 映像...${NC}"
docker build -t xiongichat:latest .
echo -e "${GREEN}✓ 映像建立完成${NC}"

# 停止舊容器
echo -e "${YELLOW}[4/5] 清理舊容器...${NC}"
$COMPOSE_CMD -f docker-compose.full.yml down 2>/dev/null || true
echo -e "${GREEN}✓ 清理完成${NC}"

# 啟動服務
echo -e "${YELLOW}[5/5] 啟動所有服務...${NC}"
$COMPOSE_CMD -f docker-compose.full.yml up -d

# 等待服務就緒
echo -e "${YELLOW}等待服務啟動...${NC}"
sleep 5

# 檢查服務狀態
echo ""
echo -e "${CYAN}檢查服務狀態：${NC}"

# PostgreSQL
if $COMPOSE_CMD -f docker-compose.full.yml exec -T postgres pg_isready &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL 運行中${NC}"
else
    echo -e "${RED}❌ PostgreSQL 未就緒${NC}"
fi

# Redis
if $COMPOSE_CMD -f docker-compose.full.yml exec -T redis redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis 運行中${NC}"
else
    echo -e "${RED}❌ Redis 未就緒${NC}"
fi

# App
sleep 3
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ 應用程式運行中${NC}"
else
    echo -e "${YELLOW}⚠ 應用程式啟動中...${NC}"
fi

echo ""
echo -e "${GREEN}"
echo "================================================"
echo "         Docker 容器啟動成功！"
echo "================================================"
echo -e "${NC}"
echo -e "📍 API 文件: ${BLUE}http://localhost:8000/docs${NC}"
echo -e "📍 健康檢查: ${BLUE}http://localhost:8000/health${NC}"
echo ""
echo -e "${CYAN}容器狀態：${NC}"
$COMPOSE_CMD -f docker-compose.full.yml ps
echo ""
echo -e "${YELLOW}管理命令：${NC}"
echo "查看日誌: ${COMPOSE_CMD} -f docker-compose.full.yml logs -f"
echo "停止服務: ${COMPOSE_CMD} -f docker-compose.full.yml down"
echo "重啟服務: ${COMPOSE_CMD} -f docker-compose.full.yml restart"