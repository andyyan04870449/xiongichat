import { useState } from 'react';
import { Send, Bot, User, Paperclip } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';

export function ChatPaper() {
  const [message, setMessage] = useState('');

  const messages = [
    { id: 1, type: 'received', content: '嗨！歡迎來到網聊軸能智慧聊天室 🤖 我是你的AI心理助手！', time: '14:30' },
    { id: 2, type: 'received', content: '看到右邊那些彩色便利貼了嗎？每一張都是不同的服務資源喔 📋✨', time: '14:31' },
    { id: 3, type: 'sent', content: '哇！這個設計好棒，左右分區很清楚', time: '14:35' },
    { id: 4, type: 'received', content: '對吧！左邊是我們對話的空間，右邊隨時都能找到需要的服務 🗂️ 想試試哪個功能呢？', time: '14:36' },
    { id: 5, type: 'sent', content: '我想了解一下右邊有哪些服務可以使用', time: '14:38' },
    { id: 6, type: 'received', content: '太棒了！你可以點擊右邊任何一張便利貼 - 有聊天服務、專家諮詢、資源查詢等等，每種顏色代表不同類型的服務！🌈', time: '14:39' },
  ];

  return (
    <div className="h-full flex flex-col">
      <Card className="flex-1 bg-white/95 backdrop-blur-sm border-2 border-gray-300 shadow-2xl relative overflow-hidden">
        {/* Paper texture and lines */}
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `
              linear-gradient(0deg, transparent 24px, rgba(200,200,200,0.3) 25px, rgba(200,200,200,0.3) 26px, transparent 27px),
              linear-gradient(90deg, rgba(255,200,200,0.2) 0%, transparent 2px)
            `,
            backgroundSize: '100% 30px, 40px 100%'
          }}
        ></div>

        {/* Paper holes */}
        <div className="absolute left-4 top-0 bottom-0 flex flex-col justify-around py-8">
          {Array.from({ length: 20 }).map((_, i) => (
            <div key={i} className="w-4 h-4 bg-gray-100 border-2 border-gray-300 rounded-full shadow-inner"></div>
          ))}
        </div>

        {/* Header - Orange sticky note style header */}
        <div className="relative z-10 bg-orange-400/90 border-2 border-orange-500 mx-4 mt-4 rounded-lg shadow-lg">
          <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1 w-4 h-4 bg-red-400 rounded-full shadow-md"></div>
          <div className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/30 border-2 border-white/50 rounded-lg flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" strokeWidth={2} />
              </div>
              <div>
                <h2 className="text-xl font-black text-white">🤖 網聊軸能智慧聊天室</h2>
                <p className="text-white/90 font-bold text-sm">歡迎進入對話空間・創作談話</p>
              </div>
            </div>
          </div>
        </div>

        {/* Messages - like handwritten notes */}
        <div className="relative z-10 flex-1 p-6 overflow-y-auto space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${msg.type === 'sent' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.type === 'received' && (
                <div className="w-9 h-9 bg-blue-100 border-2 border-blue-300 rounded-lg flex items-center justify-center mt-1 shadow-sm">
                  <Bot className="w-5 h-5 text-blue-600" strokeWidth={2} />
                </div>
              )}
              
              <div className={`max-w-xs ${msg.type === 'sent' ? 'order-1' : ''}`}>
                <div
                  className={`p-4 rounded-lg border-2 shadow-md transform ${
                    msg.type === 'sent'
                      ? 'bg-blue-50 border-blue-200 rotate-1'
                      : 'bg-yellow-50 border-yellow-200 -rotate-1'
                  }`}
                >
                  <p className="text-gray-800 font-semibold leading-relaxed">{msg.content}</p>
                  <p className="text-gray-500 text-xs mt-2 font-medium">{msg.time}</p>
                </div>
              </div>

              {msg.type === 'sent' && (
                <div className="w-9 h-9 bg-green-100 border-2 border-green-300 rounded-lg flex items-center justify-center mt-1 shadow-sm order-2">
                  <User className="w-5 h-5 text-green-600" strokeWidth={2} />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input - like writing on paper */}
        <div className="relative z-10 p-6 border-t-2 border-gray-200 bg-gray-50/50">
          <div className="flex gap-3">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="在這裡寫下你的想法..."
              className="bg-white/80 border-2 border-gray-300 text-gray-800 placeholder:text-gray-500 rounded-lg font-medium shadow-sm"
            />
            <Button className="bg-blue-500 hover:bg-blue-600 text-white border-2 border-blue-600 rounded-lg px-6 font-bold shadow-md">
              <Send className="w-5 h-5" strokeWidth={2} />
            </Button>
          </div>
          <div className="flex items-center justify-center mt-3 gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <p className="text-gray-600 text-xs font-bold">📝 安全對話記錄中</p>
          </div>
        </div>

        {/* Paper corner fold effect */}
        <div className="absolute top-0 right-0 w-8 h-8 bg-gray-200 border-l-2 border-b-2 border-gray-300 transform rotate-45 translate-x-4 -translate-y-4"></div>
      </Card>
    </div>
  );
}