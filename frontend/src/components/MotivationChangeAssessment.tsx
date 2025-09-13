import { useState } from 'react'
import { ArrowLeft, Users } from 'lucide-react'
import { Button } from "./ui/button"
import { Card } from "./ui/card"
import { Label } from "./ui/label"
import { Progress } from "./ui/progress"
import { Badge } from "./ui/badge"
import { Input } from "./ui/input"
import logo from 'figma:asset/e9a9f75d2ac26ddaa75b766f16261c08e59f132c.png'
import { AssessmentComplete } from './AssessmentComplete'

interface Question {
  id: number
  title: string
  description: string
  placeholder: string
}

interface MotivationChangeAssessmentProps {
  onBack: () => void
}

export function MotivationChangeAssessment({ onBack }: MotivationChangeAssessmentProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [showResults, setShowResults] = useState(false)

  const questions: Question[] = [
    {
      id: 1,
      title: '目前來說，改變用藥行為對您來說有多重要?',
      description: '請用0~100的數字來表示您的感受程度，數字越大表示越重要。',
      placeholder: '請填入0-100之間的數字'
    },
    {
      id: 2,
      title: '目前來說，對於改變用藥行為，您有多大的信心?',
      description: '請用0~100的數字來表示您的感受程度，數字越大表示越有信心。',
      placeholder: '請填入0-100之間的數字'
    }
  ]

  const handleAnswerChange = (value: string) => {
    // 只允許數字輸入，並限制在0-100範圍內
    const numValue = value.replace(/[^0-9]/g, '')
    if (numValue === '' || (parseInt(numValue) >= 0 && parseInt(numValue) <= 100)) {
      setAnswers({ ...answers, [currentQuestion]: numValue })
    }
  }

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    } else {
      setShowResults(true)
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const isAnswerValid = () => {
    const answer = answers[currentQuestion]
    return answer && answer.trim() !== '' && parseInt(answer) >= 0 && parseInt(answer) <= 100
  }

  const progress = ((currentQuestion + 1) / questions.length) * 100

  if (showResults) {
    return <AssessmentComplete onBack={onBack} assessmentTitle="改變動機評估" />
  }

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
                  <h1 className="text-lg md:text-xl font-semibold text-gray-800">改變動機評估</h1>
                  <p className="text-xs md:text-sm text-gray-600 hidden sm:block">第 {currentQuestion + 1} 題，共 {questions.length} 題</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-4 md:p-8">
        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">進度</span>
            <span className="text-sm text-gray-600">{currentQuestion + 1} / {questions.length}</span>
          </div>
          <Progress value={progress} className="h-3" />
        </div>

        {/* Question Card */}
        <Card className="p-6 md:p-8 bg-white/90 backdrop-blur-sm border" style={{ borderColor: 'var(--theme-border)' }}>
          <div className="mb-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="text-white p-2 rounded-lg" style={{ backgroundColor: '#10b981' }}>
                <Users className="w-5 h-5" />
              </div>
              <Badge variant="outline" className="text-sm">
                題目 {currentQuestion + 1}
              </Badge>
            </div>
            <h2 className="text-xl font-semibold text-gray-800 leading-relaxed mb-3">
              {questions[currentQuestion].title}
            </h2>
            <p className="text-gray-600 text-sm mb-6">
              {questions[currentQuestion].description}
            </p>
          </div>

          {/* Number Input */}
          <div className="mb-8">
            <Label htmlFor="answer" className="text-sm font-medium text-gray-700 mb-2 block">
              填入數字
            </Label>
            <Input
              id="answer"
              type="text"
              value={answers[currentQuestion] || ''}
              onChange={(e) => handleAnswerChange(e.target.value)}
              placeholder={questions[currentQuestion].placeholder}
              className="text-lg p-4 text-center"
              style={{ borderColor: 'var(--theme-border)' }}
            />
            <div className="flex justify-between text-xs text-gray-500 mt-2">
              <span>0 (最低)</span>
              <span>100 (最高)</span>
            </div>
          </div>

          <div className="flex justify-between">
            <Button 
              variant="outline" 
              onClick={handlePrevious} 
              disabled={currentQuestion === 0}
              style={{ borderColor: 'var(--theme-border)' }}
            >
              上一題
            </Button>
            <Button 
              onClick={handleNext}
              disabled={!isAnswerValid()}
              className="text-white"
              style={{ backgroundColor: '#10b981' }}
            >
              {currentQuestion === questions.length - 1 ? '完成評估' : '下一題'}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}