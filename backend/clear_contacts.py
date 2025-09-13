#!/usr/bin/env python3
"""
清空聯絡資料表的腳本
"""
import asyncio
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, func
from app.database import AsyncSessionLocal
from app.models.upload import AuthoritativeContacts
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clear_contacts():
    """清空 authoritative_contacts 表中的所有資料"""
    async with AsyncSessionLocal() as session:
        try:
            # 先查詢現有資料數量
            count_before = await session.scalar(
                select(func.count()).select_from(AuthoritativeContacts)
            )
            logger.info(f"清空前資料數量: {count_before}")
            
            if count_before == 0:
                logger.info("資料表已經是空的")
                return
            
            # 刪除所有資料
            await session.execute(delete(AuthoritativeContacts))
            await session.commit()
            
            # 確認清空後的數量
            count_after = await session.scalar(
                select(func.count()).select_from(AuthoritativeContacts)
            )
            logger.info(f"清空後資料數量: {count_after}")
            logger.info(f"成功清空 {count_before} 筆聯絡資料")
            
        except Exception as e:
            logger.error(f"清空資料時發生錯誤: {e}")
            await session.rollback()
            raise

async def main():
    """主程式"""
    logger.info("開始清空聯絡資料表...")
    
    try:
        await clear_contacts()
        logger.info("✅ 清空作業完成")
    except Exception as e:
        logger.error(f"❌ 清空作業失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())