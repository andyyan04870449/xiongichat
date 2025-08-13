# 02 - API 層設計文件

## 快速恢復指南
如果你忘記了這個模組，記住：這是系統的對外接口，分為兩部分：給使用者的聊天 API 和給市府平台的拉取 API。使用 FastAPI 實作，重點是游標分頁和權限控制。

## 核心技術棧
- FastAPI (異步 Web 框架)
- Pydantic (資料驗證)
- OAuth2 + JWT (認證授權)
- Redis (Rate Limiting)

## 專案結構
```
api/
├── __init__.py
├── main.py              # FastAPI app 入口
├── dependencies.py      # 依賴注入
├── middleware.py        # 中間件 (認證、限流等)
├── routers/
│   ├── chat.py         # 聊天 API
│   ├── sync.py         # 同步拉取 API
│   ├── health.py       # 健康檢查
│   └── profiles.py     # 個案檔案 API
├── schemas/            # Pydantic models
│   ├── conversation.py
│   ├── message.py
│   └── profile.py
└── utils/
    ├── cursor.py       # 游標處理
    ├── auth.py         # OAuth2 實作
    └── pagination.py   # 分頁邏輯
```

## FastAPI 應用初始化

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時初始化
    app.state.redis = await redis.from_url("redis://localhost:6379")
    app.state.db = DatabaseHelper()
    yield
    # 關閉時清理
    await app.state.redis.close()

app = FastAPI(
    title="雄i聊 API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",  # 開發時使用，生產環境應關閉
    redoc_url="/api/redoc"
)

# 中間件配置
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kao.gov.tw"],  # 生產環境限制
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)

# 路由註冊
from api.routers import chat, sync, health, profiles
app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(sync.router, prefix="/api/v1")
app.include_router(profiles.router, prefix="/api/v1")
```

## 認證與授權

```python
# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jose import JWTError, jwt
from typing import Optional, List

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")
http_bearer = HTTPBearer()

class OAuth2Scopes:
    CONVERSATIONS_READ = "conversations.read"
    MESSAGES_READ = "messages.read"
    MESSAGES_READ_FULL = "messages.read_full"
    PROFILES_READ = "profiles.read"

