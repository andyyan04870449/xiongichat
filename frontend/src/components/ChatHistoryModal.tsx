import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { History, X, Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import { Resizable } from 're-resizable'
import { Button } from "./ui/button"
import { Card } from "./ui/card"
import { Avatar, AvatarImage, AvatarFallback } from "./ui/avatar"
import { ScrollArea } from "./ui/scroll-area"
import { Alert, AlertDescription } from "./ui/alert"
import { Badge } from "./ui/badge"
import {
  getConversationHistory,
  getConversationDetail,
  generateUserId,
  type ConversationHistory,
  type ConversationDetail,
  type ConversationMessage,
  type ApiError
} from '../services/chatApi'
import chatbotAvatar from 'figma:asset/d2489a7281852ae82edf81f47c4ed2529464e955.png'

// ============= 類型定義 =============
interface Message {
  id: string
  sender: 'user' | 'counselor'
  content: string
  timestamp: string
  senderName?: string
  isLoading?: boolean
  isMockResponse?: boolean
}

interface ChatHistory {
  id: string
  startTime: Date
  title: string
  messages: Message[]
  lastUpdated: Date
}

interface ChatHistoryModalProps {
  isOpen: boolean
  onClose: () => void
}

interface ConversationListProps {
  chatHistories: ChatHistory[]
  selectedHistoryChat: ChatHistory | null
  onSelectHistory: (history: ChatHistory) => void
  isLoading: boolean
  error: string | null
  refreshHistory: () => void
}

interface MessageDisplayProps {
  message: ConversationMessage
}

// ============= 常數定義 =============
const CONSTANTS = {
  MOBILE_BREAKPOINT: 768,
  SIDEBAR_DEFAULT_WIDTH: 280,
  SIDEBAR_MIN_WIDTH: 240,
  SIDEBAR_MAX_WIDTH_RATIO: 0.6,
  SIDEBAR_MOBILE_WIDTH: 'w-80 max-w-[85vw]',
  ANIMATION_DURATION: 'duration-300',
  HISTORY_LIMIT: 50,
  MOCK_ID_PREFIX: ['conv_', 'msg_'],
  MOCK_CONVERSATION_ID: '1d625f51-8f29-4226-896e-8bd95111a180'
}

const STYLES = {
  primaryColor: 'var(--theme-primary)',
  secondaryColor: 'var(--theme-secondary)',
  borderColor: 'var(--theme-border)',
  surfaceColor: 'var(--theme-surface)'
}

// ============= 工具函數 =============
const parseDateTime = (dateTimeString: string): Date => {
  try {
    const date = new Date(dateTimeString)
    if (!isNaN(date.getTime())) return date

    if (!dateTimeString.includes('Z') && !dateTimeString.includes('+')) {
      return new Date(dateTimeString + 'Z')
    }

    console.warn('無法解析時間格式:', dateTimeString)
    return new Date()
  } catch (error) {
    console.error('時間解析錯誤:', error)
    return new Date()
  }
}

const generateConversationTitle = (startTime: Date, conversationId: string): string => {
  const now = new Date()
  const daysDiff = Math.floor((now.getTime() - startTime.getTime()) / (1000 * 3600 * 24))
  const timeStr = startTime.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })

  if (daysDiff === 0) return `今日諮詢 ${timeStr}`
  if (daysDiff === 1) return `昨日諮詢 ${timeStr}`
  if (daysDiff < 7) return `${daysDiff}天前諮詢`
  return `諮詢記錄 ${startTime.toLocaleDateString('zh-TW', { month: '2-digit', day: '2-digit' })}`
}

const checkIsMockData = (conversations: ConversationHistory[]): boolean => {
  if (conversations.length === 0) return false
  return conversations[0].id === CONSTANTS.MOCK_CONVERSATION_ID ||
         conversations.some(conv => conv.started_at.includes('2025-01-'))
}

