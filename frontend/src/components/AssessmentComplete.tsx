import { ArrowLeft } from 'lucide-react'
import { Button } from "./ui/button"
import logo from 'figma:asset/e9a9f75d2ac26ddaa75b766f16261c08e59f132c.png'

interface AssessmentCompleteProps {
  onBack: () => void
  assessmentTitle?: string
}

export function AssessmentComplete({ onBack, assessmentTitle = '評估' }: AssessmentCompleteProps) {
  return (
    <div 
      className="min-h-screen"
      style={{
        background: `linear-gradient(135deg, var(--theme-background), var(--theme-surface))`
      }}
    >
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-sm shadow-sm border-b" style={{ borderColor: 'var(--theme-border)' }}>
        <div className="max-w-4xl mx-auto px-4 py-3 md:py-4">
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
                <h1 className="text-lg md:text-xl font-semibold text-gray-800">{assessmentTitle}完成</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-4 md:p-8">
        {/* Logo and Thank You Message - No Card wrapper */}
        <div className="text-center py-6 md:py-12">
          <div className="flex justify-center mb-6">
            <img src={logo} alt="雄i聊" className="h-12 md:h-16 w-auto" />
          </div>
          
          <h2 className="text-xl md:text-2xl font-semibold text-gray-800 mb-4">
            評估完成
          </h2>

          <p className="text-base md:text-lg text-gray-700 mb-6">
            感謝您完成評估
          </p>

          <div className="flex justify-center">
            <Button
              onClick={onBack}
              className="px-6 py-2.5 text-white"
              style={{ backgroundColor: 'var(--theme-primary)' }}
            >
              返回評量中心
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}