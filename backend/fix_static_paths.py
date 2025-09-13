#!/usr/bin/env python
"""修正所有 HTML 檔案中的靜態資源路徑"""

from pathlib import Path
import re

def fix_static_paths():
    """修正 HTML 檔案中的靜態資源路徑"""
    
    static_dir = Path("static")
    html_files = list(static_dir.glob("*.html"))
    
    print(f"找到 {len(html_files)} 個 HTML 檔案需要處理\n")
    
    for html_file in html_files:
        if html_file.name == "index.html":
            # index.html 已經處理過了
            continue
            
        print(f"處理 {html_file.name}...")
        content = html_file.read_text(encoding='utf-8')
        original_content = content
        
        # 修正 CSS 引用
        # href="styles.css" -> href="/static/styles.css"
        content = re.sub(
            r'href="((?!http|/static/|//)[^"]*\.css[^"]*)"',
            r'href="/static/\1"',
            content
        )
        
        # 修正 JavaScript 引用
        # src="app.js" -> src="/static/app.js"
        content = re.sub(
            r'src="((?!http|/static/|//)[^"]*\.js[^"]*)"',
            r'src="/static/\1"',
            content
        )
        
        # 修正圖片引用（如果有）
        # src="images/xxx.png" -> src="/static/images/xxx.png"
        content = re.sub(
            r'src="((?!http|/static/|//)[^"]*\.(png|jpg|jpeg|gif|svg)[^"]*)"',
            r'src="/static/\1"',
            content
        )
        
        if content != original_content:
            html_file.write_text(content, encoding='utf-8')
            print(f"  ✅ 已更新路徑")
            
            # 顯示修改的部分
            changes = []
            for line_num, (old, new) in enumerate(zip(original_content.split('\n'), content.split('\n')), 1):
                if old != new:
                    changes.append(f"    行 {line_num}: {old.strip()[:50]}... -> {new.strip()[:50]}...")
            
            if changes[:3]:  # 只顯示前3個變更
                print("  變更預覽:")
                for change in changes[:3]:
                    print(change)
        else:
            print(f"  ✓ 路徑已經正確，無需修改")
    
    print("\n✅ 所有檔案處理完成！")

if __name__ == "__main__":
    fix_static_paths()