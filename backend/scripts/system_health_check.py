#!/usr/bin/env python3
"""
系統健康檢查腳本
檢查所有關鍵組件是否正常運作
"""
import asyncio
import os
import sys
from pathlib import Path
import aiohttp
import psycopg2
from datetime import datetime

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

# 顏色輸出
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

def print_status(component, status, message=""):
    """印出狀態"""
    if status == "OK":
        print(f"{GREEN}✓{END} {component}: {GREEN}正常{END} {message}")
    elif status == "FAIL":
        print(f"{RED}✗{END} {component}: {RED}失敗{END} {message}")
    elif status == "WARN":
        print(f"{YELLOW}⚠{END} {component}: {YELLOW}警告{END} {message}")
    else:
        print(f"{BLUE}ℹ{END} {component}: {message}")


async def check_environment():
    """檢查環境變數"""
    print("\n" + "="*50)
    print("1. 檢查環境變數配置")
    print("="*50)
    
    required_vars = [
        'OPENAI_API_KEY',
        'DATABASE_URL',
        'REDIS_URL',
        'SECRET_KEY'
    ]
    
    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 遮蔽敏感資訊
            if 'KEY' in var or 'PASSWORD' in var:
                display_value = value[:8] + "..." if len(value) > 8 else "***"
            else:
                display_value = value[:30] + "..." if len(value) > 30 else value
            print_status(var, "OK", f"({display_value})")
        else:
            print_status(var, "FAIL", "未設定")
            all_ok = False
    
    return all_ok


