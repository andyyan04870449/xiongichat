"""配置管理"""

from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://xiongichat:xiongichat123@localhost:5432/xiongichat"
    database_echo: bool = False
    
    # OpenAI
    openai_api_key: str
    openai_model_chat: str = "gpt-4o"  # 主要聊天模型
    openai_model_tools: str = "gpt-4o-mini"  # 工具模型
    openai_temperature: float = 0.7
    openai_max_tokens: int = 800
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # API Settings
    api_version: str = "v1"
    api_prefix: str = "/api/v1"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # LangGraph
    langgraph_checkpoint_type: str = "postgres"
    langgraph_max_memory_turns: int = 10
    
    # JWT Security
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # CORS
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """取得設定單例"""
    return Settings()


settings = get_settings()