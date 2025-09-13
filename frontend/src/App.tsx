import { useState, useEffect, useCallback } from 'react'
import { LoginPage } from './components/LoginPage'
import { ChatPage } from './components/ChatPage'
import { AssessmentPage } from './components/AssessmentPage'
import { EmotionSuicideAssessment } from './components/EmotionSuicideAssessment'
import { SubstanceDependencyAssessment } from './components/SubstanceDependencyAssessment'
import { MotivationChangeAssessment } from './components/MotivationChangeAssessment'
import { FamilyFunctionAssessment } from './components/FamilyFunctionAssessment'
import { ColorPalette } from './components/ColorPalette'
import { ThemeProvider, useTheme } from './components/ThemeProvider'
import { Button } from './components/ui/button'
import { Palette, ChevronUp, ChevronDown } from 'lucide-react'

type AppView = 'login' | 'chat' | 'assessment' | 'assessment-detail'
type AssessmentType = 'emotion-suicide' | 'substance-dependency' | 'motivation-change' | 'family-function'

function ThemeButton() {
  const { currentScheme, setColorScheme, colorSchemes } = useTheme()
  const [showColorPalette, setShowColorPalette] = useState(false)

  // 獲取當前主題在陣列中的索引
  const getCurrentThemeIndex = useCallback(() => {
    return colorSchemes.findIndex(scheme => scheme.name === currentScheme.name)
  }, [colorSchemes, currentScheme.name])

  // 切換到下一個主題
  const switchToNextTheme = useCallback(() => {
    const currentIndex = getCurrentThemeIndex()
    const nextIndex = (currentIndex + 1) % colorSchemes.length
    setColorScheme(colorSchemes[nextIndex].name)
  }, [getCurrentThemeIndex, colorSchemes, setColorScheme])

  // 切換到上一個主題
  const switchToPrevTheme = useCallback(() => {
    const currentIndex = getCurrentThemeIndex()
    const prevIndex = currentIndex === 0 ? colorSchemes.length - 1 : currentIndex - 1
    setColorScheme(colorSchemes[prevIndex].name)
  }, [getCurrentThemeIndex, colorSchemes, setColorScheme])

  // 鍵盤事件處理
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // 只有在沒有輸入框被聚焦時才響應方向鍵
      if (document.activeElement?.tagName === 'INPUT' || 
          document.activeElement?.tagName === 'TEXTAREA') {
        return
      }

      if (event.key === 'ArrowUp') {
        event.preventDefault()
        switchToPrevTheme()
      } else if (event.key === 'ArrowDown') {
        event.preventDefault()
        switchToNextTheme()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [switchToPrevTheme, switchToNextTheme])

  return (
    <>
      <div className="fixed top-4 right-4 z-40 flex flex-col items-end space-y-2">
        {/* Debug模式指示器 */}
        <div className="bg-red-500/90 backdrop-blur-sm text-white text-xs px-2 py-1 rounded shadow-lg">
          🐛 DEBUG MODE (F12)
        </div>
        
        {/* 主題預覽卡片 */}
        <div 
          className="bg-white/95 backdrop-blur-sm border border-gray-300 rounded-lg shadow-lg p-3 min-w-[200px]"
          style={{ borderColor: 'var(--theme-border)' }}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-600">當前主題</span>
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              <ChevronUp className="w-3 h-3" />
              <ChevronDown className="w-3 h-3" />
            </div>
          </div>
          <div className="flex items-center space-x-2 mb-2">
            <div 
              className="w-4 h-4 rounded border border-gray-300"
              style={{ backgroundColor: 'var(--theme-primary)' }}
            />
            <span className="font-medium text-sm" style={{ color: 'var(--theme-text)' }}>
              {currentScheme.shortName || currentScheme.displayName}
            </span>
          </div>
          <p className="text-xs text-gray-600 mb-2">{currentScheme.description}</p>
          
          {/* 色彩預覽 */}
          <div className="grid grid-cols-4 gap-1">
            <div 
              className="w-full h-4 rounded border border-gray-200"
              style={{ backgroundColor: currentScheme.colors.primary }}
              title="主要色"
            />
            <div 
              className="w-full h-4 rounded border border-gray-200"
              style={{ backgroundColor: currentScheme.colors.secondary }}
              title="次要色"
            />
            <div 
              className="w-full h-4 rounded border border-gray-200"
              style={{ backgroundColor: currentScheme.colors.accent }}
              title="強調色"
            />
            <div 
              className="w-full h-4 rounded border border-gray-200"
              style={{ backgroundColor: currentScheme.colors.surface }}
              title="表面色"
            />
          </div>
          
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-gray-500">
              {getCurrentThemeIndex() + 1}/{colorSchemes.length}
            </span>
            <div className="flex items-center space-x-1">
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
                onClick={switchToPrevTheme}
              >
                <ChevronUp className="w-3 h-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
                onClick={switchToNextTheme}
              >
                <ChevronDown className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>

        {/* 調色盤按鈕 */}
        <Button
          onClick={() => setShowColorPalette(true)}
          className="bg-white/90 backdrop-blur-sm text-gray-700 border border-gray-300 hover:bg-white hover:text-gray-900 shadow-lg"
          size="sm"
          style={{ borderColor: 'var(--theme-border)' }}
        >
          <Palette className="w-4 h-4 mr-2" style={{ color: 'var(--theme-primary)' }} />
          詳細設定
        </Button>

        {/* Color Palette Panel */}
        <ColorPalette 
          isVisible={showColorPalette}
          onClose={() => setShowColorPalette(false)}
        />
      </div>

      {/* Keyboard Hint */}
      <div className="fixed bottom-4 right-4 z-30">
        <div className="bg-black/70 text-white text-xs px-2 py-1 rounded backdrop-blur-sm">
          ↑↓ 切換主題 ({getCurrentThemeIndex() + 1}/{colorSchemes.length}) | F12 關閉Debug
        </div>
      </div>
    </>
  )
}

