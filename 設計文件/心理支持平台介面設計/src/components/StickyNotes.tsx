import { 
  MessageCircle, 
  Users, 
  BookOpen, 
  Search, 
  FileText, 
  Baby, 
  Shield, 
  Heart, 
  Sparkles 
} from 'lucide-react';
import { Card } from './ui/card';

interface StickyNotesProps {
  activeFunction: string | null;
  onFunctionClick: (functionId: string) => void;
}

export function StickyNotes({ activeFunction, onFunctionClick }: StickyNotesProps) {
  const stickyNotes = [
    {
      id: 'chat',
      icon: MessageCircle,
      title: '聊天吧',
      emoji: '💬',
      description: '24小時真人聊天服務',
      color: 'bg-orange-400 text-white',
      bgColor: 'bg-orange-400/90',
      borderColor: 'border-orange-500'
    },
    {
      id: 'counseling',
      icon: Users,
      title: '專家諮詢',
      emoji: '👥',
      description: '心理師專業一對一輔導',
      color: 'bg-orange-400 text-white',
      bgColor: 'bg-orange-400/90',
      borderColor: 'border-orange-500'
    },
    {
      id: 'comprehensive',
      icon: Users,
      title: '全能諮詢',
      emoji: '🎯',
      description: '專業多元諮詢服務',
      color: 'bg-orange-400 text-white',
      bgColor: 'bg-orange-400/90',
      borderColor: 'border-orange-500'
    },
    {
      id: 'skills',
      icon: BookOpen,
      title: '技能普查',
      emoji: '📊',
      description: '心理健康技能評估',
      color: 'bg-teal-500 text-white',
      bgColor: 'bg-teal-500/90',
      borderColor: 'border-teal-600'
    },
    {
      id: 'counseling1',
      icon: Heart,
      title: '情境輔導',
      emoji: '💝',
      description: '專業個案情境分析輔導',
      color: 'bg-red-500 text-white',
      bgColor: 'bg-red-500/90',
      borderColor: 'border-red-600'
    },
    {
      id: 'counseling2',
      icon: Heart,
      title: '情境輔導',
      emoji: '❤️',
      description: '深度心理情境輔導',
      color: 'bg-red-500 text-white',
      bgColor: 'bg-red-500/90',
      borderColor: 'border-red-600'
    },
    {
      id: 'exploration',
      icon: Sparkles,
      title: '自我探索',
      emoji: '🔮',
      description: '探索內在自我與潛能發展',
      color: 'bg-purple-500 text-white',
      bgColor: 'bg-purple-500/90',
      borderColor: 'border-purple-600'
    },
    {
      id: 'resources',
      icon: Search,
      title: '資源查詢',
      emoji: '🔍',
      description: '心理健康相關資源查詢',
      color: 'bg-cyan-500 text-white',
      bgColor: 'bg-cyan-500/90',
      borderColor: 'border-cyan-600'
    },
    {
      id: 'wishes',
      icon: Sparkles,
      title: '天燈Go',
      emoji: '🏮',
      description: '心願祈福與正能量傳遞',
      color: 'bg-orange-400 text-white',
      bgColor: 'bg-orange-400/90',
      borderColor: 'border-orange-500'
    }
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Services Header - Orange sticky note */}
      <div className="bg-orange-400/90 border-2 border-orange-500 rounded-lg shadow-lg transform rotate-1 mb-6 relative">
        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1 w-4 h-4 bg-red-400 rounded-full shadow-md"></div>
        <div className="p-4 text-center">
          <h2 className="text-xl font-black text-white mb-1">📋 服務資源</h2>
          <p className="text-white/90 font-bold text-sm">專業心理健康服務</p>
        </div>
      </div>

      {/* Services List */}
      <div className="flex-1 space-y-3 overflow-y-auto">
        {stickyNotes.map((note, index) => (
          <Card
            key={note.id}
            className={`${note.bgColor} ${note.borderColor} border-2 shadow-lg cursor-pointer transition-all duration-300 hover:scale-105 active:scale-95 transform ${
              index % 2 === 0 ? 'rotate-1' : '-rotate-1'
            } hover:rotate-0 overflow-hidden relative group`}
            onClick={() => onFunctionClick(note.id)}
          >
            {/* Pin/thumb tack */}
            <div className="absolute top-1 right-3 w-3 h-3 bg-red-400 border border-red-500 rounded-full shadow-md"></div>
            
            {/* Content */}
            <div className="p-4">
              <div className="flex items-center gap-3">
                {/* Icon circle */}
                <div className={`w-12 h-12 ${note.color} rounded-full flex items-center justify-center border-2 border-white/30 shadow-md group-hover:scale-110 transition-transform duration-300`}>
                  <div className="text-lg mb-0.5">{note.emoji}</div>
                </div>
                
                {/* Text content */}
                <div className="flex-1">
                  <h3 className="font-black text-white mb-1 group-hover:scale-105 transition-transform duration-300">
                    {note.title}
                  </h3>
                  <p className="text-white/90 text-sm font-bold leading-tight">
                    {note.description}
                  </p>
                </div>
              </div>
            </div>

            {/* Sticky note texture lines */}
            <div 
              className="absolute inset-0 opacity-10 pointer-events-none"
              style={{
                backgroundImage: `
                  linear-gradient(0deg, transparent 8px, currentColor 9px, currentColor 10px, transparent 11px)
                `,
                backgroundSize: '100% 16px'
              }}
            ></div>

            {/* Shadow under the note */}
            <div className="absolute inset-0 bg-black/10 rounded-lg transform translate-x-1 translate-y-1 -z-10"></div>
          </Card>
        ))}
      </div>

      {/* Bottom decoration - scattered office supplies */}
      <div className="relative mt-4 h-8">
        <div className="absolute bottom-0 left-1/4 w-6 h-2 bg-gray-400 rounded-full opacity-60 transform rotate-12"></div>
        <div className="absolute bottom-0 right-1/3 w-4 h-4 border-2 border-gray-400 rounded-full opacity-50"></div>
        <div className="absolute bottom-2 left-1/2 w-8 h-1 bg-blue-400 rounded-full opacity-40 transform -rotate-6"></div>
      </div>
    </div>
  );
}