async def check_database():
    """檢查資料庫連接"""
    print("\n" + "="*50)
    print("2. 檢查資料庫連接")
    print("="*50)
    
    try:
        # 從環境變數取得資料庫連接資訊
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/kaohsiung_care')
        
        # 轉換為 psycopg2 格式
        if database_url.startswith('postgresql+asyncpg://'):
            database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 檢查版本
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print_status("PostgreSQL 連接", "OK", f"版本: {version.split(',')[0]}")
        
        # 檢查 pgvector 擴展
        cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
        vector_version = cursor.fetchone()
        if vector_version:
            print_status("pgvector 擴展", "OK", f"版本: {vector_version[0]}")
        else:
            print_status("pgvector 擴展", "FAIL", "未安裝")
        
        # 檢查重要資料表
        tables_to_check = [
            'knowledge_documents',
            'knowledge_embeddings',
            'conversations',
            'messages',
            'upload_records',
            'authoritative_media',
            'authoritative_contacts'
        ]
        
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table}';")
            exists = cursor.fetchone()[0] > 0
            if exists:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print_status(f"資料表 {table}", "OK", f"({count} 筆資料)")
            else:
                print_status(f"資料表 {table}", "FAIL", "不存在")
        
        # 檢查 metadata 欄位
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'knowledge_documents' AND column_name = 'metadata';
        """)
        metadata_column = cursor.fetchone()
        if metadata_column:
            print_status("metadata 欄位", "OK", f"類型: {metadata_column[1]}")
        else:
            print_status("metadata 欄位", "WARN", "不存在 (需要執行遷移)")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print_status("資料庫連接", "FAIL", str(e))
        return False


async def check_openai_api():
    """檢查 OpenAI API 連接"""
    print("\n" + "="*50)
    print("3. 檢查 OpenAI API 連接")
    print("="*50)
    
    try:
        import openai
        from openai import AsyncOpenAI
        
        # 設定 API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print_status("OpenAI API Key", "FAIL", "未設定")
            return False
        
        client = AsyncOpenAI(api_key=api_key)
        
        # 測試 API 連接
        print_status("OpenAI API Key", "OK", f"已設定 ({api_key[:8]}...)")
        
        # 測試模型列表
        models = await client.models.list()
        available_models = [m.id for m in models.data]
        
        # 檢查關鍵模型
        required_models = ['gpt-4o', 'gpt-4', 'gpt-3.5-turbo']
        for model in required_models:
            if any(model in m for m in available_models):
                print_status(f"模型 {model}", "OK", "可用")
            else:
                print_status(f"模型 {model}", "WARN", "不可用")
        
        # 測試 embeddings
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input="測試文本"
        )
        if response.data:
            print_status("Embeddings API", "OK", f"向量維度: {len(response.data[0].embedding)}")
        
        # 測試 chat completion
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "回覆OK"}],
            max_tokens=10
        )
        if response.choices:
            print_status("Chat API", "OK", "回應正常")
        
        return True
        
    except Exception as e:
        print_status("OpenAI API", "FAIL", str(e))
        return False


async def check_redis():
    """檢查 Redis 連接"""
    print("\n" + "="*50)
    print("4. 檢查 Redis 連接")
    print("="*50)
    
    try:
        import redis.asyncio as redis
        
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        r = redis.from_url(redis_url)
        
        # 測試連接
        await r.ping()
        print_status("Redis 連接", "OK", redis_url)
        
        # 測試設定和取得
        await r.set('health_check', datetime.now().isoformat())
        value = await r.get('health_check')
        if value:
            print_status("Redis 讀寫", "OK")
        
        # 檢查記憶體使用
        info = await r.info('memory')
        used_memory = info.get('used_memory_human', 'N/A')
        print_status("Redis 記憶體", "OK", f"使用: {used_memory}")
        
        await r.close()
        return True
        
    except Exception as e:
        print_status("Redis", "WARN", f"無法連接: {str(e)}")
        return False


async def check_api_endpoints():
    """檢查 API 端點"""
    print("\n" + "="*50)
    print("5. 檢查 API 端點")
    print("="*50)
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        ("GET", "/health", None),
        ("GET", "/api/chat/test", None),
        ("POST", "/api/chat/message", {
            "user_id": "test_user",
            "message": "測試訊息",
            "conversation_id": None
        }),
        ("GET", "/api/admin/drug-knowledge/list", None),
    ]
    
    async with aiohttp.ClientSession() as session:
        for method, endpoint, data in endpoints:
            url = f"{base_url}{endpoint}"
            try:
                if method == "GET":
                    async with session.get(url) as response:
                        if response.status in [200, 404]:
                            print_status(f"{method} {endpoint}", "OK", f"狀態碼: {response.status}")
                        else:
                            print_status(f"{method} {endpoint}", "WARN", f"狀態碼: {response.status}")
                else:
                    async with session.post(url, json=data) as response:
                        if response.status in [200, 201, 422]:
                            print_status(f"{method} {endpoint}", "OK", f"狀態碼: {response.status}")
                        else:
                            print_status(f"{method} {endpoint}", "WARN", f"狀態碼: {response.status}")
            except Exception as e:
                print_status(f"{method} {endpoint}", "FAIL", f"錯誤: {str(e)[:50]}")


async def test_rag_flow():
    """測試 RAG 檢索流程"""
    print("\n" + "="*50)
    print("6. 測試 RAG 檢索流程")
    print("="*50)
    
    try:
        from app.services.embeddings import EmbeddingService
        from app.services.rag_retriever import RAGRetriever
        
        # 初始化服務
        embedding_service = EmbeddingService()
        retriever = RAGRetriever(embedding_service)
        
        # 測試向量生成
        test_text = "測試毒品防制相關內容"
        embedding = await embedding_service.embed_text(test_text)
        if embedding and len(embedding) > 0:
            print_status("向量生成", "OK", f"維度: {len(embedding)}")
        else:
            print_status("向量生成", "FAIL")
            return False
        
        # 測試檢索
        results = await retriever.retrieve(
            query="毒品防制",
            k=5,
            similarity_threshold=0.3
        )
        
        if results is not None:
            print_status("RAG 檢索", "OK", f"找到 {len(results)} 筆結果")
            
            # 顯示前3筆結果
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result.title[:50]}... (相似度: {result.similarity_score:.3f})")
        else:
            print_status("RAG 檢索", "WARN", "無結果")
        
        return True
        
    except Exception as e:
        print_status("RAG 流程", "FAIL", str(e))
        return False


async def main():
    """主函數"""
    print("\n" + "="*60)
    print("🏥 高雄市毒防局關懷聊天 AI 系統 - 健康檢查")
    print("="*60)
    print(f"檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 執行各項檢查
    env_ok = await check_environment()
    db_ok = await check_database()
    openai_ok = await check_openai_api()
    redis_ok = await check_redis()
    await check_api_endpoints()
    await test_rag_flow()
    
    # 總結
    print("\n" + "="*50)
    print("檢查總結")
    print("="*50)
    
    if env_ok and db_ok and openai_ok:
        print(f"{GREEN}✓ 系統核心組件運作正常{END}")
    else:
        print(f"{RED}✗ 系統存在問題，請檢查上述錯誤{END}")
    
    if not redis_ok:
        print(f"{YELLOW}⚠ Redis 未連接，但系統仍可運作{END}")
    
    print("\n建議動作:")
    if not env_ok:
        print("1. 檢查 .env 檔案是否正確設定")
    if not db_ok:
        print("2. 確認資料庫服務是否啟動")
        print("   執行: docker-compose up -d postgres")
        print("   執行遷移: psql -f migrations/add_metadata_to_knowledge.sql")
    if not openai_ok:
        print("3. 檢查 OpenAI API key 是否有效")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(main())