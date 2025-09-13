"""增強版記憶管理服務 - 解決LLM記憶丟失問題"""

import hashlib
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy import select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from cachetools import TTLCache

from app.models import ConversationMessage
from app.database import get_db_context

logger = logging.getLogger(__name__)


class EnhancedMemoryService:
    """增強版對話記憶管理服務"""
    
    def __init__(
        self,
        max_turns: int = 15,  # 增加記憶輪數
        summary_interval: int = 10,  # 每10輪總結一次
        cache_ttl: int = 1800  # 快取30分鐘
    ):
        self.max_turns = max_turns
        self.summary_interval = summary_interval
        self.cache = TTLCache(maxsize=100, ttl=cache_ttl)
        self.context_cache = {}  # 本地上下文快取
        
    async def load_conversation_memory(
        self, 
        conversation_id: str,
        include_summary: bool = True
    ) -> Dict[str, Any]:
        """載入對話記憶，包含歷史摘要和關鍵資訊"""
        
        cache_key = f"memory:{conversation_id}"
        
        # 檢查快取
        if cache_key in self.cache:
            logger.info(f"Memory cache hit for {conversation_id}")
            return self.cache[cache_key]
        
        try:
            async with get_db_context() as db:
                # 載入完整對話歷史
                stmt = select(ConversationMessage).where(
                    ConversationMessage.conversation_id == conversation_id
                ).order_by(
                    ConversationMessage.created_at.desc()
                ).limit(self.max_turns * 2)
                
                result = await db.execute(stmt)
                messages = list(reversed(result.scalars().all()))
                
                # 轉換為記憶格式
                memory_messages = []
                for msg in messages:
                    memory_messages.append({
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.created_at.isoformat() if msg.created_at else None
                    })
                
                # 生成記憶增強資訊
                memory_data = {
                    "messages": memory_messages,
                    "summary": await self._generate_summary(memory_messages) if include_summary else None,
                    "key_facts": self._extract_key_facts(memory_messages),
                    "context_markers": self._create_context_markers(memory_messages),
                    "conversation_flow": self._analyze_conversation_flow(memory_messages),
                    "total_messages": len(memory_messages),
                    "conversation_id": conversation_id
                }
                
                # 快取結果
                self.cache[cache_key] = memory_data
                
                logger.info(f"Enhanced memory loaded: {len(memory_messages)} messages for {conversation_id}")
                return memory_data
                
        except Exception as e:
            logger.error(f"Error loading enhanced memory: {str(e)}")
            return {
                "messages": [],
                "summary": None,
                "key_facts": {},
                "context_markers": [],
                "conversation_flow": [],
                "total_messages": 0,
                "conversation_id": conversation_id
            }
    
    def _extract_key_facts(self, messages: List[Dict]) -> Dict[str, Any]:
        """提取對話中的關鍵事實"""
        key_facts = {
            "user_mentions": set(),
            "topics": set(),
            "emotional_states": [],
            "important_info": []
        }
        
        for msg in messages:
            content = msg.get("content", "")
            
            # 提取使用者提到的重要資訊
            if "我叫" in content or "我是" in content:
                key_facts["user_mentions"].add(content[:50])
            
            # 提取主題關鍵詞
            keywords = ["戒毒", "治療", "家人", "工作", "健康", "心情", "困擾"]
            for keyword in keywords:
                if keyword in content:
                    key_facts["topics"].add(keyword)
            
            # 記錄情緒狀態
            if msg["role"] == "user":
                if any(word in content for word in ["難過", "痛苦", "焦慮", "害怕", "擔心"]):
                    key_facts["emotional_states"].append({
                        "content": content[:30],
                        "timestamp": msg.get("timestamp")
                    })
        
        # 轉換set為list以便JSON序列化
        key_facts["user_mentions"] = list(key_facts["user_mentions"])
        key_facts["topics"] = list(key_facts["topics"])
        
        return key_facts
    
    def _create_context_markers(self, messages: List[Dict]) -> List[str]:
        """創建上下文標記，幫助LLM理解對話脈絡"""
        markers = []
        
        if not messages:
            return markers
        
        # 標記對話開始
        markers.append(f"對話開始於: {messages[0].get('timestamp', 'unknown')}")
        
        # 標記話題轉換
        prev_topic = None
        for i, msg in enumerate(messages):
            if msg["role"] == "user":
                current_topic = self._detect_topic(msg["content"])
                if current_topic and current_topic != prev_topic:
                    markers.append(f"話題轉換到: {current_topic} (第{i+1}則訊息)")
                    prev_topic = current_topic
        
        # 標記重要時刻
        for i, msg in enumerate(messages):
            if "謝謝" in msg.get("content", ""):
                markers.append(f"使用者表達感謝 (第{i+1}則訊息)")
            if "再見" in msg.get("content", "") or "拜拜" in msg.get("content", ""):
                markers.append(f"對話結束信號 (第{i+1}則訊息)")
        
        return markers
    
    def _analyze_conversation_flow(self, messages: List[Dict]) -> List[Dict]:
        """分析對話流程，標記重要轉折點"""
        flow = []
        
        for i in range(0, len(messages), 2):  # 每個對話輪次
            if i + 1 < len(messages):
                user_msg = messages[i] if messages[i]["role"] == "user" else None
                assistant_msg = messages[i+1] if messages[i+1]["role"] == "assistant" else None
                
                if user_msg and assistant_msg:
                    flow.append({
                        "turn": i // 2 + 1,
                        "user_intent": self._detect_intent(user_msg["content"]),
                        "assistant_action": self._detect_action(assistant_msg["content"]),
                        "continuity": self._check_continuity(user_msg, assistant_msg)
                    })
        
        return flow
    
    def _detect_topic(self, content: str) -> Optional[str]:
        """偵測訊息主題"""
        topics_map = {
            "求助": ["幫助", "怎麼辦", "求助", "協助"],
            "情緒": ["難過", "痛苦", "開心", "焦慮"],
            "諮詢": ["地址", "電話", "時間", "服務"],
            "戒毒": ["戒毒", "戒癮", "毒品", "藥物"],
            "家庭": ["家人", "父母", "孩子", "配偶"]
        }
        
        for topic, keywords in topics_map.items():
            if any(keyword in content for keyword in keywords):
                return topic
        
        return None
    
    def _detect_intent(self, content: str) -> str:
        """偵測使用者意圖"""
        if any(word in content for word in ["嗎", "？", "怎麼", "什麼"]):
            return "詢問"
        elif any(word in content for word in ["謝謝", "感謝"]):
            return "感謝"
        elif any(word in content for word in ["難過", "痛苦", "焦慮"]):
            return "表達情緒"
        elif any(word in content for word in ["地址", "電話", "位置"]):
            return "查詢資訊"
        else:
            return "陳述"
    
    def _detect_action(self, content: str) -> str:
        """偵測助手動作"""
        if any(word in content for word in ["電話", "地址", "時間"]):
            return "提供資訊"
        elif any(word in content for word in ["理解", "明白", "聽起來"]):
            return "同理回應"
        elif any(word in content for word in ["建議", "可以試試", "或許"]):
            return "提供建議"
        else:
            return "一般回應"
    
    def _check_continuity(self, user_msg: Dict, assistant_msg: Dict) -> bool:
        """檢查對話連續性"""
        # 簡單檢查：助手回應是否包含使用者提到的關鍵詞
        user_keywords = set(user_msg["content"].split())
        assistant_keywords = set(assistant_msg["content"].split())
        
        overlap = user_keywords & assistant_keywords
        return len(overlap) > 0
    
    async def _generate_summary(self, messages: List[Dict]) -> Optional[str]:
        """生成對話摘要（可選：使用LLM生成）"""
        if len(messages) < 4:
            return None
        
        # 簡單摘要：提取關鍵資訊
        summary_parts = []
        
        # 第一則使用者訊息
        for msg in messages:
            if msg["role"] == "user":
                summary_parts.append(f"使用者開始詢問關於: {msg['content'][:30]}")
                break
        
        # 主要話題
        topics = set()
        for msg in messages:
            topic = self._detect_topic(msg["content"])
            if topic:
                topics.add(topic)
        
        if topics:
            summary_parts.append(f"討論話題包括: {', '.join(topics)}")
        
        # 對話結果
        if messages and messages[-1]["role"] == "assistant":
            summary_parts.append(f"最後回應: {messages[-1]['content'][:30]}")
        
        return " | ".join(summary_parts) if summary_parts else None
    
    def format_for_llm(self, memory_data: Dict[str, Any]) -> str:
        """格式化記憶資料供LLM使用"""
        
        formatted_parts = []
        
        # 加入摘要
        if memory_data.get("summary"):
            formatted_parts.append(f"【對話摘要】{memory_data['summary']}")
        
        # 加入關鍵事實
        if memory_data.get("key_facts"):
            facts = memory_data["key_facts"]
            if facts.get("user_mentions"):
                formatted_parts.append(f"【使用者資訊】{'; '.join(facts['user_mentions'])}")
            if facts.get("topics"):
                formatted_parts.append(f"【討論話題】{', '.join(facts['topics'])}")
        
        # 加入上下文標記
        if memory_data.get("context_markers"):
            formatted_parts.append(f"【對話脈絡】{'; '.join(memory_data['context_markers'][:3])}")
        
        # 加入最近的對話（保留最重要的部分）
        messages = memory_data.get("messages", [])
        if messages:
            recent_context = []
            for msg in messages[-6:]:  # 最近3輪對話
                role = "使用者" if msg["role"] == "user" else "助手"
                content = msg["content"][:100]  # 限制長度
                recent_context.append(f"{role}: {content}")
            
            formatted_parts.append(f"【最近對話】\n" + "\n".join(recent_context))
        
        return "\n\n".join(formatted_parts)
    
    def create_memory_checkpoint(self, memory_data: Dict[str, Any]) -> str:
        """創建記憶檢查點，用於驗證LLM是否記住關鍵資訊"""
        
        checkpoint = {
            "conversation_id": memory_data.get("conversation_id"),
            "message_count": memory_data.get("total_messages", 0),
            "key_topics": memory_data.get("key_facts", {}).get("topics", []),
            "last_user_message": None,
            "last_assistant_response": None
        }
        
        messages = memory_data.get("messages", [])
        
        # 找出最後的使用者訊息和助手回應
        for msg in reversed(messages):
            if msg["role"] == "user" and not checkpoint["last_user_message"]:
                checkpoint["last_user_message"] = msg["content"][:50]
            elif msg["role"] == "assistant" and not checkpoint["last_assistant_response"]:
                checkpoint["last_assistant_response"] = msg["content"][:50]
            
            if checkpoint["last_user_message"] and checkpoint["last_assistant_response"]:
                break
        
        # 生成檢查點hash，用於驗證
        checkpoint_str = json.dumps(checkpoint, sort_keys=True, ensure_ascii=False)
        checkpoint["hash"] = hashlib.md5(checkpoint_str.encode()).hexdigest()[:8]
        
        return json.dumps(checkpoint, ensure_ascii=False)
    
    async def validate_memory_recall(
        self,
        response: str,
        memory_checkpoint: str
    ) -> Dict[str, Any]:
        """驗證LLM回應是否包含記憶中的關鍵資訊"""
        
        try:
            checkpoint = json.loads(memory_checkpoint)
        except:
            return {"valid": False, "reason": "Invalid checkpoint"}
        
        validation_result = {
            "valid": True,
            "issues": [],
            "score": 100
        }
        
        # 檢查是否提到關鍵話題
        key_topics = checkpoint.get("key_topics", [])
        mentioned_topics = sum(1 for topic in key_topics if topic in response)
        
        if key_topics and mentioned_topics == 0:
            validation_result["issues"].append("未提及任何關鍵話題")
            validation_result["score"] -= 30
        
        # 檢查是否與最近對話有連續性
        last_user = checkpoint.get("last_user_message", "")
        if last_user and len(response) > 20:
            # 簡單的相關性檢查
            user_keywords = set(last_user.split())
            response_keywords = set(response.split())
            
            if len(user_keywords & response_keywords) < 2:
                validation_result["issues"].append("回應與最近對話缺乏連續性")
                validation_result["score"] -= 20
        
        validation_result["valid"] = validation_result["score"] >= 50
        
        return validation_result