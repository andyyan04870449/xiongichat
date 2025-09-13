"""分析專案中所有測試腳本的功能和用途"""

import os
import glob
from pathlib import Path

def analyze_test_scripts():
    """分析所有測試腳本的主要功能"""
    
    backend_dir = "/Users/yangandy/KaohsiungCare/backend"
    test_files = []
    
    # 查找所有測試文件
    patterns = [
        "test_*.py",
        "run_*.py", 
        "*test*.py"
    ]
    
    for pattern in patterns:
        test_files.extend(glob.glob(f"{backend_dir}/{pattern}"))
        test_files.extend(glob.glob(f"{backend_dir}/**/{pattern}", recursive=True))
    
    # 去重並排序
    test_files = sorted(list(set(test_files)))
    
    print(f"📊 專案測試腳本分析報告")
    print(f"總共找到 {len(test_files)} 個測試腳本")
    print("=" * 80)
    
    categories = {
        "對話流程測試": [],
        "RAG檢索測試": [],
        "工作流測試": [], 
        "記憶系統測試": [],
        "資料上傳測試": [],
        "危機偵測測試": [],
        "品質評估測試": [],
        "性能壓力測試": [],
        "架構功能測試": [],
        "其他測試": []
    }
    
    for test_file in test_files:
        filename = os.path.basename(test_file)
        
        # 讀取文件前幾行獲取描述
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]  # 只讀前10行
                description = ""
                for line in lines:
                    if line.strip().startswith('"""') or line.strip().startswith("'''"):
                        description = line.strip().replace('"""', '').replace("'''", '')
                        break
                    elif line.strip().startswith('#') and len(line.strip()) > 5:
                        description = line.strip()[1:].strip()
                        break
        except:
            description = "無法讀取描述"
        
        # 分類
        if any(keyword in filename.lower() for keyword in ['conversation', 'chat', 'emotion', 'long_', 'dialogue']):
            categories["對話流程測試"].append((filename, description))
        elif any(keyword in filename.lower() for keyword in ['rag', 'search', 'retriev', 'knowledge']):
            categories["RAG檢索測試"].append((filename, description))
        elif any(keyword in filename.lower() for keyword in ['workflow', 'ultimate', 'fast', 'pure']):
            categories["工作流測試"].append((filename, description))
        elif any(keyword in filename.lower() for keyword in ['memory', 'context']):
            categories["記憶系統測試"].append((filename, description))
        elif any(keyword in filename.lower() for keyword in ['upload', 'csv', 'batch']):
            categories["資料上傳測試"].append((filename, description))
        elif any(keyword in filename.lower() for keyword in ['crisis', 'risk', 'safety']):
            categories["危機偵測測試"].append((filename, description))
        elif any(keyword in filename.lower() for keyword in ['quality', 'logger', 'report']):
            categories["品質評估測試"].append((filename, description))
        elif any(keyword in filename.lower() for keyword in ['stress', 'performance', 'load', 'extreme']):
            categories["性能壓力測試"].append((filename, description))
        elif any(keyword in filename.lower() for keyword in ['architecture', 'integration', 'complete', 'scenarios']):
            categories["架構功能測試"].append((filename, description))
        else:
            categories["其他測試"].append((filename, description))
    
    # 輸出分類結果
    for category, files in categories.items():
        if files:
            print(f"\n🔧 {category} ({len(files)}個)")
            print("-" * 60)
            for filename, description in files[:10]:  # 只顯示前10個
                desc_short = description[:50] + "..." if len(description) > 50 else description
                print(f"  • {filename}")
                if description and description != "無法讀取描述":
                    print(f"    {desc_short}")
            if len(files) > 10:
                print(f"    ... 還有 {len(files) - 10} 個文件")
    
    print(f"\n📈 主要測試類別統計:")
    for category, files in categories.items():
        if files:
            print(f"  {category}: {len(files)} 個")
    
    print(f"\n💡 建議:")
    print("1. 對話流程測試最多，說明重點關注用戶體驗")
    print("2. RAG檢索測試豐富，確保知識檢索準確性") 
    print("3. 工作流測試完整，驗證不同架構方案")
    print("4. 可以考慮整理重複或過時的測試腳本")

if __name__ == "__main__":
    analyze_test_scripts()