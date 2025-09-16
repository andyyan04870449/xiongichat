/**
 * 統一時間配置
 * 所有時間相關的配置和常數都在這裡定義
 */

export const TIME_CONFIG = {
  // 時區設定
  TIMEZONE: 'Asia/Taipei' as const,
  LOCALE: 'zh-TW' as const,

  // 時間格式選項
  FORMATS: {
    // 僅時間 (例如: 下午3:30)
    TIME_ONLY: {
      hour: '2-digit' as const,
      minute: '2-digit' as const,
      hour12: true
    },

    // 日期和時間 (例如: 09/16 下午3:30)
    DATE_TIME_SHORT: {
      month: '2-digit' as const,
      day: '2-digit' as const,
      hour: '2-digit' as const,
      minute: '2-digit' as const,
      hour12: true
    },

    // 完整日期時間 (例如: 2025年9月16日 下午3:30)
    DATE_TIME_FULL: {
      year: 'numeric' as const,
      month: 'long' as const,
      day: 'numeric' as const,
      hour: '2-digit' as const,
      minute: '2-digit' as const,
      hour12: true
    },

    // 僅日期 (例如: 09/16)
    DATE_ONLY: {
      month: '2-digit' as const,
      day: '2-digit' as const
    }
  } as const
} as const

// 匯出類型定義
export type TimeFormatKey = keyof typeof TIME_CONFIG.FORMATS