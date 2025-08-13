#!/bin/bash

# API 測試腳本
set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# API 基礎 URL
BASE_URL="https://xiongichat.ngrok.io"
API_URL="${BASE_URL}/api/v1"

echo -e "${BLUE}"
echo "================================================"
echo "         雄i聊 API 測試 (Ngrok 版本)"
echo "================================================"
echo -e "${NC}"

# 檢查服務是否運行
echo -e "${YELLOW}[1/5] 檢查服務狀態...${NC}"
if curl -s "${BASE_URL}/health" > /dev/null; then
    echo -e "${GREEN}✓ 服務運行中${NC}"
else
    echo -e "${RED}❌ 服務未運行或 ngrok 通道未啟動${NC}"
    echo -e "${YELLOW}請確認：${NC}"
    echo "1. 本地服務已啟動: ./start.sh"
    echo "2. ngrok 通道已啟動: ./start-ngrok-xiongichat.sh"
    exit 1
fi

# 測試健康檢查
echo -e "${YELLOW}[2/5] 測試健康檢查端點...${NC}"
response=$(curl -s "${BASE_URL}/health")
echo -e "${CYAN}回應: ${response}${NC}"
echo -e "${GREEN}✓ 健康檢查成功${NC}"
echo ""

# 測試第一次聊天
echo -e "${YELLOW}[3/5] 測試新對話...${NC}"
echo -e "${CYAN}發送: 你好，我是測試用戶${NC}"
response=$(curl -s -X POST "${API_URL}/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "message": "你好，我是測試用戶"
  }')

# 提取 conversation_id
conv_id=$(echo $response | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('conversation_id', ''))")
if [ -z "$conv_id" ]; then
    echo -e "${RED}❌ 聊天測試失敗${NC}"
    echo "回應: $response"
    exit 1
fi

echo -e "${GREEN}✓ 新對話建立成功${NC}"
echo -e "${CYAN}對話ID: ${conv_id}${NC}"
echo -e "${CYAN}回應: $(echo $response | python3 -c "import sys, json; print(json.load(sys.stdin).get('reply', '')[:100])")...${NC}"
echo ""

# 測試延續對話
echo -e "${YELLOW}[4/5] 測試延續對話...${NC}"
echo -e "${CYAN}發送: 我剛剛說了什麼？${NC}"
response=$(curl -s -X POST "${API_URL}/chat/" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"test_user_001\",
    \"conversation_id\": \"${conv_id}\",
    \"message\": \"我剛剛說了什麼？\"
  }")

reply=$(echo $response | python3 -c "import sys, json; print(json.load(sys.stdin).get('reply', '')[:100])" 2>/dev/null || echo "解析失敗")
if [[ $reply == *"測試"* ]] || [[ $reply == *"你好"* ]]; then
    echo -e "${GREEN}✓ 記憶功能正常${NC}"
else
    echo -e "${YELLOW}⚠ 記憶功能可能異常${NC}"
fi
echo -e "${CYAN}回應: ${reply}...${NC}"
echo ""

# 測試對話歷史
echo -e "${YELLOW}[5/5] 測試對話歷史查詢...${NC}"
response=$(curl -s "${API_URL}/conversations/${conv_id}")
msg_count=$(echo $response | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('messages', [])))" 2>/dev/null || echo "0")

if [ "$msg_count" -gt 0 ]; then
    echo -e "${GREEN}✓ 對話歷史查詢成功 (共 ${msg_count} 條訊息)${NC}"
else
    echo -e "${RED}❌ 對話歷史查詢失敗${NC}"
fi

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}        測試完成！${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "更多測試選項："
echo "1. 查看 API 文件: ${BLUE}${BASE_URL}/docs${NC}"
echo "2. 查看對話列表: curl ${API_URL}/conversations/user/test_user_001"
echo "3. 壓力測試: ab -n 100 -c 10 -p post.json -T application/json ${API_URL}/chat"