import { useState } from 'react'
import { ArrowLeft, ClipboardList, Heart, Brain, Users, Home, ChevronRight, Info, Shield } from 'lucide-react'
import { Button } from "./ui/button"
import { Card } from "./ui/card"
import { Badge } from "./ui/badge"
import logo from 'figma:asset/e9a9f75d2ac26ddaa75b766f16261c08e59f132c.png'

interface AssessmentCategory {
  id: string
  title: string
  description: string
  duration: string
  questions: number
  icon: React.ReactNode
  color: string
  bgColor: string
  importance: string
}

interface AssessmentPageProps {
  onBack: () => void
  onStartAssessment: (assessmentId: string) => void
}

export function AssessmentPage({ onBack, onStartAssessment }: AssessmentPageProps) {
  const assessmentCategories: AssessmentCategory[] = [
    {
      id: 'emotion-suicide',
      title: '情緒與自殺風險評估',
      description: '評估當前的情緒狀態、壓力水平及自殺風險因子，幫助及早發現需要協助的狀況',
      duration: '3-5分鐘',
      questions: 6,
      icon: <Heart className="w-8 h-8 md:w-10 md:h-10" />,
      color: '#ef4444',
      bgColor: '#fef2f2',
      importance: '高度重要'
    },
    {
      id: 'substance-dependency',
      title: '物質依賴評估',
      description: '檢測對各種物質的依賴程度，包括酒精、毒品等，提供專業的依賴程度分析',
      duration: '3-5分鐘',
      questions: 5,
      icon: <Brain className="w-8 h-8 md:w-10 md:h-10" />,
      color: '#f59e0b',
      bgColor: '#fffbeb',
      importance: '核心評估'
    },
    {
      id: 'motivation-change',
      title: '改變動機評估',
      description: '評估個人對於改變現狀的動機與準備度，協助制定適合的康復計畫',
      duration: '2-3分鐘',
      questions: 2,
      icon: <Users className="w-8 h-8 md:w-10 md:h-10" />,
      color: '#10b981',
      bgColor: '#ecfdf5',
      importance: '重要指標'
    },
    {
      id: 'family-function',
      title: '家庭功能評估表',
      description: '分析家庭支持系統的完整性與功能性，評估家庭關係對康復過程的影響',
      duration: '3-5分鐘',
      questions: 5,
      icon: <Home className="w-8 h-8 md:w-10 md:h-10" />,
      color: '#8b5cf6',
      bgColor: '#f5f3ff',
      importance: '支持系統'
    }
  ]

  return (
    <div 
      className="min-h-screen"
      style={{
        background: `linear-gradient(135deg, var(--theme-background), var(--theme-surface))`
      }}
    >
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-sm shadow-sm border-b" style={{ borderColor: 'var(--theme-border)' }}>
        <div className="max-w-7xl mx-auto px-4 py-3 md:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 md:space-x-4">
              <Button variant="ghost" size="sm" onClick={onBack} className="text-gray-600 hover:text-gray-800">
                <ArrowLeft className="w-4 h-4 mr-0 md:mr-2" />
                <span className="hidden md:inline">返回</span>
              </Button>
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <img src={logo} alt="雄i聊" className="h-8 md:h-12 w-auto" />
                </div>
                <div>
                  <h1 className="text-lg md:text-xl font-semibold text-gray-800">自我評量中心</h1>
                  <p className="text-xs md:text-sm text-gray-600 hidden sm:block">專業評估工具 · 了解自我狀況</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-4 md:p-8">
        {/* Introduction Section */}
        <div className="mb-8 md:mb-12">
          <Card className="p-6 md:p-8 bg-white/90 backdrop-blur-sm border" style={{ borderColor: 'var(--theme-border)' }}>
            <div className="flex items-start space-x-4">
              <div 
                className="text-white p-3 rounded-lg flex-shrink-0"
                style={{ backgroundColor: 'var(--theme-primary)' }}
              >
                <ClipboardList className="w-8 h-8" />
              </div>
              <div className="flex-1">
                <h2 className="text-xl md:text-2xl font-semibold text-gray-800 mb-3">專業自我評量系統</h2>
                <p className="text-gray-600 leading-relaxed mb-4">
                  我們提供四種專業評量工具，協助您更深入了解自己的狀況。每項評量都經過專業設計，
                  結果將有助於制定個人化的康復計畫和支持策略。
                </p>
                <div className="flex flex-wrap gap-2 mb-4">
                  <Badge variant="outline" className="text-xs" style={{ borderColor: 'var(--theme-primary)', color: 'var(--theme-primary)' }}>
                    專業設計
                  </Badge>
                  <Badge variant="outline" className="text-xs" style={{ borderColor: 'var(--theme-secondary)', color: 'var(--theme-secondary)' }}>
                    保密安全
                  </Badge>
                  <Badge variant="outline" className="text-xs" style={{ borderColor: 'var(--theme-accent)', color: 'var(--theme-accent)' }}>
                    即時結果
                  </Badge>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start space-x-3">
                  <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm text-blue-800 font-medium mb-1">重要提醒</p>
                    <p className="text-sm text-blue-700">
                      評量結果僅供參考，不能取代專業醫療診斷。如有嚴重困擾，請尋求專業協助。
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Assessment Categories */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
          {assessmentCategories.map((assessment) => (
            <Card 
              key={assessment.id}
              className="group hover:shadow-lg transition-all duration-300 border-2 hover:border-current bg-white/80 backdrop-blur-sm"
              style={{ borderColor: 'var(--theme-border)' }}
            >
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div 
                    className="text-white p-3 rounded-lg flex-shrink-0"
                    style={{ backgroundColor: assessment.color }}
                  >
                    {assessment.icon}
                  </div>
                  <div className="text-right">
                    <Badge 
                      variant="outline" 
                      className="text-xs mb-2"
                      style={{ 
                        borderColor: assessment.color, 
                        color: assessment.color,
                        backgroundColor: assessment.bgColor
                      }}
                    >
                      {assessment.importance}
                    </Badge>
                  </div>
                </div>

                {/* Content */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">
                    {assessment.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed text-sm mb-4">
                    {assessment.description}
                  </p>
                  
                  {/* Stats */}
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-1">
                        <ClipboardList className="w-4 h-4" />
                        <span>{assessment.questions}題</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <circle cx="12" cy="12" r="10"></circle>
                          <polyline points="12,6 12,12 16,14"></polyline>
                        </svg>
                        <span>{assessment.duration}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Action Button */}
                <Button 
                  onClick={() => onStartAssessment(assessment.id)}
                  className="w-full group-hover:scale-105 transition-transform duration-200 text-white"
                  style={{
                    background: `linear-gradient(to right, ${assessment.color}, ${assessment.color}dd)`
                  }}
                >
                  開始評量
                  <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </Card>
          ))}
        </div>

        {/* Privacy Notice */}
        <Card className="mt-8 p-6 bg-gray-50/80 backdrop-blur-sm border" style={{ borderColor: 'var(--theme-border)' }}>
          <div className="flex items-start space-x-3">
            <Shield className="w-6 h-6 text-gray-600 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-gray-800 mb-2">隱私保護承諾</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                所有評量資料均經過加密處理，僅用於生成個人化建議。我們承諾不會將您的資料用於其他目的，
                並嚴格遵守相關隱私保護法規。您可隨時要求刪除個人資料。
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}