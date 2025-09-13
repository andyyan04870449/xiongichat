"""智能回應長度管理器"""

import re
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class ResponseLengthManager:
    """回應長度管理器 - 根據內容智能決定長度限制"""
    
    # 內容類型識別關鍵詞
    KEYWORDS = {
        "contact": ["電話", "聯絡", "地址", "號", "路", "07-", "1995", "@"],
        "institution": ["醫院", "中心", "機構", "協會", "基金會", "診所", "局"],
        "service": ["服務", "提供", "協助", "輔導", "治療", "諮詢", "戒癮"],
        "crisis": ["自殺", "想死", "活不下去", "結束生命"],
        "greeting": ["你好", "嗨", "早安", "午安", "晚安"],
        "emotion": ["難過", "傷心", "害怕", "擔心", "焦慮"]
    }
    
    # 分級長度限制
    LENGTH_LIMITS = {
        "greeting": 300,         # 問候：簡短
        "general": 400,          # 一般對話：標準
        "emotion": 450,          # 情緒支持：稍長
        "crisis": 500,           # 危機回應：確保資源清楚
        "contact": 600,          # 純聯絡資訊
        "service": 800,          # 服務說明
        "institution": 1000,     # 機構完整介紹
        "complex": 1200,         # 複雜查詢（多個資訊點）
    }
    
    @classmethod
    def analyze_content(cls, text: str) -> Dict[str, bool]:
        """分析文本內容類型"""
        result = {}
        for category, keywords in cls.KEYWORDS.items():
            result[f"has_{category}"] = any(kw in text for kw in keywords)
        return result
    
    @classmethod
    def get_limit(cls, text: str, intent: str = None, risk_level: str = None) -> int:
        """根據內容智能決定字數限制"""
        
        # 分析內容
        content = cls.analyze_content(text)
        
        # 優先級判斷
        if content.get("has_crisis") or risk_level == "high":
            return cls.LENGTH_LIMITS["crisis"]
        
        # 機構介紹（最長）
        if content.get("has_institution") and content.get("has_service"):
            return cls.LENGTH_LIMITS["institution"]
        
        # 服務說明
        if content.get("has_service"):
            return cls.LENGTH_LIMITS["service"]
        
        # 聯絡資訊
        if content.get("has_contact"):
            # 如果同時有多個聯絡資訊，需要更多空間
            contact_count = sum([
                text.count("電話"),
                text.count("地址"),
                text.count("@")
            ])
            if contact_count > 1:
                return cls.LENGTH_LIMITS["service"]  # 80字
            return cls.LENGTH_LIMITS["contact"]  # 60字
        
        # 問候
        if content.get("has_greeting") or intent == "問候":
            return cls.LENGTH_LIMITS["greeting"]
        
        # 情緒支持
        if content.get("has_emotion") or intent == "情緒支持":
            return cls.LENGTH_LIMITS["emotion"]
        
        # 預設
        return cls.LENGTH_LIMITS["general"]
    
    @classmethod
    def smart_truncate(cls, text: str, limit: int) -> str:
        """智能截斷 - 保留關鍵資訊"""
        
        if len(text) <= limit:
            return text
        
        # 提取關鍵資訊
        phones = re.findall(r'\d{2,4}-\d{4,8}|\d{4}', text)
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
        
        # 如果有聯絡資訊，優先保留
        if phones or emails:
            # 嘗試保留完整句子 + 聯絡資訊
            sentences = re.split(r'[。！？]', text)
            if sentences:
                # 保留第一句 + 聯絡資訊
                first_part = sentences[0]
                contact_info = []
                if phones:
                    contact_info.append(f"電話：{phones[0]}")
                if emails:
                    contact_info.append(f"信箱：{emails[0]}")
                
                result = f"{first_part[:limit-20]}。{' '.join(contact_info)}"
                if len(result) <= limit:
                    return result
        
        # 智能斷句
        # 優先在句號斷開
        if "。" in text[:limit]:
            cut_point = text.rfind("。", 0, limit) + 1
            return text[:cut_point]
        
        # 其次在逗號斷開
        if "，" in text[:limit]:
            cut_point = text.rfind("，", 0, limit)
            return text[:cut_point] + "。"
        
        # 最後強制截斷
        return text[:limit-3] + "..."
    
    @classmethod
    def format_response(cls, text: str, intent: str = None, risk_level: str = None) -> Tuple[str, int, str]:
        """格式化回應並返回處理結果
        
        Returns:
            Tuple[str, int, str]: (處理後文本, 使用的限制, 內容類型)
        """
        
        # 獲取限制
        limit = cls.get_limit(text, intent, risk_level)
        
        # 決定內容類型
        content = cls.analyze_content(text)
        if content.get("has_institution") and content.get("has_service"):
            content_type = "機構介紹"
        elif content.get("has_service"):
            content_type = "服務說明"
        elif content.get("has_contact"):
            content_type = "聯絡資訊"
        elif content.get("has_crisis"):
            content_type = "危機回應"
        elif content.get("has_greeting"):
            content_type = "問候"
        elif content.get("has_emotion"):
            content_type = "情緒支持"
        else:
            content_type = "一般對話"
        
        # 智能截斷
        result = cls.smart_truncate(text, limit)
        
        # 記錄
        if len(text) > limit:
            logger.info(f"[{content_type}] 截斷: {len(text)}字 -> {len(result)}字 (限制{limit})")
        else:
            logger.debug(f"[{content_type}] 未截斷: {len(text)}字 (限制{limit})")
        
        return result, limit, content_type


# 使用範例
if __name__ == "__main__":
    # 測試案例
    test_cases = [
        ("你好！", None, None),
        ("生命線電話是1995，24小時都可以打。", None, None),
        ("高雄市立凱旋醫院位於苓雅區凱旋二路130號，電話07-7513171，提供藥癮戒治、心理諮商等服務。", None, None),
        ("我覺得活不下去了", None, "high"),
        ("今天天氣真好", None, None),
    ]
    
    manager = ResponseLengthManager()
    
    for text, intent, risk in test_cases:
        result, limit, content_type = manager.format_response(text, intent, risk)
        print(f"\n原文({len(text)}字): {text}")
        print(f"類型: {content_type}, 限制: {limit}字")
        print(f"結果({len(result)}字): {result}")
        print("-" * 50)