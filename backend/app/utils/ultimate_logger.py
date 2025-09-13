"""UltimateWorkflow 專用的日誌記錄器"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import os

class UltimateLogger:
    """極簡工作流的專用日誌記錄器
    
    記錄3個階段的詳細資訊：
    1. IntentAnalyzer - 意圖分析
    2. SmartRAG - 智能檢索（條件性）
    3. MasterLLM - 最終生成
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = None
        self.stage_times = {}
        self.log_data = {}
        
        # 設置日誌目錄
        log_dir = Path(os.getenv("LOG_PATH", "logs")) / "ultimate_workflow"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 按日期分檔
        today = datetime.now().strftime("%Y%m%d")
        self.log_file = log_dir / f"ultimate_{today}.log"
        
        # 配置logger
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger_name = f"ultimate_{self.session_id}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # 防止重複handler
        if logger.handlers:
            return logger
        
        # 文件handler
        handler = logging.FileHandler(self.log_file, encoding='utf-8')
        handler.setLevel(logging.DEBUG)
        
        # 格式化器 - 使用簡潔格式
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    def start_request(self, user_id: str, message: str, conversation_id: Optional[str] = None):
        """記錄請求開始"""
        self.start_time = time.time()
        self.log_data = {
            "session_id": self.session_id,
            "user_id": user_id,
            "message": message,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 記錄請求開始
        self.logger.info("="*80)
        self.logger.info(f"[{self.log_data['timestamp']}] 🚀 UltimateWorkflow 新請求 (5步驟)")
        self.logger.info(f"Session: {self.session_id}")
        self.logger.info(f"用戶: {user_id}")
        self.logger.info(f"訊息: {message}")
        if conversation_id:
            self.logger.info(f"對話: {conversation_id}")
        self.logger.info("")
    
    def log_stage_1_memory_loading(self, memory: List[Dict], duration_ms: int):
        """記錄階段1: 記憶載入"""
        self.stage_times["memory_loading"] = duration_ms
        
        self.logger.info(f"📚 階段1: 記憶載入 [{duration_ms}ms]")
        self.logger.info(f"  記憶條數: {len(memory)}")
        if memory:
            recent = memory[-2:] if len(memory) >= 2 else memory
            for i, msg in enumerate(recent, 1):
                role = "👤用戶" if msg.get("role") == "user" else "🤖助理"
                content = msg.get("content", "")[:50]
                self.logger.info(f"  {role}: {content}{'...' if len(msg.get('content', '')) > 50 else ''}")
        self.logger.info("")
    
    def log_stage_2_reference_answer(self, reference: str, duration_ms: int):
        """記錄階段2: GPT-4o參考回答"""
        self.stage_times["reference_answer"] = duration_ms
        
        self.logger.info(f"🧠 階段2: GPT-4o參考回答 [{duration_ms}ms]")
        self.logger.info(f"  系統提示: 簡單扼要地回答我就好")
        if reference:
            self.logger.info(f"  參考回答: {reference}")
        else:
            self.logger.info(f"  ⚠️ 未獲得參考回答")
        self.logger.info("")
    
    def log_stage_3_intent_analysis(self, 
                                   analysis: Dict[str, Any],
                                   duration_ms: int,
                                   raw_response: Optional[str] = None,
                                   error: Optional[str] = None):
        """記錄階段3: IntentAnalyzer"""
        self.stage_times["intent_analysis"] = duration_ms
        
        self.logger.info(f"📊 階段3: 意圖分析 [{duration_ms}ms]")
        
        if error:
            self.logger.info(f"  ❌ 錯誤: {error}")
            self.logger.info(f"  🔄 使用備用關鍵詞檢測")
        
        if analysis:
            self.logger.info(f"  意圖: {analysis.get('intent', 'unknown')}")
            self.logger.info(f"  風險: {analysis.get('risk_level', 'low')}")
            self.logger.info(f"  情緒: {analysis.get('emotional_state', 'neutral')}")
            self.logger.info(f"  需要RAG: {analysis.get('need_rag', False)}")
            self.logger.info(f"  緊急程度: {analysis.get('urgency', 'normal')}")
            
            # 新增關懷階段記錄
            if 'care_stage_needed' in analysis:
                care_stage = analysis.get('care_stage_needed', 1)
                is_upgrade = analysis.get('is_upgrade', False)
                upgrade_indicator = " ⬆️ [升級]" if is_upgrade else ""
                
                self.logger.info(f"  關懷階段: 第{care_stage}層{upgrade_indicator}")
                if 'care_stage_reason' in analysis:
                    self.logger.info(f"  階段理由: {analysis.get('care_stage_reason', '')}")
                if 'upgrade_reason' in analysis:
                    self.logger.info(f"  升級原因: {analysis.get('upgrade_reason', '')}")
                
                # 策略歷史分析
                if 'previous_stages_tried' in analysis:
                    prev_stages = analysis.get('previous_stages_tried', [])
                    if prev_stages:
                        self.logger.info(f"  歷史策略: {prev_stages}")
                
                # 策略有效性
                effectiveness = analysis.get('strategy_effectiveness', 'unknown')
                progress = analysis.get('treatment_progress', 'initial')
                self.logger.info(f"  策略效果: {effectiveness} | 治療進展: {progress}")
            
            # 顯示實體資訊
            entities = analysis.get('entities', {})
            if entities:
                self.logger.info(f"  實體識別:")
                if entities.get('substances'):
                    self.logger.info(f"    物質: {entities['substances']}")
                if entities.get('locations'):
                    self.logger.info(f"    地點: {entities['locations']}")
                if entities.get('symptoms'):
                    self.logger.info(f"    症狀: {entities['symptoms']}")
        
        if raw_response and len(raw_response) < 500:
            self.logger.debug(f"  原始回應: {raw_response}")
        self.logger.info("")
    
    def log_stage_4_smart_rag(self,
                             skipped: bool = False,
                             query: Optional[str] = None,
                             contextualized_query: Optional[str] = None,
                             results_count: int = 0,
                             top_results: Optional[List[Dict]] = None,
                             formatted_knowledge: Optional[str] = None,
                             duration_ms: Optional[int] = None):
        """記錄階段4: SmartRAG（條件性）"""
        if skipped:
            self.logger.info("⏭️  階段4: RAG檢索 [跳過 - 純問候]")
            return
        
        self.stage_times["rag_retrieval"] = duration_ms
        
        self.logger.info(f"🔍 階段4: RAG檢索 [{duration_ms}ms]")
        if query != contextualized_query:
            self.logger.info(f"  原始查詢: {query}")
            self.logger.info(f"  語境化查詢: {contextualized_query}")
        else:
            self.logger.info(f"  查詢: {query}")
        self.logger.info(f"  檢索結果: {results_count} 筆")
        
        if top_results:
            self.logger.info("  相似度前3筆:")
            for i, result in enumerate(top_results[:3], 1):
                score = result.get('similarity_score', result.get('score', 0))
                content = result.get('content', '')[:80]
                category = result.get('category', 'unknown')
                self.logger.info(f"    {i}. [{category}] {score:.3f} - {content}...")
        
        if formatted_knowledge:
            self.logger.info(f"  格式化知識: {formatted_knowledge[:150]}...")
        else:
            self.logger.info("  ⚠️ 無有效檢索結果")
        self.logger.info("")
    
    def log_stage_5_master_llm(self,
                              response: str,
                              response_type: str,
                              length_limit: int,
                              actual_length: int,
                              duration_ms: int,
                              used_knowledge: bool = False,
                              used_reference: bool = False,
                              has_memory: bool = False,
                              prompt_tokens: Optional[int] = None,
                              completion_tokens: Optional[int] = None,
                              raw_response: Optional[str] = None):
        """記錄階段5: MasterLLM最終回應生成"""
        self.stage_times["master_llm"] = duration_ms
        
        self.logger.info(f"✨ 階段5: 最終回應生成 [{duration_ms}ms]")
        self.logger.info(f"  回應類型: {response_type}")
        
        # 資訊來源統計
        sources = []
        if has_memory:
            sources.append("記憶")
        if used_reference:
            sources.append("GPT-4o參考")
        if used_knowledge:
            sources.append("RAG知識")
        self.logger.info(f"  資訊來源: {' + '.join(sources) if sources else '無額外資訊'}")
        
        # 長度控制
        length_status = "✅" if actual_length <= length_limit else "⚠️超限"
        self.logger.info(f"  字數控制: {actual_length}/{length_limit} 字 {length_status}")
        
        if prompt_tokens and completion_tokens:
            total_tokens = prompt_tokens + completion_tokens
            self.logger.info(f"  Token消耗: {prompt_tokens}→{completion_tokens} (總計{total_tokens})")
        
        # 顯示原始回應和最終回應的差異
        if raw_response and raw_response != response:
            self.logger.info(f"  原始回應: {raw_response}")
            self.logger.info(f"  處理後回應: {response}")
        else:
            self.logger.info(f"  最終回應: {response}")
        
        self.logger.info("")
    
    def log_final_summary(self, final_response: str, error: Optional[str] = None):
        """記錄最終總結"""
        total_time = time.time() - self.start_time if self.start_time else 0
        
        self.logger.info("📈 UltimateWorkflow 處理總結")
        
        if error:
            self.logger.info(f"  ❌ 處理錯誤: {error}")
        
        # 5階段耗時分析
        stage_names = {
            "memory_loading": "記憶載入",
            "reference_answer": "GPT-4o參考",
            "intent_analysis": "意圖分析",
            "rag_retrieval": "RAG檢索",
            "master_llm": "最終生成"
        }
        
        self.logger.info("⏱️  5階段耗時分析:")
        total_stages_time = 0
        for stage_key, stage_name in stage_names.items():
            duration = self.stage_times.get(stage_key, 0)
            if duration > 0:
                percentage = (duration / (total_time * 1000)) * 100 if total_time > 0 else 0
                self.logger.info(f"  {stage_name}: {duration}ms ({percentage:.1f}%)")
                total_stages_time += duration
            else:
                self.logger.info(f"  {stage_name}: [跳過]")
        
        overhead = int((total_time * 1000) - total_stages_time)
        self.logger.info(f"  其他開銷: {overhead}ms")
        self.logger.info(f"  🎯 總處理時間: {total_time:.2f}秒")
        
        # 性能等級評估
        if total_time < 1.0:
            performance = "🚀 極速回應"
            grade = "S"
        elif total_time < 1.5:
            performance = "⚡ 快速回應" 
            grade = "A"
        elif total_time < 2.0:
            performance = "✅ 良好回應"
            grade = "B"
        elif total_time < 3.0:
            performance = "⚠️ 回應偏慢"
            grade = "C"
        else:
            performance = "❌ 回應過慢"
            grade = "D"
        
        self.logger.info(f"  性能等級: {grade}級 - {performance}")
        
        # 資源使用效率分析
        most_expensive = max(self.stage_times.items(), key=lambda x: x[1]) if self.stage_times else ("none", 0)
        if most_expensive[1] > 0:
            self.logger.info(f"  最耗時階段: {stage_names.get(most_expensive[0], most_expensive[0])} ({most_expensive[1]}ms)")
        
        # JSON格式記錄
        summary_data = {
            "session_id": self.session_id,
            "total_time_ms": int(total_time * 1000),
            "performance_grade": grade,
            "stages": self.stage_times,
            "success": error is None,
            "final_response": final_response,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.debug(f"JSON: {json.dumps(summary_data, ensure_ascii=False)}")
        self.logger.info("="*80)
        self.logger.info("")
    
    def log_debug(self, component: str, message: str, data: Optional[Dict] = None):
        """記錄除錯資訊"""
        self.logger.debug(f"🐛 [{component}] {message}")
        if data:
            self.logger.debug(f"   資料: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    def log_error(self, component: str, error: Exception):
        """記錄錯誤"""
        self.logger.error(f"❌ [{component}] 錯誤: {str(error)}")
        self.logger.error(f"   類型: {type(error).__name__}")
        
        import traceback
        tb = traceback.format_exc()
        for line in tb.split('\n'):
            if line.strip():
                self.logger.error(f"   {line}")


def get_ultimate_logger(session_id: str) -> UltimateLogger:
    """取得或建立UltimateLogger實例"""
    return UltimateLogger(session_id)