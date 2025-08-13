#!/bin/bash

# 雄i聊後端重啟腳本
set -e

# 顏色定義
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "================================================"
echo "         重新啟動雄i聊後端服務"
echo "================================================"
echo -e "${NC}"

echo -e "${YELLOW}停止服務...${NC}"
./stop.sh

echo ""
echo -e "${YELLOW}啟動服務...${NC}"
./start.sh