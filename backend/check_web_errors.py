#!/usr/bin/env python
"""檢查網頁前端錯誤"""

import asyncio
import aiohttp
import re
from pathlib import Path

async def check_web_errors():
    """檢查網頁是否有 JavaScript 錯誤"""
    
    print("🔍 檢查網頁錯誤...\n")
    
    # 檢查靜態檔案
    static_dir = Path("static")
    
    # 1. 檢查 JavaScript 語法
    print("1. 檢查 JavaScript 檔案:")
    js_files = list(static_dir.glob("*.js"))
    for js_file in js_files:
        content = js_file.read_text(encoding='utf-8')
        
        # 檢查常見的語法問題
        issues = []
        
        # 檢查未結束的字串
        if re.search(r'["\'](?:[^"\'\n\\]|\\.)*$', content, re.MULTILINE):
            issues.append("可能有未結束的字串")
        
        # 檢查重複的 const/let/var 宣告
        vars = re.findall(r'\b(?:const|let|var)\s+(\w+)\s*=', content)
        duplicates = [v for v in vars if vars.count(v) > 1]
        if duplicates:
            issues.append(f"重複宣告的變數: {set(duplicates)}")
        
        # 檢查未定義的函數呼叫（簡單檢查）
        function_calls = re.findall(r'(\w+)\s*\(', content)
        function_defs = re.findall(r'function\s+(\w+)|(\w+)\s*=\s*(?:async\s+)?(?:function|\()', content)
        function_defs = [f[0] or f[1] for f in function_defs if f[0] or f[1]]
        
        # 內建函數和全域物件
        builtins = {
            'console', 'alert', 'confirm', 'prompt', 'setTimeout', 'setInterval',
            'fetch', 'JSON', 'Date', 'Math', 'Object', 'Array', 'String', 'Number',
            'document', 'window', 'localStorage', 'sessionStorage', 'location',
            'parseInt', 'parseFloat', 'isNaN', 'isFinite', 'encodeURIComponent',
            'decodeURIComponent', 'encodeURI', 'decodeURI', 'btoa', 'atob',
            'clearTimeout', 'clearInterval', 'addEventListener', 'removeEventListener',
            'querySelector', 'querySelectorAll', 'getElementById', 'getElementsByClassName',
            'createElement', 'appendChild', 'removeChild', 'insertBefore', 'replaceChild',
            'FormData', 'URLSearchParams', 'Headers', 'Request', 'Response',
            'FileReader', 'Blob', 'File', 'Promise', 'Error', 'SyntaxError',
            'TypeError', 'ReferenceError', 'RangeError'
        }
        
        undefined_calls = [f for f in function_calls if f not in function_defs and f not in builtins]
        # 過濾掉常見的方法名
        undefined_calls = [f for f in undefined_calls if not f.endswith('Handler') and f != 'if' and f != 'for' and f != 'while' and f != 'switch' and f != 'catch' and f != 'try']
        
        if js_file.name == "app.js":
            # app.js 特定的類和方法
            app_methods = {'KnowledgeManager', 'init', 'loadDocuments', 'searchDocuments', 'deleteDocument', 'showNotification'}
            undefined_calls = [f for f in undefined_calls if f not in app_methods]
        elif js_file.name == "batch-upload.js":
            # batch-upload.js 特定的類和方法
            batch_methods = {'BatchUploadManager', 'initialize', 'handleDrop', 'handleSelect', 'scanEntry', 'processFiles', 'uploadFiles', 'createBatch', 'uploadFile', 'updateBatchStatus', 'updateFileStatus'}
            undefined_calls = [f for f in undefined_calls if f not in batch_methods]
        
        if undefined_calls[:5]:  # 只顯示前5個
            issues.append(f"可能未定義的函數: {undefined_calls[:5]}")
        
        # 檢查括號匹配
        open_parens = content.count('(')
        close_parens = content.count(')')
        if open_parens != close_parens:
            issues.append(f"括號不匹配: ( {open_parens} vs ) {close_parens}")
        
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            issues.append(f"大括號不匹配: {{ {open_braces} vs }} {close_braces}")
        
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        if open_brackets != close_brackets:
            issues.append(f"方括號不匹配: [ {open_brackets} vs ] {close_brackets}")
        
        if issues:
            print(f"  ⚠️  {js_file.name}:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print(f"  ✅ {js_file.name}: 沒有明顯的語法問題")
    
    # 2. 檢查 HTML 檔案
    print("\n2. 檢查 HTML 檔案:")
    html_files = list(static_dir.glob("*.html"))
    for html_file in html_files:
        content = html_file.read_text(encoding='utf-8')
        issues = []
        
        # 檢查 script 標籤中的錯誤引用
        script_refs = re.findall(r'<script.*?src="([^"]+)"', content)
        for ref in script_refs:
            if not ref.startswith('http') and not ref.startswith('//'):
                # 移除查詢參數
                ref_path = ref.split('?')[0]
                if not (static_dir / ref_path).exists():
                    issues.append(f"找不到 JavaScript 檔案: {ref}")
        
        # 檢查 CSS 引用
        css_refs = re.findall(r'<link.*?href="([^"]+\.css[^"]*)"', content)
        for ref in css_refs:
            if not ref.startswith('http') and not ref.startswith('//'):
                ref_path = ref.split('?')[0]
                if not (static_dir / ref_path).exists():
                    issues.append(f"找不到 CSS 檔案: {ref}")
        
        # 檢查內聯 JavaScript
        inline_scripts = re.findall(r'<script>(.+?)</script>', content, re.DOTALL)
        for i, script in enumerate(inline_scripts, 1):
            if 'console.error' in script or 'throw' in script:
                issues.append(f"內聯腳本 {i} 包含錯誤處理代碼")
        
        if issues:
            print(f"  ⚠️  {html_file.name}:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print(f"  ✅ {html_file.name}: 沒有明顯的問題")
    
    # 3. 檢查 API 端點
    print("\n3. 檢查 API 端點引用:")
    all_js_content = ""
    for js_file in js_files:
        all_js_content += js_file.read_text(encoding='utf-8')
    
    # 找出所有的 fetch 呼叫
    api_calls = re.findall(r'fetch\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', all_js_content)
    api_calls += re.findall(r'fetch\s*\(\s*`([^`]+)`', all_js_content)
    
    # 檢查 API 端點是否一致
    api_base = None
    issues = []
    for api_call in api_calls:
        if api_call.startswith('/api/'):
            if not api_base:
                api_base = '/api/v1'
            if not api_call.startswith(api_base):
                issues.append(f"API 路徑不一致: {api_call}")
    
    if issues:
        print("  ⚠️  API 端點問題:")
        for issue in issues:
            print(f"      - {issue}")
    else:
        print("  ✅ API 端點引用正確")
    
    # 4. 檢查依賴關係
    print("\n4. 檢查 JavaScript 依賴:")
    
    # 檢查 app.js 中定義的類是否被正確使用
    if (static_dir / "app.js").exists():
        app_content = (static_dir / "app.js").read_text(encoding='utf-8')
        
        # 找出所有的類定義
        classes = re.findall(r'class\s+(\w+)', app_content)
        
        # 檢查 HTML 中是否正確引用
        for html_file in html_files:
            html_content = html_file.read_text(encoding='utf-8')
            for cls in classes:
                if f'new {cls}' in html_content:
                    print(f"  ✅ {html_file.name} 使用了 {cls}")
                elif cls in html_content:
                    print(f"  ⚠️  {html_file.name} 引用了 {cls} 但可能沒有實例化")
    
    print("\n✅ 檢查完成！")

if __name__ == "__main__":
    asyncio.run(check_web_errors())