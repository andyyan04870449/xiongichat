"""AI 聊天流程監控日誌系統"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import os

# 建立專門的 AI 分析日誌目錄
LOG_DIR = Path(os.getenv("LOG_PATH", "logs")) / "ai_analysis"
LOG_DIR.mkdir(parents=True, exist_ok=True)


class AIAnalysisLogger:
    """AI 分析流程專用日誌器"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger = self._setup_logger()
        self.stage_timings = {}  # 記錄每個階段的耗時
        self.current_stage_start = None
        self.workflow_start_time = None
        
    def _setup_logger(self):
        """設定獨立的 AI 分析日誌器"""
        logger_name = f"ai_analysis_{self.session_id}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # 清除既有的 handlers
        logger.handlers = []
        
        # 建立詳細日誌檔案 (JSON 格式)
        json_handler = logging.FileHandler(
            LOG_DIR / f"ai_analysis_{datetime.now().strftime('%Y%m%d')}.jsonl",
            encoding='utf-8'
        )
        json_handler.setLevel(logging.DEBUG)
        json_formatter = JsonFormatter()
        json_handler.setFormatter(json_formatter)
        logger.addHandler(json_handler)
        
        # 建立人類可讀的日誌檔案
        readable_handler = logging.FileHandler(
            LOG_DIR / f"ai_analysis_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        readable_handler.setLevel(logging.INFO)
        readable_formatter = ReadableFormatter()
        readable_handler.setFormatter(readable_formatter)
        logger.addHandler(readable_handler)
        
        return logger
    
    def log_request_start(self, user_id: str, message: str, conversation_id: str = None):
        """記錄請求開始"""
        self.workflow_start_time = datetime.now()
        self.current_stage_start = datetime.now()
        self.logger.info("🚀 === AI CHAT REQUEST START ===", extra={
            "stage": "REQUEST_START",
            "user_id": user_id,
            "user_message": message,
            "conversation_id": conversation_id,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_memory_loaded(self, memory: list):
        """記錄載入的對話記憶"""
        timing = self._record_stage_timing("MEMORY_LOADING")
        self.logger.info("📚 Memory Loaded", extra={
            "stage": "MEMORY_LOADED",
            "memory_count": len(memory),
            "recent_messages": memory[-4:] if memory else [],
            "session_id": self.session_id,
            "stage_time_ms": timing
        })
    
    def log_context_understanding(self, understanding: Dict[str, Any]):
        """記錄對話理解結果"""
        timing = self._record_stage_timing("CONTEXT_UNDERSTANDING")
        self.logger.info("🧠 Context Understanding Complete", extra={
            "stage": "CONTEXT_UNDERSTANDING",
            "entities": understanding.get("entities", {}),
            "pronouns": understanding.get("pronouns_resolution", {}),
            "user_intent": understanding.get("user_intent", {}),
            "search_strategy": understanding.get("search_strategy", {}),
            "confidence": understanding.get("confidence_score", 0),
            "enhanced_query": understanding.get("search_strategy", {}).get("search_query", ""),
            "session_id": self.session_id,
            "stage_time_ms": timing
        })
    
    def log_semantic_analysis(self, analysis: Dict[str, Any]):
        """記錄語意分析結果"""
        timing = self._record_stage_timing("SEMANTIC_ANALYSIS")
        self.logger.info("💭 Semantic Analysis Complete", extra={
            "stage": "SEMANTIC_ANALYSIS",
            "mentioned_substances": analysis.get("mentioned_substances", []),
            "user_intent": analysis.get("user_intent", ""),
            "emotional_state": analysis.get("emotional_state", ""),
            "crisis_assessment": analysis.get("crisis_assessment", {}),
            "risk_indicators": analysis.get("risk_indicators", []),
            "needs_support": analysis.get("needs_support", False),
            "session_id": self.session_id,
            "stage_time_ms": timing
        })
    
    def log_drug_safety_check(self, is_safe: bool, warnings: list = None):
        """記錄毒品安全檢查"""
        timing = self._record_stage_timing("DRUG_SAFETY_CHECK")
        self.logger.info("🔒 Drug Safety Check", extra={
            "stage": "DRUG_SAFETY_CHECK",
            "is_safe": is_safe,
            "warnings": warnings or [],
            "session_id": self.session_id,
            "stage_time_ms": timing
        })
    
    def log_intent_routing(self, need_knowledge: bool, category: str):
        """記錄意圖路由決策"""
        timing = self._record_stage_timing("INTENT_ROUTING")
        self.logger.info("🔀 Intent Routing Decision", extra={
            "stage": "INTENT_ROUTING",
            "need_knowledge": need_knowledge,
            "category": category,
            "session_id": self.session_id,
            "stage_time_ms": timing
        })
    
    def log_rag_retrieval(self, query: str, filters: Dict, results_count: int, 
                         similarity_threshold: float):
        """記錄 RAG 檢索過程"""
        timing = self._record_stage_timing("RAG_RETRIEVAL")
        self.logger.info("🔍 RAG Retrieval", extra={
            "stage": "RAG_RETRIEVAL",
            "query": query,
            "filters": filters,
            "similarity_threshold": similarity_threshold,
            "results_count": results_count,
            "session_id": self.session_id,
            "stage_time_ms": timing
        })
    
    def log_retrieved_knowledge(self, knowledge: list):
        """記錄檢索到的知識"""
        for idx, item in enumerate(knowledge[:3]):  # 只記錄前3筆
            self.logger.debug(f"📖 Retrieved Knowledge #{idx+1}", extra={
                "stage": "RETRIEVED_KNOWLEDGE",
                "index": idx,
                "title": item.get("title", ""),
                "category": item.get("category", ""),
                "similarity_score": item.get("similarity_score", 0),
                "content_preview": item.get("content", "")[:200],
                "session_id": self.session_id
            })
    
    def log_response_generation(self, response: str, used_knowledge: bool):
        """記錄回應生成"""
        timing = self._record_stage_timing("RESPONSE_GENERATION")
        self.logger.info("✍️ Response Generated", extra={
            "stage": "RESPONSE_GENERATION",
            "response": response,
            "used_knowledge": used_knowledge,
            "response_length": len(response),
            "session_id": self.session_id,
            "stage_time_ms": timing
        })
    
    def log_response_validation(self, is_valid: bool, severity: str = None, 
                               modifications: str = None):
        """記錄回應驗證結果"""
        timing = self._record_stage_timing("RESPONSE_VALIDATION")
        self.logger.info("✅ Response Validation", extra={
            "stage": "RESPONSE_VALIDATION",
            "is_valid": is_valid,
            "severity": severity,
            "modifications": modifications,
            "session_id": self.session_id,
            "stage_time_ms": timing
        })
    
    def log_final_response(self, final_response: str, processing_time: float):
        """記錄最終回應"""
        self.logger.info("🎯 === FINAL RESPONSE ===", extra={
            "stage": "FINAL_RESPONSE",
            "response": final_response,
            "processing_time_seconds": processing_time,
            "stage_timings": self.stage_timings,
            "total_stages": len(self.stage_timings),
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        })
    
    def _record_stage_timing(self, stage_name: str) -> float:
        """記錄階段耗時並返回毫秒數"""
        if self.current_stage_start:
            elapsed = (datetime.now() - self.current_stage_start).total_seconds() * 1000
            self.stage_timings[stage_name] = round(elapsed, 2)
            self.current_stage_start = datetime.now()
            return elapsed
        self.current_stage_start = datetime.now()
        return 0
    
    def log_crisis_assessment(self, crisis_level: str, indicators: list, intervention_needed: bool):
        """記錄危機評估結果"""
        timing = self._record_stage_timing("CRISIS_ASSESSMENT") if self.current_stage_start else 0
        self.logger.info(f"🚨 Crisis Assessment: {crisis_level}", extra={
            "stage": "CRISIS_ASSESSMENT",
            "crisis_level": crisis_level,
            "crisis_indicators": indicators,
            "intervention_needed": intervention_needed,
            "session_id": self.session_id,
            "stage_time_ms": timing
        })
    
    def log_error(self, stage: str, error: Exception):
        """記錄錯誤"""
        timing = self._record_stage_timing(f"ERROR_{stage}") if self.current_stage_start else 0
        self.logger.error(f"❌ Error in {stage}", extra={
            "stage": f"ERROR_{stage}",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "session_id": self.session_id,
            "stage_time_ms": timing
        }, exc_info=True)
    
    def log_routing_decision(self, complexity: str, confidence: float, factors: Dict = None):
        """記錄路由決策（優化版本）"""
        timing = self._record_stage_timing("ROUTING")
        self.logger.info(f"🔀 Routing Decision: {complexity} (confidence: {confidence:.2f})", extra={
            "stage": "ROUTING_DECISION",
            "complexity": complexity,
            "confidence": confidence,
            "memory_factors": factors.get("memory_factors") if factors else {},
            "risk_signals": factors.get("risk_signals") if factors else {},
            "content_analysis": factors.get("content_analysis") if factors else {},
            "session_id": self.session_id,
            "stage_time_ms": timing
        })
    
    def log_combined_analysis(self, analysis: Dict[str, Any]):
        """記錄合併分析結果（優化版本）"""
        timing = self._record_stage_timing("COMBINED_ANALYSIS")
        self.logger.info(f"🔍 Combined Analysis Completed", extra={
            "stage": "COMBINED_ANALYSIS",
            "semantic": analysis.get("semantic_analysis", {}),
            "context": analysis.get("context_understanding", {}),
            "crisis_assessment": analysis.get("crisis_assessment", {}),
            "need_knowledge": analysis.get("need_knowledge", False),
            "intent_category": analysis.get("intent_category", ""),
            "session_id": self.session_id,
            "stage_time_ms": timing
        })


class JsonFormatter(logging.Formatter):
    """JSON 格式化器"""
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        # 加入 extra 資料
        if hasattr(record, 'stage'):
            log_obj.update({
                k: getattr(record, k) 
                for k in dir(record) 
                if not k.startswith('_') and k not in [
                    'name', 'msg', 'args', 'created', 'filename', 
                    'funcName', 'levelname', 'levelno', 'lineno',
                    'module', 'msecs', 'message', 'pathname', 'process',
                    'processName', 'relativeCreated', 'thread', 'threadName',
                    'getMessage', 'stack_info', 'exc_info', 'exc_text'
                ]
            })
        
        return json.dumps(log_obj, ensure_ascii=False)


class ReadableFormatter(logging.Formatter):
    """人類可讀格式化器"""
    
    def format(self, record):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 根據 stage 產生易讀的訊息
        if hasattr(record, 'stage'):
            stage = record.stage
            
            # 加入耗時資訊
            timing_info = f" [{record.stage_time_ms:.0f}ms]" if hasattr(record, 'stage_time_ms') else ""
            
            if stage == "REQUEST_START":
                return f"\n{'='*80}\n[{timestamp}] 🚀 新對話請求\n用戶: {record.user_id}\n訊息: {record.user_message}\n對話ID: {record.conversation_id}\n"
            
            elif stage == "MEMORY_LOADED":
                return f"[{timestamp}] 📚 記憶載入{timing_info}\n數量: {record.memory_count} 條歷史對話\n"
            
            elif stage == "ROUTING_DECISION":
                risk = "🔴" if hasattr(record, 'risk_signals') and any(record.risk_signals.values()) else "🟢"
                return f"[{timestamp}] 🔀 路由決策{timing_info}: {record.complexity} (信心度: {record.confidence:.2f}) {risk}\n"
            
            elif stage == "COMBINED_ANALYSIS":
                crisis = getattr(record, 'crisis_assessment', {})
                crisis_level = crisis.get('crisis_level', 'none') if crisis else 'none'
                crisis_icon = {"none": "✅", "low": "🟡", "medium": "🟠", "high": "🔴"}.get(crisis_level, "❓")
                return f"[{timestamp}] 🔍 合併分析{timing_info}\n危機等級: {crisis_icon} {crisis_level}\n需要知識: {'是' if record.need_knowledge else '否'}\n"
            
            elif stage == "CONTEXT_UNDERSTANDING":
                entities = json.dumps(record.entities, ensure_ascii=False)
                return f"[{timestamp}] 🧠 對話理解{timing_info}\n主要實體: {entities}\n意圖: {record.user_intent}\n增強查詢: {record.enhanced_query}\n信心度: {record.confidence:.2f}\n"
            
            elif stage == "SEMANTIC_ANALYSIS":
                crisis = getattr(record, 'crisis_assessment', {})
                crisis_level = crisis.get('crisis_level', 'none') if crisis else 'none'
                return f"[{timestamp}] 💭 語意分析{timing_info}\n情緒: {record.emotional_state}\n意圖: {record.user_intent}\n危機: {crisis_level}\n"
            
            elif stage == "DRUG_SAFETY_CHECK":
                safety = "✅ 安全" if record.is_safe else "⚠️ 風險"
                return f"[{timestamp}] 🔒 毒品檢查{timing_info}: {safety}\n"
            
            elif stage == "INTENT_ROUTING":
                return f"[{timestamp}] 🔀 意圖路由{timing_info}\n需要知識: {'是' if record.need_knowledge else '否'}\n類別: {record.category}\n"
            
            elif stage == "CRISIS_ASSESSMENT":
                icon = {"none": "✅", "low": "🟡", "medium": "🟠", "high": "🔴"}.get(record.crisis_level, "❓")
                return f"[{timestamp}] 🚨 危機評估{timing_info}: {icon} {record.crisis_level}\n介入: {'需要' if record.intervention_needed else '不需要'}\n"
            
            elif stage == "RAG_RETRIEVAL":
                return f"[{timestamp}] 🔍 知識檢索{timing_info}\n查詢: {record.query}\n結果: {record.results_count} 筆\n"
            
            elif stage == "RESPONSE_GENERATION":
                return f"[{timestamp}] ✍️ 生成回應{timing_info}\n使用知識: {'是' if record.used_knowledge else '否'}\n長度: {record.response_length} 字\n"
            
            elif stage == "RESPONSE_VALIDATION":
                status = "✅ 通過" if record.is_valid else f"⚠️ 修改 ({record.severity})"
                return f"[{timestamp}] ✅ 回應驗證{timing_info}: {status}\n"
            
            elif stage == "FINAL_RESPONSE":
                # 顯示各階段耗時統計
                stage_summary = ""
                if hasattr(record, 'stage_timings') and record.stage_timings:
                    stage_summary = "\n📊 階段耗時:\n"
                    for stage_name, time_ms in record.stage_timings.items():
                        stage_summary += f"  - {stage_name}: {time_ms:.0f}ms\n"
                    total_tracked = sum(record.stage_timings.values())
                    stage_summary += f"  - 總計: {total_tracked:.0f}ms\n"
                
                return f"[{timestamp}] 🎯 最終回應\n{record.response}\n{stage_summary}總處理時間: {record.processing_time_seconds:.2f}秒\n{'='*80}\n"
            
            elif stage.startswith("ERROR"):
                return f"[{timestamp}] ❌ 錯誤{timing_info} ({record.error_type})\n階段: {stage}\n訊息: {record.error_message}\n"
        
        return f"[{timestamp}] {record.getMessage()}"


# 全域 logger 實例
_global_logger: Optional[AIAnalysisLogger] = None


def get_ai_logger(session_id: str = None) -> AIAnalysisLogger:
    """取得或建立 AI 分析日誌器"""
    global _global_logger
    if _global_logger is None or session_id:
        _global_logger = AIAnalysisLogger(session_id)
    return _global_logger


def reset_ai_logger():
    """重設全域日誌器"""
    global _global_logger
    _global_logger = None