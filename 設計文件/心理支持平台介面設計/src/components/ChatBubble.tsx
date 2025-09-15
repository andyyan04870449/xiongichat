import { useState } from 'react';
import { Send, Bot, User, Heart, Minimize2, Maximize2 } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';

export function ChatBubble() {
  const [isMinimized, setIsMinimized] = useState(false);
  const [message, setMessage] = useState('');

  const messages = [
    { id: 1, type: 'received', content: '嗨！歡迎來到AI心靈宇宙 🌟 我是你的專屬導航員！', time: '14:30' },
    { id: 2, type: 'received', content: '看到周圍那些閃閃發光的功能了嗎？點擊探索更多驚喜 ✨', time: '14:31' },
    { id: 3, type: 'sent', content: '哇這個介面好酷！像在太空中一樣', time: '14:35' },
    { id: 4, type: 'received', content: '對吧！這裡就是你的專屬心靈太空站 🚀 隨時都可以和我聊天喔！', time: '14:36' },
  ];

  if (isMinimized) {
    return (
      <div className="fixed bottom-20 right-8 z-50">
        <div
          onClick={() => setIsMinimized(false)}
          className="w-16 h-16 bg-gradient-to-br from-pink-500/90 to-purple-600/90 backdrop-blur-lg border-4 border-white/40 rounded-full flex items-center justify-center shadow-2xl cursor-pointer hover:scale-110 transition-all duration-300 group"
        >
          <Bot className="w-8 h-8 text-white group-hover:animate-bounce" />
          <div className="absolute -top-1 -right-1 w-5 h-5 bg-green-400 rounded-full border-2 border-white animate-pulse">
            <Heart className="w-2 h-2 text-white absolute top-0.5 left-0.5" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-20 right-8 w-96 z-50">
      <Card className="bg-white/10 backdrop-blur-xl border border-white/30 shadow-2xl rounded-3xl overflow-hidden">
        {/* Chat Header */}
        <div className="p-4 bg-gradient-to-r from-pink-500/80 to-purple-600/80 backdrop-blur-sm border-b border-white/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center border-2 border-white/40">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-white font-black text-lg">AI 導航員</h3>
                <p className="text-white/80 text-sm font-bold">隨時陪伴你 💫</p>
              </div>
            </div>
            <Button
              onClick={() => setIsMinimized(true)}
              variant="ghost"
              size="sm"
              className="text-white hover:bg-white/20 rounded-full w-8 h-8 p-0"
            >
              <Minimize2 className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Messages */}
        <div className="p-4 h-64 overflow-y-auto space-y-3 bg-gradient-to-b from-transparent to-white/5">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${msg.type === 'sent' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.type === 'received' && (
                <div className="w-8 h-8 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full flex items-center justify-center border-2 border-white/40 mt-1">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}
              
              <div className={`max-w-xs ${msg.type === 'sent' ? 'order-1' : ''}`}>
                <div
                  className={`p-3 rounded-2xl ${
                    msg.type === 'sent'
                      ? 'bg-white/20 border border-white/30'
                      : 'bg-white/15 border border-white/25'
                  } backdrop-blur-sm`}
                >
                  <p className="text-white text-sm font-semibold leading-relaxed">{msg.content}</p>
                  <p className="text-white/60 text-xs mt-1 font-medium">{msg.time}</p>
                </div>
              </div>

              {msg.type === 'sent' && (
                <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full flex items-center justify-center border-2 border-white/40 mt-1 order-2">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="p-4 bg-white/5 backdrop-blur-sm border-t border-white/20">
          <div className="flex gap-2">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="輸入你的想法..."
              className="bg-white/20 border-white/30 text-white placeholder:text-white/60 rounded-full font-medium"
            />
            <Button className="bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white border-none rounded-full px-4 font-bold">
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}