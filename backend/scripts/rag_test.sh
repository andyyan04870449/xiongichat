#!/bin/bash

# RAG搜尋測試工具啟動腳本
# 自動啟用虛擬環境並執行測試工具

# 設定顏色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查是否在正確的目錄
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${YELLOW}⚠ 請在backend目錄中執行此腳本${NC}"
    echo "使用方法: cd backend && ./scripts/rag_test.sh"
    exit 1
fi

echo -e "${BLUE}🚀 啟動RAG搜尋測試工具...${NC}"

# 啟用虛擬環境
source venv/bin/activate

# 檢查是否有參數
if [ $# -eq 0 ]; then
    echo -e "${GREEN}進入互動模式...${NC}"
    python scripts/rag_search_tester.py -i
else
    echo -e "${GREEN}執行命令行模式...${NC}"
    python scripts/rag_search_tester.py "$@"
fi
