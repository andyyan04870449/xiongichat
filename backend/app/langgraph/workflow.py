"""主要工作流定義"""

import os
from app.langgraph.simple_workflow import create_chat_workflow as create_simple_workflow
from app.langgraph.optimized_workflow import create_optimized_workflow

# 根據環境變數決定使用哪個工作流程
USE_OPTIMIZED_WORKFLOW = os.getenv("USE_OPTIMIZED_WORKFLOW", "true").lower() == "true"

def create_chat_workflow():
    """建立聊天工作流程"""
    if USE_OPTIMIZED_WORKFLOW:
        # 使用優化版本（智能路由）
        return create_optimized_workflow()
    else:
        # 使用原始版本（完整流程）
        return create_simple_workflow()

__all__ = ["create_chat_workflow"]