"""透過 API 測試聊天功能（包含 Places API）"""

import requests
import json
import time

API_URL = "http://localhost:8001/api/v1"

def test_chat(message: str, session_id: str = "test_session"):
    """測試聊天 API"""

    url = f"{API_URL}/chat/"

    payload = {
        "message": message,
        "session_id": session_id,
        "user_id": "test_user"
    }

    print(f"\n{'='*60}")
    print(f"用戶輸入: {message}")
    print(f"{'='*60}")

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            print(f"AI回應: {data.get('reply', '無回應')}")

            # 如果有意圖分析，顯示
            if 'intent_analysis' in data:
                intent = data['intent_analysis']
                print(f"\n[分析結果]")
                print(f"  意圖: {intent.get('intent')}")
                print(f"  需要Places API: {intent.get('need_places_api')}")
                if intent.get('place_query_info'):
                    pqi = intent['place_query_info']
                    print(f"  查詢類型: {pqi.get('query_type')}")
                    print(f"  地點名稱: {pqi.get('place_name')}")
        else:
            print(f"❌ API 錯誤: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到後端服務")
        print("請確保後端服務正在運行: python -m app.main")
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")

def main():
    print("="*60)
    print("測試 AI 聊天 API (含 Google Places 查詢)")
    print("="*60)
    print("\n請先確保後端服務正在運行:")
    print("  cd backend && python -m app.main")
    print("="*60)

    # 測試案例
    test_messages = [
        "你好",
        "高雄市毒品防制局的電話是多少？",
        "凱旋醫院在哪裡？",
        "高雄長庚醫院幾點開門？",
        "我心情不好",
        "衛生局的地址在哪？"
    ]

    session_id = f"test_{int(time.time())}"

    for msg in test_messages:
        test_chat(msg, session_id)
        time.sleep(1)  # 避免太快

if __name__ == "__main__":
    main()