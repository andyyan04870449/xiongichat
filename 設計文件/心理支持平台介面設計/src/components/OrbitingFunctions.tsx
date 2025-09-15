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

interface OrbitingFunctionsProps {
  activeFunction: string | null;
  onFunctionClick: (functionId: string) => void;
}

export function OrbitingFunctions({ activeFunction, onFunctionClick }: OrbitingFunctionsProps) {
  const functions = [
    {
      id: 'chat',
      icon: MessageCircle,
      title: '聊天吧',
      emoji: '💬',
      description: '隨時暢聊',
      gradient: 'from-pink-400 to-rose-500',
      orbitRadius: 300,
      orbitSpeed: '20s',
      size: 'w-20 h-20',
      startAngle: 0
    },
    {
      id: 'counseling',
      icon: Users,
      title: '多元輔導',
      emoji: '👥',
      description: '專業輔導',
      gradient: 'from-purple-400 to-violet-500',
      orbitRadius: 350,
      orbitSpeed: '25s',
      size: 'w-24 h-24',
      startAngle: 40
    },
    {
      id: 'education',
      icon: BookOpen,
      title: '衛教資源',
      emoji: '📚',
      description: '知識寶庫',
      gradient: 'from-emerald-400 to-teal-500',
      orbitRadius: 280,
      orbitSpeed: '18s',
      size: 'w-18 h-18',
      startAngle: 80
    },
    {
      id: 'resources',
      icon: Search,
      title: '找助資源',
      emoji: '🔍',
      description: '尋找幫助',
      gradient: 'from-cyan-400 to-blue-500',
      orbitRadius: 320,
      orbitSpeed: '22s',
      size: 'w-22 h-22',
      startAngle: 120
    },
    {
      id: 'forms',
      icon: FileText,
      title: '資源表單',
      emoji: '📝',
      description: '快速申請',
      gradient: 'from-amber-400 to-orange-500',
      orbitRadius: 290,
      orbitSpeed: '19s',
      size: 'w-20 h-20',
      startAngle: 160
    },
    {
      id: 'children',
      icon: Baby,
      title: '幼幼專區',
      emoji: '👶',
      description: '兒童專屬',
      gradient: 'from-pink-300 to-pink-400',
      orbitRadius: 340,
      orbitSpeed: '24s',
      size: 'w-24 h-24',
      startAngle: 200
    },
    {
      id: 'recovery',
      icon: Shield,
      title: '戒癮專區',
      emoji: '🛡️',
      description: '戒治支援',
      gradient: 'from-indigo-400 to-purple-500',
      orbitRadius: 310,
      orbitSpeed: '21s',
      size: 'w-26 h-26',
      startAngle: 240
    },
    {
      id: 'assessment',
      icon: Heart,
      title: '自我評量',
      emoji: '💖',
      description: '了解自己',
      gradient: 'from-rose-400 to-pink-500',
      orbitRadius: 275,
      orbitSpeed: '17s',
      size: 'w-18 h-18',
      startAngle: 280
    },
    {
      id: 'wishes',
      icon: Sparkles,
      title: '天燈Go',
      emoji: '✨',
      description: '許願祈福',
      gradient: 'from-yellow-400 to-amber-500',
      orbitRadius: 330,
      orbitSpeed: '23s',
      size: 'w-22 h-22',
      startAngle: 320
    }
  ];

  return (
    <div className="fixed inset-0 z-20">
      {functions.map((func) => (
        <div
          key={func.id}
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
          style={{
            animation: `orbit-${func.id} ${func.orbitSpeed} linear infinite`,
          }}
        >
          <div
            className={`${func.size} transform -translate-x-1/2 -translate-y-1/2`}
            style={{
              marginTop: `-${func.orbitRadius}px`,
            }}
          >
            <Card
              className={`${func.size} bg-gradient-to-br ${func.gradient} backdrop-blur-xl border-2 border-white/40 shadow-2xl cursor-pointer transition-all duration-300 hover:scale-125 active:scale-95 rounded-full overflow-hidden group relative`}
              onClick={() => onFunctionClick(func.id)}
            >
              {/* Planet surface effect */}
              <div className="absolute inset-0 bg-white/10 group-hover:bg-white/20 transition-colors duration-300 rounded-full"></div>
              <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-white/20 rounded-full transform translate-x-2 -translate-y-2 group-hover:scale-150 transition-transform duration-500"></div>
              
              {/* Content */}
              <div className="relative z-10 h-full flex flex-col items-center justify-center p-2 text-center">
                <div className="mb-1 group-hover:scale-110 transition-transform duration-300">
                  <div className="text-lg mb-0.5 animate-bounce" style={{ animationDuration: '2s', animationDelay: `${func.startAngle / 100}s` }}>
                    {func.emoji}
                  </div>
                  <func.icon className="w-4 h-4 text-white mx-auto" strokeWidth={2.5} />
                </div>
                
                <h3 className="text-white font-black text-xs leading-tight group-hover:text-yellow-100 transition-colors duration-300">
                  {func.title}
                </h3>
              </div>

              {/* Orbital trail effect */}
              <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r from-white/20 to-transparent"></div>
            </Card>
          </div>
        </div>
      ))}

      {/* Add orbit animations with CSS */}
      <style jsx>{`
        ${functions.map((func) => `
          @keyframes orbit-${func.id} {
            from {
              transform: translate(-50%, -50%) rotate(${func.startAngle}deg);
            }
            to {
              transform: translate(-50%, -50%) rotate(${func.startAngle + 360}deg);
            }
          }
        `).join('\n')}
      `}</style>
    </div>
  );
}