"""API 路由"""

from fastapi import APIRouter
from app.api.v1 import chat, conversations, upload, drug_knowledge, contacts, knowledge, batch_upload

api_router = APIRouter()

# 註冊路由
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(drug_knowledge.router, prefix="/admin", tags=["admin"])
api_router.include_router(contacts.router, tags=["contacts"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(batch_upload.router, tags=["batch"])