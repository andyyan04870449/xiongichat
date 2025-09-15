#!/bin/bash

# 雄i聊完整服務停止腳本
# 自動停止所有相關服務

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}========================================"
echo "     雄i聊完整服務停止腳本"
echo "========================================${NC}"

# 函數：停止特定端口的服務
stop_port_service() {
    local port=$1
    local service_name=$2
    
    echo -e "${YELLOW}停止端口 $port 的服務 ($service_name)...${NC}"
    
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ ! -z "$pids" ]; then
        echo -e "${CYAN}發現端口 $port 有服務運行，正在停止...${NC}"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}✓ 端口 $port 的服務已停止${NC}"
    else
        echo -e "${GREEN}✓ 端口 $port 沒有服務運行${NC}"
    fi
}

# 函數：停止特定進程
stop_process() {
    local process_name=$1
    local service_name=$2
    
    echo -e "${YELLOW}停止 $service_name 進程...${NC}"
    
    local pids=$(pgrep -f "$process_name" || true)
    if [ ! -z "$pids" ]; then
        echo -e "${CYAN}發現 $service_name 進程，正在停止...${NC}"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}✓ $service_name 已停止${NC}"
    else
        echo -e "${GREEN}✓ $service_name 沒有運行${NC}"
    fi
}

echo -e "${YELLOW}[1/6] 停止前端服務...${NC}"
stop_port_service 8000 "前端服務"
stop_process "vite" "前端服務"
stop_process "npm run dev" "前端服務"

echo -e "${YELLOW}[2/6] 停止後端服務...${NC}"
stop_port_service 8001 "後端服務"
stop_process "uvicorn" "後端服務"

echo -e "${YELLOW}[3/6] 停止AI代理服務...${NC}"
stop_port_service 8002 "AI代理服務"
stop_process "api_server" "AI代理服務"

echo -e "${YELLOW}[4/6] 停止ngrok服務...${NC}"
stop_port_service 4040 "ngrok管理界面"
stop_process "ngrok" "ngrok服務"

echo -e "${YELLOW}[5/6] 停止Docker服務...${NC}"
cd /Users/yangandy/KaohsiungCare/backend
if docker compose -f docker-compose.yml ps | grep -q "Up"; then
    echo -e "${CYAN}停止Docker容器...${NC}"
    docker compose -f docker-compose.yml down
    echo -e "${GREEN}✓ Docker服務已停止${NC}"
else
    echo -e "${GREEN}✓ Docker服務沒有運行${NC}"
fi

echo -e "${YELLOW}[6/6] 清理完成...${NC}"

# 額外清理
echo -e "${CYAN}清理臨時文件...${NC}"
rm -f /Users/yangandy/KaohsiungCare/backend/xiongichat.log
rm -f /Users/yangandy/KaohsiungCare/backend/ngrok.log
rm -f /Users/yangandy/KaohsiungCare/frontend/frontend.log

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}     所有服務已成功停止！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}已停止的服務：${NC}"
echo -e "   ✓ 前端服務 (端口 8000)"
echo -e "   ✓ 後端服務 (端口 8001)"
echo -e "   ✓ AI代理服務 (端口 8002)"
echo -e "   ✓ 知識庫服務 (集成在後端)"
echo -e "   ✓ ngrok服務 (端口 4040)"
echo -e "   ✓ Docker服務 (PostgreSQL/Redis)"
echo ""
echo -e "${GREEN}所有服務已完全停止，可以重新啟動。${NC}"
