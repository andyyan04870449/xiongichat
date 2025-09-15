import { useState } from 'react';
import { Send, Bot, User, Sparkles, Heart } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';

export function ChatHub() {
  const [message, setMessage] = useState('');

  const messages = [
    { id: 1, type: 'received', content: '歡迎來到對話宇宙的中心！🌌 我是你的AI導航員，準備好探索了嗎？', time: '14:30' },
    { id: 2, type: 'received', content: '看見圍繞我們的功能星球了嗎？每一個都有特別的魔力等你發現 ✨', time: '14:31' },
    { id: 3, type: 'sent', content: '哇！這個宇宙好壯觀，感覺像在太空站裡！', time: '14:35' },
    { id: 4, type: 'received', content: '沒錯！我們就在宇宙的中心 🚀 想要探索哪個星球呢？還是先和我聊聊天？', time: '14:36' },
    { id: 5, type: 'sent', content: '我想先了解一下這裡有什麼功能', time: '14:38' },
    { id: 6, type: 'received', content: '太棒了！你可以點擊任何一個圍繞我們的功能星球。每個星球都有獨特的顏色和用途 🌍💫', time: '14:39' },
  ];

  return (
    <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-30">
      <Card className="w-[500px] h-[600px] bg-white/15 backdrop-blur-2xl border-2 border-white/30 shadow-2xl rounded-3xl overflow-hidden relative">
        {/* Cosmic border glow */}
        <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-pink-500/20 via-purple-500/20 to-cyan-500/20 animate-pulse"></div>
        
        {/* Header */}
        <div className="relative z-10 p-6 bg-gradient-to-r from-purple-600/80 to-pink-600/80 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center border-3 border-white/40 shadow-xl">
                <Bot className="w-8 h-8 text-white" strokeWidth={2} />
              </div>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-yellow-400 rounded-full border-2 border-white animate-spin">
                <Sparkles className="w-3 h-3 text-white absolute top-0.5 left-0.5" />
              </div>
              <div className="absolute -bottom-2 -left-2 w-5 h-5 bg-pink-400 rounded-full border-2 border-white animate-pulse">
                <Heart className="w-2 h-2 text-white absolute top-0.5 left-0.5" />
              </div>
            </div>
            <div>
              <h2 className="text-2xl font-black text-white mb-1">AI 宇宙中心</h2>
              <p className="text-white/90 font-bold">所有對話的核心 💫</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="relative z-10 flex-1 p-6 overflow-y-auto space-y-4 h-[400px]">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${msg.type === 'sent' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.type === 'received' && (
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center border-2 border-white/40 mt-1 shadow-lg">
                  <Bot className="w-5 h-5 text-white" strokeWidth={2} />
                </div>
              )}
              
              <div className={`max-w-xs ${msg.type === 'sent' ? 'order-1' : ''}`}>
                <div
                  className={`p-4 rounded-2xl ${
                    msg.type === 'sent'
                      ? 'bg-cyan-400/80 backdrop-blur-sm border border-cyan-300/50 text-white'
                      : 'bg-white/20 backdrop-blur-sm border border-white/30 text-white'
                  } shadow-lg`}
                >
                  <p className="font-semibold leading-relaxed">{msg.content}</p>
                  <p className="text-xs mt-2 opacity-70 font-medium">{msg.time}</p>
                </div>
              </div>

              {msg.type === 'sent' && (
                <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-full flex items-center justify-center border-2 border-white/40 mt-1 shadow-lg order-2">
                  <User className="w-5 h-5 text-white" strokeWidth={2} />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="relative z-10 p-6 bg-gradient-to-r from-white/10 to-white/5 backdrop-blur-sm border-t border-white/20">
          <div className="flex gap-3">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="在宇宙中心說些什麼..."
              className="bg-white/20 border-white/30 text-white placeholder:text-white/60 rounded-2xl font-medium backdrop-blur-sm"
            />
            <Button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white border-none rounded-2xl px-6 font-bold shadow-lg">
              <Send className="w-5 h-5" strokeWidth={2} />
            </Button>
          </div>
          <div className="flex items-center justify-center mt-3 gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <p className="text-white/70 text-xs font-bold">🛡️ 宇宙級安全對話</p>
          </div>
        </div>

        {/* Floating cosmic particles around chat hub */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 bg-white/60 rounded-full animate-ping"
              style={{
                top: `${10 + Math.random() * 80}%`,
                left: `${10 + Math.random() * 80}%`,
                animationDelay: `${Math.random() * 3}s`,
                animationDuration: `${1 + Math.random() * 2}s`
              }}
            ></div>
          ))}
        </div>
      </Card>
    </div>
  );
}