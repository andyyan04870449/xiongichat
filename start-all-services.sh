#!/bin/bash

# 雄i聊完整服務啟動腳本
# 自動啟動後端、前端、ngrok通道，並處理端口佔用問題

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 專案路徑
PROJECT_ROOT="/Users/yangandy/KaohsiungCare"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}========================================"
echo "     雄i聊完整服務啟動腳本"
echo "========================================${NC}"

# 函數：清理端口佔用
cleanup_port() {
    local port=$1
    local service_name=$2
    
    echo -e "${YELLOW}檢查端口 $port ($service_name)...${NC}"
    
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ ! -z "$pids" ]; then
        echo -e "${CYAN}發現端口 $port 被佔用，正在清理...${NC}"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}✓ 端口 $port 已清理${NC}"
    else
        echo -e "${GREEN}✓ 端口 $port 可用${NC}"
    fi
}

# 函數：檢查服務是否運行
check_service() {
    local url=$1
    local service_name=$2
    local max_attempts=15
    
    echo -e "${YELLOW}檢查 $service_name 服務狀態...${NC}"
    
    for i in $(seq 1 $max_attempts); do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $service_name 服務運行正常${NC}"
            return 0
        fi
        
        if [ $i -eq $max_attempts ]; then
            echo -e "${RED}❌ $service_name 服務啟動失敗${NC}"
            return 1
        fi
        
        echo -n "."
        sleep 2
    done
}

# 函數：啟動Docker服務
start_docker_services() {
    echo -e "${YELLOW}[1/6] 啟動Docker服務...${NC}"
    
    # 檢查Docker是否運行
    if ! docker ps > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Docker未運行，正在啟動...${NC}"
        open -a Docker
        echo -e "${CYAN}等待Docker啟動...${NC}"
        sleep 10
    fi
    
    # 啟動資料庫服務
    cd "$BACKEND_DIR"
    if ! docker compose -f docker-compose.yml ps | grep -q "Up"; then
        echo -e "${YELLOW}⚠ 資料庫服務未運行，正在啟動...${NC}"
        docker compose -f docker-compose.yml up -d
        echo -e "${GREEN}✓ 資料庫服務啟動完成${NC}"
    else
        echo -e "${GREEN}✓ 資料庫服務正在運行${NC}"
    fi
}

# 函數：啟動後端服務
start_backend() {
    echo -e "${YELLOW}[2/6] 啟動後端服務...${NC}"
    
    # 清理端口8001
    cleanup_port 8001 "後端服務"
    
    # 清理現有的uvicorn進程
    local uvicorn_pids=$(pgrep -f "uvicorn" || true)
    if [ ! -z "$uvicorn_pids" ]; then
        echo -e "${CYAN}清理現有uvicorn進程...${NC}"
        echo "$uvicorn_pids" | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # 切換到後端目錄
    cd "$BACKEND_DIR"
    
    # 檢查虛擬環境
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}創建虛擬環境...${NC}"
        python3 -m venv venv
    fi
    
    # 激活虛擬環境
    source venv/bin/activate
    
    # 檢查套件是否已安裝
    if ! python -c "import fastapi" 2>/dev/null; then
        echo -e "${YELLOW}安裝Python套件...${NC}"
        pip install -q -r requirements.txt
    fi
    
    # 檢查.env文件
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            echo -e "${YELLOW}複製.env.example到.env...${NC}"
            cp .env.example .env
        else
            echo -e "${RED}❌ 找不到.env或.env.example文件${NC}"
            exit 1
        fi
    fi
    
    # 啟動後端服務
    echo -e "${CYAN}啟動後端服務...${NC}"
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > xiongichat.log 2>&1 &
    BACKEND_PID=$!
    
    # 等待後端服務啟動
    if check_service "http://localhost:8001/health" "後端服務"; then
        echo -e "${GREEN}✓ 後端服務啟動成功 (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${RED}❌ 後端服務啟動失敗${NC}"
        echo "請檢查日誌: tail -f $BACKEND_DIR/xiongichat.log"
        exit 1
    fi
}

# 函數：啟動ngrok通道
start_ngrok() {
    echo -e "${YELLOW}[3/6] 啟動ngrok通道...${NC}"
    
    # 清理現有的ngrok進程
    local ngrok_pids=$(pgrep -f "ngrok" || true)
    if [ ! -z "$ngrok_pids" ]; then
        echo -e "${CYAN}清理現有ngrok進程...${NC}"
        echo "$ngrok_pids" | xargs kill 2>/dev/null || true
        sleep 3
    fi
    
    # 檢查ngrok配置
    if [ ! -f "$BACKEND_DIR/ngrok.yml" ]; then
        echo -e "${RED}❌ 找不到ngrok.yml配置文件${NC}"
        exit 1
    fi
    
    # 啟動ngrok - 同時啟動前端、後端和AI代理通道
    cd "$BACKEND_DIR"
    echo -e "${CYAN}啟動ngrok通道 (前端 + 後端 + AI代理)...${NC}"
    nohup ngrok start --config=ngrok.yml frontend backend ai_agent > ngrok.log 2>&1 &
    NGROK_PID=$!
    
    # 等待ngrok啟動
    echo -e "${CYAN}等待ngrok啟動...${NC}"
    for i in {1..15}; do
        if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
            echo -e "${GREEN}✓ ngrok啟動成功 (PID: $NGROK_PID)${NC}"
            break
        fi
        if [ $i -eq 15 ]; then
            echo -e "${RED}❌ ngrok啟動失敗${NC}"
            echo "請檢查日誌: tail -f $BACKEND_DIR/ngrok.log"
            exit 1
        fi
        echo -n "."
        sleep 2
    done
}

