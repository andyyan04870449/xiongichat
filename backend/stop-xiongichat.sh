#!/bin/bash

# 雄i聊服務停止腳本
set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}========================================"
echo "     停止雄i聊服務"
echo "========================================${NC}"

# 停止 ngrok 服務
echo -e "${YELLOW}[1/3] 停止 ngrok 通道...${NC}"
NGROK_PIDS=$(pgrep ngrok || true)
if [ ! -z "$NGROK_PIDS" ]; then
    echo -e "${CYAN}正在停止 ngrok 進程...${NC}"
    echo "$NGROK_PIDS" | while read pid; do
        if [ ! -z "$pid" ]; then
            echo -e "${CYAN}  正在終止進程 $pid...${NC}"
            kill -15 "$pid" 2>/dev/null || true
        fi
    done
    sleep 3
    
    # 強制清理殘留進程
    NGROK_PIDS=$(pgrep ngrok || true)
    if [ ! -z "$NGROK_PIDS" ]; then
        echo -e "${YELLOW}⚠ 強制清理殘留進程...${NC}"
        echo "$NGROK_PIDS" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    echo -e "${GREEN}✓ ngrok 已停止${NC}"
else
    echo -e "${GREEN}✓ 沒有運行中的 ngrok${NC}"
fi

# 停止雄i聊後端服務
echo -e "${YELLOW}[2/3] 停止雄i聊後端服務...${NC}"

# 清理端口 8000
PORT_8000_PIDS=$(lsof -ti:8000 2>/dev/null || true)
if [ ! -z "$PORT_8000_PIDS" ]; then
    echo -e "${CYAN}正在停止端口 8000 的服務...${NC}"
    echo "$PORT_8000_PIDS" | while read pid; do
        if [ ! -z "$pid" ]; then
            echo -e "${CYAN}  正在終止進程 $pid...${NC}"
            kill -15 "$pid" 2>/dev/null || true
        fi
    done
    sleep 3
    
    # 強制清理殘留進程
    PORT_8000_PIDS=$(lsof -ti:8000 2>/dev/null || true)
    if [ ! -z "$PORT_8000_PIDS" ]; then
        echo -e "${YELLOW}⚠ 強制清理端口 8000 殘留進程...${NC}"
        echo "$PORT_8000_PIDS" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    echo -e "${GREEN}✓ 端口 8000 已釋放${NC}"
else
    echo -e "${GREEN}✓ 端口 8000 未被佔用${NC}"
fi

# 清理 uvicorn 進程
UVICORN_PIDS=$(pgrep -f "uvicorn" || true)
if [ ! -z "$UVICORN_PIDS" ]; then
    echo -e "${CYAN}正在停止 uvicorn 進程...${NC}"
    echo "$UVICORN_PIDS" | while read pid; do
        if [ ! -z "$pid" ]; then
            echo -e "${CYAN}  正在終止進程 $pid...${NC}"
            kill -15 "$pid" 2>/dev/null || true
        fi
    done
    sleep 3
    
    # 強制清理殘留進程
    UVICORN_PIDS=$(pgrep -f "uvicorn" || true)
    if [ ! -z "$UVICORN_PIDS" ]; then
        echo -e "${YELLOW}⚠ 強制清理 uvicorn 殘留進程...${NC}"
        echo "$UVICORN_PIDS" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    echo -e "${GREEN}✓ uvicorn 已停止${NC}"
else
    echo -e "${GREEN}✓ 沒有運行中的 uvicorn${NC}"
fi

# 清理 Python 相關進程（可選）
echo -e "${YELLOW}[3/3] 清理相關進程...${NC}"
PYTHON_XIONGICHAT_PIDS=$(pgrep -f "app.main" || true)
if [ ! -z "$PYTHON_XIONGICHAT_PIDS" ]; then
    echo -e "${CYAN}正在停止雄i聊 Python 進程...${NC}"
    echo "$PYTHON_XIONGICHAT_PIDS" | while read pid; do
        if [ ! -z "$pid" ]; then
            echo -e "${CYAN}  正在終止進程 $pid...${NC}"
            kill -15 "$pid" 2>/dev/null || true
        fi
    done
    sleep 2
    echo -e "${GREEN}✓ Python 進程已停止${NC}"
else
    echo -e "${GREEN}✓ 沒有運行中的雄i聊 Python 進程${NC}"
fi

# 驗證停止狀態
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}驗證停止狀態：${NC}"

# 檢查服務是否已停止
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}⚠ 雄i聊服務似乎仍在運行${NC}"
else
    echo -e "${GREEN}✓ 雄i聊服務已停止${NC}"
fi

# 檢查 ngrok 是否已停止
if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
    echo -e "${RED}⚠ ngrok 服務似乎仍在運行${NC}"
else
    echo -e "${GREEN}✓ ngrok 服務已停止${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}     雄i聊服務停止完成！${NC}"
echo -e "${BLUE}========================================${NC}"

echo ""
echo -e "${YELLOW}清理的日誌文件：${NC}"
if [ -f "ngrok.log" ]; then
    echo -e "   ngrok 日誌: ${CYAN}ngrok.log${NC}"
fi
if [ -f "xiongichat.log" ]; then
    echo -e "   雄i聊日誌: ${CYAN}xiongichat.log${NC}"
fi

echo ""
echo -e "${CYAN}重新啟動服務：${NC}"
echo -e "   啟動雄i聊: ${YELLOW}./start.sh${NC}"
echo -e "   啟動 ngrok: ${YELLOW}./start-ngrok-xiongichat.sh${NC}"
