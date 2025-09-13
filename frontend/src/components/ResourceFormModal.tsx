import React, { useState } from 'react'
import { Dialog, DialogContent, DialogTitle } from './ui/dialog'
import { Button } from './ui/button'
import { Checkbox } from './ui/checkbox'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Card } from './ui/card'
import { ChevronRight, Check, Heart, X } from 'lucide-react'
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

// 醫療協助資料結構
const medicalData: FormOption[] = [
  { value: '無', label: '無' },
  // 情緒相關
  { value: '焦慮', label: '焦慮', category: '情緒相關' },
  { value: '憂鬱', label: '憂鬱', category: '情緒相關' },
  { value: '恐慌', label: '恐慌', category: '情緒相關' },
  { value: '情緒障礙', label: '情緒障礙', category: '情緒相關' },
  { value: '躁鬱', label: '躁鬱', category: '情緒相關' },
  // 生理相關
  { value: '失眠', label: '失眠', category: '生理相關' },
  { value: '自律神經失調', label: '自律神經失調', category: '生理相關' },
  // 認知相關
  { value: '失智症', label: '失智症', category: '認知相關' },
  { value: '妄想', label: '妄想', category: '認知相關' },
  { value: '思覺失調', label: '思覺失調', category: '認知相關' },
  // 發展相關
  { value: '自閉症', label: '自閉症', category: '發展相關' },
  { value: '注意力不足', label: '注意力不足', category: '發展相關' },
  { value: '過動症', label: '過動症', category: '發展相關' },
  { value: '妥瑞氏', label: '妥瑞氏', category: '發展相關' },
  // 行為相關
  { value: '強迫', label: '強迫', category: '行為相關' },
  { value: '自殺', label: '自殺', category: '行為相關' },
  { value: '自殘', label: '自殘', category: '行為相關' },
  // 特定族群
  { value: '婦女身心困擾', label: '婦女身心困擾', category: '特定族群' },
  { value: '青少年心理調適', label: '青少年心理調適', category: '特定族群' },
  { value: '其他', label: '其他', category: '特定族群' },
]

