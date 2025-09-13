import React, { useState, useEffect, useRef } from 'react'
import { Send, Phone, Heart, BookOpen, Users, Calendar, MessageCircle, LogOut, Flame, Shield, Baby, HandHeart, Menu, X, ClipboardList, AlertCircle, Loader2, WifiOff, AlertTriangle, History, FileText } from 'lucide-react'
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Card } from "./ui/card"
import { Avatar, AvatarImage, AvatarFallback } from "./ui/avatar"
import { Badge } from "./ui/badge"
import { Alert, AlertDescription } from "./ui/alert"
import { ChatHistoryModal } from "./ChatHistoryModal"
import { ResourceFormModal } from "./ResourceFormModal"
import { ScrollArea } from "./ui/scroll-area"
import { Separator } from "./ui/separator"
import logo from 'figma:asset/e9a9f75d2ac26ddaa75b766f16261c08e59f132c.png'
import chatbotAvatar from 'figma:asset/d2489a7281852ae82edf81f47c4ed2529464e955.png'
import { sendChatMessageSmart, generateUserId, testApiConnection, getCurrentApiEndpoint, getApiStatus, setApiEndpoint, getAvailableEndpoints, ApiError, type ChatResponse } from '../services/chatApi'
import { Message as MessageType, ImageContent, InfoCard } from '../types/message'
import { COMMAND_RESPONSES, isValidCommand, getCommandResponse } from '../data/commandResponses'
import { RichTextRenderer } from './message/RichTextRenderer'
import { ImageGallery } from './message/ImageGallery'
import { InfoCardCarousel } from './message/InfoCardCarousel'

// Use the imported Message type from types/message.ts
type Message = MessageType

interface ServiceCard {
  title: string
  description: string
  icon: React.ReactNode
  color: string
}

interface ChatPageProps {
  onLogout: () => void
  onNavigateToAssessment?: () => void
  userPassword?: string
}

// Markdown渲染組件
function MarkdownRenderer({ content }: { content: string }) {
  // 解析Markdown格式並轉換為React元素
  const parseMarkdown = (text: string) => {
    const elements: React.ReactNode[] = []
    
    // 分割段落 (\n\n)
    const paragraphs = text.split('\n\n')
    
    paragraphs.forEach((paragraph, pIndex) => {
      if (!paragraph.trim()) return
      
      // 檢查是否是條列項目
      const bulletListRegex = /^•\s(.+)$/gm
      const numberedListRegex = /^(\d+)\.\s(.+)$/gm
      
      const bulletMatches = [...paragraph.matchAll(bulletListRegex)]
      const numberedMatches = [...paragraph.matchAll(numberedListRegex)]
      
      if (bulletMatches.length > 0) {
        // 處理無序列表
        const listItems = bulletMatches.map((match, index) => (
          <li key={`bullet-${pIndex}-${index}`} className="ml-4 mb-1">
            {parseInlineMarkdown(match[1])}
          </li>
        ))
        elements.push(
          <ul key={`bullet-list-${pIndex}`} className="list-disc list-outside space-y-1 mb-3">
            {listItems}
          </ul>
        )
      } else if (numberedMatches.length > 0) {
        // 處理有序列表
        const listItems = numberedMatches.map((match, index) => (
          <li key={`numbered-${pIndex}-${index}`} className="ml-4 mb-1">
            {parseInlineMarkdown(match[2])}
          </li>
        ))
        elements.push(
          <ol key={`numbered-list-${pIndex}`} className="list-decimal list-outside space-y-1 mb-3">
            {listItems}
          </ol>
        )
      } else {
        // 處理一般段落
        elements.push(
          <p key={`paragraph-${pIndex}`} className="mb-3 last:mb-0">
            {parseInlineMarkdown(paragraph)}
          </p>
        )
      }
    })
    
    return elements
  }
  
  // 處理行內Markdown格式（粗體、連結）
  const parseInlineMarkdown = (text: string) => {
    const elements: React.ReactNode[] = []
    let lastIndex = 0
    
    // 匹配粗體和連結的正則表達式
    const markdownRegex = /(\*\*([^*]+)\*\*)|(\[([^\]]+)\]\(([^)]+)\))/g
    let match
    
    while ((match = markdownRegex.exec(text)) !== null) {
      // 添加匹配前的普通文字
      if (match.index > lastIndex) {
        elements.push(text.slice(lastIndex, match.index))
      }
      
      if (match[1]) {
        // 粗體文字 **text**
        elements.push(
          <strong key={`bold-${match.index}`} className="font-semibold">
            {match[2]}
          </strong>
        )
      } else if (match[3]) {
        // 連結 [text](url)
        elements.push(
          <a 
            key={`link-${match.index}`}
            href={match[5]}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline break-all"
          >
            {match[4]}
          </a>
        )
      }
      
      lastIndex = match.index + match[0].length
    }
    
    // 添加剩餘的文字
    if (lastIndex < text.length) {
      elements.push(text.slice(lastIndex))
    }
    
    return elements.length > 0 ? elements : text
  }
  
  return <div className="markdown-content">{parseMarkdown(content)}</div>
}

