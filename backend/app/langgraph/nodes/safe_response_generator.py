"""安全回應生成節點 - 根據風險評估生成適當回應"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from datetime import datetime
import logging

from app.config import settings
from app.langgraph.state import WorkflowState
from app.langgraph.prompts import CHAT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class SafeResponseGeneratorNode:
    """安全回應生成節點 - 根據風險評估和策略生成適當回應"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model_chat,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            api_key=settings.openai_api_key,
        )
        self.max_memory_turns = settings.langgraph_max_memory_turns
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """生成安全回應"""
        try:
            # 儲存當前危機等級供格式化使用
            self._current_crisis_level = state.get("crisis_level", "none")
            
            # 根據回應策略調整系統提示
            system_prompt = self._build_system_prompt(state)
            
            # 構建訊息列表
            messages = [SystemMessage(content=system_prompt)]
            
            # 加入對話歷史
            memory = state.get("memory", [])
            if memory:
                recent_memory = memory[-(self.max_memory_turns * 2):]
                for msg in recent_memory:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            # 加入當前使用者輸入（附帶安全提示）
            user_message = self._build_user_message(state)
            messages.append(HumanMessage(content=user_message))
            
            # 生成回覆
            logger.info(f"Generating safe response with strategy: {state.get('response_strategy')}")
            response = await self.llm.ainvoke(messages)
            
            # 更新狀態
            state["reply"] = response.content
            
            # 更新記憶
            new_memory = memory.copy() if memory else []
            new_memory.append({"role": "user", "content": state["input_text"]})
            new_memory.append({"role": "assistant", "content": response.content})
            state["memory"] = new_memory
            
            logger.info(f"Safe response generated for user {state['user_id']}")
            
        except Exception as e:
            logger.error(f"SafeResponseGenerator error: {str(e)}")
            state["error"] = f"SafeResponseGenerator error: {str(e)}"
            state["reply"] = "抱歉，我需要更謹慎地回應這個問題。建議您聯繫專業人員。"
        
        return state
    
    def _build_system_prompt(self, state: WorkflowState) -> str:
        """根據風險等級和策略構建系統提示"""
        
        base_prompt = CHAT_SYSTEM_PROMPT.format(
            user_id=state["user_id"],
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # 根據危機等級調整回應策略
        crisis_level = state.get("crisis_level", "none")
        if crisis_level in ["medium", "high"]:
            base_prompt += f"""

【危機介入模式 - 等級: {crisis_level}】
檢測到用戶可能處於困境，請：
1. 立即表達關心和同理心
2. 主動提供具體的協助資源
3. 如果有 retrieved_knowledge 中的機構資訊，請明確提供：
   - 機構名稱和服務內容
   - 聯絡電話（如果有）
   - 地址（如果有）
   - 服務時間（如果有）
4. 使用溫暖、支持性的語氣
5. 避免說教或批判
6. 確保用戶知道有人願意幫助他們

重要：只提供 retrieved_knowledge 中實際存在的資訊，不要編造。
"""
        
        # 添加資訊回答控制規則
        base_prompt += """

【重要：資訊回答規則】
關於事實性資訊的回答原則：

1. 具體資訊類（必須有知識庫支援）：
   - 機構地址、位置、怎麼去 → 只能使用 retrieved_knowledge
   - 電話號碼、聯絡方式 → 只能使用 retrieved_knowledge
   - 服務時間、營業時間 → 只能使用 retrieved_knowledge
   - 費用、價格、收費標準 → 只能使用 retrieved_knowledge
   
2. 如果被問到具體資訊但沒有 retrieved_knowledge：
   - 不要使用你的內建知識回答
   - 不要編造或猜測資訊
   - 使用以下回應模板：
     「關於[主題]的具體資訊，建議您可以：
      1) 撥打毒防局諮詢專線
      2) 親自前往詢問
      3) 瀏覽官方網站」

3. 可以自由回答的內容：
   - 一般性關懷和問候
   - 情感支持和同理心表達
   - 引導性問題和澄清
   - 社交互動和閒聊

4. 回答時的語氣指引：
   - 有知識庫資料時：「根據我們的資料，[具體資訊]」
   - 無知識庫資料時：保持友善但誠實，提供替代方案
"""
        
        # 根據回應策略添加特定指引
        strategy = state.get("response_strategy", "NORMAL")
        risk_level = state.get("risk_level", "SAFE")
        
        strategy_prompts = {
            "REDIRECT_TO_HELP": """
【特別指引】
用戶可能有不當意圖。請：
1. 不提供任何獲取管制藥品的資訊
2. 溫和地引導至專業協助
3. 提供官方諮詢管道
4. 保持關懷但堅定的態度
""",
            "EDUCATIONAL": """
【特別指引】
用戶需要正確資訊。請：
1. 提供客觀的教育性內容
2. 強調健康和法律風險
3. 不詳述使用方法
4. 適時提供戒癮資源
""",
            "SUPPORTIVE": """
【特別指引】
用戶需要情緒支持。請：
1. 表達同理心和關懷
2. 肯定求助的勇氣
3. 提供具體的支持資源
4. 避免說教或批判
""",
            "PREVENTIVE": """
【特別指引】
需要預防性介入。請：
1. 了解用戶的困擾
2. 提供健康的替代方案
3. 分享正確觀念
4. 建立信任關係
"""
        }
        
        # 添加策略特定提示
        if strategy in strategy_prompts:
            base_prompt += strategy_prompts[strategy]
        
        # 如果有檢索到的知識，加入參考
        if state.get("retrieved_knowledge"):
            knowledge_context = self._format_knowledge_context(state["retrieved_knowledge"])
            if knowledge_context:
                base_prompt += f"\n【參考資訊】\n{knowledge_context}"
        
        # 添加風險警示
        if risk_level in ["HIGH", "MEDIUM"]:
            base_prompt += "\n【注意】此對話涉及敏感內容，請特別謹慎回應。"
        
        return base_prompt
    
    def _build_user_message(self, state: WorkflowState) -> str:
        """構建用戶訊息，可能包含額外的安全提示"""
        
        user_input = state["input_text"]
        
        # 如果涉及毒品，添加內部提示（不顯示給用戶）
        if state.get("drug_info"):
            drug_context = f"\n[系統內部資訊：用戶提及的物質資訊：{state['drug_info']}]"
            user_input += drug_context
        
        return user_input
    
    def _format_knowledge_context(self, knowledge_items: List[Dict[str, Any]]) -> str:
        """格式化知識庫檢索結果"""
        if not knowledge_items:
            return ""
        
        # 根據危機等級決定顯示方式
        crisis_level = getattr(self, '_current_crisis_level', 'none')
        
        if crisis_level in ["medium", "high"]:
            # 危機情況下提供完整的協助資訊
            context_parts = []
            
            for idx, item in enumerate(knowledge_items[:3], 1):  # 最多顯示3個資源
                content = item.get("content", "")
                title = item.get("title", "")
                
                # 提取關鍵資訊
                if "聯絡" in content or "電話" in content or "地址" in content:
                    # 完整顯示聯絡資訊
                    if title:
                        context_parts.append(f"{idx}. {title}:\n{content}")
                    else:
                        context_parts.append(f"{idx}. {content}")
                else:
                    # 一般資訊簡短顯示
                    if len(content) > 150:
                        content = content[:150] + "..."
                    if title:
                        context_parts.append(f"{idx}. {title}: {content}")
                    else:
                        context_parts.append(f"{idx}. {content}")
            
            return "\n".join(context_parts)
        
        # 一般情況下提供精簡的知識
        top_items = knowledge_items[:2]
        context_parts = []
        
        for idx, item in enumerate(top_items, 1):
            content = item.get("content", "")
            if len(content) > 100:
                content = content[:100] + "..."
            
            title = item.get("title", "")
            if title:
                context_parts.append(f"{idx}. {title}: {content}")
            else:
                context_parts.append(f"{idx}. {content}")
        
        return "\n".join(context_parts)