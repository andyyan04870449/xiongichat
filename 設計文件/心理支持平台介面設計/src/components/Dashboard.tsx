import { Bot, TrendingUp, Clock, Star, AlertCircle, CheckCircle } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

export function Dashboard() {
  const aiReminders = [
    {
      id: 1,
      type: 'update',
      icon: TrendingUp,
      title: '多元輔導服務更新',
      content: '新增團體諮商時段，週三晚間 7-9 點開放預約',
      time: '2小時前',
      priority: 'medium'
    },
    {
      id: 2,
      type: 'tip',
      icon: Star,
      title: '功能提示',
      content: '天燈Go功能可協助個案進行情緒抒發，建議多加推廣使用',
      time: '1天前',
      priority: 'low'
    },
    {
      id: 3,
      type: 'alert',
      icon: AlertCircle,
      title: '系統提醒',
      content: '本週戒癮專區諮詢量較高，建議關注資源調配',
      time: '3天前',
      priority: 'high'
    }
  ];

  const recentInteractions = [
    {
      id: 1,
      type: 'chat',
      title: '與個案 A001 的對話',
      time: '30分鐘前',
      status: 'completed'
    },
    {
      id: 2,
      type: 'resource',
      title: '查閱戒癮相關衛教資源',
      time: '2小時前',
      status: 'completed'
    },
    {
      id: 3,
      type: 'assessment',
      title: '協助個案進行自我評量',
      time: '昨天',
      status: 'completed'
    }
  ];

  const recommendedResources = [
    {
      id: 1,
      title: '新版戒癮治療指南',
      category: '衛教資源',
      description: '最新的藥物戒治與心理輔導整合方案',
      tag: '熱門',
      bgColor: 'from-blue-50 to-indigo-50',
      borderColor: 'border-blue-200'
    },
    {
      id: 2,
      title: '青少年輔導技巧手冊',
      category: '專區服務',
      description: '針對青少年個案的專業輔導方法與技巧',
      tag: '推薦',
      bgColor: 'from-emerald-50 to-green-50',
      borderColor: 'border-emerald-200'
    },
    {
      id: 3,
      title: '家庭支持系統評估表',
      category: '資源表單',
      description: '評估個案家庭支持網絡的專業工具',
      tag: '實用',
      bgColor: 'from-purple-50 to-violet-50',
      borderColor: 'border-purple-200'
    }
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-orange-600 bg-orange-50 border-orange-200';
      default: return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-2xl text-slate-800 mb-2">個案管理儀表板</h1>
        <p className="text-slate-600">您好！歡迎使用AI助理個案管理系統</p>
      </div>

      {/* AI Reminders */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <Bot className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg text-slate-800">AI 小提醒</h2>
        </div>
        <div className="space-y-3">
          {aiReminders.map((reminder) => (
            <Card key={reminder.id} className={`p-4 ${getPriorityColor(reminder.priority)} border`}>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-white/50 rounded-lg flex items-center justify-center mt-0.5">
                  <reminder.icon className="w-4 h-4" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-sm">{reminder.title}</h3>
                    <Badge variant="secondary" className="text-xs">
                      {reminder.time}
                    </Badge>
                  </div>
                  <p className="text-sm opacity-90 leading-relaxed">{reminder.content}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Recent Interactions */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <Clock className="w-5 h-5 text-emerald-600" />
          <h2 className="text-lg text-slate-800">最近互動紀錄</h2>
        </div>
        <Card className="divide-y divide-slate-100">
          {recentInteractions.map((interaction) => (
            <div key={interaction.id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                <div>
                  <h3 className="text-sm text-slate-800">{interaction.title}</h3>
                  <p className="text-xs text-slate-500">{interaction.time}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                <span className="text-xs text-emerald-600">已完成</span>
              </div>
            </div>
          ))}
        </Card>
      </section>

      {/* Recommended Resources */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <Star className="w-5 h-5 text-amber-600" />
          <h2 className="text-lg text-slate-800">推薦資源</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recommendedResources.map((resource) => (
            <Card key={resource.id} className={`p-4 bg-gradient-to-br ${resource.bgColor} ${resource.borderColor} border hover:shadow-md transition-shadow cursor-pointer`}>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="secondary" className="text-xs">
                    {resource.category}
                  </Badge>
                  <Badge className="text-xs bg-amber-100 text-amber-700 hover:bg-amber-100">
                    {resource.tag}
                  </Badge>
                </div>
                <div>
                  <h3 className="text-sm text-slate-800 mb-2">{resource.title}</h3>
                  <p className="text-xs text-slate-600 leading-relaxed">{resource.description}</p>
                </div>
                <Button size="sm" variant="ghost" className="w-full text-xs">
                  查看詳情
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}