async def get_current_client(
    token: str = Depends(oauth2_scheme)
) -> dict:
    """驗證 OAuth2 token 並返回 client 資訊"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        client_id = payload.get("sub")
        scopes = payload.get("scopes", [])
        
        if client_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return {
            "client_id": client_id,
            "scopes": scopes
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def require_scopes(*required_scopes: str):
    """Scope 檢查裝飾器"""
    async def scope_checker(
        client: dict = Depends(get_current_client)
    ):
        client_scopes = set(client.get("scopes", []))
        required = set(required_scopes)
        
        if not required.issubset(client_scopes):
            missing = required - client_scopes
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "forbidden_scope",
                    "code": "E_SCOPE",
                    "required_scope": list(missing)[0]
                }
            )
        return client
    
    return scope_checker
```

## 限流機制

```python
# middleware.py
from fastapi import Request, HTTPException
import time

class RateLimiter:
    def __init__(self, redis_client, default_limit=5, window=1):
        self.redis = redis_client
        self.default_limit = default_limit
        self.window = window
    
    async def check_rate_limit(
        self, 
        request: Request,
        client_id: str
    ):
        """Sliding window rate limiting"""
        key = f"rate_limit:{client_id}:{request.url.path}"
        now = time.time()
        window_start = now - self.window
        
        # 使用 Redis sorted set
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcount(key, window_start, now)
        pipe.expire(key, self.window + 1)
        
        results = await pipe.execute()
        request_count = results[2]
        
        # 取得客戶端特定限制
        limit = await self.get_client_limit(client_id)
        
        if request_count > limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limited",
                    "code": "E_RATELIMIT",
                    "retry_after": f"{self.window}s"
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(now + self.window))
                }
            )
        
        # 設定回應標頭
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(limit - request_count),
            "X-RateLimit-Reset": str(int(now + self.window))
        }
    
    async def get_client_limit(self, client_id: str) -> int:
        """取得客戶端限流設定"""
        # 可從資料庫或設定檔讀取
        special_limits = {
            "kao-main-platform": 20,  # 市府平台較高限制
        }
        return special_limits.get(client_id, self.default_limit)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # 排除健康檢查
    if request.url.path == "/api/v1/healthz":
        return await call_next(request)
    
    # 取得 client_id (從 header 或 token)
    client_id = request.headers.get("X-Client-Id", "anonymous")
    
    # 檢查限流
    limiter = RateLimiter(app.state.redis)
    await limiter.check_rate_limit(request, client_id)
    
    response = await call_next(request)
    
    # 加入限流標頭
    if hasattr(request.state, "rate_limit_headers"):
        for k, v in request.state.rate_limit_headers.items():
            response.headers[k] = v
    
    return response
```

## 聊天 API 實作

```python
# routers/chat.py
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    user_id: str = Field(..., description="使用者 ID")
    conversation_id: Optional[UUID] = Field(None, description="會話 ID")
    message: str = Field(..., min_length=1, max_length=4000)
    lang: Optional[str] = Field("zh-TW", description="語言偏好")

class ChatResponse(BaseModel):
    conversation_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID
    reply: str
    risk: dict = Field(default_factory=dict)

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseHelper = Depends(get_db)
):
    """
    處理聊天請求
    1. 取得或建立會話
    2. 呼叫 LangGraph 處理
    3. 背景儲存訊息
    4. 即時回傳結果
    """
    # 取得或建立會話
    conv_id = await db.get_or_create_conversation(
        request.user_id,
        request.conversation_id
    )
    
    # 呼叫 LangGraph (見 LangGraph 設計文件)
    from langgraph_workflow import process_chat
    result = await process_chat(
        user_id=request.user_id,
        conversation_id=conv_id,
        input_text=request.message,
        lang=request.lang
    )
    
    # 背景儲存訊息
    background_tasks.add_task(
        db.save_message_pair,
        conversation_id=conv_id,
        user_content=request.message,
        assistant_content=result["reply"],
        risk_info=result["risk"],
        rag_sources=result.get("rag_sources", []),
        profile_snapshot=result.get("profile_snapshot", {})
    )
    
    return ChatResponse(
        conversation_id=conv_id,
        user_message_id=result["user_message_id"],
        assistant_message_id=result["assistant_message_id"],
        reply=result["reply"],
        risk=result["risk"]
    )
```

## 同步拉取 API 實作

```python
# routers/sync.py
from fastapi import APIRouter, Query, Depends, HTTPException
from datetime import datetime
from typing import Optional, List

router = APIRouter(tags=["sync"])

class ConversationSchema(BaseModel):
    id: UUID
    user_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    last_message_at: Optional[datetime]
    updated_at: datetime

class MessageSchema(BaseModel):
    id: UUID
    role: str
    content_redacted: str
    content: Optional[str] = None  # 需要特殊權限
    risk: dict
    rag_sources: Optional[List[dict]]
    profile_snapshot: Optional[dict]
    created_at: datetime
    updated_at: datetime

@router.get("/conversations")
async def get_conversations(
    updated_after: Optional[datetime] = Query(None),
    page_size: int = Query(500, ge=1, le=1000),
    cursor: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    client: dict = Depends(require_scopes(OAuth2Scopes.CONVERSATIONS_READ)),
    db: DatabaseHelper = Depends(get_db)
):
    """
    查詢會話 (增量同步)
    使用 cursor-based pagination
    """
    # 解析游標
    decoded_cursor = decode_cursor(cursor) if cursor else None
    
    # 建立查詢
    query = select(Conversation)
    
    if updated_after:
        query = query.where(Conversation.updated_at > updated_after)
    
    if user_id:
        query = query.where(Conversation.user_id == user_id)
    
    if decoded_cursor:
        # Keyset pagination
        query = query.where(
            or_(
                Conversation.updated_at < decoded_cursor["timestamp"],
                and_(
                    Conversation.updated_at == decoded_cursor["timestamp"],
                    Conversation.id > decoded_cursor["last_id"]
                )
            )
        )
    
    query = query.order_by(
        Conversation.updated_at.desc(),
        Conversation.id
    ).limit(page_size + 1)
    
    # 執行查詢
    async with db.get_session() as session:
        result = await session.execute(query)
        items = result.scalars().all()
    
    # 處理分頁
    has_next = len(items) > page_size
    if has_next:
        items = items[:page_size]
    
    # 產生下一頁游標
    next_cursor = None
    if has_next and items:
        last_item = items[-1]
        next_cursor = create_cursor(
            timestamp=last_item.updated_at,
            last_id=str(last_item.id)
        )
    
    return {
        "items": [ConversationSchema.from_orm(item) for item in items],
        "next_cursor": next_cursor,
        "request_id": request.state.request_id,
        "trace_id": generate_trace_id()
    }

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: UUID,
    after_id: Optional[UUID] = Query(None),
    limit: int = Query(500, ge=1, le=1000),
    include: Optional[str] = Query(None),
    client: dict = Depends(require_scopes(OAuth2Scopes.MESSAGES_READ)),
    db: DatabaseHelper = Depends(get_db)
):
    """
    查詢某會話的訊息
    支援斷點續傳
    """
    # 解析 include 參數
    include_fields = set(include.split(",")) if include else set()
    
    # 檢查是否需要完整內容權限
    if "content" in include_fields:
        if OAuth2Scopes.MESSAGES_READ_FULL not in client["scopes"]:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "forbidden_scope",
                    "code": "E_SCOPE",
                    "required_scope": OAuth2Scopes.MESSAGES_READ_FULL
                }
            )
    
    # 建立查詢
    query = select(ConversationMessage).where(
        ConversationMessage.conversation_id == conversation_id
    )
    
    if after_id:
        # 取得 after_id 的 created_at
        subquery = select(ConversationMessage.created_at).where(
            ConversationMessage.id == after_id
        )
        after_time = await session.scalar(subquery)
        
        query = query.where(
            ConversationMessage.created_at > after_time
        )
    
    query = query.order_by(
        ConversationMessage.created_at
    ).limit(limit + 1)
    
    # 執行查詢
    async with db.get_session() as session:
        result = await session.execute(query)
        items = result.scalars().all()
    
    # 處理分頁
    has_next = len(items) > limit
    if has_next:
        items = items[:limit]
    
    next_after_id = str(items[-1].id) if items else None
    
    # 處理回應資料
    response_items = []
    for item in items:
        msg_dict = {
            "id": str(item.id),
            "role": item.role,
            "content_redacted": item.content_redacted,
            "risk": {
                "level": item.risk_level or "NONE",
                "categories": item.risk_categories or []
            },
            "created_at": item.created_at,
            "updated_at": item.updated_at
        }
        
        # 根據 include 參數加入額外欄位
        if "content" in include_fields:
            msg_dict["content"] = item.content
            # 記錄審計事件
            await log_audit_event(
                client_id=client["client_id"],
                action="read_full_content",
                resource=f"message:{item.id}"
            )
        
        if "profile_snapshot" in include_fields:
            msg_dict["profile_snapshot"] = item.profile_snapshot
        
        if "rag_sources" in include_fields:
            msg_dict["rag_sources"] = item.rag_sources
        
        response_items.append(msg_dict)
    
    return {
        "items": response_items,
        "next_after_id": next_after_id,
        "request_id": request.state.request_id,
        "trace_id": generate_trace_id()
    }
```

## 游標實作

```python
# utils/cursor.py
import base64
import json
import secrets
from datetime import datetime

def create_cursor(timestamp: datetime, last_id: str) -> str:
    """
    建立 opaque cursor
    包含時間戳、最後 ID 和隨機鹽
    """
    cursor_data = {
        "t": timestamp.isoformat(),
        "id": last_id,
        "s": secrets.token_hex(4)  # 防止猜測
    }
    
    json_str = json.dumps(cursor_data, separators=(",", ":"))
    encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
    return encoded.rstrip("=")  # 移除填充

def decode_cursor(cursor: str) -> dict:
    """解析 cursor"""
    try:
        # 補回填充
        padding = 4 - len(cursor) % 4
        if padding != 4:
            cursor += "=" * padding
        
        decoded = base64.urlsafe_b64decode(cursor)
        cursor_data = json.loads(decoded)
        
        return {
            "timestamp": datetime.fromisoformat(cursor_data["t"]),
            "last_id": cursor_data["id"]
        }
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor"
        )
```

## 錯誤處理

```python
# main.py
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """統一錯誤格式"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {
            "error": exc.detail,
            "code": f"E_{exc.status_code}"
        },
        headers=exc.headers
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """未預期錯誤處理"""
    import traceback
    
    # 記錄詳細錯誤
    logger.error(f"Unhandled exception: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "code": "E_INTERNAL",
            "trace_id": generate_trace_id()
        }
    )
```

## 關鍵記憶點
1. **必須**實作 cursor-based pagination，不要用 offset
2. **記得**在取全文時記錄審計事件
3. **注意** Rate Limiting 使用 sliding window
4. **重要**所有錯誤回應要統一格式