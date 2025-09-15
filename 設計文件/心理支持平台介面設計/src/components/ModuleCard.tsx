import { LucideIcon } from 'lucide-react';
import { Card } from './ui/card';

interface ModuleCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  bgGradient: string;
  iconBg: string;
  shadowColor: string;
  onClick?: () => void;
}

export function ModuleCard({ icon: Icon, title, description, bgGradient, iconBg, shadowColor, onClick }: ModuleCardProps) {
  return (
    <Card 
      className={`p-5 ${bgGradient} border border-white/30 hover:border-white/50 transition-all duration-300 cursor-pointer group hover:shadow-lg hover:shadow-${shadowColor}/20 hover:scale-[1.02] rounded-2xl backdrop-blur-sm`}
      onClick={onClick}
    >
      <div className="flex items-start gap-4">
        <div className={`w-12 h-12 ${iconBg} rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-md shadow-${shadowColor}/30`}>
          <Icon className="w-6 h-6 text-white" strokeWidth={1.5} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-slate-700 mb-2 group-hover:text-slate-800 transition-colors duration-300">{title}</h3>
          <p className="text-sm text-slate-600 leading-relaxed group-hover:text-slate-700 transition-colors duration-300">{description}</p>
        </div>
      </div>
      
      {/* Subtle inner glow */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
    </Card>
  );
}