export function ChatPage({ onLogout, onNavigateToAssessment, userPassword }: ChatPageProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'counselor',
      content: '您好！\n歡迎進來聊一聊，分享心情💕\n\n您可以放心聊天或詢問想知道的服務資訊📝\n也可以點選快速選單為您服務喔！\n\n在乎！守護！陪伴！我們一直都在❤️',
      timestamp: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
    }
  ])

  const [newMessage, setNewMessage] = useState('')
  const [showServices, setShowServices] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [userId] = useState<string>(() => generateUserId(userPassword))
  const [error, setError] = useState<string | null>(null)
  const [apiStatus, setApiStatus] = useState<'unknown' | 'connected' | 'disconnected' | 'mock'>('unknown')
  const [isUsingMock, setIsUsingMock] = useState(false)
  const [keyboardVisible, setKeyboardVisible] = useState(false)
  const [showChatHistory, setShowChatHistory] = useState(false)
  const [showResourceForm, setShowResourceForm] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  // 自動滾動到最新訊息
  const scrollToBottom = (force = false) => {
    // 使用requestAnimationFrame確保DOM更新完成後再滾動
    requestAnimationFrame(() => {
      if (messagesEndRef.current && messagesContainerRef.current) {
        // 直接設置scrollTop到最大值
        messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight
      }
    })
  }

  // 當訊息更新時滾動到底部
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 組件載入時檢查API狀態
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        console.log('🔍 檢查API連接狀態...')
        
        // 使用靜默模式進��快速檢查
        const isConnected = await testApiConnection(true)
        
        if (isConnected) {
          setApiStatus('connected')
          console.log(`✅ API已連接: ${getCurrentApiEndpoint()}`)
        } else {
          setApiStatus('disconnected')
          console.log('📡 API服務不可用，將在需要時自動使用離線模式')
          console.log('💡 開發者工具:')
          console.log('   window.switchApiEndpoint("NGROK")  // 切換到ngrok')
          console.log('   window.switchApiEndpoint("LOCAL")  // 切換到localhost')
          console.log('   window.testAllEndpoints()          // 測試所有端點')
        }
      } catch (error) {
        console.warn('API狀態檢查失敗，將使用離線模式')
        setApiStatus('disconnected')
      }
    }

    checkApiStatus()

    // 在window對象上添加切換函數供開發者使用
    ;(window as any).switchApiEndpoint = (endpoint: string) => {
      const success = setApiEndpoint(endpoint)
      if (success) {
        console.log(`✅ 已切換到端點: ${getCurrentApiEndpoint()}`)
        checkApiStatus()
      } else {
        console.error('❌ 切換失敗，請提供有效的端點名稱或URL')
        console.log('可用選項:', Object.keys(getAvailableEndpoints()))
      }
    }

    ;(window as any).getApiStatus = async () => {
      const status = await getApiStatus()
      console.log('📊 API狀態:', status)
      return status
    }

    ;(window as any).testAllEndpoints = async () => {
      console.log('🔍 測試所有API端點...')
      const status = await getApiStatus()
      console.table(status.testedEndpoints)
      return status
    }

    return () => {
      // 清理全域函數
      delete (window as any).switchApiEndpoint
      delete (window as any).getApiStatus
      delete (window as any).testAllEndpoints
    }
  }, [])

  // 監聽鍵盤顯示/隱藏事件
  useEffect(() => {
    const handleKeyboardToggle = (event: CustomEvent) => {
      const { visible } = event.detail
      setKeyboardVisible(visible)
      
      if (visible) {
        // 鍵盤顯示時，確保滾動到底部並讓輸入框可見
        setTimeout(() => {
          scrollToBottom(true)
          
          // 額外確保輸入框可見
          if (inputRef.current) {
            inputRef.current.scrollIntoView({
              behavior: 'smooth',
              block: 'end', // 確保輸入框在視窗底部
              inline: 'nearest'
            })
          }
        }, 150) // 稍微延長時間確保鍵盤完全顯示
      } else {
        // 鍵盤隱藏時，重新滾動到底部
        setTimeout(() => {
          scrollToBottom()
        }, 150)
      }
    }

    window.addEventListener('keyboardToggle', handleKeyboardToggle as EventListener)
    
    return () => {
      window.removeEventListener('keyboardToggle', handleKeyboardToggle as EventListener)
    }
  }, [])

  // 輸入框聚焦時的處理
  const handleInputFocus = () => {
    // 聚焦時延遲滾動，確保鍵盤完全顯示後再滾動到底部
    setTimeout(() => {
      scrollToBottom(true)
      
      // 確保輸入框在可視範圍內
      if (inputRef.current && messagesContainerRef.current) {
        // 先滾動消息到底部
        messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight
        
        // 然後確保輸入框可見
        setTimeout(() => {
          inputRef.current?.scrollIntoView({
            behavior: 'smooth',
            block: 'end',
            inline: 'nearest'
          })
        }, 100)
      }
    }, 400) // 給鍵盤更多時間來顯示
  }

  // 處理輸入框點擊
  const handleInputClick = () => {
    // 點擊輸入框時也要確保滾動到底部
    setTimeout(() => {
      scrollToBottom(true)
    }, 100)
  }

  const serviceCards: ServiceCard[] = [
    {
      title: '聊天吧',
      description: '24小時線上諮詢服務',
      icon: <MessageCircle className="w-6 h-6 md:w-8 md:h-8" />,
      color: 'var(--theme-primary)'
    },
    {
      title: '衛教資源',
      description: '健康教育與防治資訊',
      icon: <BookOpen className="w-6 h-6 md:w-8 md:h-8" />,
      color: 'var(--theme-secondary)'
    },
    {
      title: '多元輔導',
      description: '專業諮詢與心理支持',
      icon: <Users className="w-6 h-6 md:w-8 md:h-8" />,
      color: 'var(--theme-accent)'
    },
    {
      title: '扶助資源',
      description: '社會資源與協助服務',
      icon: <HandHeart className="w-6 h-6 md:w-8 md:h-8" />,
      color: '#10b981'
    },
    {
      title: '婦幼專區',
      description: '婦女兒童專屬服務',
      icon: <Baby className="w-6 h-6 md:w-8 md:h-8" />,
      color: '#f43f5e'
    },
    {
      title: '戒癮專區',
      description: '戒毒康復專業服務',
      icon: <Shield className="w-6 h-6 md:w-8 md:h-8" />,
      color: '#ef4444'
    },
    {
      title: '自我評量',
      description: '專業評估與自我檢測',
      icon: <ClipboardList className="w-6 h-6 md:w-8 md:h-8" />,
      color: '#8b5cf6'
    },
    {
      title: '資源表單',
      description: '申請表格與文件下載',
      icon: <FileText className="w-6 h-6 md:w-8 md:h-8" />,
      color: '#06b6d4'
    },
    {
      title: '天燈Go',
      description: '心靈療癒與希望寄託',
      icon: <Flame className="w-6 h-6 md:w-8 md:h-8" />,
      color: 'var(--theme-primary)'
    }
  ]

  const sendMessage = async () => {
    if (!newMessage.trim() || isLoading) return

    const messageText = newMessage.trim()
    setNewMessage('')
    setError(null)

    // 檢查是否為固定指令
    if (isValidCommand(messageText)) {
      processCommandResponse(messageText)
      return
    }

    // 添加用戶訊息
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      sender: 'user',
      content: messageText,
      timestamp: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
    }

    // 添加載入中的諮詢師訊息
    const loadingMessage: Message = {
      id: `loading_${Date.now()}`,
      sender: 'counselor',
      content: '',
      timestamp: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }),
      isLoading: true
    }

    setMessages(prev => [...prev, userMessage, loadingMessage])
    setIsLoading(true)

    // 發送訊息後確保滾動到底部
    setTimeout(() => {
      scrollToBottom(true)
    }, 50)

    try {
      // 調用智能API服務 - 確保傳遞 null 而不是 undefined
      const response: ChatResponse = await sendChatMessageSmart({
        user_id: userId,
        message: messageText,
        conversation_id: conversationId // 如果是 null 就保持 null，如果有值就傳遞值
      })

      // 更新conversation_id（如果是第一次對話）
      if (!conversationId) {
        setConversationId(response.conversation_id)
      }

      // 檢查是否使用了Mock API
      const isMockResponse = response.conversation_id.startsWith('conv_') || 
                           response.user_message_id.startsWith('msg_') ||
                           response.assistant_message_id.startsWith('msg_')
      setIsUsingMock(isMockResponse)
      setApiStatus(isMockResponse ? 'mock' : 'connected')
      
      // 如果是Mock回應，清除任何現有錯誤
      if (isMockResponse && error) {
        setError(null)
      }

      // 移除載入訊息並添加真實回覆
      setMessages(prev => {
        const withoutLoading = prev.filter(msg => msg.id !== loadingMessage.id)
        const assistantMessage: Message = {
          id: response.assistant_message_id,
          sender: 'counselor',
          content: response.reply,
          timestamp: new Date(response.timestamp).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }),
          isMockResponse
        }
        return [...withoutLoading, assistantMessage]
      })

    } catch (err) {
      console.error('發送訊息錯誤:', err)
      
      // 移除載入訊息
      setMessages(prev => prev.filter(msg => msg.id !== loadingMessage.id))
      
      // 根據錯誤類型顯示不同的錯誤訊息
      if (err instanceof ApiError) {
        // 處理 ApiError
        if (err.isCorsError) {
          setError('連接服務時發生跨域錯誤，目前使用離線模式為您提供服務。')
          setApiStatus('mock')
        } else if (err.isNetworkError) {
          setError('網路連線有問題，請檢查您的網路連線。')
          setApiStatus('disconnected')
        } else {
          setError(err.message || '發送訊息時發生錯誤')
          setApiStatus('disconnected')
        }
      } else if (err instanceof Error) {
        // 處理一般 Error
        setError(`發送訊息失敗: ${err.message}`)
        setApiStatus('disconnected')
      } else {
        // 處理未知錯誤
        setError('發送訊息時發生未知錯誤，請稍後再試。')
        setApiStatus('disconnected')
      }
    } finally {
      setIsLoading(false)
    }
  }

  // 處理固定指令回應
  const processCommandResponse = (command: string) => {
    const response = getCommandResponse(command)
    if (!response) return

    // 添加用戶訊息
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      sender: 'user',
      content: command,
      timestamp: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
    }

    // 建立機器人回應訊息
    const botMessage: Message = {
      id: `bot_${Date.now()}`,
      sender: 'counselor',
      content: response.content,
      contentType: response.type as any,
      images: response.images,
      cards: response.cards,
      richContent: response.richContent,
      timestamp: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
    }

    setMessages(prev => [...prev, userMessage, botMessage])

    // 滾動到底部
    setTimeout(() => scrollToBottom(true), 100)
  }

  const handleServiceClick = (serviceTitle: string) => {
    if (serviceTitle === '天燈Go') {
      window.open('https://clock-arc-82195815.figma.site', '_blank')
    } else if (serviceTitle === '自我評量') {
      onNavigateToAssessment?.()
    } else if (serviceTitle === '資源表單') {
      setShowResourceForm(true)
    } else if (serviceTitle === '衛教資源' || serviceTitle === '多元輔導' || serviceTitle === '扶助資源' || serviceTitle === '婦幼專區' || serviceTitle === '戒癮資源') {
      // 處理固定指令
      const command = `#${serviceTitle}`
      processCommandResponse(command)
    } else if (serviceTitle === '衛教資源' && false) {
      if (!isLoading) {
        const messageText = '#衛教資源'
        setError(null)

        const userMessage: Message = {
          id: `user_${Date.now()}`,
          sender: 'user',
          content: messageText,
          timestamp: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
        }

        const loadingMessage: Message = {
          id: `loading_${Date.now()}`,
          sender: 'counselor',
          content: '',
          timestamp: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }),
          isLoading: true
        }

        setMessages(prev => [...prev, userMessage, loadingMessage])
        setIsLoading(true)

        setTimeout(() => {
          scrollToBottom(true)
        }, 50)

        sendChatMessageSmart({
          user_id: userId,
          message: messageText,
          conversation_id: conversationId
        }).then((response: ChatResponse) => {
          if (!conversationId) {
            setConversationId(response.conversation_id)
          }

          const isMockResponse = response.conversation_id.startsWith('conv_') || 
                               response.user_message_id.startsWith('msg_') ||
                               response.assistant_message_id.startsWith('msg_')
          setIsUsingMock(isMockResponse)
          setApiStatus(isMockResponse ? 'mock' : 'connected')
          
          if (isMockResponse && error) {
            setError(null)
          }

          setMessages(prev => {
            const withoutLoading = prev.filter(msg => msg.id !== loadingMessage.id)
            const assistantMessage: Message = {
              id: response.assistant_message_id,
              sender: 'counselor',
              content: response.reply,
              timestamp: new Date(response.timestamp).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }),
              isMockResponse
            }
            return [...withoutLoading, assistantMessage]
          })
        }).catch((err) => {
          console.error('發送訊息錯誤:', err)
          
          setMessages(prev => prev.filter(msg => msg.id !== loadingMessage.id))
          
          if (err instanceof ApiError) {
            if (err.isCorsError) {
              setError('連接服務時發生跨域錯誤，目前使用離線模式為您提供服務。')
              setApiStatus('mock')
            } else if (err.isNetworkError) {
              setError('網路連線有問題，請檢查您的網路連線。')
              setApiStatus('disconnected')
            } else {
              setError(err.message || '發送訊息時發生錯誤')
              setApiStatus('disconnected')
            }
          } else if (err instanceof Error) {
            setError(`發送訊息失敗: ${err.message}`)
            setApiStatus('disconnected')
          } else {
            setError('發送訊息時發生未知錯誤，請稍後再試。')
            setApiStatus('disconnected')
          }
        }).finally(() => {
          setIsLoading(false)
        })
      }
    }
    setShowServices(false)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // API狀態徽章
  const getStatusBadge = () => {
    switch (apiStatus) {
      case 'connected':
        return (
          <Badge className="text-xs bg-green-100 text-green-800 border-green-200">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
            線上服務中
          </Badge>
        )
      case 'mock':
        return (
          <Badge className="text-xs bg-orange-100 text-orange-800 border-orange-200">
            <AlertTriangle className="w-3 h-3 mr-1" />
            離線模式
          </Badge>
        )
      case 'disconnected':
        return (
          <Badge className="text-xs bg-red-100 text-red-800 border-red-200">
            <WifiOff className="w-3 h-3 mr-1" />
            連線中斷
          </Badge>
        )
      default:
        return (
          <Badge className="text-xs bg-gray-100 text-gray-800 border-gray-200">
            檢測中...
          </Badge>
        )
    }
  }

  return (
    <div 
      ref={chatContainerRef}
      className={`w-full h-full safe-area-inset transition-all duration-300 ${
        keyboardVisible ? 'keyboard-adaptive-height' : 'min-h-screen'
      }`}
      style={{
        background: `linear-gradient(135deg, var(--theme-background), var(--theme-surface))`,
        height: keyboardVisible ? 'calc(var(--visual-vh, 1vh) * 100)' : '100vh',
        maxHeight: keyboardVisible ? 'calc(var(--visual-vh, 1vh) * 100)' : '100vh'
      }}
    >
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-sm shadow-sm border-b flex-shrink-0" style={{ borderColor: 'var(--theme-border)' }}>
        <div className="w-full px-3 md:px-4 py-3 md:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 md:space-x-4 min-w-0 flex-1">
              <div className="flex-shrink-0">
                <img src={logo} alt="雄i聊" className="h-8 md:h-12 w-auto" />
              </div>
              <div className="min-w-0 flex-1">
                <h1 className="text-base md:text-xl font-semibold text-gray-800 truncate">雄i 聊智能客服機器人</h1>
                <p className="text-xs md:text-sm text-gray-600 hidden sm:block truncate">高雄市毒品防制局 · 專業關懷 · 陪伴康復</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 flex-shrink-0">
              {getStatusBadge()}
              {/* Mobile Service Menu Toggle */}
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setShowServices(!showServices)}
                className="md:hidden text-gray-600 hover:text-gray-800 min-h-[44px]"
                style={{ borderColor: 'var(--theme-border)' }}
              >
                {showServices ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
              </Button>
              {/* Chat History Button */}
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setShowChatHistory(true)}
                className="text-gray-600 hover:text-gray-800 min-h-[44px]"
                style={{ borderColor: 'var(--theme-border)' }}
              >
                <History className="w-4 h-4 mr-0 md:mr-2" />
                <span className="hidden md:inline">對話記錄</span>
              </Button>
              
              <Button 
                variant="outline" 
                size="sm" 
                onClick={onLogout}
                className="text-gray-600 hover:text-gray-800 min-h-[44px]"
                style={{ borderColor: 'var(--theme-border)' }}
              >
                <LogOut className="w-4 h-4 mr-0 md:mr-2" />
                <span className="hidden md:inline">登出</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Service Menu Overlay */}
      {showServices && (
        <div className="fixed inset-0 bg-black/30 z-40 md:hidden" onClick={() => setShowServices(false)}>
          <div 
            className="absolute right-0 top-0 w-80 max-w-[90vw] bg-white/95 backdrop-blur-sm shadow-xl overflow-y-auto"
            style={{ 
              height: keyboardVisible ? 'calc(var(--visual-vh, 1vh) * 100)' : '100vh',
              maxHeight: keyboardVisible ? 'calc(var(--visual-vh, 1vh) * 100)' : '100vh'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 border-b" style={{ borderColor: 'var(--theme-border)' }}>
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-800">服務選單</h3>
                <Button variant="ghost" size="sm" onClick={() => setShowServices(false)} className="min-h-[44px]">
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div className="p-4 space-y-3">
              {serviceCards.map((service, index) => (
                <Card 
                  key={index} 
                  className="p-4 hover:shadow-md transition-shadow cursor-pointer border-l-4 border min-h-[44px] flex items-center"
                  style={{ 
                    borderLeftColor: 'var(--theme-primary)',
                    borderColor: 'var(--theme-border)'
                  }}
                  onClick={() => handleServiceClick(service.title)}
                >
                  <div className="flex items-center space-x-3 w-full">
                    <div 
                      className="text-white p-2 rounded-lg flex-shrink-0"
                      style={{ backgroundColor: service.color }}
                    >
                      {service.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-800 truncate">{service.title}</h3>
                      <p className="text-sm text-gray-600 truncate">{service.description}</p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div 
        className="flex-1 w-full flex flex-col md:flex-row gap-2 md:gap-6 p-2 md:p-4 overflow-hidden"
        style={{ 
          height: keyboardVisible 
            ? 'calc(var(--visual-vh, 1vh) * 100 - 70px)' 
            : 'calc(100vh - 70px)',
          maxHeight: keyboardVisible 
            ? 'calc(var(--visual-vh, 1vh) * 100 - 70px)' 
            : 'calc(100vh - 70px)'
        }}
      >
        {/* Chat Area */}
        <div 
          className="flex-1 bg-white/90 backdrop-blur-sm rounded-lg md:rounded-xl shadow-sm overflow-hidden border flex flex-col min-h-0"
          style={{ borderColor: 'var(--theme-border)' }}
        >
          {/* Chat Header */}
          <div 
            className="text-white p-3 md:p-4 flex-shrink-0"
            style={{
              background: `linear-gradient(to right, var(--theme-primary), var(--theme-secondary))`
            }}
          >
            <div className="flex items-center space-x-3">
              <Heart className="w-5 h-5 md:w-6 md:h-6 text-white/90 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <h2 className="font-semibold text-base md:text-lg truncate">雄i 聊智能客服</h2>
                <p className="text-white/90 text-xs md:text-sm truncate">
                  {apiStatus === 'mock' ? 'AI模擬諮詢服務（離線模式）' : 'AI驅動的專業諮詢服務，保密且溫暖'}
                </p>
              </div>
              <div className="flex flex-col items-end space-y-1 flex-shrink-0">
                {/* API狀態指��器 */}
                <div className={`px-2 py-1 rounded text-xs flex items-center space-x-1 ${
                  apiStatus === 'connected' ? 'bg-green-500/20 text-green-100' :
                  apiStatus === 'mock' ? 'bg-amber-500/20 text-amber-100' :
                  'bg-red-500/20 text-red-100'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    apiStatus === 'connected' ? 'bg-green-400' :
                    apiStatus === 'mock' ? 'bg-amber-400' :
                    'bg-red-400'
                  }`} />
                  <span>
                    {apiStatus === 'connected' ? '已連線' :
                     apiStatus === 'mock' ? '離線模式' :
                     apiStatus === 'disconnected' ? '未連線' :
                     '檢查中...'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <Alert className="m-3 md:m-4 bg-orange-50 border-orange-200">
              <AlertCircle className="w-4 h-4 text-orange-600" />
              <AlertDescription className="text-orange-800">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {/* Messages Area */}
          <div 
            ref={messagesContainerRef}
            className="flex-1 overflow-y-auto px-3 md:px-4 py-2 space-y-4"
            style={{ scrollBehavior: 'smooth' }}
          >
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
              >
                <div className={`flex items-start space-x-3 ${
                  message.sender === 'user' ? 'flex-row-reverse space-x-reverse max-w-[85%] md:max-w-[70%]' :
                  message.contentType === 'cards' || message.contentType === 'images' ? 'max-w-[95%] md:max-w-[85%]' : 'max-w-[85%] md:max-w-[70%]'
                }`}>
                  {/* Avatar */}
                  <Avatar className="w-8 h-8 md:w-10 md:h-10 flex-shrink-0">
                    {message.sender === 'counselor' ? (
                      <AvatarImage src={chatbotAvatar} alt="諮詢師頭像" />
                    ) : null}
                    <AvatarFallback 
                      className="text-white"
                      style={{ 
                        backgroundColor: message.sender === 'user' ? 'var(--theme-accent)' : 'var(--theme-primary)' 
                      }}
                    >
                      {message.sender === 'user' ? '我' : '諮'}
                    </AvatarFallback>
                  </Avatar>

                  {/* Message Bubble */}
                  <div className={`relative px-3 md:px-4 py-2 md:py-3 rounded-xl shadow-sm overflow-hidden ${
                    message.sender === 'user'
                      ? 'bg-gradient-to-r text-white rounded-br-sm'
                      : 'bg-white border rounded-bl-sm'
                  }`}
                  style={{
                    background: message.sender === 'user'
                      ? `linear-gradient(135deg, var(--theme-primary), var(--theme-secondary))`
                      : undefined,
                    borderColor: message.sender === 'counselor' ? 'var(--theme-border)' : undefined,
                    maxWidth: message.contentType === 'cards' || message.contentType === 'images' ? '100%' : undefined
                  }}>
                    {/* Mock Response Badge */}
                    {message.isMockResponse && (
                      <div className="mb-1">
                        <Badge className="text-xs bg-orange-100 text-orange-700 border-orange-200">
                          模擬回應
                        </Badge>
                      </div>
                    )}

                    {/* Message Content */}
                    {message.isLoading ? (
                      <div className="flex items-center space-x-2">
                        <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
                        <span className="text-gray-400 text-sm">思考中...</span>
                      </div>
                    ) : (
                      <div className={`text-sm md:text-base ${
                        message.sender === 'user' ? 'text-white' : 'text-gray-800'
                      }`}>
                        {/* 根據內容類型渲染不同組件 */}
                        {message.contentType === 'rich-text' && message.richContent ? (
                          <RichTextRenderer content={message.richContent} />
                        ) : message.contentType === 'images' && message.images ? (
                          <div className="w-full">
                            <p className="mb-3">{message.content}</p>
                            <div className="w-full overflow-hidden">
                              <ImageGallery images={message.images} />
                            </div>
                          </div>
                        ) : message.contentType === 'cards' && message.cards ? (
                          <div className="w-full">
                            <p className="mb-3">{message.content}</p>
                            <div className="w-full overflow-hidden">
                              <InfoCardCarousel
                                cards={message.cards}
                                onCommandClick={processCommandResponse}
                              />
                            </div>
                          </div>
                        ) : message.contentType === 'mixed' ? (
                          <div className="w-full">
                            {/* 混合內容：先顯示富文本，再顯示圖片 */}
                            {message.richContent && (
                              <div className="mb-4">
                                <RichTextRenderer content={message.richContent} />
                              </div>
                            )}
                            {message.images && message.images.length > 0 && (
                              <div className="w-full overflow-hidden">
                                <ImageGallery images={message.images} />
                              </div>
                            )}
                          </div>
                        ) : (
                          <MarkdownRenderer content={message.content} />
                        )}
                      </div>
                    )}

                    {/* Timestamp */}
                    <div className={`text-xs mt-2 ${
                      message.sender === 'user' ? 'text-white/70' : 'text-gray-400'
                    }`}>
                      {message.timestamp}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div 
            className="border-t bg-white/90 backdrop-blur-sm p-3 md:p-4 flex-shrink-0"
            style={{ borderColor: 'var(--theme-border)' }}
          >
            <div className="flex items-end space-x-2 md:space-x-3">
              <div className="flex-1">
                <Input
                  ref={inputRef}
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  onFocus={handleInputFocus}
                  onClick={handleInputClick}
                  placeholder="請輸入您想說的話..."
                  disabled={isLoading}
                  className="resize-none border-2 focus:ring-2 focus:ring-offset-0 min-h-[44px]"
                  style={{ 
                    borderColor: 'var(--theme-border)',
                    backgroundColor: 'var(--theme-surface)'
                  }}
                />
              </div>
              <Button
                onClick={sendMessage}
                disabled={!newMessage.trim() || isLoading}
                className="text-white shadow-sm hover:shadow-md transition-shadow min-h-[44px] min-w-[44px]"
                style={{
                  background: `linear-gradient(135deg, var(--theme-primary), var(--theme-secondary))`
                }}
                size="sm"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Desktop Service Panel */}
        <div className="hidden md:block w-80 lg:w-96">
          <Card className="h-full border shadow-sm flex flex-col overflow-hidden" style={{ borderColor: 'var(--theme-border)' }}>
            <div 
              className="text-white p-4 rounded-t-lg flex-shrink-0"
              style={{
                background: `linear-gradient(135deg, var(--theme-primary), var(--theme-secondary))`
              }}
            >
              <h3 className="font-semibold text-lg">服務選單</h3>
              <p className="text-white/90 text-sm mt-1">選擇您需要的服務</p>
            </div>
            <ScrollArea className="flex-1 overflow-auto">
              <div className="p-4 space-y-3">
                {serviceCards.map((service, index) => (
                  <Card 
                    key={index} 
                    className="p-3 hover:shadow-md transition-shadow cursor-pointer border-l-4 border"
                    style={{ 
                      borderLeftColor: service.color,
                      borderColor: 'var(--theme-border)'
                    }}
                    onClick={() => handleServiceClick(service.title)}
                  >
                    <div className="flex items-center space-x-3">
                      <div 
                        className="text-white p-2 rounded-lg flex-shrink-0"
                        style={{ backgroundColor: service.color }}
                      >
                        {React.cloneElement(service.icon as React.ReactElement, { className: "w-5 h-5" })}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-800 text-sm truncate">{service.title}</h3>
                        <p className="text-xs text-gray-600 truncate">{service.description}</p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </Card>
        </div>
      </div>

      {/* Chat History Modal */}
      <ChatHistoryModal
        isOpen={showChatHistory}
        onClose={() => setShowChatHistory(false)}
      />

      {/* Resource Form Modal */}
      <ResourceFormModal
        isOpen={showResourceForm}
        onClose={() => setShowResourceForm(false)}
      />
    </div>
  )
}