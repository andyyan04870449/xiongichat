#!/bin/bash

# 雄i聊 ngrok 通道啟動腳本
set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}========================================"
echo "     啟動雄i聊 ngrok 通道"
echo "========================================${NC}"

# 檢查並啟動雄i聊服務
echo -e "${YELLOW}[1/6] 檢查雄i聊服務狀態...${NC}"
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ 雄i聊服務正在運行${NC}"
else
    echo -e "${YELLOW}⚠ 雄i聊服務未運行，正在啟動...${NC}"
    
    # 清理端口佔用
    echo -e "${CYAN}清理端口 8000...${NC}"
    PORT_8000_PIDS=$(lsof -ti:8000 2>/dev/null || true)
    if [ ! -z "$PORT_8000_PIDS" ]; then
        echo "$PORT_8000_PIDS" | xargs kill -9 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}✓ 端口 8000 已清理${NC}"
    fi
    
    # 清理 uvicorn 進程
    UVICORN_PIDS=$(pgrep -f "uvicorn" || true)
    if [ ! -z "$UVICORN_PIDS" ]; then
        echo -e "${CYAN}清理 uvicorn 進程...${NC}"
        echo "$UVICORN_PIDS" | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # 檢查 Python 環境
    echo -e "${CYAN}檢查 Python 環境...${NC}"
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}創建虛擬環境...${NC}"
        python3 -m venv venv
    fi
    
    # 激活虛擬環境
    source venv/bin/activate
    
    # 檢查套件是否已安裝
    if ! python -c "import fastapi" 2>/dev/null; then
        echo -e "${YELLOW}安裝 Python 套件...${NC}"
        pip install -q -r requirements-simple.txt || pip install -q -r requirements.txt
    fi
    
    # 啟動雄i聊服務
    echo -e "${CYAN}啟動雄i聊服務...${NC}"
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > xiongichat.log 2>&1 &
    
    # 等待服務啟動
    echo -e "${CYAN}等待服務啟動...${NC}"
    for i in {1..15}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 雄i聊服務啟動成功${NC}"
            break
        fi
        if [ $i -eq 15 ]; then
            echo -e "${RED}❌ 雄i聊服務啟動逾時${NC}"
            echo "請檢查日誌: tail -f xiongichat.log"
            exit 1
        fi
        echo -n "."
        sleep 2
    done
fi

# 停止現有的 ngrok
echo -e "${YELLOW}[2/6] 停止現有 ngrok session...${NC}"
NGROK_PIDS=$(pgrep ngrok || true)
if [ ! -z "$NGROK_PIDS" ]; then
    echo -e "${CYAN}正在停止現有 ngrok...${NC}"
    echo "$NGROK_PIDS" | xargs kill 2>/dev/null || true
    sleep 3
    echo -e "${GREEN}✓ 現有 ngrok 已停止${NC}"
else
    echo -e "${GREEN}✓ 沒有運行中的 ngrok${NC}"
fi

# 檢查 Docker 服務（PostgreSQL 和 Redis）
echo -e "${YELLOW}[3/6] 檢查資料庫服務...${NC}"
if ! docker compose -f docker-compose.yml ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠ 資料庫服務未運行，正在啟動...${NC}"
    docker compose -f docker-compose.yml up -d
    echo -e "${GREEN}✓ 資料庫服務啟動完成${NC}"
else
    echo -e "${GREEN}✓ 資料庫服務正在運行${NC}"
fi

# 檢查配置文件
echo -e "${YELLOW}[4/6] 檢查配置文件...${NC}"
if [ ! -f "ngrok.yml" ]; then
    echo -e "${RED}❌ 找不到 ngrok.yml 配置文件${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 配置文件存在${NC}"

# 檢查 .env 文件
echo -e "${YELLOW}[5/6] 檢查環境配置...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}⚠ 複製 .env.example 到 .env...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✓ .env 文件已創建${NC}"
    else
        echo -e "${RED}❌ 找不到 .env 或 .env.example 文件${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env 文件存在${NC}"
fi

# 啟動新的 ngrok（只啟動 xiongichat）
echo -e "${YELLOW}[6/6] 啟動 ngrok 通道...${NC}"
echo -e "${CYAN}正在啟動 xiongichat 通道...${NC}"

# 使用 nohup 在背景啟動（只啟動 xiongichat）
nohup ngrok start --config=ngrok.yml xiongichat > ngrok.log 2>&1 &
NGROK_PID=$!

# 等待 ngrok 啟動
echo -e "${CYAN}等待 ngrok 啟動...${NC}"
for i in {1..15}; do
    if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
        echo -e "${GREEN}✓ ngrok 啟動成功${NC}"
        break
    fi
    if [ $i -eq 15 ]; then
        echo -e "${RED}❌ ngrok 啟動逾時${NC}"
        echo "請檢查日誌: tail -f ngrok.log"
        exit 1
    fi
    echo -n "."
    sleep 2
done

# 顯示通道資訊
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}     ngrok 通道啟動成功！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 獲取通道 URL
echo -e "${CYAN}正在獲取通道 URL...${NC}"
sleep 3

TUNNEL_INFO=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
data = json.load(sys.stdin)
for tunnel in data.get('tunnels', []):
    name = tunnel.get('name', '')
    url = tunnel.get('public_url', '')
    addr = tunnel.get('config', {}).get('addr', '')
    print(f'{name}: {url} -> {addr}')
" 2>/dev/null || echo "無法獲取通道資訊")

echo -e "${YELLOW}通道資訊：${NC}"
echo "$TUNNEL_INFO"

echo ""
echo -e "${YELLOW}管理資訊：${NC}"
echo -e "   ngrok PID: ${CYAN}$NGROK_PID${NC}"
echo -e "   查看日誌: ${YELLOW}tail -f ngrok.log${NC}"
echo -e "   停止服務: ${YELLOW}kill $NGROK_PID${NC}"
echo -e "   Web UI: ${BLUE}http://localhost:4040${NC}"
echo ""
echo -e "${GREEN}雄i聊現在可以通過 https://xiongichat.ngrok.io 訪問！${NC}"
