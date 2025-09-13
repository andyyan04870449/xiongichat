"""品質評估專用日誌記錄器 - 只記錄對話ID、輸入、輸出"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import threading

class QualityLogger:
    """品質評估日誌記錄器
    
    只記錄必要資訊供品質評分使用：
    - 對話ID
    - 用戶輸入
    - 系統輸出
    - 時間戳記
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # 設置日誌目錄
        self.log_dir = Path(os.getenv("LOG_PATH", "logs")) / "quality_assessment"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 按日期分檔
        self.today = datetime.now().strftime("%Y%m%d")
        self.log_file = self.log_dir / f"quality_{self.today}.jsonl"
        
        self._initialized = True
    
    def log_conversation(self, 
                        conversation_id: str,
                        user_input: str,
                        bot_output: str,
                        user_id: Optional[str] = None,
                        intent: Optional[str] = None,
                        risk_level: Optional[str] = None):
        """記錄一次對話交互
        
        Args:
            conversation_id: 對話ID
            user_input: 用戶輸入
            bot_output: 機器人輸出
            user_id: 用戶ID（可選）
            intent: 識別的意圖（可選）
            risk_level: 風險等級（可選）
        """
        
        # 檢查是否需要切換到新的日期檔案
        current_date = datetime.now().strftime("%Y%m%d")
        if current_date != self.today:
            self.today = current_date
            self.log_file = self.log_dir / f"quality_{self.today}.jsonl"
        
        # 準備日誌資料
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id,
            "user_input": user_input,
            "bot_output": bot_output,
            "output_length": len(bot_output),
            "user_id": user_id,
            "intent": intent,
            "risk_level": risk_level
        }
        
        # 寫入JSONL格式（每行一個JSON物件）
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Quality logger error: {str(e)}")
    
    def get_today_logs(self):
        """讀取今天的所有日誌"""
        if not self.log_file.exists():
            return []
        
        logs = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
        except Exception as e:
            print(f"Error reading quality logs: {str(e)}")
        
        return logs
    
    def export_for_evaluation(self, output_file: Optional[str] = None):
        """匯出資料供品質評估
        
        Args:
            output_file: 輸出檔案路徑，預設為quality_export_YYYYMMDD.csv
        """
        import csv
        
        if output_file is None:
            output_file = self.log_dir / f"quality_export_{self.today}.csv"
        
        logs = self.get_today_logs()
        
        if not logs:
            print("No logs to export")
            return
        
        # 寫入CSV格式
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'timestamp', 'conversation_id', 'user_input', 
                'bot_output', 'output_length', 'intent', 'risk_level'
            ])
            writer.writeheader()
            
            for log in logs:
                writer.writerow({
                    'timestamp': log.get('timestamp', ''),
                    'conversation_id': log.get('conversation_id', ''),
                    'user_input': log.get('user_input', ''),
                    'bot_output': log.get('bot_output', ''),
                    'output_length': log.get('output_length', 0),
                    'intent': log.get('intent', ''),
                    'risk_level': log.get('risk_level', '')
                })
        
        print(f"Exported {len(logs)} conversations to {output_file}")
        return output_file
    
    def get_statistics(self):
        """取得今日統計資料"""
        logs = self.get_today_logs()
        
        if not logs:
            return {
                "total_conversations": 0,
                "average_output_length": 0,
                "intents": {},
                "risk_levels": {}
            }
        
        # 計算統計
        total = len(logs)
        avg_length = sum(log.get('output_length', 0) for log in logs) / total
        
        # 統計意圖分布
        intents = {}
        for log in logs:
            intent = log.get('intent', 'unknown')
            intents[intent] = intents.get(intent, 0) + 1
        
        # 統計風險等級分布
        risk_levels = {}
        for log in logs:
            risk = log.get('risk_level', 'none')
            risk_levels[risk] = risk_levels.get(risk, 0) + 1
        
        return {
            "total_conversations": total,
            "average_output_length": round(avg_length, 1),
            "intents": intents,
            "risk_levels": risk_levels,
            "log_file": str(self.log_file)
        }


# 全域實例
_quality_logger = None

def get_quality_logger() -> QualityLogger:
    """取得品質日誌記錄器的單例實例"""
    global _quality_logger
    if _quality_logger is None:
        _quality_logger = QualityLogger()
    return _quality_logger