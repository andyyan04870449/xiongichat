"""API 路由"""

from fastapi import APIRouter
from app.api.v1 import chat, conversations

api_router = APIRouter()

# 註冊路由
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])