export default function App() {
  const [currentView, setCurrentView] = useState<AppView>('login')
  const [currentAssessment, setCurrentAssessment] = useState<AssessmentType | null>(null)
  const [keyboardVisible, setKeyboardVisible] = useState(false)
  const [debugMode, setDebugMode] = useState(false)
  const [userPassword, setUserPassword] = useState<string>('')

  // F12 Debug模式切換
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'F12') {
        event.preventDefault()
        setDebugMode(prev => !prev)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // 鍵盤檢測和viewport處理
  useEffect(() => {
    // 設定viewport meta tag
    const viewportMeta = document.querySelector('meta[name="viewport"]')
    if (viewportMeta) {
      viewportMeta.setAttribute('content', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover')
    } else {
      const meta = document.createElement('meta')
      meta.name = 'viewport'
      meta.content = 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover'
      document.head.appendChild(meta)
    }

    // 設定移動設備友好的meta tags
    const appleMeta = document.querySelector('meta[name="apple-mobile-web-app-capable"]')
    if (!appleMeta) {
      const meta = document.createElement('meta')
      meta.name = 'apple-mobile-web-app-capable'
      meta.content = 'yes'
      document.head.appendChild(meta)
    }

    const appleStatusMeta = document.querySelector('meta[name="apple-mobile-web-app-status-bar-style"]')
    if (!appleStatusMeta) {
      const meta = document.createElement('meta')
      meta.name = 'apple-mobile-web-app-status-bar-style'
      meta.content = 'default'
      document.head.appendChild(meta)
    }

    // 初始視窗高度
    let initialViewportHeight = window.innerHeight
    let initialVisualViewportHeight = window.visualViewport?.height || window.innerHeight

    // 處理移動設備的viewport高度變化和鍵盤檢測
    const updateViewportHeight = () => {
      const currentHeight = window.innerHeight
      const visualHeight = window.visualViewport?.height || currentHeight
      
      // 設定CSS變數
      const vh = currentHeight * 0.01
      const vvh = visualHeight * 0.01
      
      document.documentElement.style.setProperty('--vh', `${vh}px`)
      document.documentElement.style.setProperty('--visual-vh', `${vvh}px`)
      
      // 檢測鍵盤是否顯示
      // 如果visual viewport高度明顯小於初始高度，可能是鍵盤顯示
      const heightDifference = initialVisualViewportHeight - visualHeight
      const isKeyboardVisible = heightDifference > 150 // 閾值設為150px
      
      if (isKeyboardVisible !== keyboardVisible) {
        setKeyboardVisible(isKeyboardVisible)
        
        // 發送自定義事件通知組件
        const event = new CustomEvent('keyboardToggle', {
          detail: { visible: isKeyboardVisible, height: heightDifference }
        })
        window.dispatchEvent(event)
      }
    }

    const handleResize = () => {
      updateViewportHeight()
    }

    const handleVisualViewportChange = () => {
      updateViewportHeight()
    }

    const handleOrientationChange = () => {
      setTimeout(() => {
        // 方向改變後重新設定初始高度
        initialViewportHeight = window.innerHeight
        initialVisualViewportHeight = window.visualViewport?.height || window.innerHeight
        updateViewportHeight()
      }, 100)
    }

    // 初始設定
    updateViewportHeight()

    // 事件監聽
    window.addEventListener('resize', handleResize)
    window.addEventListener('orientationchange', handleOrientationChange)
    
    // Visual Viewport API支援（現代瀏覽器）
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', handleVisualViewportChange)
      window.visualViewport.addEventListener('scroll', handleVisualViewportChange)
    }

    // 輸入框聚焦/失焦事件監聽（備用方案）
    const handleFocusIn = (e: FocusEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        setTimeout(() => {
          updateViewportHeight()
        }, 300) // 給鍵盤一些時間來顯示
      }
    }

    const handleFocusOut = (e: FocusEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        setTimeout(() => {
          updateViewportHeight()
        }, 300) // 給鍵盤一些時間來隱藏
      }
    }

    document.addEventListener('focusin', handleFocusIn)
    document.addEventListener('focusout', handleFocusOut)

    return () => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('orientationchange', handleOrientationChange)
      
      if (window.visualViewport) {
        window.visualViewport.removeEventListener('resize', handleVisualViewportChange)
        window.visualViewport.removeEventListener('scroll', handleVisualViewportChange)
      }
      
      document.removeEventListener('focusin', handleFocusIn)
      document.removeEventListener('focusout', handleFocusOut)
    }
  }, [keyboardVisible])

  const handleLogin = (password: string) => {
    setUserPassword(password)
    setCurrentView('chat')
  }

  const handleLogout = () => {
    setCurrentView('login')
  }

  const handleNavigateToAssessment = () => {
    setCurrentView('assessment')
  }

  const handleStartAssessment = (assessmentId: string) => {
    setCurrentAssessment(assessmentId as AssessmentType)
    setCurrentView('assessment-detail')
  }

  const handleBackToAssessment = () => {
    setCurrentAssessment(null)
    setCurrentView('assessment')
  }

  const handleBackToChat = () => {
    setCurrentView('chat')
  }

  const renderCurrentView = () => {
    switch (currentView) {
      case 'login':
        return <LoginPage onLogin={handleLogin} />
      case 'chat':
        return <ChatPage onLogout={handleLogout} onNavigateToAssessment={handleNavigateToAssessment} userPassword={userPassword} />
      case 'assessment':
        return <AssessmentPage onBack={handleBackToChat} onStartAssessment={handleStartAssessment} />
      case 'assessment-detail':
        if (currentAssessment === 'emotion-suicide') {
          return <EmotionSuicideAssessment onBack={handleBackToAssessment} />
        } else if (currentAssessment === 'substance-dependency') {
          return <SubstanceDependencyAssessment onBack={handleBackToAssessment} />
        } else if (currentAssessment === 'motivation-change') {
          return <MotivationChangeAssessment onBack={handleBackToAssessment} />
        } else if (currentAssessment === 'family-function') {
          return <FamilyFunctionAssessment onBack={handleBackToAssessment} />
        }
        return <AssessmentPage onBack={handleBackToChat} onStartAssessment={handleStartAssessment} />
      default:
        return <LoginPage onLogin={handleLogin} />
    }
  }

  return (
    <ThemeProvider>
      <div className="w-full h-full">
        {/* Theme Control - Debug功能，使用F12切換 */}
        {debugMode && <ThemeButton />}

        {/* Main App Content */}
        {renderCurrentView()}
      </div>
    </ThemeProvider>
  )
}