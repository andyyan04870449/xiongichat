#!/usr/bin/env python
"""直接測試 API endpoint"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.v1.upload import get_recent_uploads

async def test_api():
    """測試 API endpoint"""
    
    print("測試 get_recent_uploads API...")
    try:
        result = await get_recent_uploads(limit=3)
        print(f"成功！返回 {len(result)} 筆記錄")
        for r in result:
            print(f"  - {r}")
    except Exception as e:
        print(f"失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api())