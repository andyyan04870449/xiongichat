"""智能回應生成節點 - 基於統一分析結果生成自然回應"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from datetime import datetime
import logging

from app.config import settings
from app.langgraph.state import WorkflowState

logger = logging.getLogger(__name__)


class IntelligentResponseGeneratorNode:
    """智能回應生成 - 基於完整分析生成最適合的回應"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model_chat,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            api_key=settings.openai_api_key,
        )
        self.max_memory_turns = settings.langgraph_max_memory_turns
    
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        """生成智能回應"""
        try:
            # 構建系統提示
            system_prompt = self._build_intelligent_prompt(state)
            
            # 構建訊息列表
            messages = [SystemMessage(content=system_prompt)]
            
            # 加入精簡的對話歷史
            messages = self._add_conversation_context(messages, state)
            
            # 加入當前輸入與分析結果
            user_message = self._build_analyzed_message(state)
            messages.append(HumanMessage(content=user_message))
            
            # 生成回應
            logger.info(f"Generating intelligent response with strategy: {state.get('response_strategy')}")
            response = await self.llm.ainvoke(messages)
            
            # 更新狀態
            state["reply"] = response.content
            
            # 更新記憶（用於下一輪對話）
            self._update_memory(state)
            
            logger.info(f"Intelligent response generated for user {state['user_id']}")
            
        except Exception as e:
            logger.error(f"IntelligentResponseGenerator error: {str(e)}")
            state["error"] = f"ResponseGenerator error: {str(e)}"
            state["reply"] = self._get_fallback_response(state)
        
        return state
    
    def _build_intelligent_prompt(self, state: WorkflowState) -> str:
        """構建智能系統提示"""
        analysis = state.get("unified_analysis", {})
        strategy = analysis.get("strategy", {})
        
        # 基礎身份設定
        base_prompt = f"""你是「雄i聊」，高雄市政府毒品防制局的AI關懷助理。
當前時間：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
用戶ID：{state['user_id']}

【核心身份】
- 專業但親切的關懷助理
- 提供毒品防制相關協助
- 關心用戶身心健康
- 引導至專業資源

【分析摘要】
{self._format_analysis_summary(analysis)}

【回應策略】
- 方法：{strategy.get('approach', 'casual')}
- 語氣：{strategy.get('tone', 'friendly')}
- 重點：{', '.join(strategy.get('key_points', ['自然對話']))}
- 避免：{', '.join(strategy.get('avoid', ['說教']))}
"""
        
        # 根據風險等級添加特別指引
        risk_level = state.get("risk_level", "none")
        if risk_level == "high":
            base_prompt += """
【高風險指引】
- 表達深切關懷但不驚慌
- 提供立即可用的求助資源
- 避免任何可能的觸發內容
- 確保用戶感受到支持
"""
        elif risk_level == "medium":
            base_prompt += """
【中風險指引】
- 適度表達關心
- 提供預防性建議
- 分享正確觀念
- 建立信任關係
"""
        
        # 如果有檢索到的知識
        if state.get("retrieved_knowledge"):
            knowledge_context = self._format_knowledge_for_generation(
                state["retrieved_knowledge"]
            )
            base_prompt += f"""
【參考知識】
{knowledge_context}

請自然地整合這些資訊，不要生硬地複製貼上。
"""
        
        return base_prompt
    
    def _build_analyzed_message(self, state: WorkflowState) -> str:
        """構建包含分析結果的用戶訊息"""
        analysis = state.get("unified_analysis", {})
        
        message = f"""用戶輸入：{state['input_text']}

【理解結果】
- 意圖：{analysis.get('intent', {}).get('specific', '一般對話')}
- 情緒：{analysis.get('emotional', {}).get('current_state', 'neutral')}
- 核心需求：{analysis.get('summary', '對話交流')}

請根據以上分析，生成自然、貼心、有幫助的回應。
記住：
1. 回應要簡潔（通常2-3句話）
2. 符合用戶當前的情緒狀態
3. 提供實質幫助而非空洞安慰
4. 保持對話的連貫性"""
        
        return message
    
    def _add_conversation_context(
        self, 
        messages: List, 
        state: WorkflowState
    ) -> List:
        """添加精簡的對話上下文"""
        memory = state.get("memory", [])
        
        if not memory:
            return messages
        
        # 只保留最近的關鍵對話
        recent_memory = self._extract_key_exchanges(memory)
        
        for msg in recent_memory:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        return messages
    
    def _extract_key_exchanges(self, memory: List[Dict]) -> List[Dict]:
        """提取關鍵對話交換"""
        analysis = self.state.get("unified_analysis", {}) if hasattr(self, 'state') else {}
        
        # 如果有代詞指向或話題延續，需要更多上下文
        if analysis.get("context", {}).get("pronouns", {}).get("resolution"):
            return memory[-6:]  # 最近3輪對話
        
        # 一般情況只需要最近的對話
        return memory[-4:]  # 最近2輪對話
    
    def _format_analysis_summary(self, analysis: Dict) -> str:
        """格式化分析摘要"""
        summary_parts = []
        
        # 意圖
        intent = analysis.get("intent", {})
        if intent.get("specific"):
            summary_parts.append(f"意圖：{intent['specific']}")
        
        # 情緒
        emotional = analysis.get("emotional", {})
        if emotional.get("current_state") != "neutral":
            summary_parts.append(
                f"情緒：{emotional['current_state']} "
                f"({emotional.get('intensity', 'medium')})"
            )
        
        # 風險
        risk = analysis.get("risk", {})
        if risk.get("level") not in ["none", "low"]:
            summary_parts.append(f"風險：{risk['level']}")
        
        # 知識需求
        knowledge = analysis.get("knowledge", {})
        if knowledge.get("expected_info"):
            summary_parts.append(f"需要：{knowledge['expected_info']}")
        
        return " | ".join(summary_parts) if summary_parts else "一般對話"
    
    def _format_knowledge_for_generation(
        self, 
        knowledge_items: List[Dict[str, Any]]
    ) -> str:
        """格式化知識供生成使用"""
        if not knowledge_items:
            return ""
        
        # 只使用最相關的前3項
        top_items = knowledge_items[:3]
        formatted = []
        
        for item in top_items:
            # 提取關鍵信息
            title = item.get("title", "")
            content = item.get("content", "")
            
            # 截取適當長度
            if len(content) > 200:
                content = content[:200] + "..."
            
            if title:
                formatted.append(f"【{title}】\n{content}")
            else:
                formatted.append(content)
        
        return "\n\n".join(formatted)
    
    def _update_memory(self, state: WorkflowState):
        """更新對話記憶"""
        memory = state.get("memory", [])
        
        # 添加本輪對話
        memory.append({"role": "user", "content": state["input_text"]})
        memory.append({"role": "assistant", "content": state["reply"]})
        
        # 限制記憶長度
        if len(memory) > self.max_memory_turns * 2:
            memory = memory[-(self.max_memory_turns * 2):]
        
        state["memory"] = memory
    
    def _get_fallback_response(self, state: WorkflowState) -> str:
        """獲取降級回應"""
        risk_level = state.get("risk_level", "none")
        
        if risk_level == "high":
            return "我了解您現在的處境可能很困難。如果需要立即協助，請撥打24小時諮詢專線。您並不孤單，我們都在這裡支持您。"
        elif state.get("emotional_state") in ["anxious", "depressed"]:
            return "我感受到您的情緒，謝謝您願意與我分享。有什麼我可以幫助您的嗎？"
        else:
            return "謝謝您的訊息。有什麼我可以協助您的嗎？"