# 函數：啟動前端服務
start_frontend() {
    echo -e "${YELLOW}[4/6] 啟動前端服務...${NC}"
    
    # 清理端口8000
    cleanup_port 8000 "前端服務"
    
    # 切換到前端目錄
    cd "$FRONTEND_DIR"
    
    # 檢查node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}安裝前端依賴...${NC}"
        npm install
    fi
    
    # 啟動前端服務
    echo -e "${CYAN}啟動前端服務...${NC}"
    nohup npm run dev > frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # 等待前端服務啟動
    sleep 5
    if check_service "http://localhost:8000" "前端服務"; then
        echo -e "${GREEN}✓ 前端服務啟動成功 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${RED}❌ 前端服務啟動失敗${NC}"
        echo "請檢查日誌: tail -f $FRONTEND_DIR/frontend.log"
        exit 1
    fi
}

# 函數：顯示服務資訊
show_service_info() {
    echo -e "${YELLOW}[5/6] 獲取服務資訊...${NC}"
    
    # 獲取ngrok通道URL
    sleep 3
    local tunnel_info=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for tunnel in data.get('tunnels', []):
        name = tunnel.get('name', '')
        url = tunnel.get('public_url', '')
        addr = tunnel.get('config', {}).get('addr', '')
        print(f'{name}: {url} -> {addr}')
except:
    print('無法獲取通道資訊')
" 2>/dev/null || echo "無法獲取通道資訊")
    
    echo -e "${YELLOW}[6/6] 服務啟動完成！${NC}"
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}     所有服務已成功啟動！${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    echo -e "${YELLOW}服務資訊：${NC}"
    echo -e "   前端服務: ${CYAN}http://localhost:8000${NC} (PID: $FRONTEND_PID)"
    echo -e "   後端服務: ${CYAN}http://localhost:8001${NC} (PID: $BACKEND_PID)"
    echo -e "   AI代理服務: ${CYAN}http://localhost:8002${NC}"
    echo -e "   知識庫服務: ${CYAN}http://localhost:8001/api/v1/knowledge${NC} (集成在後端)"
    echo -e "   ngrok管理: ${CYAN}http://localhost:4040${NC} (PID: $NGROK_PID)"
    echo ""
    
    echo -e "${YELLOW}通道資訊：${NC}"
    echo "$tunnel_info"
    echo ""
    
    echo -e "${YELLOW}管理指令：${NC}"
    echo -e "   查看後端日誌: ${CYAN}tail -f $BACKEND_DIR/xiongichat.log${NC}"
    echo -e "   查看前端日誌: ${CYAN}tail -f $FRONTEND_DIR/frontend.log${NC}"
    echo -e "   查看ngrok日誌: ${CYAN}tail -f $BACKEND_DIR/ngrok.log${NC}"
    echo -e "   停止所有服務: ${CYAN}kill $BACKEND_PID $FRONTEND_PID $NGROK_PID${NC}"
    echo ""
    
    echo -e "${GREEN}雄i聊現在可以通過以下地址訪問：${NC}"
    echo -e "   本地前端: ${BLUE}http://localhost:8000${NC}"
    echo -e "   本地後端: ${BLUE}http://localhost:8001${NC}"
    echo -e "   本地AI代理: ${BLUE}http://localhost:8002${NC}"
    echo -e "   本地知識庫: ${BLUE}http://localhost:8001/api/v1/knowledge${NC}"
    echo -e "   公開前端: ${BLUE}https://xiongichat-frontend.ngrok.io${NC}"
    echo -e "   公開後端: ${BLUE}https://xiongichat-backend.ngrok.io${NC}"
    echo -e "   公開AI代理: ${BLUE}https://xiongichat-ai.ngrok.io${NC}"
    echo ""
}

# 函數：清理函數
cleanup() {
    echo -e "\n${YELLOW}正在清理服務...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$NGROK_PID" ]; then
        kill $NGROK_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}清理完成${NC}"
}

# 設置信號處理
trap cleanup EXIT INT TERM

# 主執行流程
main() {
    start_docker_services
    start_backend
    start_ngrok
    start_frontend
    show_service_info
    
    echo -e "${GREEN}所有服務已啟動，按 Ctrl+C 停止所有服務${NC}"
    
    # 保持腳本運行
    while true; do
        sleep 10
        # 檢查服務是否還在運行
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${RED}後端服務已停止${NC}"
            break
        fi
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            echo -e "${RED}前端服務已停止${NC}"
            break
        fi
        if ! kill -0 $NGROK_PID 2>/dev/null; then
            echo -e "${RED}ngrok服務已停止${NC}"
            break
        fi
    done
}

# 執行主函數
main "$@"