// ============= Markdown 渲染組件 =============
const MarkdownRenderer = ({ content }: { content: string }) => {
  const parseInlineMarkdown = useCallback((text: string) => {
    const elements: React.ReactNode[] = []
    let lastIndex = 0
    const markdownRegex = /(\*\*([^*]+)\*\*)|(\[([^\]]+)\]\(([^)]+)\))/g
    let match

    while ((match = markdownRegex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        elements.push(text.slice(lastIndex, match.index))
      }

      if (match[1]) {
        elements.push(
          <strong key={`bold-${match.index}`} className="font-semibold">
            {match[2]}
          </strong>
        )
      } else if (match[3]) {
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

    if (lastIndex < text.length) {
      elements.push(text.slice(lastIndex))
    }

    return elements.length > 0 ? elements : text
  }, [])

  const parseMarkdown = useCallback((text: string) => {
    const paragraphs = text.split('\\n\\n')

    return paragraphs.map((paragraph, pIndex) => {
      if (!paragraph.trim()) return null

      const bulletListRegex = /^•\s(.+)$/gm
      const numberedListRegex = /^(\d+)\.\s(.+)$/gm

      const bulletMatches = [...paragraph.matchAll(bulletListRegex)]
      const numberedMatches = [...paragraph.matchAll(numberedListRegex)]

      if (bulletMatches.length > 0) {
        return (
          <ul key={`bullet-list-${pIndex}`} className="list-disc list-outside space-y-1 mb-3">
            {bulletMatches.map((match, index) => (
              <li key={`bullet-${pIndex}-${index}`} className="ml-4 mb-1">
                {parseInlineMarkdown(match[1])}
              </li>
            ))}
          </ul>
        )
      }

      if (numberedMatches.length > 0) {
        return (
          <ol key={`numbered-list-${pIndex}`} className="list-decimal list-outside space-y-1 mb-3">
            {numberedMatches.map((match, index) => (
              <li key={`numbered-${pIndex}-${index}`} className="ml-4 mb-1">
                {parseInlineMarkdown(match[2])}
              </li>
            ))}
          </ol>
        )
      }

      return (
        <p key={`paragraph-${pIndex}`} className="mb-3 last:mb-0">
          {parseInlineMarkdown(paragraph)}
        </p>
      )
    }).filter(Boolean)
  }, [parseInlineMarkdown])

  return <div className="markdown-content">{parseMarkdown(content)}</div>
}

