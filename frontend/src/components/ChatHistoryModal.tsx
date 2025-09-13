import { useState, useEffect } from 'react'
import { History, X, Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import { Resizable } from 're-resizable'
import { Button } from "./ui/button"
import { Card } from "./ui/card"
import { Avatar, AvatarImage, AvatarFallback } from "./ui/avatar"
import { ScrollArea } from "./ui/scroll-area"
import { Alert, AlertDescription } from "./ui/alert"
import { getConversationHistory, getConversationDetail, generateUserId, type ConversationHistory, type ConversationDetail, type ConversationMessage, type ApiError } from '../services/chatApi'
import chatbotAvatar from 'figma:asset/d2489a7281852ae82edf81f47c4ed2529464e955.png'

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

// 安全的時間解析輔助函數
function parseDateTime(dateTimeString: string): Date {
  try {
    // 嘗試直接解析 ISO 格式
    const date = new Date(dateTimeString)
    
    // 檢查是否為有效日期
    if (!isNaN(date.getTime())) {
      return date
    }
    
    // 如果直接解析失敗，嘗試其他格式
    // 處理沒有時區的格式 (例如: "2025-01-14T10:30:00")
    if (!dateTimeString.includes('Z') && !dateTimeString.includes('+')) {
      return new Date(dateTimeString + 'Z')
    }
    
    // 最後的備案：返回當前時間
    console.warn('無法解析時間格式:', dateTimeString)
    return new Date()
  } catch (error) {
    console.error('時間解析錯誤:', error)
    return new Date()
  }
}

// Markdown渲染組件
function MarkdownRenderer({ content }: { content: string }) {
  // 解析Markdown格式並轉換為React元素
  const parseMarkdown = (text: string) => {
    const elements: React.ReactNode[] = []
    
    // 分割段落 (\\n\\n)
    const paragraphs = text.split('\\n\\n')
    
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

// 通用對話記錄列表組件
function ConversationHistoryList({ 
  chatHistories, 
  selectedHistoryChat, 
  onSelectHistory,
  isLoading,
  error,
  refreshHistory
}: {
  chatHistories: ChatHistory[]
  selectedHistoryChat: ChatHistory | null
  onSelectHistory: (history: ChatHistory) => void
  isLoading: boolean
  error: string | null
  refreshHistory: () => void
}) {
  return (
    <div className="p-4 space-y-2">
      {/* 錯誤狀態 */}
      {error && (
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
      )}

      {/* 載入狀態 */}
      {isLoading && (
        <div className="text-center text-gray-500 py-8">
          <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin" />
          <p>載入對話記錄中...</p>
        </div>
      )}

      {/* 空狀態 */}
      {!isLoading && !error && chatHistories.length === 0 && (
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
      )}

      {/* 對話記錄列表 */}
      {!isLoading && chatHistories.length > 0 && (
        chatHistories.map((history) => (
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
        ))
      )}
    </div>
  )
}

export function ChatHistoryModal({ isOpen, onClose }: ChatHistoryModalProps) {
  const [selectedHistoryChat, setSelectedHistoryChat] = useState<ChatHistory | null>(null)
  const [selectedConversationDetail, setSelectedConversationDetail] = useState<ConversationDetail | null>(null)
  const [sidebarWidth, setSidebarWidth] = useState(280)
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
      // 同時檢查寬度和觸控設備
      const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0
      const isSmallScreen = window.innerWidth < 768
      setIsMobile(isSmallScreen || isTouchDevice)
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // 載入對話記錄
  const loadConversationHistory = async (showLoading = true) => {
    if (showLoading) {
      setIsLoading(true)
    }
    setError(null)
    
    try {
      const userId = generateUserId()
      const conversations = await getConversationHistory({
        user_id: userId,
        limit: 50,
        offset: 0
      })

      // 轉換API資料格式為組件所需格式
      const formattedHistories: ChatHistory[] = conversations.map(conv => {
        // 安全地解析時間格式
        const startTime = parseDateTime(conv.started_at)
        const lastMessageTime = parseDateTime(conv.last_message_at)
        const title = generateConversationTitle(startTime, conv.id)
        
        return {
          id: conv.id,
          startTime: startTime,
          title: title,
          messages: [], // API回應不包含詳細訊息，如需要可另外呼叫獲取
          lastUpdated: lastMessageTime
        }
      })

      setChatHistories(formattedHistories)
      
      // 檢查是否使用了模擬數據
      // 檢查特定的模擬數據 ID 或時間模式來判斷
      const isMockData = conversations.length > 0 && (
        conversations[0].id === '1d625f51-8f29-4226-896e-8bd95111a180' ||
        conversations.some(conv => conv.started_at.includes('2025-01-'))
      )
      setIsUsingMock(isMockData)
      
    } catch (err) {
      console.error('載入對話記錄失敗:', err)
      
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('載入對話記錄時發生未知錯誤')
      }
      
      // 設定空陣列避免顯示錯誤
      setChatHistories([])
    } finally {
      if (showLoading) {
        setIsLoading(false)
      }
    }
  }

  // 生成對話標題
  const generateConversationTitle = (startTime: Date, conversationId: string): string => {
    const now = new Date()
    const timeDiff = now.getTime() - startTime.getTime()
    const daysDiff = Math.floor(timeDiff / (1000 * 3600 * 24))
    
    if (daysDiff === 0) {
      return `今日諮詢 ${startTime.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}`
    } else if (daysDiff === 1) {
      return `昨日諮詢 ${startTime.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}`
    } else if (daysDiff < 7) {
      return `${daysDiff}天前諮詢`
    } else {
      return `諮詢記錄 ${startTime.toLocaleDateString('zh-TW', { month: '2-digit', day: '2-digit' })}`
    }
  }

  // 載入對話詳情
  const loadConversationDetail = async (conversationId: string) => {
    setIsLoadingDetail(true)
    setDetailError(null)
    
    try {
      const detail = await getConversationDetail(conversationId)
      setSelectedConversationDetail(detail)
    } catch (err) {
      console.error('載入對話詳情失敗:', err)
      
      if (err instanceof Error) {
        setDetailError(err.message)
      } else {
        setDetailError('載入對話詳情時發生未知錯誤')
      }
      
      setSelectedConversationDetail(null)
    } finally {
      setIsLoadingDetail(false)
    }
  }

  // 重新整理對話記錄
  const refreshHistory = () => {
    loadConversationHistory(true)
  }

  // 處理選擇對話
  const handleSelectHistory = async (history: ChatHistory) => {
    setSelectedHistoryChat(history)
    setSelectedConversationDetail(null) // 清除之前的詳情

    // 載入對話詳情
    await loadConversationDetail(history.id)

    // 手機版自動關閉側邊欄
    if (isMobile) {
      setIsSidebarOpen(false)
    }
  }

  // 當模態框打開時載入對話記錄
  useEffect(() => {
    if (isOpen) {
      loadConversationHistory(true)
      setSelectedHistoryChat(null) // 重置選擇
      setSelectedConversationDetail(null) // 重置詳情
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm">
      {/* 全屏對話記錄面板 */}
      <div className="fixed inset-0 bg-white flex flex-col">
        {/* 標題欄 */}
        <div className="flex-shrink-0 flex items-center justify-between px-4 py-3 border-b bg-white">
          <div className="flex items-center space-x-3">
            {isMobile ? (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsSidebarOpen(true)}
                className="flex items-center space-x-2 text-gray-800 hover:bg-gray-100"
              >
                <History className="w-5 h-5" style={{ color: 'var(--theme-primary)' }} />
                <span className="font-semibold">對話記錄</span>
                {isUsingMock && (
                  <span className="text-xs text-orange-600">（離線）</span>
                )}
              </Button>
            ) : (
              <>
                <History className="w-5 h-5" style={{ color: 'var(--theme-primary)' }} />
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
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 hover:bg-gray-100"
              title="關閉對話記錄"
              aria-label="關閉"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* 主要內容區域 */}
        <div className="flex-1 flex overflow-hidden">
          {/* 手機版：側邊滑入面板 */}
          {isMobile && (
            <>
              {/* 遮罩層 */}
              {isSidebarOpen && (
                <div
                  className="fixed inset-0 bg-black/50 z-40 transition-opacity"
                  onClick={() => setIsSidebarOpen(false)}
                />
              )}

              {/* 側邊面板 */}
              <div
                className={`fixed left-0 top-0 h-full w-80 max-w-[85vw] bg-gray-50/50 border-r z-50 transform transition-transform duration-300 ease-in-out ${
                  isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
                }`}
                style={{ borderColor: 'var(--theme-border)' }}
              >
                <div className="flex flex-col h-full">
                  <div className="flex-shrink-0 px-4 py-3 bg-gray-100/50 border-b flex items-center justify-between">
                    <h3 className="font-medium text-gray-800">歷史對話</h3>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsSidebarOpen(false)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      <X className="w-4 h-4" />
                    </Button>
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
                </div>
              </div>
            </>
          )}

          {/* 桌面版：可調整大小的側邊欄 */}
          {!isMobile && (
            /* 桌面設備：可調整大小 */
            <Resizable
              size={{ width: sidebarWidth, height: '100%' }}
              onResizeStop={(e, direction, ref, d) => {
                setSidebarWidth(sidebarWidth + d.width)
              }}
              minWidth={240}
              maxWidth={Math.min(600, window.innerWidth * 0.6)} // 最大不超過螢幕寬度的60%
              enable={{
                top: false,
                right: true,
                bottom: false,
                left: false,
                topRight: false,
                bottomRight: false,
                bottomLeft: false,
                topLeft: false,
              }}
              handleStyles={{
                right: {
                  background: 'var(--theme-border)',
                  width: '4px',
                  cursor: 'col-resize',
                  transition: 'background-color 0.2s ease',
                }
              }}
              handleClasses={{
                right: 'hover:bg-gray-400 active:bg-gray-500'
              }}
              className="border-r bg-gray-50/50 flex flex-col"
              style={{ borderColor: 'var(--theme-border)' }}
            >
              <div className="flex-shrink-0 px-4 py-3 bg-gray-100/50 border-b">
                <h3 className="font-medium text-gray-800">歷史對話</h3>
                <p className="text-xs text-gray-500 mt-1">拖拉右邊緣調整寬度</p>
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
            </Resizable>
          )}
          
          {/* 右側：對話內容顯示 */}
          <div className="flex-1 flex flex-col bg-white">
            {selectedHistoryChat ? (
              <>
                {/* 對話詳情標題 */}
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

                {/* 對話訊息列表 */}
                <div className="flex-1 overflow-hidden relative">
                  <ScrollArea className="absolute inset-0">
                    <div className="p-4">
                    {/* 載入詳情狀態 */}
                    {isLoadingDetail && (
                      <div className="text-center text-gray-500 py-8">
                        <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin" />
                        <p>載入對話內容中...</p>
                      </div>
                    )}

                    {/* 載入詳情錯誤狀態 */}
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

                    {/* 對話訊息 */}
                    {!isLoadingDetail && !detailError && selectedConversationDetail?.messages && (
                      <div className="space-y-4">
                        {selectedConversationDetail.messages.map((message) => (
                          <div
                            key={message.id}
                            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                          >
                            <div className={`flex max-w-[85%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3`}>
                              <Avatar className="w-7 h-7 flex-shrink-0">
                                {message.role === 'assistant' ? (
                                  <>
                                    <AvatarImage src={chatbotAvatar} alt="雄i聊機器人" />
                                    <AvatarFallback 
                                      className="text-white text-xs"
                                      style={{ backgroundColor: 'var(--theme-primary)' }}
                                    >
                                      張
                                    </AvatarFallback>
                                  </>
                                ) : (
                                  <AvatarFallback 
                                    className="text-white text-xs"
                                    style={{ backgroundColor: 'var(--theme-secondary)' }}
                                  >
                                    我
                                  </AvatarFallback>
                                )}
                              </Avatar>
                              
                              <div className={`flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
                                <div className="flex items-center mb-1 space-x-2">
                                  <span className="text-xs text-gray-500 font-medium">
                                    {message.role === 'user' ? '我' : '雄i聊'}
                                  </span>
                                  <span className="text-xs text-gray-400">
                                    {parseDateTime(message.created_at).toLocaleString('zh-TW', {
                                      hour: '2-digit',
                                      minute: '2-digit'
                                    })}
                                  </span>
                                </div>
                                
                                <div 
                                  className={`max-w-full px-4 py-3 rounded-2xl ${
                                    message.role === 'user' 
                                      ? 'text-white rounded-br-md' 
                                      : 'bg-white border rounded-bl-md'
                                  }`}
                                  style={{
                                    backgroundColor: message.role === 'user' ? 'var(--theme-primary)' : undefined,
                                    borderColor: message.role === 'assistant' ? 'var(--theme-border)' : undefined
                                  }}
                                >
                                  <MarkdownRenderer content={message.content} />
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* 空對話狀態 */}
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
            ) : (
              /* 未選擇對話時的提示 */
              <div className="flex-1 flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <History className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <p className="text-lg font-medium mb-2">選擇對話記錄</p>
                  <p className="text-sm">點擊左側的對話記錄以查看詳細內容</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}