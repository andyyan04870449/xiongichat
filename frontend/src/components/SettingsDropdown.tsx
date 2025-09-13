import { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { Button } from './ui/button'
import { Settings, Palette, LogOut, ChevronDown } from 'lucide-react'
import { ColorThemePanel } from './ColorThemePanel'

interface SettingsDropdownProps {
  onLogout: () => void
}

export function SettingsDropdown({ onLogout }: SettingsDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [showColorPalette, setShowColorPalette] = useState(false)
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, right: 0 })
  const dropdownRef = useRef<HTMLDivElement>(null)

  // 計算下拉選單位置
  useEffect(() => {
    if (isOpen && dropdownRef.current) {
      const rect = dropdownRef.current.getBoundingClientRect()
      setDropdownPosition({
        top: rect.bottom + 8,
        right: window.innerWidth - rect.right
      })
    }
  }, [isOpen])

  // 點擊外部關閉下拉選單
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      const target = event.target as HTMLElement
      // 檢查點擊是否在按鈕或下拉選單內
      if (dropdownRef.current && !dropdownRef.current.contains(target) &&
          !target.closest('[data-settings-dropdown]')) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleColorPaletteClick = () => {
    setShowColorPalette(true)
    setIsOpen(false)
  }

  const handleLogoutClick = () => {
    setIsOpen(false)
    onLogout()
  }

  return (
    <>
      <div className="relative" ref={dropdownRef}>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsOpen(!isOpen)}
          className="text-gray-600 hover:text-gray-800 min-h-[44px] flex items-center space-x-1"
          style={{ borderColor: 'var(--theme-border)' }}
        >
          <Settings className="w-4 h-4" />
          <span className="hidden md:inline">設定</span>
          <ChevronDown className={`w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </Button>

        {/* 下拉選單 - 使用Portal渲染到body */}
        {isOpen && createPortal(
          <div
               data-settings-dropdown
               className="fixed w-56 bg-white rounded-lg shadow-xl border border-gray-200 py-1 z-[9999] animate-in slide-in-from-top-2 duration-200"
               style={{
                 top: `${dropdownPosition.top}px`,
                 right: `${dropdownPosition.right}px`,
                 maxHeight: '80vh',
                 overflowY: 'auto'
               }}>
            <button
              onClick={handleColorPaletteClick}
              className="w-full flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Palette className="w-4 h-4 mr-3" style={{ color: 'var(--theme-primary)' }} />
              <span>調色盤</span>
            </button>

            <div className="border-t border-gray-100 my-1" />

            <button
              onClick={handleLogoutClick}
              className="w-full flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <LogOut className="w-4 h-4 mr-3" />
              <span>登出</span>
            </button>
          </div>,
          document.body
        )}
      </div>

      {/* 色彩主題面板 */}
      <ColorThemePanel
        isOpen={showColorPalette}
        onClose={() => setShowColorPalette(false)}
      />
    </>
  )
}