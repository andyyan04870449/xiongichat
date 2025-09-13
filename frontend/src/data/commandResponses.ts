// 前端固定指令回應資料庫
import { CommandResponse } from '../types/message'
import { EDUCATION_RESOURCES } from './educationResources'
import { MULTI_COUNSELING_RESOURCES } from './multiCounselingResources'
import { SUPPORT_RESOURCES } from './supportResources'
import { MATERNAL_CHILD_RESOURCES } from './maternalChildResources'
import { ADDICTION_RESOURCES } from './addictionResources'

// 合併所有指令回應
export const COMMAND_RESPONSES: Record<string, CommandResponse> = {
  // 衛教資源相關指令
  ...EDUCATION_RESOURCES,

  // 多元輔導相關指令
  ...MULTI_COUNSELING_RESOURCES,

  // 扶助資源相關指令
  ...SUPPORT_RESOURCES,

  // 婦幼專區相關指令
  ...MATERNAL_CHILD_RESOURCES,

  // 戒癮資源相關指令
  ...ADDICTION_RESOURCES,

  // 其他原有指令

  // 次級指令回應（由卡片連結觸發）
  '#社福詳情': {
    type: 'rich-text',
    content: '社會福利詳細資訊',
    richContent: `
      <b>📋 社會福利申請指南</b><br><br>

      <b>申請資格：</b><br>
      • 設籍高雄市滿6個月以上<br>
      • 符合低收入戶或中低收入戶資格<br>
      • 遭遇急難需要協助者<br><br>

      <b>補助項目：</b><br>
      • 生活扶助金：每月3,000-15,000元<br>
      • 醫療補助：健保費、醫療自付額補助<br>
      • 教育補助：學雜費、書籍費補助<br>
      • 急難救助：最高30,000元<br><br>

      <b>申請方式：</b><br>
      1. 攜帶身分證、戶口名簿<br>
      2. 至區公所社會課申請<br>
      3. 或線上申請：<a href="https://socbu.kcg.gov.tw" target="_blank">高雄市社會局網站</a><br><br>

      諮詢電話：07-336-8333
    `
  },

  '#職訓資訊': {
    type: 'rich-text',
    content: '職業訓練課程資訊',
    richContent: `
      <b>🎓 職業訓練課程</b><br><br>

      <b>目前開設課程：</b><br>
      • 電腦文書處理班（3個月）<br>
      • 餐飲烹調班（4個月）<br>
      • 美容美髮班（3個月）<br>
      • 水電修護班（3個月）<br>
      • 照顧服務員訓練（2個月）<br><br>

      <b>課程特色：</b><br>
      ✅ 完全免費<br>
      ✅ 提供午餐<br>
      ✅ 結訓後輔導就業<br>
      ✅ 訓練期間生活津貼<br><br>

      報名專線：07-822-9595
    `
  }
}

// 檢查是否為有效指令
export function isValidCommand(text: string): boolean {
  return text.startsWith('#') && COMMAND_RESPONSES.hasOwnProperty(text)
}

// 獲取指令回應
export function getCommandResponse(command: string): CommandResponse | null {
  return COMMAND_RESPONSES[command] || null
}