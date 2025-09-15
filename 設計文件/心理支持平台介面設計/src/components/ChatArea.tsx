import { Send, Bot, User, Heart } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';

export function ChatArea() {
  const messages = [
    { id: 1, type: 'received', content: '嗨嗨！我是你的AI心靈小助手 🌈 有什麼想聊的嗎？', time: '14:30' },
    { id: 2, type: 'received', content: '今天心情如何呢？不管開心還是煩惱，我都在這裡陪你 💖', time: '14:31' },
    { id: 3, type: 'sent', content: '最近壓力有點大，想找個人聊聊', time: '14:35' },
    { id: 4, type: 'received', content: '我懂我懂！壓力山大真的很不好受 😣 我們可以慢慢聊，或者你也可以試試右邊的功能，可能會有幫助喔！🌟', time: '14:36' },
  ];

  return (
    <Card className="h-full flex flex-col bg-gradient-to-br from-white to-pink-50/50 border-4 border-pink-200 shadow-2xl shadow-pink-200/50 rounded-3xl overflow-hidden">
      {/* Chat Header */}
      <div className="p-6 bg-gradient-to-r from-pink-400 via-purple-400 to-cyan-400 text-white">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center border-4 border-white/30 shadow-lg">
              <Bot className="w-8 h-8 text-white" strokeWidth={2} />
            </div>
            <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-400 rounded-full border-3 border-white shadow-md">
              <Heart className="w-3 h-3 text-white absolute top-1 left-1" />
            </div>
          </div>
          <div>
            <h2 className="text-2xl font-black mb-1">聊天時光 ✨</h2>
            <p className="text-white/90 font-bold">安全・溫馨・隨時在線</p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 p-6 overflow-y-auto space-y-6 bg-gradient-to-b from-transparent to-purple-50/30">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'sent' ? 'justify-end' : 'justify-start'} gap-4`}
          >
            {message.type === 'received' && (
              <div className="w-12 h-12 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full flex items-center justify-center mt-1 shadow-lg shadow-pink-300/50 border-3 border-white">
                <Bot className="w-6 h-6 text-white" strokeWidth={2} />
              </div>
            )}
            
            <div className={`max-w-xs lg:max-w-md ${message.type === 'sent' ? 'order-1' : ''}`}>
              <Card
                className={`p-5 ${
                  message.type === 'sent'
                    ? 'bg-gradient-to-br from-cyan-100 to-cyan-200 border-cyan-300 shadow-lg shadow-cyan-200/50'
                    : 'bg-gradient-to-br from-white to-pink-50 border-pink-200 shadow-lg shadow-pink-200/50'
                } rounded-2xl border-3`}
              >
                <p className="text-gray-800 mb-3 leading-relaxed font-semibold">{message.content}</p>
                <p className="text-xs text-gray-500 font-bold">{message.time}</p>
              </Card>
            </div>

            {message.type === 'sent' && (
              <div className="w-12 h-12 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full flex items-center justify-center mt-1 shadow-lg shadow-cyan-300/50 border-3 border-white order-2">
                <User className="w-6 h-6 text-white" strokeWidth={2} />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Input Area */}
      <div className="p-6 bg-gradient-to-r from-purple-50 to-cyan-50 border-t-4 border-purple-200">
        <div className="flex gap-4">
          <Input
            placeholder="輸入你的心情或想法..."
            className="flex-1 bg-white/80 border-3 border-purple-300 focus:border-pink-400 focus:ring-pink-300/30 text-gray-800 placeholder:text-gray-500 rounded-2xl font-semibold text-lg h-14 px-6"
          />
          <Button className="bg-gradient-to-r from-pink-400 via-purple-500 to-cyan-500 hover:from-pink-500 hover:via-purple-600 hover:to-cyan-600 text-white border-none shadow-lg shadow-purple-300/50 hover:shadow-purple-400/60 transition-all duration-300 rounded-2xl px-8 h-14 font-black text-lg">
            <Send className="w-6 h-6" strokeWidth={2} />
          </Button>
        </div>
        <div className="flex items-center justify-center mt-4 gap-2">
          <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse shadow-md"></div>
          <p className="text-sm text-gray-600 font-bold">🔒 你的隱私超級安全！</p>
        </div>
      </div>
    </Card>
  );
}