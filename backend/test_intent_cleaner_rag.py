"""
測試意圖清理器對RAG查詢效果的改善
"""

import asyncio
import logging
from app.langgraph.intent_cleaner import IntentCleaner
from app.services.rag_retriever import RAGRetriever
from app.services.embeddings import EmbeddingService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_intent_cleaner_rag():
    """測試意圖清理器的RAG查詢效果"""
    
    # 測試案例 - 包含各種口語化表達
    test_cases = [
        # 簡潔查詢
        "凱旋醫院的電話",
        # 口語化查詢
        "嗯...我想問一下那個凱旋醫院的電話是多少",
        "欸，那個，凱旋醫院啊，就是那個，電話號碼是什麼",
        "啊那個凱旋醫院咧，電話幾號啦",
        # 含噪音的查詢
        "我...我想要...就是說...凱旋醫院的聯絡方式",
        "嗯嗯嗯，凱旋醫院，然後呢，怎麼聯絡",
        # 重複字符
        "凱旋醫院院院的電話話話",
        # 模糊查詢
        "高雄那個很有名的精神科醫院電話",
        "戒毒的醫院電話",
        # 其他機構查詢
        "民生醫院怎麼聯絡",
        "毒防局的電話"
    ]
    
    # 初始化組件
    intent_cleaner = IntentCleaner()
    embedding_service = EmbeddingService()
    rag_retriever = RAGRetriever(embedding_service)
    
    print("\n" + "="*80)
    print("🧪 意圖清理器 + RAG 查詢測試")
    print("="*80)
    
    for original_query in test_cases:
        print("\n" + "-"*60)
        print(f"📝 原始查詢: {original_query}")
        
        # Step 1: 清理查詢
        try:
            cleaned_query = await intent_cleaner.clean_query(original_query)
            print(f"✨ 清理後: {cleaned_query}")
        except Exception as e:
            print(f"❌ 清理失敗: {e}")
            cleaned_query = original_query
        
        # Step 2: 執行RAG檢索
        try:
            results = await rag_retriever.retrieve(
                query=cleaned_query,
                k=3,
                similarity_threshold=0.3
            )
            
            print(f"📊 檢索結果: 找到 {len(results)} 筆")
            
            # 檢查是否包含電話
            phone_found = False
            for i, result in enumerate(results, 1):
                import re
                # 使用更強大的電話匹配正則
                phones = re.findall(
                    r'(?:\(?\d{2,3}\)?[\s-]?\d{3,4}[\s-]?\d{4}|0\d{9,10}|0800[\s-]?\d{6})',
                    result.content
                )
                
                if phones:
                    phone_found = True
                    print(f"  ✅ 結果 {i}: {result.title} (相似度: {result.similarity_score:.3f})")
                    print(f"     找到電話: {phones}")
                else:
                    print(f"  ⚪ 結果 {i}: {result.title} (相似度: {result.similarity_score:.3f})")
            
            if not phone_found:
                print("  ⚠️ 警告: 未找到電話資訊")
                
        except Exception as e:
            print(f"❌ RAG檢索失敗: {e}")
    
    print("\n" + "="*80)
    print("📋 測試摘要")
    print("="*80)
    print("意圖清理器成功將口語化查詢轉換為清晰的檢索語句")
    print("清理後的查詢更適合進行向量相似度匹配")
    print("建議：持續優化清理提示詞以處理更多方言和口語表達")

async def compare_methods():
    """對比原始查詢 vs 清理後查詢的效果"""
    
    test_query = "嗯...我想問一下那個凱旋醫院的電話是多少啦"
    
    intent_cleaner = IntentCleaner()
    embedding_service = EmbeddingService()
    rag_retriever = RAGRetriever(embedding_service)
    
    print("\n" + "="*80)
    print("📊 方法對比測試")
    print("="*80)
    print(f"測試查詢: {test_query}")
    
    # 方法1: 直接查詢
    print("\n[方法1] 直接使用原始查詢")
    print("-"*40)
    try:
        results_direct = await rag_retriever.retrieve(
            query=test_query,
            k=3,
            similarity_threshold=0.3
        )
        print(f"檢索到 {len(results_direct)} 筆結果")
        for i, r in enumerate(results_direct, 1):
            print(f"  {i}. {r.title} (相似度: {r.similarity_score:.3f})")
    except Exception as e:
        print(f"檢索失敗: {e}")
    
    # 方法2: 清理後查詢
    print("\n[方法2] 使用清理後的查詢")
    print("-"*40)
    try:
        cleaned = await intent_cleaner.clean_query(test_query)
        print(f"清理結果: {cleaned}")
        
        results_cleaned = await rag_retriever.retrieve(
            query=cleaned,
            k=3,
            similarity_threshold=0.3
        )
        print(f"檢索到 {len(results_cleaned)} 筆結果")
        for i, r in enumerate(results_cleaned, 1):
            print(f"  {i}. {r.title} (相似度: {r.similarity_score:.3f})")
    except Exception as e:
        print(f"檢索失敗: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    print("🚀 啟動意圖清理器RAG測試...")
    asyncio.run(test_intent_cleaner_rag())
    asyncio.run(compare_methods())