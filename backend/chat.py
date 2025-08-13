#!/usr/bin/env python3
"""
互動式聊天客戶端
使用方式: python chat.py [--user USER_ID] [--url API_URL]
"""

import requests
import json
import sys
import argparse
from typing import Optional
from datetime import datetime

# 顏色定義
RESET = '\033[0m'
BOLD = '\033[1m'
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RED = '\033[91m'


class ChatClient:
    def __init__(self, base_url: str = "http://localhost:8000", user_id: str = "user_001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.user_id = user_id
        self.conversation_id: Optional[str] = None
        self.session = requests.Session()
        
    def check_health(self) -> bool:
        """檢查服務是否正常運行"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def send_message(self, message: str) -> dict:
        """發送訊息並取得回覆"""
        payload = {
            "user_id": self.user_id,
            "message": message
        }
        
        if self.conversation_id:
            payload["conversation_id"] = self.conversation_id
        
        try:
            response = self.session.post(
                f"{self.api_url}/chat/",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                # 儲存對話ID
                if "conversation_id" in data:
                    self.conversation_id = data["conversation_id"]
                return data
            else:
                return {"error": f"API錯誤: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"連線錯誤: {str(e)}"}
    
    def get_conversation_history(self) -> Optional[dict]:
        """取得對話歷史"""
        if not self.conversation_id:
            return None
            
        try:
            response = self.session.get(
                f"{self.api_url}/conversations/{self.conversation_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except:
            return None
    
    def start_new_conversation(self):
        """開始新對話"""
        self.conversation_id = None
        print(f"\n{YELLOW}[系統] 已開始新對話{RESET}")
    
    def print_welcome(self):
        """印出歡迎訊息"""
        print(f"""
{CYAN}{'='*50}
        雄i聊 - 互動式聊天客戶端
{'='*50}{RESET}

{GREEN}使用者ID: {self.user_id}
API位址: {self.api_url}{RESET}

{YELLOW}指令說明：
  /new     - 開始新對話
  /history - 查看對話歷史
  /info    - 查看當前對話資訊
  /help    - 顯示說明
  /quit    - 結束程式{RESET}

輸入訊息開始聊天...
""")
    
    def print_history(self):
        """印出對話歷史"""
        history = self.get_conversation_history()
        if not history:
            print(f"{RED}無法取得對話歷史{RESET}")
            return
            
        print(f"\n{CYAN}{'='*50}")
        print(f"對話歷史 (ID: {self.conversation_id[:8]}...)")
        print(f"{'='*50}{RESET}")
        
        for msg in history.get("messages", []):
            timestamp = msg.get("created_at", "")[:19]
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user":
                print(f"{GREEN}[{timestamp}] 使用者:{RESET}")
                print(f"  {content}")
            else:
                print(f"{BLUE}[{timestamp}] 雄i聊:{RESET}")
                print(f"  {content}")
        
        print(f"{CYAN}{'='*50}{RESET}")
    
    def print_info(self):
        """印出當前對話資訊"""
        print(f"\n{CYAN}當前對話資訊：")
        print(f"  使用者ID: {self.user_id}")
        print(f"  對話ID: {self.conversation_id if self.conversation_id else '(新對話)'}") 
        print(f"  時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    
    def run(self):
        """執行主要聊天迴圈"""
        # 檢查服務
        if not self.check_health():
            print(f"{RED}❌ 無法連線到服務，請確認服務是否正在運行{RESET}")
            print(f"請執行: ./start.sh")
            sys.exit(1)
        
        self.print_welcome()
        
        try:
            while True:
                # 取得使用者輸入
                user_input = input(f"\n{GREEN}{BOLD}你: {RESET}").strip()
                
                if not user_input:
                    continue
                
                # 處理指令
                if user_input.startswith("/"):
                    command = user_input.lower()
                    
                    if command == "/quit":
                        print(f"\n{YELLOW}再見！{RESET}")
                        break
                    elif command == "/new":
                        self.start_new_conversation()
                    elif command == "/history":
                        self.print_history()
                    elif command == "/info":
                        self.print_info()
                    elif command == "/help":
                        self.print_welcome()
                    else:
                        print(f"{RED}未知指令: {user_input}{RESET}")
                    continue
                
                # 發送訊息
                print(f"{YELLOW}思考中...{RESET}", end="\r")
                response = self.send_message(user_input)
                
                # 清除"思考中"訊息
                print(" " * 20, end="\r")
                
                # 處理回應
                if "error" in response:
                    print(f"{RED}錯誤: {response['error']}{RESET}")
                elif "reply" in response:
                    print(f"{BLUE}{BOLD}雄i聊: {RESET}{response['reply']}")
                    
                    # 顯示對話ID（第一次）
                    if self.conversation_id and "conversation_id" in response:
                        print(f"{CYAN}(對話ID: {self.conversation_id[:8]}...){RESET}")
                else:
                    print(f"{RED}未預期的回應格式{RESET}")
                    
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}程式已中斷{RESET}")
        except Exception as e:
            print(f"\n{RED}發生錯誤: {str(e)}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="雄i聊互動式聊天客戶端")
    parser.add_argument(
        "--user", 
        default="user_001",
        help="使用者ID (預設: user_001)"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API伺服器URL (預設: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    # 建立並執行客戶端
    client = ChatClient(base_url=args.url, user_id=args.user)
    client.run()


if __name__ == "__main__":
    main()