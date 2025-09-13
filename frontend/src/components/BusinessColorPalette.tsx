import { useState, useEffect, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { X, Check } from 'lucide-react'
import { useTheme } from './ThemeProvider'

interface BusinessColorPaletteProps {
  isVisible: boolean
  onClose: () => void
}

export function BusinessColorPalette({ isVisible, onClose }: BusinessColorPaletteProps) {
  const { currentScheme, setColorScheme, colorSchemes } = useTheme()
  const [selectedTheme, setSelectedTheme] = useState(currentScheme.name)

  // 同步當前主題
  useEffect(() => {
    setSelectedTheme(currentScheme.name)
  }, [currentScheme.name])

  // 獲取當前主題在陣列中的索引
  const getCurrentThemeIndex = useCallback(() => {
    return colorSchemes.findIndex(scheme => scheme.name === selectedTheme)
  }, [colorSchemes, selectedTheme])

  // 切換到下一個主題
  const switchToNextTheme = useCallback(() => {
    const currentIndex = getCurrentThemeIndex()
    const nextIndex = (currentIndex + 1) % colorSchemes.length
    const nextTheme = colorSchemes[nextIndex].name
    setSelectedTheme(nextTheme)
    setColorScheme(nextTheme)
  }, [getCurrentThemeIndex, colorSchemes, setColorScheme])

  // 切換到上一個主題
  const switchToPrevTheme = useCallback(() => {
    const currentIndex = getCurrentThemeIndex()
    const prevIndex = currentIndex === 0 ? colorSchemes.length - 1 : currentIndex - 1
    const prevTheme = colorSchemes[prevIndex].name
    setSelectedTheme(prevTheme)
    setColorScheme(prevTheme)
  }, [getCurrentThemeIndex, colorSchemes, setColorScheme])

  // 鍵盤事件處理
  useEffect(() => {
    if (!isVisible) return

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
        // 數字鍵快速選擇
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
  }, [isVisible, switchToPrevTheme, switchToNextTheme, onClose, colorSchemes, setColorScheme])

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const handleThemeSelect = (themeName: string) => {
    setSelectedTheme(themeName)
    setColorScheme(themeName)
  }

  if (!isVisible) return null

  const currentIndex = getCurrentThemeIndex()

  return createPortal(
    <div
      className="fixed inset-0 bg-black/50 z-[9999] flex items-center justify-center p-4"
      onClick={handleOverlayClick}
    >
      {/* Modal Container - 固定尺寸的彈窗 */}
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-[90vw] sm:w-[600px] max-h-[80vh] flex flex-col">

        {/* Header */}
        <div className="flex-shrink-0 flex items-center justify-between px-4 py-3 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-semibold text-gray-900">個人化色彩設定</h2>
            <span className="text-xs text-gray-500">
              選擇您喜歡的介面配色
            </span>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors"
            aria-label="關閉"
          >
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>

        {/* Content - 可滾動 */}
        <div className="flex-1 overflow-y-auto min-h-0 p-3">
          <div className="grid grid-cols-2 gap-2">
            {colorSchemes.map((scheme, index) => (
              <button
                key={scheme.name}
                onClick={() => handleThemeSelect(scheme.name)}
                className={`
                  relative p-2.5 rounded-lg border transition-all text-left
                  ${selectedTheme === scheme.name
                    ? 'border-blue-500 bg-blue-50 shadow-sm'
                    : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                  }
                `}
              >
                {/* Number & Check */}
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] text-gray-400">#{index + 1}</span>
                  {selectedTheme === scheme.name && (
                    <div className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                      <Check className="w-2.5 h-2.5 text-white" />
                    </div>
                  )}
                </div>

                {/* Title */}
                <h3 className="text-xs font-medium text-gray-900 mb-0.5">
                  {scheme.shortName}
                </h3>
                <p className="text-[9px] text-gray-500 mb-1.5">
                  {scheme.displayName}
                </p>

                {/* Description */}
                <p className="text-[9px] text-gray-600 mb-2 line-clamp-1">
                  {scheme.description}
                </p>

                {/* Colors */}
                <div className="flex gap-0.5">
                  <div
                    className="flex-1 h-5 rounded-sm"
                    style={{ backgroundColor: scheme.colors.primary }}
                    title="主要色"
                  />
                  <div
                    className="flex-1 h-5 rounded-sm"
                    style={{ backgroundColor: scheme.colors.secondary }}
                    title="次要色"
                  />
                  <div
                    className="flex-1 h-5 rounded-sm"
                    style={{ backgroundColor: scheme.colors.accent }}
                    title="強調色"
                  />
                  <div
                    className="flex-1 h-5 rounded-sm"
                    style={{ backgroundColor: scheme.colors.surface }}
                    title="表面色"
                  />
                </div>
                <div className="flex gap-0.5 mt-0.5">
                  <span className="flex-1 text-center text-[8px] text-gray-400">主</span>
                  <span className="flex-1 text-center text-[8px] text-gray-400">次</span>
                  <span className="flex-1 text-center text-[8px] text-gray-400">強</span>
                  <span className="flex-1 text-center text-[8px] text-gray-400">面</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 px-4 py-2 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between text-[10px] text-gray-600">
            <div>
              目前：<span className="font-medium text-gray-900">{currentScheme.shortName}</span>
              <span className="text-gray-400 ml-1">({currentIndex + 1}/{colorSchemes.length})</span>
            </div>
            <div className="text-gray-500">
              <kbd className="px-1 py-0.5 bg-white rounded border text-[9px]">1-9</kbd> 選擇
              <span className="mx-1">•</span>
              <kbd className="px-1 py-0.5 bg-white rounded border text-[9px]">↑↓</kbd> 切換
              <span className="mx-1">•</span>
              <kbd className="px-1 py-0.5 bg-white rounded border text-[9px]">ESC</kbd> 關閉
            </div>
          </div>
        </div>
      </div>
    </div>,
    document.body
  )
}