// 資源協助資料結構
const resourceData: FormOption[] = [
  { value: '無', label: '無' },
  // 基本服務
  { value: '福利服務', label: '福利服務', category: '基本服務' },
  { value: '法律服務', label: '法律服務', category: '基本服務' },
  { value: '醫療服務', label: '醫療服務', category: '基本服務' },
  { value: '心理諮商服務', label: '心理諮商服務', category: '基本服務' },
  // 就業與經濟
  { value: '就業服務', label: '就業服務', category: '就業與經濟' },
  { value: '經濟支持', label: '經濟支持', category: '就業與經濟' },
  { value: '職能培力與就業輔導', label: '職能培力與就業輔導', category: '就業與經濟' },
  // 家庭與社區
  { value: '安置資源連結', label: '安置資源連結', category: '家庭與社區' },
  { value: '家庭支持與互助團體(包含愛與陪伴團體)', label: '家庭支持與互助團體', category: '家庭與社區' },
  { value: '家庭維繫、修復及支持性服務活動', label: '家庭維繫、修復及支持性服務', category: '家庭與社區' },
  // 預防與教育
  { value: '戒癮相關知識', label: '戒癮相關知識', category: '預防與教育' },
  { value: '毒品防制宣導活動', label: '毒品防制宣導活動', category: '預防與教育' },
  { value: '邀請參與社區相關活動', label: '邀請參與社區相關活動', category: '預防與教育' },
  { value: '其他', label: '其他', category: '預防與教育' },
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

  // 按類別分組醫療協助
  const groupedMedical = medicalData.reduce((acc, item) => {
    if (!item.category) {
      acc['其他'] = acc['其他'] || []
      acc['其他'].push(item)
    } else {
      acc[item.category] = acc[item.category] || []
      acc[item.category].push(item)
    }
    return acc
  }, {} as Record<string, FormOption[]>)

  // 按類別分組資源協助
  const groupedResource = resourceData.reduce((acc, item) => {
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
        className="w-[1200px] max-w-[95vw] h-[700px] max-h-[90vh] p-0 overflow-hidden flex flex-col"
        hideCloseButton={true}
        aria-describedby="resource-form-description"
        style={{
          background: 'linear-gradient(to bottom, var(--theme-background), var(--theme-surface))',
          WebkitFontSmoothing: 'antialiased',
          MozOsxFontSmoothing: 'grayscale',
          textRendering: 'geometricPrecision',
        }}
      >
        <DialogTitle className="sr-only">資源需求調查表</DialogTitle>
        <p id="resource-form-description" className="sr-only">
          請填寫您的資源需求，共三個問題
        </p>
        {currentStep < 4 ? (
          <>
            {/* Header - 固定在頂部 */}
            <div
              className="px-6 py-4 text-white flex-shrink-0 relative"
              style={{
                background: 'linear-gradient(135deg, var(--theme-primary), var(--theme-secondary))',
              }}
            >
              <div>
                <h2 className="text-xl font-bold mb-1">資源需求調查表</h2>
                <div className="flex items-center gap-2 text-white/80 text-sm">
                  <span>第 {currentStep} 題</span>
                  <span>/</span>
                  <span>共 3 題</span>
                </div>
              </div>
              {/* 關閉按鈕 */}
              <button
                onClick={handleClose}
                className="absolute top-4 right-4 p-2 rounded-lg hover:bg-white/20 transition-colors"
                aria-label="關閉"
              >
                <X className="w-5 h-5 text-white" />
              </button>
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

                  {/* 無選項 */}
                  <Card className="p-3 border-2 inline-block" style={{ borderColor: 'var(--theme-border)' }}>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <Checkbox
                        checked={formData.medical.has('無')}
                        onCheckedChange={() => handleCheckboxChange('medical', '無')}
                        className="w-4 h-4"
                      />
                      <span className="text-base font-medium">無需其他協助</span>
                    </label>
                  </Card>

                  {/* 分類顯示 */}
                  {Object.entries(groupedMedical).map(([category, items]) => {
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
                                borderColor: formData.medical.has(item.value)
                                  ? 'var(--theme-primary)'
                                  : 'var(--theme-border)',
                                borderWidth: '2px',
                                background: formData.medical.has(item.value)
                                  ? 'var(--theme-surface)'
                                  : 'white'
                              }}
                            >
                              <label className="flex items-center gap-2 px-3 py-2 cursor-pointer">
                                <Checkbox
                                  checked={formData.medical.has(item.value)}
                                  onCheckedChange={() => handleCheckboxChange('medical', item.value)}
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
                  
                  {formData.medical.has('其他') && (
                    <div className="mt-4 pl-4">
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

                  {/* 無選項 */}
                  <Card className="p-3 border-2 inline-block" style={{ borderColor: 'var(--theme-border)' }}>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <Checkbox
                        checked={formData.resources.has('無')}
                        onCheckedChange={() => handleCheckboxChange('resources', '無')}
                        className="w-4 h-4"
                      />
                      <span className="text-base font-medium">無需其他協助</span>
                    </label>
                  </Card>

                  {/* 分類顯示 */}
                  {Object.entries(groupedResource).map(([category, items]) => {
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
                                borderColor: formData.resources.has(item.value)
                                  ? 'var(--theme-primary)'
                                  : 'var(--theme-border)',
                                borderWidth: '2px',
                                background: formData.resources.has(item.value)
                                  ? 'var(--theme-surface)'
                                  : 'white'
                              }}
                            >
                              <label className="flex items-center gap-2 px-3 py-2 cursor-pointer">
                                <Checkbox
                                  checked={formData.resources.has(item.value)}
                                  onCheckedChange={() => handleCheckboxChange('resources', item.value)}
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
                  
                  {formData.resources.has('其他') && (
                    <div className="mt-4 pl-4">
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
          /* 感謝頁面 - 使用與題目相同的結構 */
          <>
            {/* Header - 固定在頂部 */}
            <div
              className="px-6 py-4 text-white flex-shrink-0 relative"
              style={{
                background: 'linear-gradient(135deg, var(--theme-primary), var(--theme-secondary))',
              }}
            >
              <div>
                <h2 className="text-xl font-bold mb-1">資源需求調查表</h2>
                <div className="flex items-center gap-2 text-white/80 text-sm">
                  <span>填寫完成</span>
                </div>
              </div>
              {/* 關閉按鈕 */}
              <button
                onClick={handleClose}
                className="absolute top-4 right-4 p-2 rounded-lg hover:bg-white/20 transition-colors"
                aria-label="關閉"
              >
                <X className="w-5 h-5 text-white" />
              </button>
            </div>

            {/* Content - 可滾動區域 */}
            <div className="flex-1 overflow-y-auto px-6 py-4 flex flex-col items-center justify-center min-h-[500px]">
              {/* 成功勾選動畫 */}
              <div className="mb-6">
                <div
                  className="w-24 h-24 rounded-full flex items-center justify-center shadow-lg"
                  style={{
                    background: 'linear-gradient(135deg, white, var(--theme-surface))'
                  }}
                >
                  <div
                    className="w-20 h-20 rounded-full flex items-center justify-center"
                    style={{
                      background: 'linear-gradient(135deg, var(--theme-primary), var(--theme-secondary))'
                    }}
                  >
                    <Check className="w-12 h-12 text-white stroke-[3]" />
                  </div>
                </div>
              </div>

              {/* 標題文字 */}
              <div className="text-center mb-6">
                <h2 className="text-2xl md:text-3xl font-bold mb-2" style={{ color: 'var(--theme-text)' }}>
                  感謝您的回覆
                </h2>
                <p className="text-base md:text-lg max-w-sm mx-auto" style={{ color: 'var(--theme-text-secondary)' }}>
                  您的寶貴意見將幫助我們提供更好的服務
                </p>
              </div>

              {/* Logo 和機構資訊 */}
              <div className="mb-6">
                <img src={logo} alt="雄i聊" className="w-16 h-16 mx-auto mb-3 object-contain" />
                <div className="text-center space-y-1">
                  <p className="text-base font-bold" style={{ color: 'var(--theme-primary)' }}>
                    高雄市政府毒品防制局
                  </p>
                  <p className="text-sm" style={{ color: 'var(--theme-text-secondary)' }}>
                    關心您的健康與福祉
                  </p>
                </div>
              </div>

            </div>

            {/* Footer - 固定在底部 */}
            <div
              className="px-6 py-3 border-t flex items-center justify-between flex-shrink-0"
              style={{ borderColor: 'var(--theme-border)' }}
            >
              {/* Progress Dots - 全部完成 */}
              <div className="flex gap-2">
                {[1, 2, 3].map(step => (
                  <div
                    key={step}
                    className="w-3 h-3 rounded-full transition-all duration-300"
                    style={{
                      backgroundColor: 'var(--theme-secondary)'
                    }}
                  />
                ))}
              </div>

              {/* 關閉按鈕 */}
              <Button
                onClick={handleClose}
                className="px-8 py-2 text-white font-medium shadow-md hover:shadow-lg transition-all"
                style={{
                  background: 'linear-gradient(135deg, var(--theme-primary), var(--theme-secondary))'
                }}
              >
                關閉
              </Button>
            </div>
          </>

        )}
      </DialogContent>
    </Dialog>
  )
}