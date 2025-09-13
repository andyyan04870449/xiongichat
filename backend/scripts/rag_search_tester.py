#!/usr/bin/env python3
"""
RAG向量搜尋測試工具
用於測試AI工作流中的RAG搜尋功能，模擬AI工作流的搜尋方式
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List

# 添加專案根目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent.parent))

from app.services.rag_retriever import RAGRetriever
from app.services.embeddings import EmbeddingService
from app.database import get_db_context
from sqlalchemy import text
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGSearchTester:
    """RAG搜尋測試器"""
    
    def __init__(self):
        self.retriever = RAGRetriever()
        self.embedding_service = EmbeddingService()
    
    async def test_embedding_generation(self, query: str) -> List[float]:
        """測試嵌入生成"""
        print(f"🔍 生成查詢向量: '{query}'")
        embedding = await self.embedding_service.embed_text(query)
        print(f"   向量維度: {len(embedding)}")
        print(f"   前5個值: {embedding[:5]}")
        return embedding
    
    async def test_vector_search(
        self, 
        query: str, 
        k: int = 5, 
        threshold: float = 0.3,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """測試向量搜尋（模擬AI工作流的搜尋方式）"""
        
        print(f"\n🎯 執行向量搜尋")
        print(f"   查詢: {query}")
        print(f"   參數: k={k}, threshold={threshold}")
        if filters:
            print(f"   過濾條件: {filters}")
        
        try:
            # 使用RAGRetriever進行搜尋（與AI工作流相同的方式）
            results = await self.retriever.retrieve(
                query=query,
                k=k,
                filters=filters,
                similarity_threshold=threshold
            )
            
            print(f"   找到 {len(results)} 個結果")
            return results
            
        except Exception as e:
            print(f"   ❌ 搜尋錯誤: {str(e)}")
            return []
    
    async def test_direct_sql_search(
        self, 
        query: str, 
        k: int = 5, 
        threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """測試直接SQL搜尋（用於對比）"""
        
        print(f"\n🔧 執行直接SQL搜尋")
        
        try:
            # 生成查詢向量
            embedding = await self.embedding_service.embed_text(query)
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            async with get_db_context() as db:
                sql_query = f"""
                SELECT 
                    ke.content,
                    ke.metadata,
                    ke.chunk_index,
                    kd.title,
                    kd.source,
                    kd.category,
                    kd.lang,
                    kd.published_date,
                    1 - (ke.embedding <=> '{embedding_str}'::vector) as similarity_score
                FROM knowledge_embeddings ke
                JOIN knowledge_documents kd ON ke.document_id = kd.id
                WHERE 1 - (ke.embedding <=> '{embedding_str}'::vector) > {threshold}
                ORDER BY similarity_score DESC 
                LIMIT {k}
                """
                
                result = await db.execute(text(sql_query))
                rows = result.fetchall()
                
                # 轉換結果
                results = []
                for row in rows:
                    result_dict = {
                        "content": row[0],
                        "metadata": row[1] or {},
                        "chunk_index": row[2],
                        "title": row[3],
                        "source": row[4],
                        "category": row[5],
                        "lang": row[6],
                        "published_date": row[7].isoformat() if row[7] else None,
                        "similarity_score": float(row[8])
                    }
                    results.append(result_dict)
                
                print(f"   找到 {len(results)} 個結果")
                return results
                
        except Exception as e:
            print(f"   ❌ SQL搜尋錯誤: {str(e)}")
            return []
    
    def format_results(self, results: List[Any], title: str = "搜尋結果"):
        """格式化顯示結果"""
        print(f"\n📋 {title}")
        print("=" * 80)
        
        if not results:
            print("❌ 未找到相關結果")
            print("💡 建議:")
            print("   1. 降低相似度閾值")
            print("   2. 調整查詢關鍵字")
            print("   3. 檢查過濾條件")
            return
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.title if hasattr(result, 'title') else result.get('title', '無標題')}")
            print(f"   📊 相似度: {result.similarity_score if hasattr(result, 'similarity_score') else result.get('similarity_score', 0):.4f}")
            print(f"   📁 來源: {result.source if hasattr(result, 'source') else result.get('source', '未知')}")
            print(f"   🏷️  類別: {result.category if hasattr(result, 'category') else result.get('category', '未知')}")
            
            content = result.content if hasattr(result, 'content') else result.get('content', '')
            print(f"   📝 內容: {content[:200]}...")
            
            if hasattr(result, 'metadata') and result.metadata:
                print(f"   🔍 元數據: {json.dumps(result.metadata, ensure_ascii=False, indent=2)}")
            elif isinstance(result, dict) and result.get('metadata'):
                print(f"   🔍 元數據: {json.dumps(result['metadata'], ensure_ascii=False, indent=2)}")
            
            print("-" * 80)
    
    async def run_comprehensive_test(
        self, 
        query: str, 
        k: int = 5, 
        threshold: float = 0.3,
        filters: Optional[Dict[str, Any]] = None
    ):
        """執行完整的測試流程"""
        
        print(f"\n🚀 開始RAG搜尋測試")
        print(f"查詢內容: '{query}'")
        print("=" * 60)
        
        # 1. 測試嵌入生成
        await self.test_embedding_generation(query)
        
        # 2. 測試RAG檢索器搜尋（與AI工作流相同）
        rag_results = await self.test_vector_search(query, k, threshold, filters)
        self.format_results(rag_results, "RAG檢索器結果")
        
        # 3. 測試直接SQL搜尋（對比用）
        sql_results = await self.test_direct_sql_search(query, k, threshold)
        self.format_results(sql_results, "直接SQL搜尋結果")
        
        # 4. 結果對比
        print(f"\n📊 結果對比")
        print(f"   RAG檢索器: {len(rag_results)} 個結果")
        print(f"   直接SQL: {len(sql_results)} 個結果")
        
        if rag_results and sql_results:
            # 比較最高分數
            rag_top_score = max(r.similarity_score if hasattr(r, 'similarity_score') else r.get('similarity_score', 0) for r in rag_results)
            sql_top_score = max(r.get('similarity_score', 0) for r in sql_results)
            print(f"   最高相似度 - RAG: {rag_top_score:.4f}, SQL: {sql_top_score:.4f}")


async def interactive_mode():
    """互動模式"""
    tester = RAGSearchTester()
    
    print("🎯 RAG向量搜尋測試工具")
    print("=" * 40)
    print("輸入 'quit' 或 'exit' 結束程式")
    print("輸入 'help' 查看說明")
    print()
    
    while True:
        try:
            query = input("🔍 請輸入查詢內容: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 再見！")
                break
            
            if query.lower() in ['help', 'h']:
                print("\n📖 使用說明:")
                print("1. 直接輸入查詢內容進行搜尋")
                print("2. 支援中文查詢")
                print("3. 使用預設參數: k=5, threshold=0.3")
                print("4. 輸入 'quit' 結束程式")
                print()
                continue
            
            if not query:
                print("❌ 請輸入查詢內容")
                continue
            
            # 詢問是否使用自訂參數
            use_custom = input("🔧 使用自訂參數？ (y/n) [n]: ").strip().lower()
            
            k = 5
            threshold = 0.3
            filters = None
            
            if use_custom in ['y', 'yes']:
                try:
                    k_input = input("📊 返回結果數量 (k) [5]: ").strip()
                    k = int(k_input) if k_input else 5
                    
                    threshold_input = input("🎯 相似度閾值 (0.0-1.0) [0.3]: ").strip()
                    threshold = float(threshold_input) if threshold_input else 0.3
                    
                    category_input = input("🏷️  類別過濾 (可選): ").strip()
                    if category_input:
                        filters = {"category": category_input}
                    
                except ValueError:
                    print("❌ 參數格式錯誤，使用預設值")
                    k = 5
                    threshold = 0.3
            
            # 執行測試
            await tester.run_comprehensive_test(query, k, threshold, filters)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 再見！")
            break
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")


async def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="RAG向量搜尋測試工具")
    parser.add_argument("query", nargs="?", help="查詢內容")
    parser.add_argument("-k", "--count", type=int, default=5, help="返回結果數量")
    parser.add_argument("-t", "--threshold", type=float, default=0.3, help="相似度閾值")
    parser.add_argument("-c", "--category", help="類別過濾")
    parser.add_argument("-l", "--lang", help="語言過濾")
    parser.add_argument("-i", "--interactive", action="store_true", help="互動模式")
    
    args = parser.parse_args()
    
    tester = RAGSearchTester()
    
    if args.interactive or not args.query:
        await interactive_mode()
    else:
        filters = {}
        if args.category:
            filters["category"] = args.category
        if args.lang:
            filters["lang"] = args.lang
        
        await tester.run_comprehensive_test(
            args.query, 
            args.count, 
            args.threshold, 
            filters if filters else None
        )


if __name__ == "__main__":
    asyncio.run(main())
