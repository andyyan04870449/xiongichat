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
  Home,
  ChevronRight
} from 'lucide-react';
import { Card } from './ui/card';
import { Button } from './ui/button';

interface SidebarProps {
  activeModule: string;
  onModuleChange: (module: string) => void;
}

export function Sidebar({ activeModule, onModuleChange }: SidebarProps) {
  const moduleGroups = [
    {
      title: '首頁儀表板',
      modules: [
        {
          id: 'dashboard',
          icon: Home,
          title: '儀表板',
          description: '總覽與AI助理'
        }
      ]
    },
    {
      title: '即時互動',
      modules: [
        {
          id: 'chat',
          icon: MessageCircle,
          title: '聊天吧',
          description: '即時對話支持'
        },
        {
          id: 'counseling',
          icon: Users,
          title: '多元輔導',
          description: '專業輔導服務'
        }
      ]
    },
    {
      title: '資源中心',
      modules: [
        {
          id: 'education',
          icon: BookOpen,
          title: '衛教資源',
          description: '健康教育資料'
        },
        {
          id: 'resources',
          icon: Search,
          title: '找助資源',
          description: '協助資源查詢'
        },
        {
          id: 'forms',
          icon: FileText,
          title: '資源表單',
          description: '申請與登記表單'
        }
      ]
    },
    {
      title: '專區服務',
      modules: [
        {
          id: 'children',
          icon: Baby,
          title: '幼幼專區',
          description: '兒童專屬服務'
        },
        {
          id: 'recovery',
          icon: Shield,
          title: '戒癮專區',
          description: '戒治支援服務'
        }
      ]
    },
    {
      title: '自我探索',
      modules: [
        {
          id: 'assessment',
          icon: Heart,
          title: '自我評量',
          description: '健康狀態評估'
        },
        {
          id: 'wishes',
          icon: Sparkles,
          title: '天燈Go',
          description: '許願祈福平台'
        }
      ]
    }
  ];

  return (
    <aside className="w-80 bg-slate-50 border-r border-slate-200 flex flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-6">
          {moduleGroups.map((group, groupIndex) => (
            <div key={groupIndex}>
              <h3 className="text-sm text-slate-600 mb-3 px-2">{group.title}</h3>
              <div className="space-y-1">
                {group.modules.map((module) => (
                  <Button
                    key={module.id}
                    onClick={() => onModuleChange(module.id)}
                    variant="ghost"
                    className={`w-full justify-start p-3 h-auto ${
                      activeModule === module.id
                        ? 'bg-blue-50 border border-blue-200 text-blue-700 hover:bg-blue-50'
                        : 'hover:bg-white hover:border hover:border-slate-200 text-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        activeModule === module.id
                          ? 'bg-blue-100'
                          : 'bg-slate-100'
                      }`}>
                        <module.icon className={`w-4 h-4 ${
                          activeModule === module.id ? 'text-blue-600' : 'text-slate-600'
                        }`} />
                      </div>
                      <div className="text-left flex-1">
                        <div className="text-sm mb-0.5">{module.title}</div>
                        <div className="text-xs text-slate-500">{module.description}</div>
                      </div>
                      {activeModule === module.id && (
                        <ChevronRight className="w-4 h-4 text-blue-600" />
                      )}
                    </div>
                  </Button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-slate-200">
        <Card className="p-3 bg-gradient-to-r from-red-50 to-orange-50 border-red-200">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <p className="text-xs text-red-700">
              緊急專線：1995 (24小時)
            </p>
          </div>
        </Card>
      </div>
    </aside>
  );
}