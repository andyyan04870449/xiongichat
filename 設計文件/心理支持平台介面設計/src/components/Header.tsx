import { Bell, Bot, Shield } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

export function Header() {
  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shadow-sm">
      {/* Left side - System branding */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gradient-to-br from-slate-600 to-slate-700 rounded-lg flex items-center justify-center shadow-md">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg text-slate-800">毒品防治局個案管理系統</h1>
          <p className="text-xs text-slate-500">Drug Prevention Bureau Case Management</p>
        </div>
      </div>

      {/* Right side - AI Assistant & Notifications */}
      <div className="flex items-center gap-4">
        {/* AI Status */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-full">
          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
          <Bot className="w-4 h-4 text-emerald-600" />
          <span className="text-sm text-emerald-700">AI 助理在線</span>
        </div>

        {/* Notifications */}
        <Button variant="ghost" size="sm" className="relative">
          <Bell className="w-5 h-5 text-slate-600" />
          <Badge className="absolute -top-1 -right-1 w-5 h-5 p-0 flex items-center justify-center bg-blue-500 hover:bg-blue-500 text-xs">
            3
          </Badge>
        </Button>

        {/* User info placeholder */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 rounded-lg border border-slate-200">
          <div className="w-6 h-6 bg-slate-400 rounded-full"></div>
          <span className="text-sm text-slate-700">管理員</span>
        </div>
      </div>
    </header>
  );
}