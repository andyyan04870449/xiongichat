import { useState } from 'react'
import { Button } from './ui/button'
import { Card } from './ui/card'
import { Badge } from './ui/badge'
import { Palette, X, Copy, Check, ChevronUp, ChevronDown } from 'lucide-react'
import { useTheme } from './ThemeProvider'

interface ColorPaletteProps {
  isVisible: boolean
  onClose: () => void
}

export function ColorPalette({ isVisible, onClose }: ColorPaletteProps) {
  const { currentScheme, setColorScheme, colorSchemes } = useTheme()
  const [copiedColor, setCopiedColor] = useState<string | null>(null)

  const copyToClipboard = async (color: string, colorName: string) => {
    try {
      await navigator.clipboard.writeText(color)
      setCopiedColor(colorName)
      setTimeout(() => setCopiedColor(null), 2000)
    } catch (err) {
      console.error('Failed to copy color:', err)
    }
  }

  const handleOverlayClick = (e: React.MouseEvent) => {
    // 只有點擊到背景overlay時才關閉，避免點擊面板內容也關閉
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  if (!isVisible) return null

  return (
    <div 
      className="fixed inset-0 bg-black/30 z-[200] flex items-start justify-end p-4" 
      onClick={handleOverlayClick}
    >
      <div className="bg-white rounded-xl shadow-xl w-96 max-w-[90vw] max-h-[90vh] overflow-y-auto animate-in slide-in-from-right-4 duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b sticky top-0 bg-white z-10 rounded-t-xl">
          <div className="flex items-center space-x-2">
            <Palette className="w-5 h-5 text-gray-600" />
            <h3 className="font-semibold text-gray-900">色彩調適面板</h3>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Current Theme Info */}
        <div className="p-4 border-b bg-gray-50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">當前主題</span>
            <div className="flex items-center space-x-2">
              <Badge variant="secondary">{currentScheme.shortName}</Badge>
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                <ChevronUp className="w-3 h-3" />
                <ChevronDown className="w-3 h-3" />
              </div>
            </div>
          </div>
          <p className="text-xs text-gray-600 mb-2">{currentScheme.description}</p>
          <div className="text-xs text-gray-500">鍵盤 ↑↓ 可快速切換主題</div>
        </div>

        {/* Color Schemes */}
        <div className="p-4">
          <h4 className="font-medium text-gray-900 mb-3">預設配色方案 ({colorSchemes.length} 種)</h4>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {colorSchemes.map((scheme, index) => (
              <Card 
                key={scheme.name}
                className={`p-3 cursor-pointer border-2 transition-all hover:shadow-md ${
                  currentScheme.name === scheme.name 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setColorScheme(scheme.name)}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-sm">{scheme.shortName}</span>
                    <span className="text-xs text-gray-500">({scheme.displayName})</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {currentScheme.name === scheme.name && (
                      <Badge variant="default" className="text-xs">使用中</Badge>
                    )}
                    <span className="text-xs text-gray-400">#{index + 1}</span>
                  </div>
                </div>
                <p className="text-xs text-gray-600 mb-3">{scheme.description}</p>
                
                {/* Color Preview */}
                <div className="grid grid-cols-4 gap-1.5">
                  <div 
                    className="w-full h-7 rounded border border-gray-200"
                    style={{ backgroundColor: scheme.colors.primary }}
                    title="主要色"
                  />
                  <div 
                    className="w-full h-7 rounded border border-gray-200"
                    style={{ backgroundColor: scheme.colors.secondary }}
                    title="次要色"
                  />
                  <div 
                    className="w-full h-7 rounded border border-gray-200"
                    style={{ backgroundColor: scheme.colors.accent }}
                    title="強調色"
                  />
                  <div 
                    className="w-full h-7 rounded border border-gray-200"
                    style={{ backgroundColor: scheme.colors.surface }}
                    title="表面色"
                  />
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Current Colors Detail */}
        <div className="p-4 border-t bg-gray-50 sticky bottom-0">
          <h4 className="font-medium text-gray-900 mb-3">當前色碼 - {currentScheme.shortName}</h4>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {Object.entries(currentScheme.colors).map(([key, value]) => {
              const colorNames: Record<string, string> = {
                primary: '主要色',
                secondary: '次要色',
                accent: '強調色',
                background: '背景色',
                surface: '表面色',
                text: '文字色',
                textSecondary: '次要文字',
                border: '邊框色',
                gradientFrom: '漸變起始',
                gradientVia: '漸變中間',
                gradientTo: '漸變結束'
              }
              
              return (
                <div key={key} className="flex items-center justify-between p-2 bg-white rounded border hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-4 h-4 rounded border border-gray-300"
                      style={{ backgroundColor: value }}
                    />
                    <span className="text-xs font-medium text-gray-700">{colorNames[key]}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <code className="text-xs bg-gray-100 px-1.5 py-0.5 rounded font-mono">{value}</code>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-6 w-6 p-0 hover:bg-gray-200"
                      onClick={(e) => {
                        e.stopPropagation()
                        copyToClipboard(value, key)
                      }}
                    >
                      {copiedColor === key ? (
                        <Check className="w-3 h-3 text-green-600" />
                      ) : (
                        <Copy className="w-3 h-3 text-gray-500" />
                      )}
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Usage Note */}
        <div className="p-4 border-t">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-xs text-blue-800">
              <strong>使用提示：</strong> 使用 ↑↓ 方向鍵快速切換主題，或直接點選配色方案。點擊色碼旁的複製按鈕可複製到剪貼板。點擊面板外的空白處可關閉調色盤。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}