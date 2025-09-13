// 訊息相關的類型定義

export interface Message {
  id: string
  sender: 'user' | 'counselor'
  content: string
  timestamp: string
  isLoading?: boolean
  isMockResponse?: boolean
  contentType?: 'text' | 'rich-text' | 'images' | 'cards' | 'mixed'
  images?: ImageContent[]
  cards?: InfoCard[]
  richContent?: string
}

export interface ImageContent {
  url: string
  alt?: string
  caption?: string
}

export interface InfoCard {
  id: string
  title: string
  description: string
  links: CardLink[]
  style?: 'default' | 'highlight'
}

export interface CardLink {
  text: string
  type: 'url' | 'command'
  action: string
}

export interface CommandResponse {
  type: 'rich-text' | 'images' | 'cards' | 'mixed'
  content: string
  images?: ImageContent[]
  cards?: InfoCard[]
  richContent?: string
}