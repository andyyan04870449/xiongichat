import { useState, useEffect } from 'react'
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Heart, Shield, Users, BookOpen } from 'lucide-react'
import logo from 'figma:asset/e9a9f75d2ac26ddaa75b766f16261c08e59f132c.png'
import bearAvatar from 'figma:asset/d2489a7281852ae82edf81f47c4ed2529464e955.png'

interface LoginPageProps {
  onLogin: (password: string) => void
}

export function LoginPage({ onLogin }: LoginPageProps) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [displayedText, setDisplayedText] = useState('')
  const [textIndex, setTextIndex] = useState(0)
  
  const welcomeMessage = "歡迎您的到來，\n很高興為您服務！\n有需要我們來協助嗎？\n\n請輸入通關密碼💡"
  
  // 打字機效果
  useEffect(() => {
    if (textIndex < welcomeMessage.length) {
      const timer = setTimeout(() => {
        setDisplayedText(prev => prev + welcomeMessage[textIndex])
        setTextIndex(prev => prev + 1)
      }, 100) // 調整打字速度 - 減慢一半
      
      return () => clearTimeout(timer)
    }
  }, [textIndex, welcomeMessage])

  const handleLogin = () => {
    // 驗證密碼不為空
    if (password && password.trim().length > 0) {
      onLogin(password.trim())
    } else {
      setError('請輸入通關密碼')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleLogin()
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden" style={{
      background: `linear-gradient(135deg, var(--theme-gradient-from), var(--theme-gradient-via), var(--theme-gradient-to))`
    }}>
      {/* Custom Background Design */}
      <div className="absolute inset-0">
        {/* Geometric shapes for visual interest */}
        <div className="absolute top-0 left-0 w-64 h-64 md:w-96 md:h-96 bg-white/10 rounded-full"></div>
        <div className="absolute bottom-0 right-0 w-48 h-48 md:w-80 md:h-80 rounded-full" style={{
          backgroundColor: `${CSS.supports('color', 'var(--theme-secondary)') ? 'var(--theme-secondary)' : '#fbbf24'}15`
        }}></div>
        <div className="absolute top-1/2 left-1/4 w-32 h-32 md:w-64 md:h-64 bg-white/15 rounded-full"></div>
        
        {/* Floating elements */}
        <div className="absolute top-20 right-20 w-4 h-4 bg-white/25 rounded-full animate-pulse"></div>
        <div className="absolute top-40 right-40 w-6 h-6 bg-white/20 rounded-full animate-pulse delay-1000"></div>
        <div className="absolute bottom-40 left-20 w-5 h-5 bg-white/25 rounded-full animate-pulse delay-2000"></div>
        
        {/* Pattern overlay */}
        <div className="absolute inset-0" style={{
          background: `linear-gradient(to top, ${CSS.supports('color', 'var(--theme-accent)') ? 'var(--theme-accent)' : '#d97706'}20, transparent, white/8)`
        }}></div>
      </div>

      {/* Content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="p-4 md:p-8">
          <div className="flex items-center space-x-3 md:space-x-6">
            <div className="bg-white rounded-xl md:rounded-2xl p-2 md:p-3 shadow-sm">
              <img src={logo} alt="雄i聊" className="h-15 md:h-16 w-auto" />
            </div>
            <div className="text-gray-700">
              <h1 className="text-xl md:text-3xl font-bold mb-1 md:mb-2" style={{ color: 'var(--theme-text)' }}>
                雄i 聊智能客服機器人
              </h1>
              <p className="text-sm md:text-xl" style={{ color: 'var(--theme-text-secondary)' }}>
                高雄市毒品防制局
              </p>
              <p className="text-xs md:text-lg mt-0.5 md:mt-1" style={{ color: 'var(--theme-text-secondary)' }}>
                專業關懷 · 陪伴康復
              </p>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <div className="flex-1 flex items-center justify-center px-4 md:px-8">
          <div className="max-w-6xl w-full">
            {/* Mobile and Desktop Layout */}
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-8 lg:space-y-0">
              {/* Welcome content */}
              <div className="flex-1 max-w-lg mx-auto lg:mx-0 lg:max-w-lg space-y-6 md:space-y-12">
                {/* Main Welcome */}
                <div className="text-center space-y-4 md:space-y-8">
                  {/* 手機版熊熊圖示 - 放大200% */}
                  <div className="block md:hidden">
                    <div className="inline-flex items-center justify-center w-60 h-60 bg-white/20 rounded-full mb-4">
                      <img src={bearAvatar} alt="雄i聊熊熊" className="w-45 h-45 object-contain" />
                    </div>
                  </div>
                  <div>
                    <div className="min-h-[120px] md:min-h-[200px] flex items-center justify-center">
                      <p className="text-lg md:text-2xl leading-relaxed text-center whitespace-pre-line" style={{ color: 'var(--theme-text)' }}>
                        {displayedText}
                        <span className="animate-pulse">|</span>
                      </p>
                    </div>
                  </div>
                </div>

                {/* Visual Elements */}
                <div className="flex justify-center space-x-4 md:space-x-8">
                  <div className="text-center">
                    <div className="w-12 h-12 md:w-16 md:h-16 bg-white/15 rounded-full flex items-center justify-center mb-2 md:mb-3">
                      <Heart className="w-5 h-5 md:w-8 md:h-8" style={{ color: 'var(--theme-primary)' }} />
                    </div>
                    <p className="text-xs md:text-sm" style={{ color: 'var(--theme-text)' }}>用愛陪伴</p>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 md:w-16 md:h-16 bg-white/15 rounded-full flex items-center justify-center mb-2 md:mb-3">
                      <Shield className="w-5 h-5 md:w-8 md:h-8" style={{ color: 'var(--theme-secondary)' }} />
                    </div>
                    <p className="text-xs md:text-sm" style={{ color: 'var(--theme-text)' }}>安全保密</p>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 md:w-16 md:h-16 bg-white/15 rounded-full flex items-center justify-center mb-2 md:mb-3">
                      <Users className="w-5 h-5 md:w-8 md:h-8" style={{ color: 'var(--theme-accent)' }} />
                    </div>
                    <p className="text-xs md:text-sm" style={{ color: 'var(--theme-text)' }}>專業諮詢</p>
                  </div>
                </div>
              </div>

              {/* Video animation space - Hidden on mobile, shown on desktop */}
              <div className="hidden lg:flex flex-1 justify-center items-center">
                <div className="flex items-center justify-center">
                  <img src={bearAvatar} alt="雄i聊熊熊" className="w-80 h-80 object-contain" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Login Section */}
        <div className="bg-white border-t border-gray-200 p-4 md:p-8">
          <div className="max-w-6xl mx-auto">
            {/* Mobile Layout */}
            <div className="block md:hidden space-y-4">
              <div className="flex items-center justify-center space-x-2 mb-3">
                <Shield className="w-5 h-5" style={{ color: 'var(--theme-primary)' }} />
                <label className="text-gray-700 font-semibold">通關密碼</label>
              </div>
              <div className="space-y-3">
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    setError('')
                  }}
                  placeholder="請輸入您的通關密碼"
                  className="h-12 text-base bg-white border-gray-300"
                  style={{
                    borderColor: 'var(--theme-border)',
                    '--tw-ring-color': 'var(--theme-primary)'
                  }}
                  onKeyPress={handleKeyPress}
                />
                {error && (
                  <p className="text-red-500 text-sm">{error}</p>
                )}
                <Button 
                  onClick={handleLogin}
                  className="w-full font-semibold py-3 h-12 text-white"
                  style={{
                    background: `linear-gradient(to right, var(--theme-primary), var(--theme-secondary))`,
                    color: 'white'
                  }}
                >
                  進入系統
                </Button>
              </div>
            </div>

            {/* Desktop Layout */}
            <div className="hidden md:flex items-center justify-center space-x-6">
              <div className="flex items-center space-x-2">
                <Shield className="w-6 h-6" style={{ color: 'var(--theme-primary)' }} />
                <label className="text-gray-700 font-semibold text-lg">通關密碼</label>
              </div>
              <div className="flex-1 max-w-lg">
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    setError('')
                  }}
                  placeholder="請輸入您的通關密碼"
                  className="h-12 text-lg bg-white border-gray-300"
                  style={{
                    borderColor: 'var(--theme-border)',
                    '--tw-ring-color': 'var(--theme-primary)'
                  }}
                  onKeyPress={handleKeyPress}
                />
                {error && (
                  <p className="text-red-500 text-sm mt-2">{error}</p>
                )}
              </div>
              <Button 
                onClick={handleLogin}
                className="font-semibold px-8 py-3 h-12 text-lg text-white"
                style={{
                  background: `linear-gradient(to right, var(--theme-primary), var(--theme-secondary))`,
                  color: 'white'
                }}
              >
                進入系統
              </Button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div 
          className="text-center py-4 md:py-6"
          style={{ 
            backgroundColor: `${CSS.supports('color', 'var(--theme-accent)') ? 'var(--theme-accent)' : '#d97706'}CC`
          }}
        >
          <div className="flex items-center justify-center space-x-2 mb-2">
            <Heart className="w-4 h-4 md:w-5 md:h-5 text-white/80" />
            <span className="text-white font-medium text-sm md:text-base">雄i 聊 · 用愛陪伴</span>
          </div>
          <p className="text-xs md:text-sm text-white/90">
            ※ 為保護您的隱私，請妥善保管通關密碼
          </p>
          <p className="text-xs text-white/80 mt-1">
            高雄市毒品防制局 © 2025 版權所有
          </p>
        </div>
      </div>
    </div>
  )
}