import { useState, useEffect, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { X, Check, Palette, Layers, BookOpen } from 'lucide-react'
import { useTheme } from './ThemeProvider'
import '../styles/color-panel-scrollbar.css'

interface ColorThemePanelProps {
  isOpen: boolean
  onClose: () => void
}

export function ColorThemePanel({ isOpen, onClose }: ColorThemePanelProps) {
  const { currentScheme, setColorScheme, colorSchemes } = useTheme()
  const [selectedTheme, setSelectedTheme] = useState(currentScheme.name)
  const [appTheme, setAppTheme] = useState<'basic' | 'notebook'>(() => {
    return (localStorage.getItem('appTheme') as 'basic' | 'notebook') || 'basic'
  })

  // 保存應用主題到 localStorage
  useEffect(() => {
    localStorage.setItem('appTheme', appTheme)
    // 發送自定義事件通知主題變更
    window.dispatchEvent(new CustomEvent('appThemeChange', { detail: appTheme }))
  }, [appTheme])

  useEffect(() => {
    setSelectedTheme(currentScheme.name)
  }, [currentScheme.name])

  const getCurrentThemeIndex = useCallback(() => {
    return colorSchemes.findIndex(scheme => scheme.name === selectedTheme)
  }, [colorSchemes, selectedTheme])

  const switchToNextTheme = useCallback(() => {
    const currentIndex = getCurrentThemeIndex()
    const nextIndex = (currentIndex + 1) % colorSchemes.length
    const nextTheme = colorSchemes[nextIndex].name
    setSelectedTheme(nextTheme)
    setColorScheme(nextTheme)
  }, [getCurrentThemeIndex, colorSchemes, setColorScheme])

  const switchToPrevTheme = useCallback(() => {
    const currentIndex = getCurrentThemeIndex()
    const prevIndex = currentIndex === 0 ? colorSchemes.length - 1 : currentIndex - 1
    const prevTheme = colorSchemes[prevIndex].name
    setSelectedTheme(prevTheme)
    setColorScheme(prevTheme)
  }, [getCurrentThemeIndex, colorSchemes, setColorScheme])

  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (event: KeyboardEvent) => {
      if (document.activeElement?.tagName === 'INPUT' ||
          document.activeElement?.tagName === 'TEXTAREA') {
        return
      }

      if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
        event.preventDefault()
        switchToPrevTheme()
      } else if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
        event.preventDefault()
        switchToNextTheme()
      } else if (event.key === 'Escape') {
        event.preventDefault()
        onClose()
      } else if (event.key >= '1' && event.key <= '9') {
        const index = parseInt(event.key) - 1
        if (index < colorSchemes.length) {
          const selectedScheme = colorSchemes[index].name
          setSelectedTheme(selectedScheme)
          setColorScheme(selectedScheme)
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, switchToPrevTheme, switchToNextTheme, onClose, colorSchemes, setColorScheme])

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const handleThemeSelect = (themeName: string) => {
    setSelectedTheme(themeName)
    setColorScheme(themeName)
  }

  if (!isOpen) return null

  return createPortal(
    <>
      {/* 背景遮罩 */}
      <div
        className="fixed inset-0 bg-black/30 z-[9998] transition-opacity duration-300"
        onClick={handleOverlayClick}
      />

      {/* 側邊滑出面板 */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          right: 0,
          height: '100%',
          width: '400px',
          maxWidth: '90vw',
          backgroundColor: 'white',
          boxShadow: '-4px 0 24px rgba(0, 0, 0, 0.15)',
          zIndex: 9999,
          transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 0.3s ease-out',
          willChange: 'transform'
        }}
      >
        {/* 面板頭部 */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <Palette className="w-5 h-5" style={{ color: 'var(--theme-primary)' }} />
            <h2 className="text-lg font-semibold text-gray-900">色彩主題</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors"
            aria-label="關閉"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* 面板內容 - 可滾動區域 */}
        <div
          className="color-theme-panel-scroll"
          style={{
            position: 'absolute',
            top: '64px',
            bottom: '76px',
            left: 0,
            right: 0,
            overflowY: 'scroll',
            overflowX: 'hidden',
            padding: '16px',
            paddingRight: '8px',
            scrollBehavior: 'smooth',
            scrollbarWidth: 'thin',
            scrollbarColor: '#94a3b8 #e2e8f0'
          }}
        >
          {/* 應用主題切換區塊 */}
          <div className="mb-6 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">應用主題</h3>
            <div className="flex gap-3">
              <button
                onClick={() => setAppTheme('basic')}
                className={`
                  flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg border-2 transition-all
                  ${appTheme === 'basic'
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                  }
                `}
              >
                <Layers className="w-5 h-5 text-indigo-600" />
                <span className="text-sm font-medium">基本</span>
              </button>
              <button
                onClick={() => setAppTheme('notebook')}
                disabled
                className={`
                  flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg border-2 transition-all opacity-50 cursor-not-allowed
                  ${appTheme === 'notebook'
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 bg-white'
                  }
                `}
              >
                <BookOpen className="w-5 h-5 text-gray-400" />
                <span className="text-sm font-medium text-gray-400">筆記本</span>
                <span className="text-xs text-gray-400">(開發中)</span>
              </button>
            </div>
          </div>

          {/* 顏色主題選擇 */}
          <div className="space-y-3 pb-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">顏色配置</h3>
            {colorSchemes.map((scheme, index) => (
              <button
                key={scheme.name}
                onClick={() => handleThemeSelect(scheme.name)}
                className={`
                  w-full p-4 rounded-lg border-2 transition-all text-left
                  ${selectedTheme === scheme.name
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                  }
                `}
              >
                {/* 主題頭部 */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">#{index + 1}</span>
                    <h3 className="text-sm font-semibold text-gray-900">
                      {scheme.shortName}
                    </h3>
                  </div>
                  {selectedTheme === scheme.name && (
                    <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                      <Check className="w-3 h-3 text-white" />
                    </div>
                  )}
                </div>

                {/* 主題名稱 */}
                <p className="text-xs text-gray-600 mb-2">
                  {scheme.displayName}
                </p>

                {/* 主題描述 */}
                <p className="text-xs text-gray-500 mb-3">
                  {scheme.description}
                </p>

                {/* 色彩預覽 */}
                <div className="flex gap-1">
                  <div
                    className="flex-1 h-8 rounded"
                    style={{ backgroundColor: scheme.colors.primary }}
                    title="主要色"
                  />
                  <div
                    className="flex-1 h-8 rounded"
                    style={{ backgroundColor: scheme.colors.secondary }}
                    title="次要色"
                  />
                  <div
                    className="flex-1 h-8 rounded"
                    style={{ backgroundColor: scheme.colors.accent }}
                    title="強調色"
                  />
                  <div
                    className="flex-1 h-8 rounded border border-gray-200"
                    style={{ backgroundColor: scheme.colors.surface }}
                    title="表面色"
                  />
                </div>
                <div className="flex gap-1 mt-1">
                  <span className="flex-1 text-center text-[10px] text-gray-400">主要</span>
                  <span className="flex-1 text-center text-[10px] text-gray-400">次要</span>
                  <span className="flex-1 text-center text-[10px] text-gray-400">強調</span>
                  <span className="flex-1 text-center text-[10px] text-gray-400">表面</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* 面板底部 - 增強的快捷鍵提示 */}
        <div className="absolute bottom-0 left-0 right-0 px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="space-y-2">
            {/* 當前主題 */}
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-600">
                目前使用：<span className="font-semibold text-gray-900">{currentScheme.shortName}</span>
                <span className="text-gray-400 ml-1">({getCurrentThemeIndex() + 1}/{colorSchemes.length})</span>
              </span>
            </div>
            {/* 快捷鍵提示 - 只在桌面版顯示 */}
            <div className="hidden md:flex items-center justify-between text-[10px] text-gray-500">
              <div className="flex gap-3">
                <span>
                  <kbd className="px-1 py-0.5 bg-white rounded border">↑↓</kbd> 切換主題
                </span>
                <span>
                  <kbd className="px-1 py-0.5 bg-white rounded border">1-9</kbd> 快速選擇
                </span>
              </div>
              <span>
                <kbd className="px-1 py-0.5 bg-white rounded border">ESC</kbd> 關閉
              </span>
            </div>
          </div>
        </div>
      </div>
    </>,
    document.body
  )
}