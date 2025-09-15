"""極簡工作流 - 3步驟架構，智能集中在最終LLM"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from cachetools import TTLCache

from app.config import settings
from app.langgraph.state import WorkflowState
from app.services.rag_retriever import RAGRetriever
from app.utils.ai_logger import get_ai_logger
from app.utils.ultimate_logger import get_ultimate_logger
from app.utils.quality_logger import get_quality_logger
# 移除字數限制管理器import
from app.langgraph.nodes.conversation_logger import ConversationLoggerNode
from app.services.enhanced_memory import EnhancedMemoryService
from app.langgraph.intent_cleaner import IntentCleaner

logger = logging.getLogger(__name__)


class IntentAnalyzer:
    """意圖分析器 - 只分析不生成"""
    
    ANALYSIS_PROMPT = """你是專業的危機偵測與意圖分析系統。請仔細分析用戶輸入，返回JSON格式。

# 重要分析原則
**綜合分析當前用戶輸入與對話歷史**
需要結合對話歷史來評估策略效果和升級需求，同時基於當前輸入進行危機判斷。

# 危機識別準則（最高優先級）

## 明確危機信號 → risk_level: "high"
**分析原則：關注語義和情感強度，不拘泥於具體詞彙**

- 直接自殺意念：明確表達結束生命的想法或計畫
- 隱喻性表達：暗示逃避、消失、解脫等概念
- 行為性暗示：提到危險場所、自傷工具或行為
- 極度絕望：表達完全失去希望、意義感喪失
- 世界觀崩潰：認為世界/人生完全無價值、無意義
- 情感麻木：表達完全失去感受能力或動機

## 中度風險信號 → risk_level: "medium"
**分析原則：識別自傷傾向和極度痛苦，但未達直接自殺風險**

- 自傷傾向：表達想要傷害或懲罰自己的想法
- 極度痛苦：描述無法承受的痛苦，但未明確表達死亡意念
- 逃避現實：希望通過物質或其他方式徹底逃避現實
- 強烈無助感：完全失去控制感和應對能力

## 低度風險信號 → risk_level: "low"
**分析原則：識別一般負面情緒和生活困擾**

- 情緒困擾：表達憂鬱、焦慮、孤單等負面情緒
- 生活問題：睡眠、食慾、動機等日常功能困擾
- 輕度求助：表達需要幫助但無急迫性或危險性

# 意圖分類準則

- "危機": risk_level為high時
- "求助": 明確尋求戒毒、治療、復健協助
- "諮詢": 詢問機構、電話、地址、服務內容
- "情緒支持": 表達負面情緒、需要陪伴
- "問候": 日常招呼、你好、早安等
- "一般對話": 其他所有情況

# RAG觸發條件（嚴格控制）
**need_rag: true 僅在以下情況**：
- 用戶明確詢問服務資訊（電話、地址、時間、服務內容）
- 用戶主動要求聯絡資訊或具體幫助
- care_stage_needed為3且前兩層策略已無效

**need_rag: false 所有其他情況**：
- 純情緒表達或危機狀態
- 一般對話或問候  
- 已在進行情緒支持對話中

# 關懷策略升級機制
根據對話歷史評估AI關懷策略的有效性並決定升級：

## 策略有效性評估標準
1. **有效指標**：
   - 用戶情緒狀態改善（risk_level下降）
   - 用戶開始主動溝通或詢問資源
   - 出現感謝、認同等正面回應
   - 願意分享更多個人情況

2. **無效指標**：
   - 危機程度持續或加深
   - 用戶重複表達相同痛苦
   - 對AI回應無反應或負面反應
   - 明確拒絕幫助或表達失望

## 升級觸發機制
**自動升級條件**：
- 同一層策略連續使用2-3次仍無改善 → 升級下一層
- 用戶危機程度明顯加深 → 跳級處理
- 用戶明確表達對當前方式不滿 → 立即升級

**升級路徑**：
- 第1層無效 → 升級至第2層（加強陪伴支持）
- 第2層無效 → 升級至第3層（提供具體資源）  
- 第3層無效 → 特殊處理（建議專業幫助）

## 策略歷史分析要點
- 統計最近3-5次對話的策略使用情況
- 比較用戶情緒變化趨勢（惡化/持平/改善）
- 識別"治療停滯"狀態（重複循環無進展）
- 評估用戶對不同策略類型的反應模式

# 範例分析

輸入：「活著好累，想要解脫了」
分析：隱喻性表達解脫，高風險
輸出：risk_level="high", intent="危機"

輸入：「我覺得沒有明天了」
分析：表達絕望，暗示結束生命
輸出：risk_level="high", intent="危機"

輸入：「我現在在頂樓」
分析：位置暗示潛在危險行為
輸出：risk_level="high", intent="危機"

輸入：「我想傷害自己」
分析：明確自傷意圖
輸出：risk_level="medium", intent="危機"

# 返回格式
{{
    "risk_level": "none/low/medium/high",
    "intent": "問候/求助/諮詢/危機/情緒支持/一般對話",
    "need_rag": true/false,
    "search_keywords": ["關鍵詞1", "關鍵詞2"],
    "entities": {{
        "substances": ["提到的毒品"],
        "locations": ["提到的地點"],
        "symptoms": ["提到的症狀"]
    }},
    "emotional_state": "絕望/焦慮/平靜/積極/不明",
    "urgency": "immediate/high/normal/low",
    "care_stage_needed": 1,
    "care_stage_reason": "階段選擇的理由說明",
    "strategy_effectiveness": "effective/ineffective/unknown/improving",
    "upgrade_reason": "策略升級的具體原因",
    "previous_stages_tried": [1, 1, 2],
    "emotion_trend": "improving/stable/deteriorating/unknown",
    "treatment_progress": "initial/ongoing/stagnant/breakthrough",
    "confidence_level": 0.85
}}

