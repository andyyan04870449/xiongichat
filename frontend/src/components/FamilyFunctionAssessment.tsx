import { useState } from 'react'
import { ArrowLeft, Home } from 'lucide-react'
import { Button } from "./ui/button"
import { Card } from "./ui/card"
import { RadioGroup, RadioGroupItem } from "./ui/radio-group"
import { Label } from "./ui/label"
import { Progress } from "./ui/progress"
import { Badge } from "./ui/badge"
import logo from 'figma:asset/e9a9f75d2ac26ddaa75b766f16261c08e59f132c.png'
import { AssessmentComplete } from './AssessmentComplete'

interface Question {
  id: number
  question: string
  options: {
    value: string
    label: string
    score: number
  }[]
}

interface FamilyFunctionAssessmentProps {
  onBack: () => void
}

export function FamilyFunctionAssessment({ onBack }: FamilyFunctionAssessmentProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [showResults, setShowResults] = useState(false)

  const questions: Question[] = [
    {
      id: 1,
      question: '當您遇到困難時，可以求助於家人。',
      options: [
        { value: '2', label: '經常滿意', score: 2 },
        { value: '1', label: '有時滿意', score: 1 },
        { value: '0', label: '幾乎沒有', score: 0 }
      ]
    },
    {
      id: 2,
      question: '家人可以和您討論事情及分攤問題。',
      options: [
        { value: '2', label: '經常滿意', score: 2 },
        { value: '1', label: '有時滿意', score: 1 },
        { value: '0', label: '幾乎沒有', score: 0 }
      ]
    },
    {
      id: 3,
      question: '當您希望從事新活動，或有新的發展方向時，家人都能夠接受且給予鼓勵支持。',
      options: [
        { value: '2', label: '經常滿意', score: 2 },
        { value: '1', label: '有時滿意', score: 1 },
        { value: '0', label: '幾乎沒有', score: 0 }
      ]
    },
    {
      id: 4,
      question: '對於您的情緒表達，家人都能接受。',
      options: [
        { value: '2', label: '經常滿意', score: 2 },
        { value: '1', label: '有時滿意', score: 1 },
        { value: '0', label: '幾乎沒有', score: 0 }
      ]
    },
    {
      id: 5,
      question: '家人與您相處的方式。',
      options: [
        { value: '2', label: '經常滿意', score: 2 },
        { value: '1', label: '有時滿意', score: 1 },
        { value: '0', label: '幾乎沒有', score: 0 }
      ]
    }
  ]

  const handleAnswerChange = (value: string) => {
    setAnswers({ ...answers, [currentQuestion]: value })
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

  const progress = ((currentQuestion + 1) / questions.length) * 100

  if (showResults) {
    return <AssessmentComplete onBack={onBack} assessmentTitle="家庭功能評估表" />
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
                  <h1 className="text-lg md:text-xl font-semibold text-gray-800">家庭功能評估表</h1>
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
              <div className="text-white p-2 rounded-lg" style={{ backgroundColor: '#8b5cf6' }}>
                <Home className="w-5 h-5" />
              </div>
              <Badge variant="outline" className="text-sm">
                題目 {currentQuestion + 1}
              </Badge>
            </div>
            <h2 className="text-xl font-semibold text-gray-800 leading-relaxed">
              {questions[currentQuestion].question}
            </h2>
          </div>

          <RadioGroup value={answers[currentQuestion] || ''} onValueChange={handleAnswerChange}>
            <div className="space-y-4">
              {questions[currentQuestion].options.map((option) => (
                <div key={option.value} className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-gray-50 transition-colors" style={{ borderColor: 'var(--theme-border)' }}>
                  <RadioGroupItem value={option.value} id={option.value} />
                  <Label htmlFor={option.value} className="flex-1 cursor-pointer text-gray-700">
                    {option.label}
                  </Label>
                </div>
              ))}
            </div>
          </RadioGroup>

          <div className="flex justify-between mt-8">
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
              disabled={!answers[currentQuestion]}
              className="text-white"
              style={{ backgroundColor: '#8b5cf6' }}
            >
              {currentQuestion === questions.length - 1 ? '完成評估' : '下一題'}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}