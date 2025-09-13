import React, { useState } from 'react'
import { Dialog, DialogContent, DialogTitle } from './ui/dialog'
import { Button } from './ui/button'
import { Checkbox } from './ui/checkbox'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Card } from './ui/card'
import { ChevronRight, Check, Heart } from 'lucide-react'
import logo from 'figma:asset/e9a9f75d2ac26ddaa75b766f16261c08e59f132c.png'

interface ResourceFormModalProps {
  isOpen: boolean
  onClose: () => void
}

interface FormOption {
  value: string
  label: string
  category?: string
}

// 組織單位資料結構
const assistanceData: FormOption[] = [
  { value: '無', label: '無' },
  // 主要單位
  { value: '毒防局', label: '毒防局', category: '主要單位' },
  { value: '警察局', label: '警察局', category: '主要單位' },
  { value: '地檢署', label: '地檢署', category: '主要單位' },
  { value: '少年及家事法院', label: '少年及家事法院', category: '主要單位' },
  { value: '少輔會', label: '少輔會', category: '主要單位' },
  { value: '原民會', label: '原民會', category: '主要單位' },
  // 社會局
  { value: '社福中心', label: '社福中心', category: '社會局' },
  { value: '家防中心', label: '家防中心', category: '社會局' },
  { value: '無障礙之家', label: '無障礙之家', category: '社會局' },
  // 衛生局
  { value: '社區心衛中心', label: '社區心衛中心', category: '衛生局' },
  { value: '自殺防治中心', label: '自殺防治中心', category: '衛生局' },
  { value: '衛生所', label: '衛生所', category: '衛生局' },
  { value: '長期照顧中心', label: '長期照顧中心', category: '衛生局' },
  // 教育局
  { value: '學生輔導諮商中心', label: '學生輔導諮商中心', category: '教育局' },
  { value: '家庭教育中心', label: '家庭教育中心', category: '教育局' },
  // 勞工局
  { value: '訓練就業中心', label: '訓練就業中心', category: '勞工局' },
  { value: '博愛職業技能訓練中心', label: '博愛職業技能訓練中心', category: '勞工局' },
  // 民政局
  { value: '里辦公室', label: '里辦公室', category: '民政局' },
  { value: '區公所', label: '區公所', category: '民政局' },
  // 其他單位
  { value: '醫院', label: '醫院', category: '其他單位' },
  { value: '中途之家', label: '中途之家', category: '其他單位' },
  { value: '更生保護會', label: '更生保護會', category: '其他單位' },
  { value: '張老師基金會', label: '張老師基金會', category: '其他單位' },
  { value: '高雄市生命線協會', label: '高雄市生命線協會', category: '其他單位' },
  { value: '善慧恩社會慈善基金會', label: '善慧恩社會慈善基金會', category: '其他單位' },
  { value: '高市慈善團體聯合總會', label: '高市慈善團體聯合總會', category: '其他單位' },
]

const medicalOptions = [
  '無', '焦慮', '失眠', '自律神經失調', '情緒障礙', '憂鬱', '恐慌', 
  '失智症', '自閉症', '注意力不足', '過動症', '妄想', '強迫', 
  '躁鬱', '自殺', '思覺失調', '妥瑞氏', '自殘', 
  '婦女身心困擾', '青少年心理調適', '其他'
]

const resourceOptions = [
  '無', '福利服務', '法律服務', '就業服務', '醫療服務', '心理諮商服務',
  '經濟支持', '職能培力與就業輔導', '安置資源連結',
  '家庭支持與互助團體(包含愛與陪伴團體)', '家庭維繫、修復及支持性服務活動',
  '戒癮相關知識', '毒品防制宣導活動', '邀請參與社區相關活動', '其他'
]

