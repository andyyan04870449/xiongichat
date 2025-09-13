"""主要工作流定義"""

import os
from app.langgraph.simple_workflow import create_chat_workflow as create_simple_workflow
from app.langgraph.optimized_workflow import create_optimized_workflow
from app.langgraph.fast_workflow import create_fast_workflow
from app.langgraph.ultimate_workflow import create_ultimate_workflow

# 根據環境變數決定使用哪個工作流程
USE_ULTIMATE_WORKFLOW = os.getenv("USE_ULTIMATE_WORKFLOW", "true").lower() == "true"
USE_FAST_WORKFLOW = os.getenv("USE_FAST_WORKFLOW", "false").lower() == "true"
USE_OPTIMIZED_WORKFLOW = os.getenv("USE_OPTIMIZED_WORKFLOW", "false").lower() == "true"

def create_chat_workflow():
    """建立聊天工作流程"""
    if USE_ULTIMATE_WORKFLOW:
        # 使用極簡版本（3步驟，智能集中在最終LLM）
        return create_ultimate_workflow()
    elif USE_FAST_WORKFLOW:
        # 使用快速版本（3步驟，<1秒）
        return create_fast_workflow()
    elif USE_OPTIMIZED_WORKFLOW:
        # 使用優化版本（智能路由，但較慢）
        return create_optimized_workflow()
    else:
        # 使用原始版本（完整流程）
        return create_simple_workflow()

__all__ = ["create_chat_workflow"]