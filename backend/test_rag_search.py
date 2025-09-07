#!/usr/bin/env python
"""直接測試 RAG 搜尋功能"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_retriever import RAGRetriever
from app.services.embeddings import EmbeddingService

async def test_rag_search():
    """測試 RAG 搜尋"""
    
    embedding_service = EmbeddingService()
    retriever = RAGRetriever(embedding_service)
    
    queries = [
        "戒毒諮詢",
        "高雄市毒品危害防制中心",
        "聯絡電話",
        "機構"
    ]
    
    for query in queries:
        print(f"\n搜尋: '{query}'")
        print("-" * 50)
        
        try:
            # 測試不同的類別過濾
            for category in [None, "contacts", "authoritative_contacts"]:
                filters = {"category": category} if category else None
                filter_desc = f"(類別: {category})" if category else "(無過濾)"
                
                results = await retriever.retrieve(
                    query=query,
                    k=3,
                    filters=filters
                )
                
                print(f"\n{filter_desc} 找到 {len(results)} 個結果:")
                
                for i, result in enumerate(results, 1):
                    print(f"\n  {i}. 相似度: {result.similarity_score:.3f}")
                    print(f"     標題: {result.title}")
                    print(f"     類別: {result.category}")
                    print(f"     來源: {result.source}")
                    print(f"     內容: {result.content[:100]}...")
                    
        except Exception as e:
            print(f"  ❌ 搜尋失敗: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_rag_search())