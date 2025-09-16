"""時區工具函數"""

from datetime import datetime, timezone, timedelta

# 定義台灣時區
TZ_TAIWAN = timezone(timedelta(hours=8))


def get_taiwan_time() -> datetime:
    """取得當前台灣時間"""
    return datetime.now(TZ_TAIWAN)


def to_taiwan_time(dt: datetime) -> datetime:
    """將 datetime 轉換為台灣時間

    Args:
        dt: 要轉換的 datetime 物件

    Returns:
        台灣時區的 datetime 物件
    """
    if dt.tzinfo is None:
        # 如果沒有時區資訊，假設為 UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TZ_TAIWAN)


def utc_to_taiwan(dt: datetime) -> datetime:
    """將 UTC 時間轉換為台灣時間

    Args:
        dt: UTC datetime 物件

    Returns:
        台灣時區的 datetime 物件
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TZ_TAIWAN)