"""資料結構定義"""

from .chat import ChatRequest, ChatResponse
from .conversation import ConversationResponse, MessageResponse

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "ConversationResponse",
    "MessageResponse",
]