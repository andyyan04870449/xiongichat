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

export function FunctionGrid() {
  const functions = [
    {
      id: 'chat',
      icon: MessageCircle,
      title: '聊天吧',
      emoji: '💬',
      description: '和我們聊天吧！',
      gradient: 'from-pink-400 to-rose-500',
      hoverGradient: 'hover:from-pink-500 hover:to-rose-600',
      shadowColor: 'shadow-pink-300/50',
      hoverShadow: 'hover:shadow-pink-400/60'
    },
    {
      id: 'counseling',
      icon: Users,
      title: '多元輔導',
      emoji: '👥',
      description: '專業輔導服務',
      gradient: 'from-purple-400 to-violet-500',
      hoverGradient: 'hover:from-purple-500 hover:to-violet-600',
      shadowColor: 'shadow-purple-300/50',
      hoverShadow: 'hover:shadow-purple-400/60'
    },
    {
      id: 'education',
      icon: BookOpen,
      title: '衛教資源',
      emoji: '📚',
      description: '健康知識大寶庫',
      gradient: 'from-emerald-400 to-teal-500',
      hoverGradient: 'hover:from-emerald-500 hover:to-teal-600',
      shadowColor: 'shadow-emerald-300/50',
      hoverShadow: 'hover:shadow-emerald-400/60'
    },
    {
      id: 'resources',
      icon: Search,
      title: '找助資源',
      emoji: '🔍',
      description: '找到適合的幫助',
      gradient: 'from-cyan-400 to-blue-500',
      hoverGradient: 'hover:from-cyan-500 hover:to-blue-600',
      shadowColor: 'shadow-cyan-300/50',
      hoverShadow: 'hover:shadow-cyan-400/60'
    },
    {
      id: 'forms',
      icon: FileText,
      title: '資源表單',
      emoji: '📝',
      description: '簡單快速申請',
      gradient: 'from-amber-400 to-orange-500',
      hoverGradient: 'hover:from-amber-500 hover:to-orange-600',
      shadowColor: 'shadow-amber-300/50',
      hoverShadow: 'hover:shadow-amber-400/60'
    },
    {
      id: 'children',
      icon: Baby,
      title: '幼幼專區',
      emoji: '👶',
      description: '小朋友專屬空間',
      gradient: 'from-pink-300 to-pink-400',
      hoverGradient: 'hover:from-pink-400 hover:to-pink-500',
      shadowColor: 'shadow-pink-200/50',
      hoverShadow: 'hover:shadow-pink-300/60'
    },
    {
      id: 'recovery',
      icon: Shield,
      title: '戒癮專區',
      emoji: '🛡️',
      description: '戒治支援服務',
      gradient: 'from-indigo-400 to-purple-500',
      hoverGradient: 'hover:from-indigo-500 hover:to-purple-600',
      shadowColor: 'shadow-indigo-300/50',
      hoverShadow: 'hover:shadow-indigo-400/60'
    },
    {
      id: 'assessment',
      icon: Heart,
      title: '自我評量',
      emoji: '💖',
      description: '了解自己的狀態',
      gradient: 'from-rose-400 to-pink-500',
      hoverGradient: 'hover:from-rose-500 hover:to-pink-600',
      shadowColor: 'shadow-rose-300/50',
      hoverShadow: 'hover:shadow-rose-400/60'
    },
    {
      id: 'wishes',
      icon: Sparkles,
      title: '天燈Go',
      emoji: '✨',
      description: '許願放飛心情',
      gradient: 'from-yellow-400 to-amber-500',
      hoverGradient: 'hover:from-yellow-500 hover:to-amber-600',
      shadowColor: 'shadow-yellow-300/50',
      hoverShadow: 'hover:shadow-yellow-400/60'
    }
  ];

  return (
    <div className="h-full overflow-y-auto">
      <div className="mb-6 text-center">
        <h2 className="text-3xl font-black bg-gradient-to-r from-purple-600 to-cyan-600 bg-clip-text text-transparent mb-2">
          🎯 功能大集合
        </h2>
        <p className="text-lg text-gray-600 font-bold">點擊探索各種酷炫功能！</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
        {functions.map((func) => (
          <Card
            key={func.id}
            className={`p-6 bg-gradient-to-br ${func.gradient} ${func.hoverGradient} border-none shadow-2xl ${func.shadowColor} ${func.hoverShadow} transition-all duration-300 cursor-pointer group hover:scale-105 active:scale-95 rounded-3xl overflow-hidden relative`}
            onClick={() => console.log(`點擊了 ${func.title}`)}
          >
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-20 h-20 bg-white/10 rounded-full -translate-y-10 translate-x-10 group-hover:scale-150 transition-transform duration-500"></div>
            <div className="absolute bottom-0 left-0 w-16 h-16 bg-white/5 rounded-full translate-y-8 -translate-x-8 group-hover:scale-125 transition-transform duration-500"></div>
            
            <div className="relative z-10">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center border-3 border-white/30 shadow-lg group-hover:scale-110 transition-transform duration-300">
                  <func.icon className="w-8 h-8 text-white" strokeWidth={2.5} />
                </div>
                <div className="text-4xl group-hover:scale-110 transition-transform duration-300">
                  {func.emoji}
                </div>
              </div>
              
              <h3 className="text-2xl font-black text-white mb-2 group-hover:scale-105 transition-transform duration-300">
                {func.title}
              </h3>
              <p className="text-white/90 font-bold leading-relaxed group-hover:text-white transition-colors duration-300">
                {func.description}
              </p>
              
              {/* Click indicator */}
              <div className="mt-4 flex items-center gap-2 text-white/80 group-hover:text-white transition-colors duration-300">
                <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse"></div>
                <span className="text-sm font-bold">點我試試看！</span>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Bottom decorative section */}
      <div className="mt-8 p-6 bg-gradient-to-r from-red-200 via-pink-200 to-orange-200 rounded-3xl border-4 border-red-300 shadow-xl shadow-red-200/50">
        <div className="text-center">
          <div className="text-3xl mb-2">🆘</div>
          <p className="text-lg font-black text-red-700 mb-1">緊急求助專線</p>
          <p className="text-2xl font-black text-red-800">1995</p>
          <p className="text-sm font-bold text-red-600">24小時全年無休 💪</p>
        </div>
      </div>
    </div>
  );
}