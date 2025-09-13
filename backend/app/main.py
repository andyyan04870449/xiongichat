"""主應用程式"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

from app.config import settings
from app.database import init_db, close_db
from app.api import api_router

# 配置日誌
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時
    logger.info("Starting XiongIChat backend...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # 關閉時
    logger.info("Shutting down XiongIChat backend...")
    await close_db()
    logger.info("Database connections closed")


# 建立應用程式
app = FastAPI(
    title="雄i聊 - 高雄市毒防局個案聊天AI",
    description="提供溫暖關懷與毒防資源的智能聊天系統",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# 配置 CORS - 完全開放（開發階段）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 註冊路由
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """根路徑 - 返回首頁"""
    index_path = Path("static/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return {
            "service": "XiongIChat",
            "version": "0.1.0",
            "status": "running",
            "message": "Welcome! Visit /docs for API documentation"
        }


@app.get("/{filename}.html")
async def serve_html(filename: str):
    """提供 HTML 檔案服務"""
    html_path = Path(f"static/{filename}.html")
    if html_path.exists() and html_path.is_file():
        return FileResponse(html_path)
    else:
        return FileResponse("static/index.html")  # 找不到時返回首頁


# 靜態檔案服務（放在最後，避免覆蓋特定路由）
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "service": "XiongIChat",
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )