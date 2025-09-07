#!/usr/bin/env python
"""測試向量嵌入生成"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.embeddings import EmbeddingService
from app.services.knowledge_manager import KnowledgeManager
from app.database import get_db_context
from sqlalchemy import select
from app.models.knowledge import KnowledgeDocument, KnowledgeEmbedding

async def test_embedding():
    """測試向量嵌入生成"""
    
    # 測試 EmbeddingService
    print("1. 測試 EmbeddingService...")
    embedding_service = EmbeddingService()
    
    try:
        test_text = "高雄市毒品危害防制中心提供戒毒諮詢服務"
        embedding = await embedding_service.embed_text(test_text)
        print(f"   ✅ 生成向量成功，維度: {len(embedding)}")
    except Exception as e:
        print(f"   ❌ 生成向量失敗: {e}")
        return
    
    # 檢查現有的知識文件
    print("\n2. 檢查 authoritative_contacts 類別的文件...")
    async with get_db_context() as db:
        stmt = select(KnowledgeDocument).where(
            KnowledgeDocument.category == "authoritative_contacts"
        )
        result = await db.execute(stmt)
        documents = result.scalars().all()
        
        print(f"   找到 {len(documents)} 個文件")
        
        for doc in documents[:3]:  # 只顯示前3個
            print(f"   - {doc.title[:50]}... (ID: {doc.id})")
            
            # 檢查是否有向量嵌入
            stmt = select(KnowledgeEmbedding).where(
                KnowledgeEmbedding.document_id == doc.id
            )
            result = await db.execute(stmt)
            embeddings = result.scalars().all()
            
            if embeddings:
                print(f"     已有 {len(embeddings)} 個向量嵌入")
            else:
                print(f"     ⚠️ 沒有向量嵌入")
                
                # 嘗試重新生成向量嵌入
                print(f"     嘗試重新生成向量嵌入...")
                try:
                    from app.services.chunker import DocumentChunker
                    
                    chunker = DocumentChunker(chunk_size=500, overlap=50)
                    chunks = chunker.chunk_document(
                        title=doc.title,
                        content=doc.content,
                        source=doc.source,
                        category=doc.category,
                        lang=doc.lang,
                        published_date=doc.published_date.isoformat() if doc.published_date else None
                    )
                    
                    for chunk in chunks:
                        embedding = await embedding_service.embed_text(chunk.content)
                        
                        embedding_record = KnowledgeEmbedding(
                            document_id=doc.id,
                            chunk_index=chunk.chunk_index,
                            content=chunk.content,
                            embedding=embedding,
                            metadata_json=chunk.metadata
                        )
                        db.add(embedding_record)
                    
                    await db.commit()
                    print(f"     ✅ 成功生成 {len(chunks)} 個向量嵌入")
                    
                except Exception as e:
                    print(f"     ❌ 生成失敗: {e}")
                    await db.rollback()

if __name__ == "__main__":
    asyncio.run(test_embedding())