"""Google Places API 服務"""

import aiohttp
import logging
from typing import Optional, Dict, List, Any
from cachetools import TTLCache
import json

from app.config import settings

logger = logging.getLogger(__name__)


class GooglePlacesService:
    """Google Places API 查詢服務"""

    BASE_URL = "https://maps.googleapis.com/maps/api/place"

    def __init__(self):
        self.api_key = settings.google_api_key
        self.cache = TTLCache(maxsize=100, ttl=3600)  # 快取1小時

        if not self.api_key:
            logger.warning("Google API key not configured")

    async def search_place(self, query: str, location_bias: str = "高雄") -> Optional[Dict]:
        """搜尋地點資訊

        Args:
            query: 搜尋關鍵字（例如："高雄市毒品防制局"）
            location_bias: 地理位置偏好（預設高雄）

        Returns:
            包含地點資訊的字典，包含名稱、電話、地址等
        """

        if not self.api_key:
            logger.error("Google API key not available")
            return None

        # 檢查快取
        cache_key = f"place:{query}:{location_bias}"
        if cache_key in self.cache:
            logger.info(f"Cache hit for place search: {query}")
            return self.cache[cache_key]

        try:
            # 建構完整查詢（加上地理位置偏好）
            full_query = f"{query} {location_bias}" if location_bias else query

            # Text Search API
            search_url = f"{self.BASE_URL}/textsearch/json"
            params = {
                "query": full_query,
                "key": self.api_key,
                "language": "zh-TW",
                "region": "tw"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Places API error: {response.status}")
                        return None

                    data = await response.json()

                    if data.get("status") != "OK":
                        logger.warning(f"Places API status: {data.get('status')}")
                        if data.get("status") == "ZERO_RESULTS":
                            return None
                        return None

                    results = data.get("results", [])
                    if not results:
                        return None

                    # 取第一個結果
                    place = results[0]
                    place_id = place.get("place_id")

                    if not place_id:
                        return self._format_basic_result(place)

                    # 取得詳細資訊
                    details = await self._get_place_details(place_id, session)

                    if details:
                        result = self._format_detailed_result(details)
                        self.cache[cache_key] = result
                        return result
                    else:
                        result = self._format_basic_result(place)
                        self.cache[cache_key] = result
                        return result

        except Exception as e:
            logger.error(f"Error searching place: {str(e)}")
            return None

    async def _get_place_details(self, place_id: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        """取得地點詳細資訊"""

        details_url = f"{self.BASE_URL}/details/json"
        params = {
            "place_id": place_id,
            "key": self.api_key,
            "language": "zh-TW",
            "fields": "name,formatted_address,formatted_phone_number,international_phone_number,opening_hours,website,rating,types"
        }

        try:
            async with session.get(details_url, params=params) as response:
                if response.status != 200:
                    return None

                data = await response.json()

                if data.get("status") == "OK":
                    return data.get("result")

                return None

        except Exception as e:
            logger.error(f"Error getting place details: {str(e)}")
            return None

    def _format_basic_result(self, place: Dict) -> Dict:
        """格式化基本搜尋結果"""

        return {
            "name": place.get("name", ""),
            "address": place.get("formatted_address", ""),
            "phone": "",  # 基本搜尋沒有電話
            "rating": place.get("rating", 0),
            "types": place.get("types", []),
            "place_id": place.get("place_id", "")
        }

    def _format_detailed_result(self, details: Dict) -> Dict:
        """格式化詳細資訊結果"""

        # 處理營業時間
        opening_hours = ""
        if details.get("opening_hours"):
            weekday_text = details["opening_hours"].get("weekday_text", [])
            if weekday_text:
                opening_hours = "；".join(weekday_text)

        return {
            "name": details.get("name", ""),
            "address": details.get("formatted_address", ""),
            "phone": details.get("formatted_phone_number", "") or details.get("international_phone_number", ""),
            "website": details.get("website", ""),
            "opening_hours": opening_hours,
            "rating": details.get("rating", 0),
            "types": details.get("types", [])
        }

    async def batch_search(self, queries: List[str]) -> List[Dict]:
        """批次搜尋多個地點

        Args:
            queries: 搜尋關鍵字列表

        Returns:
            地點資訊列表
        """

        results = []
        for query in queries:
            result = await self.search_place(query)
            if result:
                results.append(result)

        return results

    def format_for_response(self, place_info: Dict) -> str:
        """格式化為回應文字（HTML格式）

        Args:
            place_info: 地點資訊字典

        Returns:
            格式化的HTML文字回應
        """

        if not place_info:
            return ""

        lines = []

        # 機構名稱（粗體）
        if place_info.get("name"):
            lines.append(f"<strong>{place_info['name']}</strong>")

        # 電話（可點擊的tel連結）
        if place_info.get("phone"):
            # 移除電話號碼中的空格和破折號，用於tel連結
            phone_clean = place_info['phone'].replace(' ', '').replace('-', '')
            lines.append(f'📞 電話：<a href="tel:{phone_clean}">{place_info["phone"]}</a>')

        # 地址
        if place_info.get("address"):
            lines.append(f"📍 地址：{place_info['address']}")

        # 營業時間（簡化顯示）
        if place_info.get("opening_hours"):
            hours = place_info["opening_hours"].split("；")
            if hours:
                # 如果是24小時營業
                if "24 小時營業" in hours[0]:
                    lines.append(f"🕐 營業時間：24小時營業")
                else:
                    # 顯示第一天作為範例
                    lines.append(f"🕐 營業時間：{hours[0]}")

        # 網站（可點擊的連結）
        if place_info.get("website"):
            lines.append(f'🔗 網站：<a href="{place_info["website"]}">官方網站</a>')

        return "<br>".join(lines)


class PlaceQueryDetector:
    """地點查詢意圖偵測器"""

    # 查詢關鍵詞
    QUERY_KEYWORDS = [
        "電話", "地址", "在哪", "怎麼去", "位置", "聯絡",
        "營業時間", "幾點", "開到幾點", "有開嗎",
        "網站", "官網", "網址"
    ]

    # 地點類型關鍵詞
    PLACE_TYPES = [
        "醫院", "診所", "中心", "機構", "基金會",
        "毒防局", "衛生局", "警察局", "派出所",
        "教會", "廟", "寺", "社區", "協會"
    ]

    @classmethod
    def detect_place_query(cls, text: str) -> Dict[str, Any]:
        """偵測是否為地點查詢

        Returns:
            {
                "is_place_query": bool,
                "query_type": str,  # "phone", "address", "hours", "general"
                "place_name": str,  # 可能的地點名稱
                "confidence": float
            }
        """

        text_lower = text.lower()

        # 檢查是否包含查詢關鍵詞
        has_query_keyword = any(kw in text for kw in cls.QUERY_KEYWORDS)

        # 檢查是否包含地點類型
        has_place_type = any(pt in text for pt in cls.PLACE_TYPES)

        # 判斷查詢類型
        query_type = "general"
        if "電話" in text or "聯絡" in text:
            query_type = "phone"
        elif "地址" in text or "在哪" in text or "怎麼去" in text:
            query_type = "address"
        elif "營業時間" in text or "幾點" in text:
            query_type = "hours"

        # 嘗試提取地點名稱
        place_name = cls._extract_place_name(text)

        # 計算信心分數
        confidence = 0.0
        if has_query_keyword:
            confidence += 0.5
        if has_place_type:
            confidence += 0.3
        if place_name:
            confidence += 0.2

        return {
            "is_place_query": confidence >= 0.5,
            "query_type": query_type,
            "place_name": place_name,
            "confidence": min(confidence, 1.0)
        }

    @classmethod
    def _extract_place_name(cls, text: str) -> str:
        """嘗試從文字中提取地點名稱"""

        # 簡單的規則：尋找包含地點類型詞的片段
        for place_type in cls.PLACE_TYPES:
            if place_type in text:
                # 嘗試找出完整的機構名稱
                import re
                # 匹配中文機構名稱的模式
                pattern = r'[\u4e00-\u9fa5]*' + place_type + r'[\u4e00-\u9fa5]*'
                matches = re.findall(pattern, text)
                if matches:
                    # 返回最長的匹配
                    return max(matches, key=len)

        # 如果有「的」，可能是「XXX的電話/地址」
        if "的" in text:
            parts = text.split("的")
            if len(parts) >= 2:
                potential_name = parts[0].strip()
                # 過濾掉太短或太長的名稱
                if 2 <= len(potential_name) <= 20:
                    return potential_name

        return ""