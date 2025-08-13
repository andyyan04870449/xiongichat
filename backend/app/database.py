"""資料庫連線管理"""

from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import MetaData, create_engine
from contextlib import asynccontextmanager
import re

from app.config import settings

# 檢查是否為異步 URL
def is_async_url(url: str) -> bool:
    """檢查是否為異步資料庫 URL"""
    return 'asyncpg' in url or 'async' in url

# 轉換為同步 URL
def get_sync_url(url: str) -> str:
    """將異步 URL 轉換為同步 URL"""
    if 'asyncpg' in url:
        return url.replace('asyncpg', 'psycopg2')
    elif 'async' in url:
        return url.replace('async', 'sync')
    return url

# 建立引擎（支援同步和異步）
if is_async_url(settings.database_url):
    # 異步引擎
    engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_size=20,
        max_overflow=40,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
else:
    # 同步引擎
    sync_url = get_sync_url(settings.database_url)
    engine = create_engine(
        sync_url,
        echo=settings.database_echo,
        pool_size=20,
        max_overflow=40,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

# 建立 session（支援同步和異步）
if is_async_url(settings.database_url):
    # 異步 session
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
else:
    # 同步 session
    SessionLocal = sessionmaker(
        engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

# 定義 metadata
metadata = MetaData()

# 定義 Base
Base = declarative_base(metadata=metadata)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """取得資料庫 session（異步版本）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """Context manager for database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化資料庫"""
    # 暫時跳過資料庫初始化，因為資料庫已經通過 Docker 初始化
    pass


async def close_db():
    """關閉資料庫連線"""
    if is_async_url(settings.database_url):
        await engine.dispose()
    else:
        engine.dispose()