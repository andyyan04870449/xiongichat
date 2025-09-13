#!/bin/bash
# 批次上傳腳本

API_URL="http://localhost:8000/api/v1"

# 1. 建立批次（假設上傳3個檔案）
echo "建立批次任務..."
BATCH_RESPONSE=$(curl -s -X POST "${API_URL}/batch/create?file_count=3")
BATCH_ID=$(echo $BATCH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['batch_id'])")
echo "批次ID: $BATCH_ID"

# 2. 上傳檔案
echo "上傳檔案..."

# 上傳第一個檔案
curl -X POST "${API_URL}/batch/${BATCH_ID}/upload" \
  -F "file=@/path/to/your/file1.pdf" \
  -F "category=knowledge" \
  -F "source=manual" \
  -F "lang=zh-TW"

# 上傳第二個檔案
curl -X POST "${API_URL}/batch/${BATCH_ID}/upload" \
  -F "file=@/path/to/your/file2.txt" \
  -F "category=knowledge" \
  -F "source=manual" \
  -F "lang=zh-TW"

# 上傳第三個檔案
curl -X POST "${API_URL}/batch/${BATCH_ID}/upload" \
  -F "file=@/path/to/your/file3.md" \
  -F "category=knowledge" \
  -F "source=manual" \
  -F "lang=zh-TW"

# 3. 檢查狀態
echo "檢查批次狀態..."
curl -s "${API_URL}/batch/${BATCH_ID}/status" | python3 -m json.tool