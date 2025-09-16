/**
 * 統一的日期時間工具函數
 * 所有時間顯示都通過這些函數處理，確保一致性
 */

import { TIME_CONFIG, type TimeFormatKey } from '../config/timeConfig'

/**
 * 解析日期時間字串
 * 處理各種格式的時間字串，包含時區資訊
 * @param dateTimeString 日期時間字串
 * @returns Date 物件
 */
export function parseDateTime(dateTimeString: string | Date | undefined | null): Date {
  // 如果已經是 Date 物件，直接返回
  if (dateTimeString instanceof Date) {
    return dateTimeString
  }

  // 如果是空值，返回當前時間
  if (!dateTimeString) {
    console.warn('[DateUtils] Empty datetime string, using current time')
    return new Date()
  }

  try {
    const date = new Date(dateTimeString)

    // 檢查是否為有效日期
    if (isNaN(date.getTime())) {
      console.error('[DateUtils] Invalid date:', dateTimeString)
      return new Date()
    }

    return date
  } catch (error) {
    console.error('[DateUtils] Parse error:', error, 'Input:', dateTimeString)
    return new Date()
  }
}

/**
 * 格式化日期時間為台灣時區
 * 使用預定義的格式或自定義選項
 * @param date Date 物件或日期字串
 * @param formatKey 預定義格式的鍵值或自定義選項
 * @returns 格式化後的字串
 */
export function formatTaiwanTime(
  date: Date | string | undefined | null,
  formatKey?: TimeFormatKey | Intl.DateTimeFormatOptions
): string {
  // 解析日期
  const parsedDate = parseDateTime(date)

  // 決定格式選項
  let options: Intl.DateTimeFormatOptions

  if (!formatKey) {
    // 預設使用日期時間短格式
    options = TIME_CONFIG.FORMATS.DATE_TIME_SHORT
  } else if (typeof formatKey === 'string') {
    // 使用預定義格式
    options = TIME_CONFIG.FORMATS[formatKey]
  } else {
    // 使用自定義選項
    options = formatKey
  }

  // 確保包含時區設定
  const finalOptions: Intl.DateTimeFormatOptions = {
    timeZone: TIME_CONFIG.TIMEZONE,
    ...options
  }

  try {
    const formatter = new Intl.DateTimeFormat(TIME_CONFIG.LOCALE, finalOptions)
    return formatter.format(parsedDate)
  } catch (error) {
    console.error('[DateUtils] Format error:', error)
    return parsedDate.toLocaleString(TIME_CONFIG.LOCALE)
  }
}

/**
 * 格式化為僅時間（例如: 下午3:30）
 */
export function formatTaiwanTimeOnly(date: Date | string | undefined | null): string {
  return formatTaiwanTime(date, 'TIME_ONLY')
}

/**
 * 格式化為僅日期（例如: 09/16）
 */
export function formatTaiwanDateOnly(date: Date | string | undefined | null): string {
  return formatTaiwanTime(date, 'DATE_ONLY')
}

/**
 * 格式化為短日期時間（例如: 09/16 下午3:30）
 */
export function formatTaiwanDateTimeShort(date: Date | string | undefined | null): string {
  return formatTaiwanTime(date, 'DATE_TIME_SHORT')
}

/**
 * 格式化為完整日期時間（例如: 2025年9月16日 下午3:30）
 */
export function formatTaiwanDateTimeFull(date: Date | string | undefined | null): string {
  return formatTaiwanTime(date, 'DATE_TIME_FULL')
}

/**
 * 生成對話標題（根據開始時間）
 */
export function generateConversationTitle(startTime: Date | string | undefined | null): string {
  const parsedTime = parseDateTime(startTime)
  const now = new Date()
  const daysDiff = Math.floor((now.getTime() - parsedTime.getTime()) / (1000 * 3600 * 24))

  const timeStr = formatTaiwanTimeOnly(parsedTime)

  if (daysDiff === 0) return `今日諮詢 ${timeStr}`
  if (daysDiff === 1) return `昨日諮詢 ${timeStr}`
  if (daysDiff < 7) return `${daysDiff}天前諮詢`

  const dateStr = formatTaiwanDateOnly(parsedTime)
  return `諮詢記錄 ${dateStr}`
}

/**
 * 取得當前台灣時間的時間字串（用於新訊息）
 */
export function getCurrentTaiwanTimeString(): string {
  return formatTaiwanTimeOnly(new Date())
}

/**
 * 從後端時間戳記格式化顯示時間
 * 後端返回的格式通常是 ISO 8601 含時區（例如: 2025-09-16T21:00:00+08:00）
 */
export function formatBackendTimestamp(timestamp: string | undefined | null): string {
  if (!timestamp) {
    return getCurrentTaiwanTimeString()
  }
  return formatTaiwanTimeOnly(timestamp)
}