import { 
  MessageCircle, 
  Users, 
  BookOpen, 
  Search, 
  FileText, 
  Baby, 
  Shield, 
  Heart, 
  Sparkles,
  Leaf
} from 'lucide-react';
import { ModuleCard } from './ModuleCard';

export function FunctionPanel() {
  const moduleGroups = [
    {
      title: '即時支持',
      icon: MessageCircle,
      titleColor: 'text-green-600',
      accentLine: 'bg-gradient-to-r from-green-300 to-emerald-300',
      modules: [
        {
          icon: MessageCircle,
          title: '聊天吧',
          description: '與專業心理師或溫暖志工即時對話交流',
          bgGradient: 'bg-gradient-to-br from-green-50/80 to-emerald-50/80',
          iconBg: 'bg-gradient-to-br from-green-400 to-emerald-500',
          shadowColor: 'green-200'
        },
        {
          icon: Users,
          title: '多元輔導',
          description: '個人、團體、家庭等多樣化溫馨輔導服務',
          bgGradient: 'bg-gradient-to-br from-green-50/80 to-emerald-50/80',
          iconBg: 'bg-gradient-to-br from-emerald-400 to-teal-500',
          shadowColor: 'emerald-200'
        }
      ]
    },
    {
      title: '資源導覽',
      icon: BookOpen,
      titleColor: 'text-sky-600',
      accentLine: 'bg-gradient-to-r from-sky-300 to-blue-300',
      modules: [
        {
          icon: BookOpen,
          title: '衛教資源',
          description: '心理健康知識與溫柔自我照護指南',
          bgGradient: 'bg-gradient-to-br from-sky-50/80 to-blue-50/80',
          iconBg: 'bg-gradient-to-br from-sky-400 to-blue-500',
          shadowColor: 'sky-200'
        },
        {
          icon: Search,
          title: '找助資源',
          description: '尋找適合的專業協助與溫暖支持機構',
          bgGradient: 'bg-gradient-to-br from-sky-50/80 to-blue-50/80',
          iconBg: 'bg-gradient-to-br from-blue-400 to-indigo-500',
          shadowColor: 'blue-200'
        },
        {
          icon: FileText,
          title: '資源表單',
          description: '各類申請表單與貼心服務登記',
          bgGradient: 'bg-gradient-to-br from-sky-50/80 to-blue-50/80',
          iconBg: 'bg-gradient-to-br from-indigo-400 to-purple-500',
          shadowColor: 'indigo-200'
        }
      ]
    },
    {
      title: '特殊服務',
      icon: Shield,
      titleColor: 'text-amber-600',
      accentLine: 'bg-gradient-to-r from-amber-300 to-orange-300',
      modules: [
        {
          icon: Baby,
          title: '幼幼專區',
          description: '兒童心理健康專業溫柔支持服務',
          bgGradient: 'bg-gradient-to-br from-amber-50/80 to-orange-50/80',
          iconBg: 'bg-gradient-to-br from-amber-400 to-orange-500',
          shadowColor: 'amber-200'
        },
        {
          icon: Shield,
          title: '戒癮專區',
          description: '成癮問題專業諮詢與溫暖戒治支援',
          bgGradient: 'bg-gradient-to-br from-amber-50/80 to-orange-50/80',
          iconBg: 'bg-gradient-to-br from-orange-400 to-red-500',
          shadowColor: 'orange-200'
        }
      ]
    },
    {
      title: '自我探索',
      icon: Heart,
      titleColor: 'text-pink-600',
      accentLine: 'bg-gradient-to-r from-pink-300 to-rose-300',
      modules: [
        {
          icon: Heart,
          title: '自我評量',
          description: '心理健康狀態溫和自我檢測與評估',
          bgGradient: 'bg-gradient-to-br from-pink-50/80 to-rose-50/80',
          iconBg: 'bg-gradient-to-br from-pink-400 to-rose-500',
          shadowColor: 'pink-200'
        },
        {
          icon: Sparkles,
          title: '天燈Go',
          description: '許願祈福，輕柔釋放心靈深處的壓力',
          bgGradient: 'bg-gradient-to-br from-pink-50/80 to-rose-50/80',
          iconBg: 'bg-gradient-to-br from-rose-400 to-pink-500',
          shadowColor: 'rose-200'
        }
      ]
    }
  ];

  return (
    <div className="h-full bg-white/60 backdrop-blur-sm border border-green-200/50 rounded-3xl shadow-lg shadow-green-100/50 overflow-hidden">
      <div className="h-full overflow-y-auto p-6">
        {/* Header */}
        <div className="mb-8 text-center relative">
          <div className="flex items-center justify-center gap-3 mb-3">
            <Leaf className="w-8 h-8 text-green-500" strokeWidth={1.5} />
            <h1 className="text-2xl text-slate-700 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              心靈療癒服務
            </h1>
            <Leaf className="w-8 h-8 text-green-500 scale-x-[-1]" strokeWidth={1.5} />
          </div>
          <p className="text-sm text-slate-500">選擇適合您的療癒服務</p>
        </div>

        {/* Module Groups */}
        <div className="space-y-8">
          {moduleGroups.map((group, groupIndex) => (
            <div key={groupIndex} className="group">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-9 h-9 bg-gradient-to-br from-white to-gray-50 border border-gray-200/50 rounded-2xl flex items-center justify-center shadow-sm">
                  <group.icon className={`w-5 h-5 ${group.titleColor}`} strokeWidth={1.5} />
                </div>
                <h2 className={`text-lg ${group.titleColor} group-hover:opacity-80 transition-opacity duration-300`}>
                  {group.title}
                </h2>
                <div className={`flex-1 h-0.5 ${group.accentLine} opacity-30 rounded-full`}></div>
              </div>
              
              <div className="space-y-4">
                {group.modules.map((module, moduleIndex) => (
                  <ModuleCard
                    key={moduleIndex}
                    icon={module.icon}
                    title={module.title}
                    description={module.description}
                    bgGradient={module.bgGradient}
                    iconBg={module.iconBg}
                    shadowColor={module.shadowColor}
                    onClick={() => console.log(`進入 ${module.title}`)}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Emergency Contact */}
        <div className="mt-8 p-4 bg-gradient-to-r from-red-50/80 to-orange-50/80 backdrop-blur-sm border border-red-200/50 rounded-2xl shadow-sm shadow-red-100/30">
          <div className="flex items-center gap-3 justify-center">
            <div className="w-3 h-3 bg-red-400 rounded-full animate-pulse shadow-sm"></div>
            <p className="text-sm text-red-600">
              🆘 緊急協助請撥打生命線 1995
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}