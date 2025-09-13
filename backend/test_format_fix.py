"""
測試修復後的格式化功能
"""

import re

def test_phone_extraction():
    """測試電話號碼提取"""
    
    # 測試內容（從實際RAG結果複製）
    test_contents = [
        "機構名稱：高雄市立凱旋醫院  類別：醫療院所  服務項目：藥癮戒治, 心理諮商, 替代療法  地址：高雄市市苓雅區凱旋二路130號  電話：077513171",
        "高雄市立凱旋醫院\n地址：80276 高雄市苓雅區凱旋二路130號\n電話：(07) 751-3171",
        "電話：07-7513171",
        "聯絡電話：0912345678",
        "免費專線：0800-123456"
    ]
    
    # 新的正則表達式
    phone_pattern = r'(?:\(?\d{2,3}\)?[\s-]?\d{3,4}[\s-]?\d{4}|0\d{9,10}|0800[\s-]?\d{6})'
    
    print("=" * 60)
    print("測試電話提取正則表達式")
    print("=" * 60)
    
    for i, content in enumerate(test_contents, 1):
        print(f"\n測試 {i}:")
        print(f"內容: {content[:80]}...")
        phones = re.findall(phone_pattern, content)
        if phones:
            print(f"找到電話: {phones}")
        else:
            print("未找到電話")
    
    print("\n" + "=" * 60)
    
    # 測試完整的格式化邏輯
    def format_results_test(content):
        """模擬_format_results的邏輯"""
        formatted_items = []
        seen = set()
        
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
    
    print("\n測試完整格式化功能")
    print("=" * 60)
    
    test_content = "機構名稱：高雄市立凱旋醫院  類別：醫療院所  服務項目：藥癮戒治, 心理諮商, 替代療法  地址：高雄市市苓雅區凱旋二路130號  電話：077513171"
    result = format_results_test(test_content)
    print(f"輸入: {test_content[:60]}...")
    print(f"輸出: {result}")
    
    test_content2 = "高雄市立凱旋醫院\n地址：80276 高雄市苓雅區凱旋二路130號\n電話：(07) 751-3171"
    result2 = format_results_test(test_content2)
    print(f"\n輸入: {test_content2[:60]}...")
    print(f"輸出: {result2}")

if __name__ == "__main__":
    test_phone_extraction()