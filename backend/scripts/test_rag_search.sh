#!/bin/bash

# RAG向量搜尋測試腳本
# 用於測試AI工作流中的RAG搜尋功能

# 設定顏色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 設定預設值
DEFAULT_K=5
DEFAULT_THRESHOLD=0.3
DEFAULT_CATEGORY=""
DEFAULT_LANG=""

# 顯示標題
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}    RAG向量搜尋測試工具${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 檢查Python環境
check_python_env() {
    echo -e "${BLUE}檢查Python環境...${NC}"
    
    # 檢查是否在虛擬環境中
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo -e "${GREEN}✓ 已啟用虛擬環境: $VIRTUAL_ENV${NC}"
    else
        echo -e "${YELLOW}⚠ 未檢測到虛擬環境，建議先啟用venv${NC}"
        echo "  執行: source venv/bin/activate"
    fi
    
    # 檢查必要的套件
    python3 -c "import sys; sys.path.append('.'); from app.services.rag_retriever import RAGRetriever" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ RAG模組載入成功${NC}"
    else
        echo -e "${RED}✗ RAG模組載入失敗，請檢查環境設定${NC}"
        exit 1
    fi
    echo ""
}

# 顯示使用說明
show_help() {
    echo -e "${YELLOW}使用說明:${NC}"
    echo "1. 輸入查詢內容（支援中文）"
    echo "2. 可選擇調整搜尋參數："
    echo "   - k: 返回結果數量 (預設: $DEFAULT_K)"
    echo "   - threshold: 相似度閾值 (預設: $DEFAULT_THRESHOLD)"
    echo "   - category: 文件類別過濾"
    echo "   - lang: 語言過濾 (zh-tw, en等)"
    echo "3. 輸入 'quit' 或 'exit' 結束程式"
    echo "4. 輸入 'help' 顯示此說明"
    echo ""
}

# 執行RAG搜尋
run_rag_search() {
    local query="$1"
    local k="$2"
    local threshold="$3"
    local category="$4"
    local lang="$5"
    
    echo -e "${BLUE}執行RAG搜尋...${NC}"
    echo -e "${CYAN}查詢: ${query}${NC}"
    echo -e "${CYAN}參數: k=${k}, threshold=${threshold}${NC}"
    if [ -n "$category" ]; then
        echo -e "${CYAN}類別過濾: ${category}${NC}"
    fi
    if [ -n "$lang" ]; then
        echo -e "${CYAN}語言過濾: ${lang}${NC}"
    fi
    echo ""
    
    # 建立Python腳本
    cat > /tmp/rag_search.py << EOF
#!/usr/bin/env python3
import asyncio
import sys
import json
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent.parent))

from app.services.rag_retriever import RAGRetriever

async def main():
    try:
        # 建立檢索器
        retriever = RAGRetriever()
        
        # 設定過濾條件
        filters = {}
        if "$category":
            filters["category"] = "$category"
        if "$lang":
            filters["lang"] = "$lang"
        
        # 執行搜尋
        results = await retriever.retrieve(
            query="$query",
            k=$k,
            filters=filters if filters else None,
            similarity_threshold=$threshold
        )
        
        # 輸出結果
        print(f"找到 {len(results)} 個結果:")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\\n{i}. {result.title}")
            print(f"   相似度: {result.similarity_score:.4f}")
            print(f"   來源: {result.source}")
            print(f"   類別: {result.category}")
            print(f"   內容: {result.content[:200]}...")
            if result.metadata:
                print(f"   元數據: {json.dumps(result.metadata, ensure_ascii=False, indent=2)}")
            print("-" * 80)
        
        if not results:
            print("未找到相關結果，建議:")
            print("1. 降低相似度閾值")
            print("2. 調整查詢關鍵字")
            print("3. 檢查過濾條件")
            
    except Exception as e:
        print(f"搜尋錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    # 執行Python腳本
    python3 /tmp/rag_search.py
    
    # 清理臨時文件
    rm -f /tmp/rag_search.py
}

# 互動式搜尋
interactive_search() {
    while true; do
        echo -e "${GREEN}請輸入查詢內容 (或輸入 'help' 查看說明, 'quit' 結束):${NC}"
        read -r query
        
        # 檢查退出指令
        if [[ "$query" == "quit" || "$query" == "exit" || "$query" == "q" ]]; then
            echo -e "${YELLOW}再見！${NC}"
            break
        fi
        
        # 檢查說明指令
        if [[ "$query" == "help" || "$query" == "h" ]]; then
            show_help
            continue
        fi
        
        # 檢查空輸入
        if [[ -z "$query" ]]; then
            echo -e "${RED}請輸入查詢內容${NC}"
            continue
        fi
        
        # 詢問搜尋參數
        echo -e "${BLUE}使用預設參數嗎？ (y/n) [y]:${NC}"
        read -r use_default
        use_default=${use_default:-y}
        
        k=$DEFAULT_K
        threshold=$DEFAULT_THRESHOLD
        category=$DEFAULT_CATEGORY
        lang=$DEFAULT_LANG
        
        if [[ "$use_default" != "y" && "$use_default" != "Y" ]]; then
            echo -e "${BLUE}返回結果數量 (k) [$DEFAULT_K]:${NC}"
            read -r input_k
            k=${input_k:-$DEFAULT_K}
            
            echo -e "${BLUE}相似度閾值 (0.0-1.0) [$DEFAULT_THRESHOLD]:${NC}"
            read -r input_threshold
            threshold=${input_threshold:-$DEFAULT_THRESHOLD}
            
            echo -e "${BLUE}文件類別過濾 (可選):${NC}"
            read -r input_category
            category=${input_category:-$DEFAULT_CATEGORY}
            
            echo -e "${BLUE}語言過濾 (可選，如: zh-tw, en):${NC}"
            read -r input_lang
            lang=${input_lang:-$DEFAULT_LANG}
        fi
        
        echo ""
        run_rag_search "$query" "$k" "$threshold" "$category" "$lang"
        echo ""
    done
}

# 主程式
main() {
    check_python_env
    show_help
    interactive_search
}

# 執行主程式
main