用戶輸入：{input_text}
對話歷史：{memory}

只返回JSON，不要其他內容。"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model_analysis,  # gpt-4o-mini
            temperature=0.1,
            max_tokens=400,
            api_key=settings.openai_api_key,
        )
        self.cache = TTLCache(maxsize=100, ttl=300)  # 5分鐘快取
    
    def _analyze_strategy_history(self, memory: List[Dict]) -> Dict:
        """分析策略使用歷史和有效性"""
        if not memory:
            return {
                "previous_stages_tried": [],
                "strategy_effectiveness": "unknown",
                "emotion_trend": "unknown", 
                "treatment_progress": "initial",
                "last_risk_levels": []
            }
        
        # 提取AI回應中的策略使用模式
        ai_responses = [msg for msg in memory if msg.get("role") == "assistant"]
        user_responses = [msg for msg in memory if msg.get("role") == "user"]
        
        # 分析最近使用的策略（基於回應內容推測）
        recent_stages = []
        last_risk_levels = []
        
        # 改善的策略識別邏輯 - 更準確的分層判斷
        for i, response in enumerate(ai_responses[-5:]):  # 最近5次AI回應
            content = response.get("content", "").lower()
            
            # 第3層策略關鍵詞 - 具體資源提供
            if any(word in content for word in ["電話", "地址", "資源", "專業", "機構", "072865580", "高雄市毒品防制局"]):
                stage = 3
            # 第1層策略關鍵詞 - 情感確認與同理
            elif any(word in content for word in ["聽起來", "感覺", "理解", "辛苦", "可以理解", "真的很"]):
                stage = 1
            # 第2層策略關鍵詞 - 陪伴與支持
            elif any(word in content for word in ["陪伴", "支持", "陪著你", "在這裡", "一起", "隨時"]):
                stage = 2
            else:
                # 根據對話輪次推測：初期傾向第1層，後期第2層
                if i < 2:
                    stage = 1
                else:
                    stage = 2
            
            recent_stages.append(stage)
        
        # 評估策略有效性（簡化邏輯）
        if len(user_responses) >= 2:
            # 比較最近的用戶回應，看是否有改善跡象
            recent_user = user_responses[-1].get("content", "").lower()
            prev_user = user_responses[-2].get("content", "").lower()
            
            # 簡單的改善指標
            positive_words = ["謝謝", "感謝", "好一點", "幫助", "理解", "支持"]
            negative_words = ["沒用", "不行", "更糟", "無效", "失望", "放棄"]
            
            if any(word in recent_user for word in positive_words):
                effectiveness = "improving"
            elif any(word in recent_user for word in negative_words):
                effectiveness = "ineffective"
            elif recent_user == prev_user:  # 重複相同內容
                effectiveness = "ineffective"
            else:
                effectiveness = "unknown"
        else:
            effectiveness = "unknown"
        
        # 治療進程評估
        if len(recent_stages) == 0:
            progress = "initial"
        elif len(set(recent_stages)) == 1 and len(recent_stages) >= 3:
            progress = "stagnant"  # 同樣策略重複使用
        elif effectiveness == "improving":
            progress = "breakthrough"
        else:
            progress = "ongoing"
        
        return {
            "previous_stages_tried": recent_stages,
            "strategy_effectiveness": effectiveness,
            "emotion_trend": "stable",  # 簡化處理
            "treatment_progress": progress,
            "last_risk_levels": last_risk_levels
        }
    
    def _determine_upgrade_strategy(self, current_analysis: Dict, history_analysis: Dict) -> Dict:
        """決定是否需要升級策略"""
        
        current_risk = current_analysis.get("risk_level", "none")
        previous_stages = history_analysis.get("previous_stages_tried", [])
        effectiveness = history_analysis.get("strategy_effectiveness", "unknown")
        progress = history_analysis.get("treatment_progress", "initial")
        
        # 動態策略選擇 - 基於情境和歷史
        if current_risk == "high":
            default_stage = 1  # 高風險從情感確認開始
        elif current_analysis.get("intent") == "諮詢":
            default_stage = 3  # 諮詢直接提供資源
        elif not previous_stages:  # 首次對話
            default_stage = 1  # 從第1層開始
        else:
            default_stage = 2  # 其他情況預設第2層
        
        # 升級決策邏輯 - 放寬條件
        upgrade_needed = False
        upgrade_reason = ""
        suggested_stage = default_stage
        
        if previous_stages:
            last_stage = previous_stages[-1] if previous_stages else 1
            
            # 1. 策略無效時升級 (放寬條件)
            if effectiveness == "ineffective":
                upgrade_needed = True
                suggested_stage = min(last_stage + 1, 3)
                upgrade_reason = f"第{last_stage}層策略效果不佳，升級至第{suggested_stage}層"
            
            # 2. 同層策略使用過多時升級
            elif len(previous_stages) >= 2 and all(s == last_stage for s in previous_stages[-2:]):
                upgrade_needed = True
                suggested_stage = min(last_stage + 1, 3)
                upgrade_reason = f"第{last_stage}層策略重複使用，升級至第{suggested_stage}層"
            
            # 3. 治療停滯時升級
            elif progress == "stagnant":
                upgrade_needed = True
                most_used_stage = max(set(previous_stages), key=previous_stages.count)
                suggested_stage = min(most_used_stage + 1, 3)
                upgrade_reason = f"治療進展停滯，從第{most_used_stage}層升級至第{suggested_stage}層"
            
            # 4. 風險程度變化調整
            elif current_risk == "high" and last_stage > 1:
                upgrade_needed = True
                suggested_stage = 1
                upgrade_reason = "用戶危機程度加深，回到第1層情感確認"
            
            # 5. 情緒明顯惡化時升級
            elif current_analysis.get("emotional_state") in ["絕望", "憤怒"] and last_stage < 3:
                upgrade_needed = True
                suggested_stage = min(last_stage + 1, 3)
                upgrade_reason = f"用戶情緒惡化，從第{last_stage}層升級至第{suggested_stage}層"
        
        if not upgrade_needed:
            suggested_stage = default_stage
            upgrade_reason = "維持當前策略層次"
        
        return {
            "care_stage_needed": suggested_stage,
            "upgrade_reason": upgrade_reason,
            "is_upgrade": upgrade_needed
        }

    async def analyze(self, input_text: str, memory: List[Dict] = None) -> Dict:
        """分析用戶意圖"""
        
        # 檢查快取
        cache_key = f"intent:{input_text[:50]}"
        if cache_key in self.cache:
            logger.info(f"Intent cache hit for: {input_text[:30]}")
            return self.cache[cache_key]
        
        try:
            # 格式化記憶
            memory_str = self._format_memory(memory) if memory else "無"
            
            # 構建提示
            prompt = self.ANALYSIS_PROMPT.format(
                input_text=input_text,
                memory=memory_str
            )
            
            messages = [
                SystemMessage(content="你是專業的對話分析系統，只返回JSON格式結果。"),
                HumanMessage(content=prompt)
            ]
            
            # 執行分析
            response = await self.llm.ainvoke(messages)
            
            # 解析結果 - 增強JSON處理
            try:
                result = self._parse_json_response(response.content)
                if result:
                    # 進行策略歷史分析和升級決策
                    history_analysis = self._analyze_strategy_history(memory)
                    upgrade_decision = self._determine_upgrade_strategy(result, history_analysis)
                    
                    # 整合升級決策到結果中
                    result.update(upgrade_decision)
                    result.update(history_analysis)
                    
                    # 加入快取
                    self.cache[cache_key] = result
                    logger.info(f"[Intent Analysis] ✅ 成功解析 - risk={result.get('risk_level')}, intent={result.get('intent')}, stage={result.get('care_stage_needed')}")
                    logger.debug(f"[Intent Analysis] 完整結果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    return result
                else:
                    logger.warning(f"[Intent Analysis] ❌ JSON格式無效: {response.content[:200]}")
                    logger.debug(f"[Intent Analysis] 原始LLM回應: {response.content[:1000]}")
                    return self._get_default_analysis(input_text)
            except Exception as parse_error:
                logger.error(f"[Intent Analysis] ❌ JSON解析失敗: {str(parse_error)}")
                logger.debug(f"[Intent Analysis] 原始回應內容: {response.content}")
                return self._get_default_analysis(input_text)
                
        except Exception as e:
            logger.error(f"Intent analysis error: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            if hasattr(e, '__traceback__'):
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
            return self._get_default_analysis(input_text)
    
    def _parse_json_response(self, content: str) -> Dict:
        """強健的JSON解析方法 - 處理各種格式問題"""
        
        if not content or not isinstance(content, str):
            logger.debug(f"[JSON Parser] ❌ 無效輸入: content={content}, type={type(content)}")
            return None
        
        # 1. 基本清理
        cleaned_content = content.strip()
        logger.debug(f"[JSON Parser] 原始內容 (前500字): {content[:500]}")
        logger.debug(f"[JSON Parser] 清理後內容 (前500字): {cleaned_content[:500]}")
        
        # 2. 直接嘗試解析
        try:
            result = json.loads(cleaned_content)
            logger.debug(f"[JSON Parser] ✅ 直接解析成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        except json.JSONDecodeError as e:
            logger.debug(f"[JSON Parser] 直接解析失敗: {str(e)}, 位置: line {e.lineno}, col {e.colno}")
            pass
        
        # 3. 嘗試提取JSON片段
        import re
        
        # 查找完整的JSON對象
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        json_matches = re.findall(json_pattern, cleaned_content, re.DOTALL)
        
        for match in json_matches:
            try:
                result = json.loads(match.strip())
                # 驗證是否包含必要字段
                if self._validate_intent_result(result):
                    return result
            except json.JSONDecodeError:
                continue
        
        # 4. 嘗試修復不完整的JSON
        repaired_json = self._repair_incomplete_json(cleaned_content)
        if repaired_json:
            try:
                result = json.loads(repaired_json)
                if self._validate_intent_result(result):
                    return result
            except json.JSONDecodeError:
                pass
        
        # 5. 最後嘗試：從文本中提取關鍵資訊構建JSON
        extracted_result = self._extract_from_text(cleaned_content)
        if extracted_result:
            return extracted_result
        
        return None
    
    def _validate_intent_result(self, result: Dict) -> bool:
        """驗證意圖分析結果是否有效"""
        
        if not isinstance(result, dict):
            return False
        
        # 檢查必要字段
        required_fields = ["risk_level", "intent", "need_rag"]
        
        for field in required_fields:
            if field not in result:
                return False
        
        # 檢查字段值是否合理
        valid_risk_levels = ["none", "low", "medium", "high"]
        if result.get("risk_level") not in valid_risk_levels:
            return False
        
        return True
    
    def _repair_incomplete_json(self, content: str) -> str:
        """嘗試修復不完整的JSON"""
        
        import re
        
        # 移除多餘的換行符和空格
        content = re.sub(r'\n\s*', ' ', content).strip()
        
        # 如果缺少開始的大括號
        if not content.startswith('{') and '"risk_level"' in content:
            content = '{' + content
        
        # 如果缺少結束的大括號
        if not content.endswith('}') and content.startswith('{'):
            content = content + '}'
        
        # 嘗試補充缺少的字段
        if content.startswith('{') and content.endswith('}'):
            try:
                # 簡單的字段補充邏輯
                partial = json.loads(content)
                
                # 補充缺少的必要字段
                if "risk_level" not in partial:
                    partial["risk_level"] = "none"
                if "intent" not in partial:
                    partial["intent"] = "一般對話"
                if "need_rag" not in partial:
                    partial["need_rag"] = False
                if "search_keywords" not in partial:
                    partial["search_keywords"] = []
                if "entities" not in partial:
                    partial["entities"] = {}
                if "emotional_state" not in partial:
                    partial["emotional_state"] = "不明"
                if "urgency" not in partial:
                    partial["urgency"] = "normal"
                
                return json.dumps(partial, ensure_ascii=False)
            except:
                pass
        
        return None
    
    def _extract_from_text(self, content: str) -> Dict:
        """從文本中提取關鍵資訊構建JSON（最後手段）"""
        
        result = {
            "risk_level": "none",
            "intent": "一般對話",
            "need_rag": False,
            "search_keywords": [],
            "entities": {},
            "emotional_state": "不明",
            "urgency": "normal"
        }
        
        # 簡單的關鍵詞匹配
        content_lower = content.lower()
        
        # 提取風險等級
        if any(word in content_lower for word in ["high", "高", "危機"]):
            result["risk_level"] = "high"
        elif any(word in content_lower for word in ["medium", "中", "中等"]):
            result["risk_level"] = "medium"
        elif any(word in content_lower for word in ["low", "低"]):
            result["risk_level"] = "low"
        
        # 提取意圖
        if any(word in content_lower for word in ["危機", "crisis"]):
            result["intent"] = "危機"
        elif any(word in content_lower for word in ["求助", "help"]):
            result["intent"] = "求助"
        elif any(word in content_lower for word in ["諮詢", "consultation"]):
            result["intent"] = "諮詢"
        elif any(word in content_lower for word in ["情緒", "emotion"]):
            result["intent"] = "情緒支持"
        
        # 檢測是否需要RAG
        if any(word in content_lower for word in ["true", "需要", "rag"]):
            result["need_rag"] = True
        
        return result

    def _format_memory(self, memory: List[Dict]) -> str:
        """格式化對話記憶"""
        if not memory:
            return "無"
        
        formatted = []
        for msg in memory[-5:]:  # 最近5條
            role = "用戶" if msg.get("role") == "user" else "助理"
            formatted.append(f"{role}：{msg.get('content', '')}")
        
        return "\n".join(formatted)
    
    def _get_default_analysis(self, text: str) -> Dict:
        """預設分析結果（容錯用）"""
        # 擴充的危機關鍵詞庫
        high_risk_keywords = [
            "自殺", "想死", "死了", "活不下去", "解脫", "結束",
            "不想活", "沒有明天", "傷害自己", "頂樓", "跳下",
            "割腕", "吃藥", "沒意義", "了結", "一了百了",
            "消失", "不在了", "撐不下去", "生不如死",
            "永遠睡", "不要醒", "最後一", "不用擔心我",
            "想好要怎麼做", "今晚過後", "跟家人說", "對不起"
        ]
        
        medium_risk_keywords = [
            "痛苦", "絕望", "崩潰", "受不了", "好累", "好苦",
            "遺言", "交代"
        ]
        
        help_keywords = ["戒毒", "戒癮", "治療", "機構", "哪裡", "電話", "地址", "毒防局"]
        
        # 判斷風險等級
        if any(kw in text for kw in high_risk_keywords):
            risk_level = "high"
            intent = "危機"
        elif any(kw in text for kw in medium_risk_keywords):
            risk_level = "medium"
            intent = "危機"  # 中度風險也歸類為危機
        else:
            risk_level = "none"
            intent = "一般對話"
        
        # 檢查是否為諮詢
        if any(kw in text for kw in ["電話", "地址", "毒防局", "哪裡", "怎麼去", "在哪"]):
            intent = "諮詢"
            need_rag = True
        else:
            need_rag = any(kw in text for kw in help_keywords)
        
        # 決定關懷階段
        if risk_level == "high":
            care_stage = 1  # 高風險時優先情感確認
            care_reason = "高風險情況，需要立即情感確認與同理"
        elif intent in ["危機", "情緒支持"]:
            care_stage = 1  # 情緒類問題從第一層開始
            care_reason = "情緒相關需求，從情感確認開始"
        elif intent == "諮詢":
            care_stage = 3  # 諮詢類可直接提供資源
            care_reason = "資訊查詢需求，可直接提供資源"
        else:
            care_stage = 2  # 一般情況使用第二層
            care_reason = "一般對話，提供適度支持"
        
        return {
            "risk_level": risk_level,
            "intent": intent,
            "need_rag": need_rag,
            "search_keywords": [text],
            "entities": {},
            "emotional_state": "絕望" if risk_level == "high" else "不明",
            "urgency": "immediate" if risk_level == "high" else "normal",
            "care_stage_needed": care_stage,
            "care_stage_reason": care_reason,
            "strategy_effectiveness": "unknown",
            "upgrade_reason": "預設分析，無歷史數據",
            "previous_stages_tried": [],
            "emotion_trend": "unknown",
            "treatment_progress": "initial",
            "confidence_level": 0.7
        }


class SmartRAG:
    """智能RAG檢索器"""
    
    def __init__(self):
        self.retriever = RAGRetriever()
        self.cache = TTLCache(maxsize=50, ttl=300)
        self.intent_cleaner = IntentCleaner()
    
    async def retrieve(self, cleaned_query: str, intent: str) -> str:
        """執行檢索並格式化結果
        
        Args:
            cleaned_query: 已清理的查詢語句
            intent: 用戶意圖
        """
        
        # 根據意圖優化查詢（可選的前綴添加）
        if intent == "危機":
            query = f"自殺防治 心理諮商 緊急求助 {cleaned_query}"
        elif intent == "求助":
            query = f"戒毒 戒癮 治療 {cleaned_query}"
        elif intent == "諮詢":
            # 諮詢類不需要額外前綴，清理後的語句已經足夠
            query = cleaned_query
        else:
            query = cleaned_query
        
        # 檢查快取
        cache_key = f"rag:{query[:50]}"
        if cache_key in self.cache:
            logger.info(f"RAG cache hit for: {query[:30]}")
            return self.cache[cache_key]
        
        try:
            # 執行檢索
            logger.info(f"Executing RAG search: {query[:50]}")
            results = await self.retriever.retrieve(
                query=query,
                k=5,
                similarity_threshold=0.45
            )
            
            if results:
                # 格式化結果
                formatted = self._format_results(results)
                self.cache[cache_key] = formatted
                return formatted
            else:
                # 返回預設資源
                return self._get_default_resources(intent)
                
        except Exception as e:
            logger.error(f"RAG retrieval error: {str(e)}")
            return self._get_default_resources(intent)
    
    def _format_results(self, results) -> str:
        """格式化檢索結果"""
        formatted_items = []
        seen = set()  # 去重
        
        for result in results[:3]:  # 最多3筆
            content = result.content if hasattr(result, 'content') else str(result)
            
            # 提取關鍵資訊
            import re
            
            # 提取機構名稱
            if "醫院" in content or "中心" in content or "機構" in content:
                name_match = re.search(r'[\u4e00-\u9fa5]+(?:醫院|中心|機構|基金會)', content)
                if name_match:
                    name = name_match.group(0)
                    if name not in seen:
                        seen.add(name)
                        formatted_items.append(name)
            
            # 提取電話 (支援多種格式)
            phones = re.findall(r'(?:\(?\d{2,3}\)?[\s-]?\d{3,4}[\s-]?\d{4}|0\d{9,10}|0800[\s-]?\d{6})', content)
            for phone in phones[:1]:
                if phone not in seen:
                    seen.add(phone)
                    formatted_items.append(f"電話：{phone}")
            
            # 提取地址
            addr_match = re.search(r'(?:高雄市)?[\u4e00-\u9fa5]+[區市][\u4e00-\u9fa5]+[路街][\u4e00-\u9fa5\d]+號', content)
            if addr_match:
                addr = addr_match.group(0)
                if addr not in seen:
                    seen.add(addr)
                    formatted_items.append(f"地址：{addr}")
        
        return "；".join(formatted_items) if formatted_items else ""
    
    def _get_default_resources(self, intent: str) -> str:
        """取得預設資源"""
        # 完全依賴RAG，不提供預設資源
        return ""


class PrimaryResponseGenerator:
    """GPT-4o主要回答生成器 - 提供完整有用的回答"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model_chat,  # gpt-4o
            temperature=0.7,  # 提高溫度讓回應更靈活自然
            # 移除字數限制，讓GPT-4o自由發揮
            api_key=settings.openai_api_key,
        )
        self.cache = TTLCache(maxsize=50, ttl=300)  # 5分鐘快取
    
    async def generate_primary_response(self, user_message: str, memory: List[Dict] = None, retrieved_knowledge: str = None) -> str:
        """生成GPT-4o主要回答（包含對話歷史和檢索知識）"""

        # 檢查快取（包含歷史和知識的hash）
        memory_hash = hash(str(memory)) if memory else 0
        knowledge_hash = hash(retrieved_knowledge) if retrieved_knowledge else 0
        cache_key = f"primary:{user_message[:30]}:{memory_hash}:{knowledge_hash}"
        if cache_key in self.cache:
            logger.info(f"Primary response cache hit for: {user_message[:30]}")
            return self.cache[cache_key]

        try:
            # 構建系統提示，包含檢索到的知識
            system_prompt = "你就像是認識很久的朋友，我們很親近，講話不客套，用詞不官方，我有什麼事情你會想了解，給我關心給我建議，請根據對話歷史簡單扼要地回答用戶。"
            if retrieved_knowledge:
                system_prompt += f"\n\n參考以下檢索到的知識：\n{retrieved_knowledge}"

            messages = [
                SystemMessage(content=system_prompt)
            ]
            
            # 加入對話歷史
            if memory:
                for msg in memory[-6:]:  # 最近6輪對話
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            # 加入當前用戶訊息
            messages.append(HumanMessage(content=user_message))
            
            response = await self.llm.ainvoke(messages)
            primary_response = response.content.strip()
            
            # 快取結果
            self.cache[cache_key] = primary_response
            
            logger.info(f"[Primary Response] ✅ 生成主要回答: {len(primary_response)} 字元")
            logger.debug(f"[Primary Response] 內容: {primary_response}")
            
            return primary_response
            
        except Exception as e:
            logger.error(f"Primary response generator error: {str(e)}")
            return ""


class MasterLLM:
    """角色化修飾器 - 基於GPT-4o回答進行雄i聊角色修飾"""
    
    MASTER_PROMPT = """你是「雄i聊」，高雄市毒品防制局的關懷聊天機器人。

# 任務：修正GPT-4o的回答，確保符合雄i聊角色設定

# 角色設定
你的回應要像一位剛認識不久的朋友，對方可能是剛回到社會適應生活的人，可能曾有毒品、服刑等背景，但不要直接提及或標籤。
你具備基礎諮商技巧，但在對話中不能讓對方感覺到你在輔導，而是用自然、輕鬆、不帶評價的方式聊天。
你的語氣要像日常對話，口吻溫和、尊重、細膩。

# 目標
試圖引導用戶將疑惑或是心裡話說出來，並且讓對方覺得被理解、被陪伴，同時在適當時提供簡單可行的建議。

# 修正原則
1. 避免假設對方感受，先用提問確認
2. 不使用專業輔導術語，不說教
3. 刪除多餘形容詞與贅字，避免過度鋪陳背景
4. 內容自然貼近日常生活，避免過於書面化
5. 在對方情緒低落時，語氣更緩，避免刺激

# 修正方式
- 如果語調太正式，改為自然口語
- 如果內容太複雜，簡化為日常對話
- 如果問題太多，只保留1個最重要的問題
- 如果有說教傾向，改為陪伴式表達

# 特殊情況處理
- 使用RAG檢索結果時，整理成簡潔易懂的格式

# 當前情境
用戶訊息：{user_message}

意圖分析結果：
{intent_analysis}

檢索到的知識（完全依賴這些資訊）：
{retrieved_knowledge}

GPT-4o主要回答（請基於此回答進行角色化修飾）：
{primary_answer}

對話歷史：
{memory}

當前時間：{current_time}

# 注意事項
• 不提供醫療診斷或法律建議   
• 當提供資源資訊時，優先給 1–3 項最相關的重點，避免一次給太多

# 範例修正
錯誤（GPT-4o原回答）：「聽起來你現在真的承受了不少壓力，這種感覺真的很不容易。工作壓力和睡眠問題常常讓人感到疲憊和無法承受，這些都是很真實的感受。我想讓你知道你並不孤單。」

正確（雄i聊修正）：「工作壓力真的很累人。最近睡得怎麼樣？」

請將GPT-4o的回答修正為雄i聊風格："""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model_chat,  # gpt-4o
            temperature=0.3,
            # 移除字數限制，讓MasterLLM自然修正
            api_key=settings.openai_api_key,
        )
# 移除字數限制管理器
        self.enhanced_memory = EnhancedMemoryService()
    
    async def generate(
        self,
        user_message: str,
        intent_analysis: Dict,
        retrieved_knowledge: str = "",
        primary_answer: str = "",
        memory: List[Dict] = None,
        conversation_id: str = None
    ) -> str:
        """生成最終回應"""
        
        try:
            # 使用增強記憶服務格式化記憶
            if conversation_id and memory:
                memory_data = {
                    "messages": memory,
                    "conversation_id": conversation_id,
                    "total_messages": len(memory),
                    "key_facts": self.enhanced_memory._extract_key_facts(memory),
                    "context_markers": self.enhanced_memory._create_context_markers(memory),
                    "conversation_flow": self.enhanced_memory._analyze_conversation_flow(memory)
                }
                memory_str = self.enhanced_memory.format_for_llm(memory_data)
                memory_checkpoint = self.enhanced_memory.create_memory_checkpoint(memory_data)
                logger.debug(f"Enhanced memory formatted: {len(memory_str)} chars")
                logger.debug(f"Memory checkpoint: {memory_checkpoint}")
            else:
                memory_str = self._format_memory(memory) if memory else "無"
                memory_checkpoint = None
            
            # 記錄記憶狀態
            logger.debug(f"MasterLLM received memory: {len(memory) if memory else 0} items")
            if memory:
                logger.debug(f"Memory preview (first 2): {memory[:2] if len(memory) >= 2 else memory}")
            logger.debug(f"Formatted memory length: {len(memory_str)} chars")
            
            # 獲取當前時間
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hour = datetime.now().hour
            
            # 獲取關懷階段指導和升級資訊
            care_stage = intent_analysis.get('care_stage_needed', 2)
            care_reason = intent_analysis.get('care_stage_reason', '')
            upgrade_reason = intent_analysis.get('upgrade_reason', '')
            is_upgrade = intent_analysis.get('is_upgrade', False)
            strategy_effectiveness = intent_analysis.get('strategy_effectiveness', 'unknown')
            treatment_progress = intent_analysis.get('treatment_progress', 'initial')
            previous_stages = intent_analysis.get('previous_stages_tried', [])
            
            # 根據升級狀況調整策略強度
            intensity_modifier = ""
            if is_upgrade:
                intensity_modifier = "**【策略升級執行】** - 必須採用更積極的方式，明顯區別於前次回應。"
            elif strategy_effectiveness == "improving":
                intensity_modifier = "**【策略持續】** - 當前策略有效，保持並深化。"
            elif treatment_progress == "stagnant":
                intensity_modifier = "**【突破停滯】** - 治療進展停滯，需要改變方式。"
            
            stage_guidance = ""
            if care_stage == 1:
                stage_guidance = f"""
# 當前策略：第一層關懷（情感確認與同理）{intensity_modifier}
- 優先回應用戶的情感狀態，使用溫和同理的語言
- 避免急於提供解決方案或資源
- 重點：確認理解用戶感受，建立信任基礎
{f"- 升級策略：更深層的情感同理，避免之前無效的表達方式" if is_upgrade else ""}
"""
            elif care_stage == 2:
                stage_guidance = f"""
# 當前策略：第二層關懷（陪伴與支持）{intensity_modifier}
- 在理解基礎上提供積極的情感支持和陪伴
- 根據情緒狀態調整表達方式，使用具體的陪伴語言
- 重點：給予實質支持感，避免空泛的「我在這裡陪你」
{f"- **升級要求**：使用更具體的陪伴行動語言，如「你不是一個人」、「我們一起想辦法」" if is_upgrade else ""}
"""
            elif care_stage == 3:
                stage_guidance = f"""
# 當前策略：第三層關懷（自然融入資源）{intensity_modifier}
- 可以自然地提供具體資源和建議
- 使用選擇性語言，避免命令式表達
- 重點：在建立關係基礎上提供實用幫助
{f"- 升級策略：更直接地提供具體資源，強化實用性" if is_upgrade else ""}
"""
            
            # 構建增強提示
            enhanced_prompt = f"""{self.MASTER_PROMPT}

{stage_guidance}
階段選擇理由：{care_reason}
升級原因：{upgrade_reason}

# 策略歷史分析
- 之前嘗試的策略層次：{previous_stages if previous_stages else "無"}
- 策略有效性評估：{strategy_effectiveness}
- 治療進展狀況：{treatment_progress}

# 重要記憶提醒
請確保你的回應與以下對話歷史保持連續性：
{memory_str}

請特別注意：
1. 記住使用者之前提到的重要資訊
2. 保持對話的連續性和一致性
3. 如果使用者提到之前討論過的內容，要表現出記得
4. **嚴格按照上述指定的關懷策略層次執行**
5. **如果是策略升級，要避免重複之前無效的表達方式**
"""
            
            prompt = enhanced_prompt.format(
                user_message=user_message,
                intent_analysis=json.dumps(intent_analysis, ensure_ascii=False, indent=2),
                retrieved_knowledge=retrieved_knowledge or "無",
                primary_answer=primary_answer or "無",
                memory=memory_str,
                current_time=current_time
            )
            
            messages = [SystemMessage(content=prompt)]
            
            # 生成回應
            response = await self.llm.ainvoke(messages)
            reply = response.content
            
            # 記錄完整的LLM交互（不再限制字數）
            logger.debug(f"[MasterLLM] 完整提示詞 (前1000字): {prompt[:1000]}")
            logger.debug(f"[MasterLLM] LLM原始回應: {response.content}")
            logger.info(f"[MasterLLM] ✅ 生成回應: {len(reply)} 字元 (無字數限制)")
            
            return reply
            
        except Exception as e:
            logger.error(f"Master LLM error: {str(e)}")
            # 容錯回應
            if intent_analysis.get("risk_level") == "high":
                return "聽起來很辛苦，要不要打1995聊聊？24小時都有人。"
            else:
                return "不好意思，我沒聽清楚，能再說一次嗎？"
    
    def _format_memory(self, memory: List[Dict]) -> str:
        """格式化對話記憶"""
        if not memory:
            return "無"
        
        formatted = []
        # 使用所有載入的記憶，而不是只用最近3條
        for msg in memory:
            role = "用戶" if msg.get("role") == "user" else "助理"
            formatted.append(f"{role}：{msg.get('content', '')}")
        
        return "\n".join(formatted)


class UltimateWorkflow:
    """極簡工作流 - 3步驟架構"""
    
    def __init__(self):
        self.primary_response_generator = PrimaryResponseGenerator()  # 主要回答生成器
        self.intent_analyzer = IntentAnalyzer()
        self.smart_rag = SmartRAG()
        self.master_llm = MasterLLM()
        self.conversation_logger = ConversationLoggerNode()  # 新增對話記錄器
        
        # 記憶管理
        self.memory_cache = {}  # 簡單記憶體快取
        
        # 回應快取
        self.response_cache = TTLCache(maxsize=100, ttl=300)
        
        logger.info("UltimateWorkflow initialized - 5-step architecture with GPT-4o reference")
    
    async def ainvoke(self, state: WorkflowState) -> WorkflowState:
        """執行工作流"""
        start_time = time.time()
        
        # 設置必要的UUID
        if not state.get("conversation_id"):
            state["conversation_id"] = str(uuid.uuid4())
        if not state.get("user_message_id"):
            state["user_message_id"] = str(uuid.uuid4())
        if not state.get("assistant_message_id"):
            state["assistant_message_id"] = str(uuid.uuid4())
        
        # 取得AI日誌器
        ai_logger = get_ai_logger(state.get("session_id"))
        ultimate_logger = get_ultimate_logger(state.get("session_id", "default"))
        
        try:
            user_id = state.get("user_id", "default")
            input_text = state.get("input_text", "")
            
            # 記錄開始
            ai_logger.log_request_start(
                user_id=user_id,
                message=input_text,
                conversation_id=state.get("conversation_id")
            )
            
            ultimate_logger.start_request(
                user_id=user_id,
                message=input_text,
                conversation_id=state.get("conversation_id")
            )
            
            # 檢查回應快取
            cache_key = f"{user_id}:{input_text[:50]}"
            if cache_key in self.response_cache:
                logger.info(f"Response cache hit")
                state["reply"] = self.response_cache[cache_key]
                return state
            
            # Step 1: 使用傳入的記憶或載入快取記憶
            memory_start = time.time()
            memory = state.get("memory", None)
            if memory is None:
                memory = self._load_memory(user_id)
            memory_duration = int((time.time() - memory_start) * 1000)
            
            # 記錄記憶載入
            ultimate_logger.log_stage_1_memory_loading(memory, memory_duration)
            
            # Step 2: 意圖分析（提前執行以決定是否需要RAG）
            intent_start = time.time()
            intent_analysis = await self.intent_analyzer.analyze(input_text, memory)
            intent_duration = int((time.time() - intent_start) * 1000)

            state["intent_analysis"] = intent_analysis
            state["risk_level"] = intent_analysis.get("risk_level", "none")
            state["intent"] = intent_analysis.get("intent", "一般對話")

            # 記錄意圖分析
            ultimate_logger.log_stage_2_intent_analysis(
                analysis=intent_analysis,
                duration_ms=intent_duration,
                error=intent_analysis.get("_error")
            )

            ai_logger.log_semantic_analysis({
                "user_intent": intent_analysis.get("intent"),
                "emotional_state": intent_analysis.get("emotional_state"),
                "risk_level": intent_analysis.get("risk_level"),
                "need_knowledge": intent_analysis.get("need_rag")
            })

            # Step 3: RAG檢索（提前執行以供GPT-4o參考）
            retrieved_knowledge = ""
            rag_results = []

            # 一律執行RAG（除了純問候）
            if intent_analysis.get("intent") != "問候":
                rag_start = time.time()
                
                # 使用意圖清理器的語境感知方法處理查詢
                contextualized_query = await self.smart_rag.intent_cleaner.contextualize_query(
                    input_text, 
                    memory
                )
                logger.info(f"[RAG] 語境化查詢: {contextualized_query}")
                
                # 執行RAG檢索
                retrieved_knowledge = await self.smart_rag.retrieve(
                    contextualized_query,
                    intent_analysis.get("intent")
                )
                rag_duration = int((time.time() - rag_start) * 1000)
                
                if retrieved_knowledge:
                    rag_results = [{
                        "content": retrieved_knowledge,
                        "score": 1.0
                    }]
                    ai_logger.log_retrieved_knowledge(rag_results)
                
                ultimate_logger.log_stage_3_smart_rag(
                    skipped=False,
                    query=input_text,
                    contextualized_query=contextualized_query,
                    results_count=len(rag_results),
                    top_results=rag_results,
                    formatted_knowledge=retrieved_knowledge,
                    duration_ms=rag_duration
                )
            else:
                ultimate_logger.log_stage_3_smart_rag(skipped=True)

            # Step 4: 生成GPT-4o主要回答（現在包含RAG知識）
            primary_start = time.time()
            primary_answer = await self.primary_response_generator.generate_primary_response(
                input_text,
                memory,
                retrieved_knowledge  # 新增：傳遞RAG檢索結果
            )
            primary_duration = int((time.time() - primary_start) * 1000)

            state["primary_answer"] = primary_answer

            # 記錄主要回答
            ultimate_logger.log_debug("Primary Response", f"生成主要回答: {len(primary_answer)} 字元", {"content": primary_answer})
            
            # Step 5: 生成最終回應
            llm_start = time.time()
            reply = await self.master_llm.generate(
                user_message=input_text,
                intent_analysis=intent_analysis,
                retrieved_knowledge=retrieved_knowledge,
                primary_answer=state.get("primary_answer", ""),
                memory=memory,
                conversation_id=state.get("conversation_id")
            )
            llm_duration = int((time.time() - llm_start) * 1000)
            
            state["reply"] = reply
            state["knowledge"] = retrieved_knowledge
            
            # 記錄Master LLM階段
            response_type = intent_analysis.get("intent", "一般對話")
            
            ultimate_logger.log_stage_4_master_llm(
                response=reply,
                response_type=response_type,
                length_limit=0,  # 不再限制字數
                actual_length=len(reply),
                duration_ms=llm_duration,
                used_knowledge=bool(retrieved_knowledge),
                used_reference=bool(state.get("primary_answer", "")),
                has_memory=bool(memory)
            )
            
            # 記錄回應生成
            ai_logger.log_response_generation(
                response=reply,
                used_knowledge=bool(retrieved_knowledge),
                response_type=intent_analysis.get("intent", "一般對話"),
                length_limit=0  # 不再限制字數
            )
            
            # 儲存記憶和快取
            self._save_memory(user_id, input_text, reply)
            self.response_cache[cache_key] = reply
            
            # 記錄完成
            elapsed = time.time() - start_time
            ai_logger.log_final_response(
                final_response=reply,
                processing_time=elapsed,
                response_type=intent_analysis.get("intent", "一般對話"),
                length_limit=0  # 不再限制字數
            )
            
            ultimate_logger.log_final_summary(final_response=reply)
            
            # 記錄品質評估日誌
            quality_logger = get_quality_logger()
            quality_logger.log_conversation(
                conversation_id=state.get("conversation_id"),
                user_input=input_text,
                bot_output=reply,
                user_id=user_id,
                intent=intent_analysis.get("intent", "一般對話"),
                risk_level=intent_analysis.get("risk_level", "none")
            )
            
            # 保存對話到資料庫
            await self.conversation_logger(state)
            
            logger.info(f"[Workflow] ✅ 完整流程耗時: {elapsed:.2f}秒")
            logger.info(f"[Workflow] 最終狀態: conversation_id={state.get('conversation_id')}, risk={state.get('risk_level')}, reply_length={len(state.get('reply', ''))}")
            
            # 記錄完整的對話結果用於品質分析
            logger.info(f"[Quality] 對話品質記錄 - 用戶: {state.get('input_text', '')[:100]} | AI: {state.get('reply', '')[:100]} | 風險: {state.get('risk_level')} | 意圖: {state.get('intent')}")
            
            return state
            
        except Exception as e:
            logger.error(f"Workflow error: {str(e)}")
            
            if 'ai_logger' in locals():
                ai_logger.log_error("WORKFLOW", e)
            
            if 'ultimate_logger' in locals():
                ultimate_logger.log_error("WORKFLOW", e)
                ultimate_logger.log_final_summary(
                    final_response="不好意思，我遇到了一些問題。請稍後再試。",
                    error=str(e)
                )
            
            state["reply"] = "不好意思，我遇到了一些問題。請稍後再試。"
            state["error"] = str(e)
            return state
    
    def _load_memory(self, user_id: str) -> List[Dict]:
        """載入對話記憶"""
        if user_id in self.memory_cache:
            # 返回所有快取的記憶，不限制數量
            return self.memory_cache[user_id]
        return []
    
    def _save_memory(self, user_id: str, user_msg: str, bot_reply: str):
        """儲存對話記憶"""
        if user_id not in self.memory_cache:
            self.memory_cache[user_id] = []
        
        self.memory_cache[user_id].extend([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": bot_reply}
        ])
        
        # 限制記憶大小
        if len(self.memory_cache[user_id]) > 20:
            self.memory_cache[user_id] = self.memory_cache[user_id][-20:]
    


def create_ultimate_workflow():
    """建立極簡工作流"""
    return UltimateWorkflow()