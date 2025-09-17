"""簡單測試 Google Places API 服務（不需要完整環境）"""

import asyncio
import os
import sys
from pathlib import Path

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent))

# 設定環境變數
os.environ['GOOGLE_API_KEY'] = 'AIzaSyD1THfdpPUj2dC8YnHSbRBDOTjy4rmuEm4'


async def test_places_service():
    """直接測試 Places 服務"""

    # 只導入需要的服務
    from app.services.google_places_service import GooglePlacesService, PlaceQueryDetector

    service = GooglePlacesService()

    test_queries = [
        "高雄市毒品防制局",
        "凱旋醫院",
        "高雄長庚醫院",
        "高雄市政府衛生局"
    ]

    print("="*60)
    print("Google Places API 服務測試")
    print("="*60)

    for query in test_queries:
        print(f"\n查詢: {query}")
        print("-"*40)

        try:
            result = await service.search_place(query)

            if result:
                print(f"✅ 找到結果:")
                print(f"  名稱: {result.get('name')}")
                print(f"  地址: {result.get('address')}")
                print(f"  電話: {result.get('phone')}")
                print(f"  營業時間: {result.get('opening_hours', '未提供')[:50]}...")
                print(f"  評分: {result.get('rating', '無')}")

                # 測試格式化輸出
                formatted = service.format_for_response(result)
                print(f"\n  格式化輸出: {formatted}")
            else:
                print(f"❌ 未找到結果")

        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")

    # 測試意圖偵測
    print("\n" + "="*60)
    print("測試地點查詢意圖偵測")
    print("="*60)

    test_texts = [
        "高雄市毒品防制局的電話是多少？",
        "凱旋醫院在哪裡？",
        "高雄長庚醫院營業時間",
        "我心情不好",
        "你好"
    ]

    for text in test_texts:
        detection = PlaceQueryDetector.detect_place_query(text)
        print(f"\n文字: {text}")
        print(f"  是否為地點查詢: {detection['is_place_query']}")
        print(f"  查詢類型: {detection['query_type']}")
        print(f"  地點名稱: {detection['place_name']}")
        print(f"  信心分數: {detection['confidence']}")


if __name__ == "__main__":
    asyncio.run(test_places_service())