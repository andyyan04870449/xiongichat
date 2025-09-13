"""
測試RAG檢索器是否能正確檢索凱旋醫院的資訊
"""

import asyncio
import logging
from app.services.rag_retriever import RAGRetriever
from app.services.embeddings import EmbeddingService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_rag_search():
    """測試各種查詢詞的RAG檢索結果"""
    
    # 初始化服務
    embedding_service = EmbeddingService()
    rag = RAGRetriever(embedding_service)
    
    # 測試查詢詞
    test_queries = [
        "凱旋醫院",
        "凱旋醫院電話",
        "高雄市立凱旋醫院",
        "凱旋醫院 07-7513171",
        "高雄市苓雅區凱旋二路130號",
        "07-7513171",
        "藥癮戒治",
        "心理諮商"
    ]
    
    print("=" * 80)
    print("RAG檢索測試")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n查詢: {query}")
        print("-" * 40)
        
        try:
            # 執行檢索
            results = await rag.retrieve(query, k=3, similarity_threshold=0.3)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"\n結果 {i} (相似度: {result.similarity_score:.3f}):")
                    print(f"  標題: {result.title}")
                    print(f"  來源: {result.source}")
                    print(f"  類別: {result.category}")
                    print(f"  內容預覽: {result.content[:200]}...")
                    if len(result.content) > 200:
                        print(f"  (全文長度: {len(result.content)} 字)")
            else:
                print("  無檢索結果")
                
        except Exception as e:
            print(f"  錯誤: {str(e)}")
            logger.error(f"檢索失敗: {str(e)}", exc_info=True)
    
    print("\n" + "=" * 80)
    print("測試完成")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_rag_search())