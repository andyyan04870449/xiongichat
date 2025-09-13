#!/usr/bin/env python3
"""
匯入機構聯絡資料的腳本
"""
import asyncio
import sys
import csv
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import AsyncSessionLocal
# 先匯入 BatchTask 以避免關聯錯誤
from app.models.batch import BatchTask
from app.models.upload import AuthoritativeContacts
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def import_contacts_from_csv(csv_file_path: str):
    """從 CSV 檔案匯入聯絡資料"""
    async with AsyncSessionLocal() as session:
        try:
            # 讀取 CSV 檔案
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                imported_count = 0
                skipped_count = 0
                
                for row in csv_reader:
                    # 跳過空的 organization
                    if not row.get('organization'):
                        skipped_count += 1
                        continue
                    
                    # 準備標籤資料
                    tags = []
                    if row.get('tags'):
                        tags = [tag.strip() for tag in row['tags'].split(',')]
                    
                    # 建立聯絡資料物件
                    contact = AuthoritativeContacts(
                        id=uuid4(),
                        organization=row['organization'].strip(),
                        phone=row.get('phone', '').strip() or None,
                        email=row.get('email', '').strip() or None,
                        address=row.get('address', '').strip() or None,
                        tags=tags if tags else None,
                        notes=row.get('notes', '').strip() or None,
                    )
                    
                    # 加入到 session
                    session.add(contact)
                    imported_count += 1
                    
                    # 每 50 筆提交一次
                    if imported_count % 50 == 0:
                        await session.commit()
                        logger.info(f"已匯入 {imported_count} 筆資料...")
                
                # 提交剩餘的資料
                await session.commit()
                
                # 查詢總數確認
                total_count = await session.scalar(
                    select(func.count()).select_from(AuthoritativeContacts)
                )
                
                logger.info(f"✅ 匯入完成！")
                logger.info(f"  - 成功匯入: {imported_count} 筆")
                logger.info(f"  - 跳過空白: {skipped_count} 筆")
                logger.info(f"  - 資料庫總數: {total_count} 筆")
                
                return imported_count, skipped_count
                
        except Exception as e:
            logger.error(f"匯入資料時發生錯誤: {e}")
            await session.rollback()
            raise

async def main():
    """主程式"""
    csv_file = "/Users/yangandy/KaohsiungCare/institution_contacts_analysis.csv"
    
    # 檢查檔案是否存在
    if not Path(csv_file).exists():
        logger.error(f"找不到檔案: {csv_file}")
        sys.exit(1)
    
    logger.info(f"開始匯入聯絡資料從: {csv_file}")
    
    try:
        imported, skipped = await import_contacts_from_csv(csv_file)
        logger.info("✅ 匯入作業完成")
    except Exception as e:
        logger.error(f"❌ 匯入作業失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())