export function ResourceFormModal({ isOpen, onClose }: ResourceFormModalProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({
    assistance: new Set<string>(),
    medical: new Set<string>(),
    medicalOther: '',
    resources: new Set<string>(),
    resourcesOther: ''
  })

  const handleCheckboxChange = (field: 'assistance' | 'medical' | 'resources', value: string) => {
    setFormData(prev => {
      const newSet = new Set(prev[field])
      if (value === '無') {
        return { ...prev, [field]: new Set(['無']) }
      } else {
        newSet.delete('無')
        if (newSet.has(value)) {
          newSet.delete(value)
        } else {
          newSet.add(value)
        }
        return { ...prev, [field]: newSet }
      }
    })
  }

  const handleNext = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1)
    } else {
      setCurrentStep(4)
    }
  }

  const handleClose = () => {
    setCurrentStep(1)
    setFormData({
      assistance: new Set<string>(),
      medical: new Set<string>(),
      medicalOther: '',
      resources: new Set<string>(),
      resourcesOther: ''
    })
    onClose()
  }

  // 按類別分組協助單位
  const groupedAssistance = assistanceData.reduce((acc, item) => {
    if (!item.category) {
      acc['其他'] = acc['其他'] || []
      acc['其他'].push(item)
    } else {
      acc[item.category] = acc[item.category] || []
      acc[item.category].push(item)
    }
    return acc
  }, {} as Record<string, FormOption[]>)

  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogContent 
        className="max-w-7xl w-[95vw] max-h-[90vh] p-0 overflow-hidden flex flex-col"
        hideCloseButton={true}
        style={{
          background: 'linear-gradient(to bottom, var(--theme-background), var(--theme-surface))',
          WebkitFontSmoothing: 'antialiased',
          MozOsxFontSmoothing: 'grayscale',
          textRendering: 'geometricPrecision',
        }}
      >
        <DialogTitle className="sr-only">資源需求調查表</DialogTitle>
        {currentStep < 4 ? (
          <>
            {/* Header - 固定在頂部 */}
            <div 
              className="px-6 py-4 text-white flex-shrink-0"
              style={{
                background: 'linear-gradient(135deg, var(--theme-primary), var(--theme-secondary))',
              }}
            >
              <h2 className="text-xl font-bold mb-1">資源需求調查表</h2>
              <div className="flex items-center gap-2 text-white/80 text-sm">
                <span>第 {currentStep} 題</span>
                <span>/</span>
                <span>共 3 題</span>
              </div>
            </div>

            {/* Content - 可滾動區域 */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
              {/* Step 1: 協助單位 */}
              {currentStep === 1 && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold sticky top-0 bg-white py-2 z-10" style={{ color: 'var(--theme-text)' }}>
                    1. 請問您還有需要哪個單位進一步的協助嗎？
                  </h3>
                  
                  {/* 無選項 */}
                  <Card className="p-3 border-2 inline-block" style={{ borderColor: 'var(--theme-border)' }}>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <Checkbox
                        checked={formData.assistance.has('無')}
                        onCheckedChange={() => handleCheckboxChange('assistance', '無')}
                        className="w-4 h-4"
                      />
                      <span className="text-base font-medium">無需其他協助</span>
                    </label>
                  </Card>

                  {/* 分類顯示 */}
                  {Object.entries(groupedAssistance).map(([category, items]) => {
                    if (category === '其他') return null
                    
                    return (
                      <div key={category} className="space-y-2">
                        <h4 
                          className="font-semibold text-base flex items-center gap-1"
                          style={{ color: 'var(--theme-primary)' }}
                        >
                          <ChevronRight className="w-3 h-3" />
                          {category}
                        </h4>
                        <div className="flex flex-wrap gap-3 pl-4">
                          {items.map(item => (
                            <Card 
                              key={item.value}
                              className="hover:shadow-md transition-shadow cursor-pointer"
                              style={{ 
                                borderColor: formData.assistance.has(item.value) 
                                  ? 'var(--theme-primary)' 
                                  : 'var(--theme-border)',
                                borderWidth: '2px',
                                background: formData.assistance.has(item.value)
                                  ? 'var(--theme-surface)'
                                  : 'white'
                              }}
                            >
                              <label className="flex items-center gap-2 px-3 py-2 cursor-pointer">
                                <Checkbox
                                  checked={formData.assistance.has(item.value)}
                                  onCheckedChange={() => handleCheckboxChange('assistance', item.value)}
                                  className="w-4 h-4"
                                />
                                <span className="text-sm whitespace-nowrap">{item.label}</span>
                              </label>
                            </Card>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}

              {/* Step 2: 就醫協助 */}
              {currentStep === 2 && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold sticky top-0 bg-white py-2 z-10" style={{ color: 'var(--theme-text)' }}>
                    2. 請問您還有需要哪方面進一步的就醫協助嗎？
                  </h3>
                  
                  <div className="flex flex-wrap gap-3">
                    {medicalOptions.map(option => (
                      <Card 
                        key={option}
                        className="hover:shadow-md transition-shadow cursor-pointer"
                        style={{ 
                          borderColor: formData.medical.has(option) 
                            ? 'var(--theme-primary)' 
                            : 'var(--theme-border)',
                          borderWidth: '2px',
                          background: formData.medical.has(option)
                            ? 'var(--theme-surface)'
                            : 'white'
                        }}
                      >
                        <label className="flex items-center gap-2 px-3 py-2 cursor-pointer">
                          <Checkbox
                            checked={formData.medical.has(option)}
                            onCheckedChange={() => handleCheckboxChange('medical', option)}
                            className="w-4 h-4"
                          />
                          <span className="text-sm whitespace-nowrap">{option}</span>
                        </label>
                      </Card>
                    ))}
                  </div>
                  
                  {formData.medical.has('其他') && (
                    <div className="mt-4">
                      <Input
                        placeholder="請輸入其他就醫協助..."
                        value={formData.medicalOther}
                        onChange={(e) => setFormData(prev => ({ ...prev, medicalOther: e.target.value }))}
                        className="w-full max-w-lg text-base"
                        style={{ 
                          borderColor: 'var(--theme-border)',
                          background: 'white'
                        }}
                      />
                    </div>
                  )}
                </div>
              )}

              {/* Step 3: 資源協助 */}
              {currentStep === 3 && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold sticky top-0 bg-white py-2 z-10" style={{ color: 'var(--theme-text)' }}>
                    3. 請問您還有需要哪方面進一步的資源協助嗎？
                  </h3>
                  
                  <div className="flex flex-wrap gap-3">
                    {resourceOptions.map(option => (
                      <Card 
                        key={option}
                        className="hover:shadow-md transition-shadow cursor-pointer"
                        style={{ 
                          borderColor: formData.resources.has(option) 
                            ? 'var(--theme-primary)' 
                            : 'var(--theme-border)',
                          borderWidth: '2px',
                          background: formData.resources.has(option)
                            ? 'var(--theme-surface)'
                            : 'white',
                          minWidth: option.length > 15 ? '280px' : 'auto'
                        }}
                      >
                        <label className="flex items-center gap-2 px-3 py-2 cursor-pointer">
                          <Checkbox
                            checked={formData.resources.has(option)}
                            onCheckedChange={() => handleCheckboxChange('resources', option)}
                            className="w-4 h-4"
                          />
                          <span className="text-sm">{option}</span>
                        </label>
                      </Card>
                    ))}
                  </div>
                  
                  {formData.resources.has('其他') && (
                    <div className="mt-4">
                      <Input
                        placeholder="請輸入其他資源協助..."
                        value={formData.resourcesOther}
                        onChange={(e) => setFormData(prev => ({ ...prev, resourcesOther: e.target.value }))}
                        className="w-full max-w-lg text-base"
                        style={{ 
                          borderColor: 'var(--theme-border)',
                          background: 'white'
                        }}
                      />
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Footer - 固定在底部 */}
            <div 
              className="px-6 py-3 border-t flex items-center justify-between flex-shrink-0"
              style={{ borderColor: 'var(--theme-border)' }}
            >
              {/* Progress Dots */}
              <div className="flex gap-2">
                {[1, 2, 3].map(step => (
                  <div
                    key={step}
                    className="w-3 h-3 rounded-full transition-all duration-300"
                    style={{
                      backgroundColor: step === currentStep
                        ? 'var(--theme-primary)'
                        : step < currentStep
                        ? 'var(--theme-secondary)'
                        : 'var(--theme-border)'
                    }}
                  />
                ))}
              </div>

              {/* Next Button */}
              <Button 
                onClick={handleNext}
                className="px-8 py-2 text-white font-medium shadow-md hover:shadow-lg transition-all"
                style={{
                  background: 'linear-gradient(135deg, var(--theme-primary), var(--theme-secondary))'
                }}
              >
                {currentStep === 3 ? '提交' : '下一題'}
              </Button>
            </div>
          </>
        ) : (
          /* 感謝頁面 */
          <div 
            className="relative min-h-[600px] overflow-hidden"
            style={{
              background: 'linear-gradient(135deg, var(--theme-gradient-from), var(--theme-gradient-via), var(--theme-gradient-to))'
            }}
          >
            {/* 裝飾背景元素 */}
            <div className="absolute top-0 left-0 w-48 h-48 bg-white/10 rounded-full -translate-x-1/2 -translate-y-1/2" />
            <div className="absolute bottom-0 right-0 w-64 h-64 bg-white/10 rounded-full translate-x-1/3 translate-y-1/3" />
            <div className="absolute top-1/3 right-1/4 w-32 h-32 bg-white/5 rounded-full" />
            
            {/* 主要內容 */}
            <div className="relative z-10 flex flex-col items-center justify-center min-h-[600px] p-8">
              {/* 成功勾選動畫 */}
              <div className="mb-8">
                <div 
                  className="w-32 h-32 rounded-full flex items-center justify-center shadow-lg animate-pulse"
                  style={{
                    background: 'linear-gradient(135deg, white, var(--theme-surface))'
                  }}
                >
                  <div 
                    className="w-24 h-24 rounded-full flex items-center justify-center"
                    style={{
                      background: 'linear-gradient(135deg, var(--theme-primary), var(--theme-secondary))'
                    }}
                  >
                    <Check className="w-14 h-14 text-white stroke-[3]" />
                  </div>
                </div>
              </div>

              {/* 標題文字 */}
              <div className="text-center mb-8">
                <h2 className="text-3xl md:text-4xl font-bold mb-3" style={{ color: 'var(--theme-text)' }}>
                  感謝您的回覆
                </h2>
                <p className="text-lg md:text-xl max-w-sm mx-auto" style={{ color: 'var(--theme-text)', opacity: 0.8 }}>
                  您的寶貴意見將幫助我們提供更好的服務
                </p>
              </div>

              {/* Logo 和機構資訊 */}
              <div className="mb-8">
                <img src={logo} alt="雄i聊" className="w-24 h-24 mx-auto mb-4 object-contain" />
                <div className="text-center space-y-2">
                  <p className="text-lg font-bold" style={{ color: 'var(--theme-primary)' }}>
                    高雄市政府毒品防制局
                  </p>
                  <p className="text-sm" style={{ color: 'var(--theme-text)', opacity: 0.7 }}>
                    關心您的健康與福祉
                  </p>
                </div>
              </div>

              {/* 關閉按鈕 */}
              <Button 
                onClick={handleClose}
                className="px-16 py-4 text-lg font-semibold text-white shadow-xl hover:shadow-2xl transition-all hover:scale-105"
                style={{
                  background: 'linear-gradient(135deg, var(--theme-primary), var(--theme-secondary))',
                  borderRadius: '2rem'
                }}
              >
                關閉
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}