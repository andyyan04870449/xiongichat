#!/usr/bin/env python3
"""
快速測試系統狀態
"""
import os
import asyncio

print("\n=== 系統健康檢查 ===\n")

# 1. 檢查環境變數
print("1. 環境變數:")
api_key = os.getenv('OPENAI_API_KEY', '')
if api_key:
    print(f"   ✓ OPENAI_API_KEY: {api_key[:20]}...")
else:
    print("   ✗ OPENAI_API_KEY: 未設定")

db_url = os.getenv('DATABASE_URL', '')
if db_url:
    print(f"   ✓ DATABASE_URL: {db_url[:30]}...")
else:
    print("   ✗ DATABASE_URL: 未設定")

# 2. 測試 OpenAI API
print("\n2. OpenAI API 測試:")
try:
    import openai
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    # 測試 chat completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "回覆OK"}],
        max_tokens=10
    )
    
    if response.choices:
        print(f"   ✓ Chat API: {response.choices[0].message.content}")
    
    # 測試 embeddings
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="測試文本"
    )
    
    if response.data:
        print(f"   ✓ Embeddings API: 維度 {len(response.data[0].embedding)}")
    
except Exception as e:
    print(f"   ✗ OpenAI API 錯誤: {str(e)[:100]}")

# 3. 測試資料庫連接
print("\n3. 資料庫連接測試:")
try:
    import psycopg2
    
    # 修正資料庫連接字串
    db_url = "postgresql://xiongichat:xiongichat123@localhost:5432/xiongichat"
    
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # 測試查詢
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"   ✓ PostgreSQL: {version.split(',')[0]}")
    
    # 檢查 pgvector
    cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
    vector_version = cursor.fetchone()
    if vector_version:
        print(f"   ✓ pgvector: 版本 {vector_version[0]}")
    else:
        print("   ⚠ pgvector: 未安裝")
    
    # 檢查重要資料表
    tables = ['knowledge_documents', 'knowledge_embeddings', 'conversations', 'messages']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table}';")
        exists = cursor.fetchone()[0] > 0
        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"   ✓ 表 {table}: {count} 筆資料")
        else:
            print(f"   ✗ 表 {table}: 不存在")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ✗ 資料庫錯誤: {str(e)[:100]}")

# 4. 測試 API 端點
print("\n4. API 端點測試:")
try:
    import requests
    
    # 測試健康檢查
    response = requests.get("http://localhost:8000/health", timeout=2)
    if response.status_code == 200:
        print(f"   ✓ Health Check: {response.status_code}")
    else:
        print(f"   ⚠ Health Check: {response.status_code}")
        
except Exception as e:
    print(f"   ✗ API 服務未啟動: {str(e)[:50]}")

print("\n=== 檢查完成 ===\n")

# 總結
print("建議動作:")
print("1. 如果資料庫連接失敗，執行: docker-compose up -d")
print("2. 如果 API 服務未啟動，執行: python app/main.py")
print("3. 如果 OpenAI API 失敗，檢查 API key 是否有效")