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

interface FloatingFunctionsProps {
  activeFunction: string | null;
  onFunctionClick: (functionId: string) => void;
}

export function FloatingFunctions({ activeFunction, onFunctionClick }: FloatingFunctionsProps) {
  const functions = [
    {
      id: 'chat',
      icon: MessageCircle,
      title: '聊天吧',
      emoji: '💬',
      description: '隨時暢聊',
      position: 'top-32 left-20',
      gradient: 'from-pink-400/80 to-rose-500/80',
      size: 'w-32 h-32',
      delay: '0s'
    },
    {
      id: 'counseling',
      icon: Users,
      title: '多元輔導',
      emoji: '👥',
      description: '專業輔導',
      position: 'top-48 right-32',
      gradient: 'from-purple-400/80 to-violet-500/80',
      size: 'w-36 h-36',
      delay: '0.5s'
    },
    {
      id: 'education',
      icon: BookOpen,
      title: '衛教資源',
      emoji: '📚',
      description: '知識寶庫',
      position: 'top-1/3 left-1/4',
      gradient: 'from-emerald-400/80 to-teal-500/80',
      size: 'w-28 h-28',
      delay: '1s'
    },
    {
      id: 'resources',
      icon: Search,
      title: '找助資源',
      emoji: '🔍',
      description: '尋找幫助',
      position: 'bottom-1/2 right-20',
      gradient: 'from-cyan-400/80 to-blue-500/80',
      size: 'w-34 h-34',
      delay: '1.5s'
    },
    {
      id: 'forms',
      icon: FileText,
      title: '資源表單',
      emoji: '📝',
      description: '快速申請',
      position: 'bottom-1/3 left-32',
      gradient: 'from-amber-400/80 to-orange-500/80',
      size: 'w-30 h-30',
      delay: '2s'
    },
    {
      id: 'children',
      icon: Baby,
      title: '幼幼專區',
      emoji: '👶',
      description: '兒童專屬',
      position: 'top-1/2 left-12',
      gradient: 'from-pink-300/80 to-pink-400/80',
      size: 'w-32 h-32',
      delay: '2.5s'
    },
    {
      id: 'recovery',
      icon: Shield,
      title: '戒癮專區',
      emoji: '🛡️',
      description: '戒治支援',
      position: 'bottom-40 right-1/3',
      gradient: 'from-indigo-400/80 to-purple-500/80',
      size: 'w-36 h-36',
      delay: '3s'
    },
    {
      id: 'assessment',
      icon: Heart,
      title: '自我評量',
      emoji: '💖',
      description: '了解自己',
      position: 'top-2/3 right-12',
      gradient: 'from-rose-400/80 to-pink-500/80',
      size: 'w-28 h-28',
      delay: '3.5s'
    },
    {
      id: 'wishes',
      icon: Sparkles,
      title: '天燈Go',
      emoji: '✨',
      description: '許願祈福',
      position: 'bottom-32 left-1/3',
      gradient: 'from-yellow-400/80 to-amber-500/80',
      size: 'w-32 h-32',
      delay: '4s'
    }
  ];

  return (
    <div className="fixed inset-0 z-10">
      {functions.map((func) => (
        <Card
          key={func.id}
          className={`absolute ${func.position} ${func.size} bg-gradient-to-br ${func.gradient} backdrop-blur-xl border-2 border-white/40 shadow-2xl cursor-pointer transition-all duration-500 hover:scale-110 active:scale-95 rounded-3xl overflow-hidden group animate-fadeInScale`}
          style={{ 
            animationDelay: func.delay,
            animationDuration: '0.8s',
            animationFillMode: 'both'
          }}
          onClick={() => onFunctionClick(func.id)}
        >
          {/* Background effects */}
          <div className="absolute inset-0 bg-white/10 group-hover:bg-white/20 transition-colors duration-300"></div>
          <div className="absolute top-0 right-0 w-16 h-16 bg-white/20 rounded-full -translate-y-8 translate-x-8 group-hover:scale-150 transition-transform duration-500"></div>
          
          {/* Content */}
          <div className="relative z-10 h-full flex flex-col items-center justify-center p-4 text-center">
            <div className="mb-2 group-hover:scale-110 transition-transform duration-300">
              <div className="text-3xl mb-1 animate-bounce" style={{ animationDuration: '2s', animationDelay: func.delay }}>
                {func.emoji}
              </div>
              <div className="w-12 h-12 bg-white/30 rounded-full flex items-center justify-center">
                <func.icon className="w-6 h-6 text-white" strokeWidth={2} />
              </div>
            </div>
            
            <h3 className="text-white font-black text-sm mb-1 group-hover:text-yellow-100 transition-colors duration-300">
              {func.title}
            </h3>
            <p className="text-white/80 text-xs font-bold group-hover:text-white transition-colors duration-300">
              {func.description}
            </p>
            
            {/* Glow effect */}
            <div className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r from-white/10 to-transparent"></div>
          </div>

          {/* Floating particles for each card */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className="absolute w-1 h-1 bg-white/60 rounded-full animate-ping"
                style={{
                  top: `${20 + Math.random() * 60}%`,
                  left: `${20 + Math.random() * 60}%`,
                  animationDelay: `${Math.random() * 2}s`,
                  animationDuration: `${1 + Math.random() * 2}s`
                }}
              ></div>
            ))}
          </div>
        </Card>
      ))}

      {/* Add custom CSS for animations */}
      <style jsx>{`
        @keyframes fadeInScale {
          0% {
            opacity: 0;
            transform: scale(0.8) translateY(20px);
          }
          100% {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
        
        .animate-fadeInScale {
          animation: fadeInScale 0.8s ease-out;
        }
      `}</style>
    </div>
  );
}