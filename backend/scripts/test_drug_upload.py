#!/usr/bin/env python3
"""
測試毒品知識上傳 API
"""
import asyncio
import aiohttp
import pandas as pd
import json
from pathlib import Path
import io

# API 基礎 URL
BASE_URL = "http://localhost:8000/api"


async def test_download_template():
    """測試下載模板"""
    print("\n=== 測試下載 Excel 模板 ===")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/admin/drug-knowledge/template") as response:
            if response.status == 200:
                content = await response.read()
                # 儲存模板
                with open("drug_template_test.xlsx", "wb") as f:
                    f.write(content)
                print("✅ 成功下載模板：drug_template_test.xlsx")
                
                # 讀取並顯示內容
                df = pd.read_excel(io.BytesIO(content))
                print(f"模板欄位：{df.columns.tolist()}")
                print(f"範例資料筆數：{len(df)}")
                return True
            else:
                print(f"❌ 下載失敗：{response.status}")
                return False


async def test_json_upload():
    """測試 JSON 上傳"""
    print("\n=== 測試 JSON 上傳 ===")
    
    test_data = [
        {
            "formal_name": "氯胺酮",
            "common_names": ["K他命", "K仔", "K粉", "Special K"],
            "control_level": "第三級",
            "medical_use": "動物麻醉劑，人體麻醉（受限使用）",
            "health_risks": "膀胱炎、記憶力受損、認知功能障礙",
            "legal_info": "毒品危害防制條例第4條第3項"
        },
        {
            "formal_name": "MDMA",
            "common_names": ["搖頭丸", "快樂丸", "E仔", "衣服"],
            "control_level": "第二級",
            "medical_use": "無合法醫療用途",
            "health_risks": "脫水、體溫過高、心律不整",
            "legal_info": "毒品危害防制條例第4條第2項"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/admin/drug-knowledge/upload-json",
            json=test_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ 上傳成功：{result.get('message')}")
                return True
            else:
                print(f"❌ 上傳失敗：{response.status}")
                text = await response.text()
                print(f"錯誤訊息：{text}")
                return False


async def test_excel_upload():
    """測試 Excel 上傳"""
    print("\n=== 測試 Excel 上傳 ===")
    
    # 建立測試資料
    test_df = pd.DataFrame({
        '正式名稱': ['古柯鹼', '卡西酮類'],
        '俗名（逗號分隔）': ['可卡因,快克,雪花', '浴鹽,喵喵'],
        '管制等級': ['第一級', '第二級'],
        '醫療用途': ['局部麻醉（極少使用）', '無'],
        '健康風險': ['心臟病、中風、成癮性極高', '幻覺、暴力行為、精神錯亂'],
        '相關法條': ['毒品危害防制條例第4條第1項', '毒品危害防制條例第4條第2項'],
        '備註': ['', '新興毒品']
    })
    
    # 儲存為 Excel
    excel_buffer = io.BytesIO()
    test_df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    
    # 準備上傳
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field('file',
                      excel_buffer,
                      filename='test_drugs.xlsx',
                      content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        data.add_field('uploaded_by', 'test_admin')
        data.add_field('batch_name', 'test_batch')
        
        async with session.post(
            f"{BASE_URL}/admin/drug-knowledge/upload-excel",
            data=data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Excel 上傳成功：{result.get('message')}")
                return True
            else:
                print(f"❌ Excel 上傳失敗：{response.status}")
                text = await response.text()
                print(f"錯誤訊息：{text}")
                return False


async def test_list_knowledge():
    """測試列出知識庫"""
    print("\n=== 測試列出毒品知識 ===")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/admin/drug-knowledge/list") as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ 查詢成功：共 {result.get('total', 0)} 筆資料")
                
                # 顯示前3筆
                items = result.get('items', [])[:3]
                for item in items:
                    print(f"  - {item['title']}")
                    if item.get('metadata'):
                        print(f"    俗名：{item['metadata'].get('common_names', [])}")
                        print(f"    等級：{item['metadata'].get('control_level', 'N/A')}")
                return True
            else:
                print(f"❌ 查詢失敗：{response.status}")
                return False


async def test_search_rag():
    """測試 RAG 檢索是否能找到毒品資訊"""
    print("\n=== 測試 RAG 檢索毒品資訊 ===")
    
    test_queries = [
        "K他命是什麼",
        "搖頭丸的風險",
        "喵喵是什麼毒品"
    ]
    
    from app.services.rag_retriever import RAGRetriever
    from app.services.embeddings import EmbeddingService
    
    retriever = RAGRetriever(EmbeddingService())
    
    for query in test_queries:
        print(f"\n查詢：{query}")
        results = await retriever.retrieve(
            query=query,
            k=3,
            filters={"category": "drug_information"},
            similarity_threshold=0.5
        )
        
        if results:
            print(f"  找到 {len(results)} 筆相關資料")
            for i, result in enumerate(results[:2], 1):
                print(f"  {i}. {result.title[:50]}...")
                print(f"     相似度：{result.similarity_score:.3f}")
        else:
            print("  未找到相關資料")


async def main():
    """執行所有測試"""
    print("開始測試毒品知識上傳功能...")
    
    # 執行測試
    await test_download_template()
    await test_json_upload()
    await test_excel_upload()
    await test_list_knowledge()
    
    # 等待處理完成
    print("\n等待背景處理完成...")
    await asyncio.sleep(3)
    
    # 測試檢索
    await test_search_rag()
    
    print("\n測試完成！")


if __name__ == "__main__":
    asyncio.run(main())