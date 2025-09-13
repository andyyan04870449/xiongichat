"""
LLM 服務 - 使用 OpenAI GPT-4o-mini 進行資料辨識
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError
from app.config import settings

logger = logging.getLogger(__name__)


class ContactInfo(BaseModel):
    """聯絡人資訊模型"""
    name: str = Field(..., description="機構名稱")
    category: Optional[str] = Field(None, description="機構類別")
    phone: Optional[str] = Field(None, description="電話號碼")
    address: Optional[str] = Field(None, description="地址")
    services: Optional[str] = Field(None, description="服務項目")
    email: Optional[str] = Field(None, description="電子郵件")
    contact_person: Optional[str] = Field(None, description="聯絡人")
    notes: Optional[str] = Field(None, description="備註")


class LLMService:
    """LLM 服務類別"""
    
    def __init__(self):
        """初始化 LLM 服務"""
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        logger.info(f"LLMService initialized with model: {self.model}")
    
    async def extract_contacts_from_text(self, text: str) -> List[ContactInfo]:
        """
        從文字中提取聯絡人資訊
        
        Args:
            text: 原始文字內容
            
        Returns:
            List[ContactInfo]: 辨識出的聯絡人資訊列表
        """
        try:
            # 系統提示詞
            system_prompt = """你是一個專業的資料辨識助手，專門從非結構化文字中提取機構聯絡資訊。
你的任務是：
1. 仔細閱讀文字內容
2. 識別所有機構、組織或單位的聯絡資訊
3. 將資訊結構化為 JSON 格式

請注意：
- 確保提取所有可能的機構資訊
- 如果某個欄位找不到資訊，請設為 null
- 電話號碼請保持原始格式
- 地址儘可能完整
- 服務項目可以是多個，用逗號分隔
"""
            
            # 用戶提示詞
            user_prompt = f"""請從以下文字中辨識所有機構的聯絡資訊，並轉換為 JSON 格式。

必須包含的欄位：
- name: 機構名稱（必填）
- category: 機構類別（如：政府機關、醫療院所、社福機構、民間團體等）
- phone: 電話號碼
- address: 地址
- services: 服務項目（多個項目用逗號分隔）
- email: 電子郵件
- contact_person: 聯絡人姓名
- notes: 其他備註資訊

請以 JSON 陣列格式回傳，例如：
[
    {{
        "name": "高雄市毒品危害防制中心",
        "category": "政府機關",
        "phone": "07-123-4567",
        "address": "高雄市前金區自強二路71號",
        "services": "藥癮戒治, 心理諮商, 家庭支持",
        "email": "contact@example.gov.tw",
        "contact_person": "王主任",
        "notes": "週一至週五 08:00-17:00"
    }}
]

以下是需要辨識的文字內容：
---
{text}
---

請只回傳 JSON 陣列，不要包含其他說明文字。"""
            
            # 調用 LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # 降低溫度以提高準確性
                max_tokens=4000
                # 移除 response_format 以允許返回陣列
            )
            
            # 解析回應
            content = response.choices[0].message.content
            logger.info(f"LLM response: {content[:500]}...")  # 記錄前500字元
            
            # 解析 JSON
            try:
                # 清理回應內容，移除可能的 markdown 標記
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                # 嘗試直接解析為 JSON
                data = json.loads(content)
                
                # 如果回傳的是包含 contacts 鍵的物件
                if isinstance(data, dict) and "contacts" in data:
                    data = data["contacts"]
                # 如果回傳的是包含其他列表鍵的物件
                elif isinstance(data, dict):
                    # 尋找可能的陣列鍵
                    for key in ["data", "items", "results", "list", "organizations", "institutions"]:
                        if key in data and isinstance(data[key], list):
                            data = data[key]
                            break
                    else:
                        # 如果是單一物件且有 name 欄位，轉為陣列
                        if "name" in data:
                            data = [data]
                        else:
                            logger.warning(f"Unexpected dict format, keys: {list(data.keys())}")
                            data = []
                # 確保是陣列
                elif not isinstance(data, list):
                    logger.warning(f"Unexpected data format: {type(data)}")
                    data = []
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                logger.error(f"Raw content: {content}")
                return []
            
            # 驗證並轉換為 ContactInfo 物件
            contacts = []
            for item in data:
                try:
                    # 資料清理
                    if isinstance(item, dict):
                        # 移除空字串，轉為 None
                        cleaned_item = {
                            k: (v if v and v.strip() else None) if isinstance(v, str) else v
                            for k, v in item.items()
                        }
                        
                        # 建立 ContactInfo 物件
                        contact = ContactInfo(**cleaned_item)
                        contacts.append(contact)
                        logger.info(f"Successfully parsed contact: {contact.name}")
                        
                except ValidationError as e:
                    logger.warning(f"Validation error for contact: {e}")
                    logger.warning(f"Raw item: {item}")
                    continue
            
            logger.info(f"Extracted {len(contacts)} contacts from text")
            return contacts
            
        except Exception as e:
            logger.error(f"Error extracting contacts: {e}")
            return []
    
    async def enhance_contact_description(self, contact: ContactInfo) -> str:
        """
        為聯絡人資訊生成增強描述（用於向量搜尋）
        
        Args:
            contact: 聯絡人資訊
            
        Returns:
            str: 增強的描述文字
        """
        parts = [f"機構名稱：{contact.name}"]
        
        if contact.category:
            parts.append(f"類別：{contact.category}")
        if contact.services:
            parts.append(f"服務項目：{contact.services}")
        if contact.address:
            parts.append(f"地址：{contact.address}")
        if contact.phone:
            parts.append(f"電話：{contact.phone}")
        if contact.contact_person:
            parts.append(f"聯絡人：{contact.contact_person}")
        if contact.email:
            parts.append(f"電子郵件：{contact.email}")
        if contact.notes:
            parts.append(f"備註：{contact.notes}")
        
        # 組合描述
        description = " | ".join(parts)
        
        # 加入語義增強
        semantic_desc = f"{contact.name} 是一個{contact.category or '機構'}"
        if contact.services:
            semantic_desc += f"，提供{contact.services}等服務"
        if contact.address:
            semantic_desc += f"，位於{contact.address}"
        
        return f"{description}\n{semantic_desc}"
    
    def standardize_phone(self, phone: Optional[str]) -> Optional[str]:
        """
        標準化電話號碼格式
        
        Args:
            phone: 原始電話號碼
            
        Returns:
            Optional[str]: 標準化後的電話號碼
        """
        if not phone:
            return None
        
        # 移除所有非數字字元（保留分機號碼的 # 或 ext）
        import re
        
        # 保留原始格式，只做基本清理
        phone = phone.strip()
        
        # 統一分機號碼格式
        phone = re.sub(r'[Ee]xt\.?\s*', '#', phone)
        phone = re.sub(r'分機\s*', '#', phone)
        
        return phone
    
    def standardize_address(self, address: Optional[str]) -> Optional[str]:
        """
        標準化地址格式
        
        Args:
            address: 原始地址
            
        Returns:
            Optional[str]: 標準化後的地址
        """
        if not address:
            return None
        
        # 移除多餘空白
        address = " ".join(address.split())
        
        # 確保有「市」「區」等字
        address = address.replace("高雄", "高雄市")
        
        return address