# RAG向量搜尋測試工具

這個工具用於測試AI工作流中的RAG搜尋功能，讓您可以輸入查詢內容並查看向量庫中的搜尋結果。

## 功能特色

- 🔍 **模擬AI工作流搜尋**: 使用與AI工作流相同的RAGRetriever進行搜尋
- 🎯 **向量相似度搜尋**: 基於語義相似度的智能搜尋
- 📊 **結果對比**: 同時顯示RAG檢索器和直接SQL搜尋的結果
- 🛠️ **參數調整**: 可調整搜尋參數（k值、相似度閾值、過濾條件）
- 🎨 **美化輸出**: 彩色輸出和格式化顯示

## 使用方法

### 1. 互動模式（推薦）

```bash
# 進入backend目錄
cd backend

# 啟用虛擬環境
source venv/bin/activate

# 執行互動模式
python scripts/rag_search_tester.py -i
```

### 2. 命令行模式

```bash
# 基本搜尋
python scripts/rag_search_tester.py "美沙冬治療"

# 自訂參數
python scripts/rag_search_tester.py "戒毒機構" -k 10 -t 0.5

# 加入過濾條件
python scripts/rag_search_tester.py "心理諮商" -c "services" -l "zh-tw"
```

### 3. Shell腳本模式

```bash
# 執行shell腳本
./scripts/test_rag_search.sh
```

## 參數說明

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `query` | 查詢內容 | 必填 |
| `-k, --count` | 返回結果數量 | 5 |
| `-t, --threshold` | 相似度閾值 (0.0-1.0) | 0.3 |
| `-c, --category` | 類別過濾 | 無 |
| `-l, --lang` | 語言過濾 | 無 |
| `-i, --interactive` | 互動模式 | False |

## 使用範例

### 範例1: 搜尋戒毒相關資訊
```bash
python scripts/rag_search_tester.py "美沙冬治療 戒毒"
```

### 範例2: 搜尋心理諮商服務
```bash
python scripts/rag_search_tester.py "心理諮商 高雄" -k 8 -t 0.4
```

### 範例3: 搜尋特定類別的服務
```bash
python scripts/rag_search_tester.py "緊急求助" -c "services" -l "zh-tw"
```

## 輸出說明

工具會顯示以下資訊：

1. **嵌入生成**: 查詢向量的維度和前幾個值
2. **RAG檢索器結果**: 使用RAGRetriever的搜尋結果
3. **直接SQL搜尋結果**: 直接SQL查詢的結果（用於對比）
4. **結果對比**: 兩種搜尋方式的結果數量對比

每個搜尋結果包含：
- 📊 相似度分數
- 📁 來源
- 🏷️ 類別
- 📝 內容預覽
- 🔍 元數據（如果有）

## 常見問題

### Q: 為什麼搜尋結果為空？
A: 可能的原因：
1. 相似度閾值太高，嘗試降低threshold值
2. 查詢關鍵字不夠精確
3. 資料庫中沒有相關內容

### Q: 如何提高搜尋準確度？
A: 建議：
1. 使用更具體的關鍵字
2. 調整相似度閾值
3. 使用類別過濾縮小搜尋範圍

### Q: RAG檢索器和直接SQL搜尋結果不同？
A: 這是正常的，因為：
1. RAG檢索器可能有額外的處理邏輯
2. 兩者的查詢方式略有不同
3. 可以通過對比來驗證搜尋效果

## 技術細節

- 使用與AI工作流相同的`RAGRetriever`類別
- 支援向量相似度搜尋和關鍵字搜尋
- 基於PostgreSQL的pgvector擴展
- 使用OpenAI的text-embedding-ada-002模型

## 注意事項

1. 確保已啟用虛擬環境
2. 確保資料庫連接正常
3. 確保向量資料庫已建立並有資料
4. 建議先使用互動模式熟悉功能