// ============= 對話列表組件 =============
const ConversationHistoryList = ({
  chatHistories,
  selectedHistoryChat,
  onSelectHistory,
  isLoading,
  error,
  refreshHistory
}: ConversationListProps) => {
  if (error) {
    return (
      <div className="p-4">
        <Alert className="mb-4">
          <AlertCircle className="w-4 h-4" />
          <AlertDescription>
            {error}
            <Button
              variant="link"
              className="p-0 ml-2 h-auto text-sm underline"
              onClick={refreshHistory}
            >
              重試
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="text-center text-gray-500 py-8">
        <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin" />
        <p>載入對話記錄中...</p>
      </div>
    )
  }

  if (chatHistories.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        <History className="w-12 h-12 mx-auto mb-3 opacity-30" />
        <p>尚無對話記錄</p>
        <Button
          variant="link"
          className="p-0 mt-2 text-sm"
          onClick={refreshHistory}
        >
          重新整理
        </Button>
      </div>
    )
  }

  return (
    <div className="p-4 space-y-2">
      {chatHistories.map((history) => (
        <Card
          key={history.id}
          className={`p-3 cursor-pointer transition-colors hover:bg-gray-100 ${
            selectedHistoryChat?.id === history.id ? 'ring-2 ring-blue-200 bg-blue-50' : ''
          }`}
          onClick={() => onSelectHistory(history)}
        >
          <div className="space-y-1">
            <h4 className="font-medium text-sm text-gray-800 truncate">
              {history.title}
            </h4>
            <p className="text-xs text-gray-500">
              {history.startTime.toLocaleDateString('zh-TW', {
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
            <p className="text-xs text-gray-400 truncate">
              最後更新: {history.lastUpdated.toLocaleString('zh-TW', {
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>
        </Card>
      ))}
    </div>
  )
}

// ============= 訊息顯示組件 =============
const MessageDisplay = ({ message }: MessageDisplayProps) => {
  const isUser = message.role === 'user'
  const timeStr = parseDateTime(message.created_at).toLocaleString('zh-TW', {
    hour: '2-digit',
    minute: '2-digit'
  })

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3`}>
        <Avatar className="w-7 h-7 flex-shrink-0">
          {!isUser ? (
            <>
              <AvatarImage src={chatbotAvatar} alt="雄i聊機器人" />
              <AvatarFallback
                className="text-white text-xs"
                style={{ backgroundColor: STYLES.primaryColor }}
              >
                張
              </AvatarFallback>
            </>
          ) : (
            <AvatarFallback
              className="text-white text-xs"
              style={{ backgroundColor: STYLES.secondaryColor }}
            >
              我
            </AvatarFallback>
          )}
        </Avatar>

        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div className="flex items-center mb-1 space-x-2">
            <span className="text-xs text-gray-500 font-medium">
              {isUser ? '我' : '雄i聊'}
            </span>
            <span className="text-xs text-gray-400">{timeStr}</span>
          </div>

          <div
            className={`max-w-full px-4 py-3 rounded-2xl ${
              isUser ? 'text-white rounded-br-md' : 'bg-white border rounded-bl-md'
            }`}
            style={{
              backgroundColor: isUser ? STYLES.primaryColor : undefined,
              borderColor: !isUser ? STYLES.borderColor : undefined
            }}
          >
            <MarkdownRenderer content={message.content} />
          </div>
        </div>
      </div>
    </div>
  )
}

// ============= 主組件 =============
export function ChatHistoryModal({ isOpen, onClose }: ChatHistoryModalProps) {
  // 狀態管理
  const [selectedHistoryChat, setSelectedHistoryChat] = useState<ChatHistory | null>(null)
  const [selectedConversationDetail, setSelectedConversationDetail] = useState<ConversationDetail | null>(null)
  const [sidebarWidth, setSidebarWidth] = useState(CONSTANTS.SIDEBAR_DEFAULT_WIDTH)
  const [isMobile, setIsMobile] = useState(false)
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingDetail, setIsLoadingDetail] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [detailError, setDetailError] = useState<string | null>(null)
  const [isUsingMock, setIsUsingMock] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  // 檢測移動設備
  useEffect(() => {
    const checkMobile = () => {
      const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0
      const isSmallScreen = window.innerWidth < CONSTANTS.MOBILE_BREAKPOINT
      setIsMobile(isSmallScreen || isTouchDevice)
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // 載入對話記錄
  const loadConversationHistory = useCallback(async (showLoading = true) => {
    if (showLoading) setIsLoading(true)
    setError(null)

    try {
      const userId = generateUserId()
      const conversations = await getConversationHistory({
        user_id: userId,
        limit: CONSTANTS.HISTORY_LIMIT,
        offset: 0
      })

      const formattedHistories: ChatHistory[] = conversations.map(conv => ({
        id: conv.id,
        startTime: parseDateTime(conv.started_at),
        title: generateConversationTitle(parseDateTime(conv.started_at), conv.id),
        messages: [],
        lastUpdated: parseDateTime(conv.last_message_at)
      }))

      setChatHistories(formattedHistories)
      setIsUsingMock(checkIsMockData(conversations))
    } catch (err) {
      console.error('載入對話記錄失敗:', err)
      setError(err instanceof Error ? err.message : '載入對話記錄時發生未知錯誤')
      setChatHistories([])
    } finally {
      if (showLoading) setIsLoading(false)
    }
  }, [])

  // 載入對話詳情
  const loadConversationDetail = useCallback(async (conversationId: string) => {
    setIsLoadingDetail(true)
    setDetailError(null)

    try {
      const detail = await getConversationDetail(conversationId)
      setSelectedConversationDetail(detail)
    } catch (err) {
      console.error('載入對話詳情失敗:', err)
      setDetailError(err instanceof Error ? err.message : '載入對話詳情時發生未知錯誤')
      setSelectedConversationDetail(null)
    } finally {
      setIsLoadingDetail(false)
    }
  }, [])

  // 處理選擇對話
  const handleSelectHistory = useCallback(async (history: ChatHistory) => {
    setSelectedHistoryChat(history)
    setSelectedConversationDetail(null)
    await loadConversationDetail(history.id)
    if (isMobile) setIsSidebarOpen(false)
  }, [isMobile, loadConversationDetail])

  // 重新整理
  const refreshHistory = useCallback(() => {
    loadConversationHistory(true)
  }, [loadConversationHistory])

  // 側邊欄最大寬度
  const sidebarMaxWidth = useMemo(() =>
    Math.min(600, window.innerWidth * CONSTANTS.SIDEBAR_MAX_WIDTH_RATIO),
    []
  )

  // 當模態框打開時載入
  useEffect(() => {
    if (isOpen) {
      loadConversationHistory(true)
      setSelectedHistoryChat(null)
      setSelectedConversationDetail(null)
    }
  }, [isOpen, loadConversationHistory])

  if (!isOpen) return null

  // 渲染頭部
  const renderHeader = () => (
    <div className="flex-shrink-0 flex items-center justify-between px-4 py-3 border-b bg-white">
      <div className="flex items-center space-x-3">
        {isMobile ? (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsSidebarOpen(true)}
            className="flex items-center space-x-2 text-gray-800 hover:bg-gray-100"
          >
            <History className="w-5 h-5" style={{ color: STYLES.primaryColor }} />
            <span className="font-semibold">對話記錄</span>
            {isUsingMock && <span className="text-xs text-orange-600">（離線）</span>}
          </Button>
        ) : (
          <>
            <History className="w-5 h-5" style={{ color: STYLES.primaryColor }} />
            <div>
              <h2 className="font-semibold text-gray-800">對話記錄</h2>
              {isUsingMock && (
                <p className="text-xs text-orange-600">離線模式 - 顯示示範資料</p>
              )}
            </div>
          </>
        )}
      </div>
      <div className="flex items-center space-x-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={refreshHistory}
          disabled={isLoading}
          className="text-gray-500 hover:text-gray-700"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={(e) => {
            e.preventDefault()
            e.stopPropagation()
            onClose()
          }}
          className="text-gray-500 hover:text-gray-700 hover:bg-gray-100"
          title="關閉對話記錄"
          aria-label="關閉"
        >
          <X className="w-5 h-5" />
        </Button>
      </div>
    </div>
  )

  // 渲染側邊欄
  const renderSidebar = () => {
    const sidebarContent = (
      <>
        <div className="flex-shrink-0 px-4 py-3 bg-gray-100/50 border-b flex items-center justify-between">
          <h3 className="font-medium text-gray-800">歷史對話</h3>
          {isMobile && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                setIsSidebarOpen(false)
              }}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-4 h-4" />
            </Button>
          )}
          {!isMobile && (
            <p className="text-xs text-gray-500">拖拉右邊緣調整寬度</p>
          )}
        </div>
        <ScrollArea className="flex-1">
          <ConversationHistoryList
            chatHistories={chatHistories}
            selectedHistoryChat={selectedHistoryChat}
            onSelectHistory={handleSelectHistory}
            isLoading={isLoading}
            error={error}
            refreshHistory={refreshHistory}
          />
        </ScrollArea>
      </>
    )

    if (isMobile) {
      return (
        <>
          {isSidebarOpen && (
            <div
              className="fixed inset-0 bg-black/50 z-40 transition-opacity"
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                setIsSidebarOpen(false)
              }}
            />
          )}
          <div
            className={`fixed left-0 top-0 h-full ${CONSTANTS.SIDEBAR_MOBILE_WIDTH} bg-gray-50/50 border-r z-50 transform transition-transform ${CONSTANTS.ANIMATION_DURATION} ease-in-out ${
              isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
            }`}
            style={{ borderColor: STYLES.borderColor }}
          >
            <div className="flex flex-col h-full">{sidebarContent}</div>
          </div>
        </>
      )
    }

    return (
      <Resizable
        size={{ width: sidebarWidth, height: '100%' }}
        onResizeStop={(e, direction, ref, d) => {
          setSidebarWidth(sidebarWidth + d.width)
        }}
        minWidth={CONSTANTS.SIDEBAR_MIN_WIDTH}
        maxWidth={sidebarMaxWidth}
        enable={{ right: true }}
        handleStyles={{
          right: {
            background: STYLES.borderColor,
            width: '4px',
            cursor: 'col-resize',
            transition: 'background-color 0.2s ease',
          }
        }}
        handleClasses={{
          right: 'hover:bg-gray-400 active:bg-gray-500'
        }}
        className="border-r bg-gray-50/50 flex flex-col"
        style={{ borderColor: STYLES.borderColor }}
      >
        {sidebarContent}
      </Resizable>
    )
  }

  // 渲染對話詳情
  const renderConversationDetail = () => {
    if (!selectedHistoryChat) {
      return (
        <div className="flex-1 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <History className="w-16 h-16 mx-auto mb-4 opacity-30" />
            <p className="text-lg font-medium mb-2">選擇對話記錄</p>
            <p className="text-sm">點擊左側的對話記錄以查看詳細內容</p>
          </div>
        </div>
      )
    }

    return (
      <>
        <div className="flex-shrink-0 p-4 border-b bg-white">
          <h3 className="font-semibold text-gray-800">{selectedHistoryChat.title}</h3>
          <p className="text-sm text-gray-500 mt-1">
            {selectedHistoryChat.startTime.toLocaleString('zh-TW', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </p>
        </div>

        <div className="flex-1 overflow-hidden relative">
          <ScrollArea className="absolute inset-0">
            <div className="p-4">
              {isLoadingDetail && (
                <div className="text-center text-gray-500 py-8">
                  <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin" />
                  <p>載入對話內容中...</p>
                </div>
              )}

              {detailError && (
                <Alert className="mb-4">
                  <AlertCircle className="w-4 h-4" />
                  <AlertDescription>
                    {detailError}
                    <Button
                      variant="link"
                      className="p-0 ml-2 h-auto text-sm underline"
                      onClick={() => loadConversationDetail(selectedHistoryChat.id)}
                    >
                      重試
                    </Button>
                  </AlertDescription>
                </Alert>
              )}

              {!isLoadingDetail && !detailError && selectedConversationDetail?.messages && (
                <div className="space-y-4">
                  {selectedConversationDetail.messages.map((message) => (
                    <MessageDisplay key={message.id} message={message} />
                  ))}
                </div>
              )}

              {!isLoadingDetail && !detailError && selectedConversationDetail &&
               (!selectedConversationDetail.messages || selectedConversationDetail.messages.length === 0) && (
                <div className="text-center text-gray-500 py-8">
                  <History className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p className="text-lg font-medium mb-2">此對話尚無訊息</p>
                  <p className="text-sm">對話記錄中沒有找到任何訊息內容</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
      </>
    )
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm">
      <div className="fixed inset-0 bg-white flex flex-col">
        {renderHeader()}
        <div className="flex-1 flex overflow-hidden">
          {renderSidebar()}
          <div className="flex-1 flex flex-col bg-white">
            {renderConversationDetail()}
          </div>
        </div>
      </div>
    </div>
  )
}