#!/usr/bin/env python3
"""測試RAG系統"""

import asyncio
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent.parent))

from app.services.embeddings import EmbeddingService
from app.services.rag_retriever import RAGRetriever
from app.database import get_db_context
from sqlalchemy import text

async def test_embedding():
    """測試嵌入生成"""
    print("測試嵌入生成...")
    
    embedding_service = EmbeddingService()
    
    # 生成測試嵌入
    test_text = "美沙冬治療"
    embedding = await embedding_service.embed_text(test_text)
    
    print(f"嵌入維度: {len(embedding)}")
    print(f"嵌入前5個值: {embedding[:5]}")
    
    return embedding

async def test_direct_sql():
    """測試直接SQL查詢"""
    print("\n測試直接SQL查詢...")
    
    embedding = await test_embedding()
    
    # 將向量轉換為字符串格式
    embedding_str = '[' + ','.join(map(str, embedding)) + ']'
    
    try:
        async with get_db_context() as db:
            sql_query = """
            SELECT 
                ke.content,
                kd.title,
                1 - (ke.embedding <=> $1::vector) as similarity_score
            FROM knowledge_embeddings ke
            JOIN knowledge_documents kd ON ke.document_id = kd.id
            ORDER BY similarity_score DESC
            LIMIT 3
            """
            
            result = await db.execute(text(sql_query), [embedding_str])
            rows = result.fetchall()
            
            print(f"找到 {len(rows)} 個結果:")
            for i, row in enumerate(rows, 1):
                print(f"{i}. {row[1]} (相似度: {row[2]:.3f})")
                print(f"   內容: {row[0][:100]}...")
                
    except Exception as e:
        print(f"SQL查詢錯誤: {str(e)}")

async def test_rag_retriever():
    """測試RAG檢索器"""
    print("\n測試RAG檢索器...")
    
    retriever = RAGRetriever()
    
    try:
        results = await retriever.retrieve("美沙冬治療", k=3)
        print(f"RAG檢索結果: {len(results)} 個")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title} (相似度: {result.similarity_score:.3f})")
            print(f"   內容: {result.content[:100]}...")
            
    except Exception as e:
        print(f"RAG檢索錯誤: {str(e)}")

async def main():
    """主函數"""
    print("開始測試RAG系統...")
    
    await test_embedding()
    await test_direct_sql()
    await test_rag_retriever()
    
    print("\n測試完成！")

if __name__ == "__main__":
    asyncio.run(main())

