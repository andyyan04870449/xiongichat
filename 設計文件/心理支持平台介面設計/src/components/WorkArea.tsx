import { Dashboard } from './Dashboard';
import { ChatArea } from './ChatArea';
import { Card } from './ui/card';
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

interface WorkAreaProps {
  activeModule: string;
}

export function WorkArea({ activeModule }: WorkAreaProps) {
  const renderModuleContent = () => {
    switch (activeModule) {
      case 'dashboard':
        return <Dashboard />;
      
      case 'chat':
        return <ChatArea />;
      
      default:
        return (
          <div className="flex-1 flex items-center justify-center p-8">
            <Card className="p-8 text-center max-w-md">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                {getModuleIcon(activeModule)}
              </div>
              <h3 className="text-lg text-slate-800 mb-2">{getModuleTitle(activeModule)}</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                此功能模組正在開發中，敬請期待。
              </p>
            </Card>
          </div>
        );
    }
  };

  const getModuleIcon = (moduleId: string) => {
    const iconMap: { [key: string]: React.ComponentType<any> } = {
      counseling: Users,
      education: BookOpen,
      resources: Search,
      forms: FileText,
      children: Baby,
      recovery: Shield,
      assessment: Heart,
      wishes: Sparkles
    };
    
    const IconComponent = iconMap[moduleId] || MessageCircle;
    return <IconComponent className="w-8 h-8 text-slate-600" />;
  };

  const getModuleTitle = (moduleId: string) => {
    const titleMap: { [key: string]: string } = {
      counseling: '多元輔導',
      education: '衛教資源',
      resources: '找助資源',
      forms: '資源表單',
      children: '幼幼專區',
      recovery: '戒癮專區',
      assessment: '自我評量',
      wishes: '天燈Go'
    };
    
    return titleMap[moduleId] || '功能模組';
  };

  return (
    <main className="flex-1 bg-white flex flex-col">
      {renderModuleContent()}
    </main>
  );
}