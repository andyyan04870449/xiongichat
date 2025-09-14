import { useState, useEffect } from 'react'
import { X, Menu, History, Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import { Button } from "./ui/button"
import { Card } from "./ui/card"
import { Alert, AlertDescription } from "./ui/alert"
import { ScrollArea } from "./ui/scroll-area"
import { Avatar, AvatarImage, AvatarFallback } from "./ui/avatar"
import chatbotAvatar from 'figma:asset/d2489a7281852ae82edf81f47c4ed2529464e955.png'
import {
  getConversationHistory,
  getConversationDetail,
  generateUserId,
  type ConversationHistory,
  type ConversationDetail,
  type ConversationMessage
} from '../services/chatApi'

interface ChatHistoryModalProps {
  isOpen: boolean
  onClose: () => void
}

interface ChatHistory {
  id: string
  title: string
  startTime: Date
  lastUpdated: Date
}

// 工具函數
const parseDateTime = (dateTimeString: string): Date => {
  try {
    const date = new Date(dateTimeString)
    if (!isNaN(date.getTime())) return date
    if (!dateTimeString.includes('Z') && !dateTimeString.includes('+')) {
      return new Date(dateTimeString + 'Z')
    }
    return new Date()
  } catch {
    return new Date()
  }
}

const generateConversationTitle = (startTime: Date): string => {
  const now = new Date()
  const daysDiff = Math.floor((now.getTime() - startTime.getTime()) / (1000 * 3600 * 24))
  const timeStr = startTime.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })

  if (daysDiff === 0) return `今日諮詢 ${timeStr}`
  if (daysDiff === 1) return `昨日諮詢 ${timeStr}`
  if (daysDiff < 7) return `${daysDiff}天前諮詢`
  return `諮詢記錄 ${startTime.toLocaleDateString('zh-TW', { month: '2-digit', day: '2-digit' })}`
}

export function ChatHistoryModal({ isOpen, onClose }: ChatHistoryModalProps) {
  // 狀態管理
  const [isSidebarOpen, setIsSidebarOpen] = useState(true) // 預設開啟側邊欄
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>([])
  const [selectedHistory, setSelectedHistory] = useState<ChatHistory | null>(null)
  const [selectedDetail, setSelectedDetail] = useState<ConversationDetail | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isDetailLoading, setIsDetailLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 載入對話記錄
  const loadHistories = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const userId = generateUserId()
      const conversations = await getConversationHistory({
        user_id: userId,
        limit: 50,
        offset: 0
      })

      const formattedHistories: ChatHistory[] = conversations.map(conv => ({
        id: conv.id,
        title: generateConversationTitle(parseDateTime(conv.started_at)),
        startTime: parseDateTime(conv.started_at),
        lastUpdated: parseDateTime(conv.last_message_at)
      }))

      setChatHistories(formattedHistories)
    } catch (err) {
      console.error('載入對話記錄失敗:', err)
      setError(err instanceof Error ? err.message : '載入失敗')
    } finally {
      setIsLoading(false)
    }
  }

  // 載入對話詳情
  const loadConversationDetail = async (historyId: string) => {
    setIsDetailLoading(true)

    try {
      const detail = await getConversationDetail(historyId)
      setSelectedDetail(detail)
    } catch (err) {
      console.error('載入對話詳情失敗:', err)
      setSelectedDetail(null)
    } finally {
      setIsDetailLoading(false)
    }
  }

  // 選擇對話
  const handleSelectHistory = (history: ChatHistory) => {
    setSelectedHistory(history)
    setSelectedDetail(null)
    loadConversationDetail(history.id)
  }

  // 處理關閉
  const handleClose = () => {
    setIsSidebarOpen(false)
    onClose()
  }

  // 處理側邊欄切換
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen)
  }

  // 載入數據
  useEffect(() => {
    if (isOpen) {
      loadHistories()
    }
  }, [isOpen])

  // 組件未開啟時不渲染
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm">
      {/* 全螢幕容器 */}
      <div className="fixed inset-0 bg-white flex flex-col">

        {/* 標題欄 */}
        <header className="flex-shrink-0 flex items-center justify-between px-4 py-3 border-b bg-white shadow-sm relative z-50">
          {/* 左側：歷史對話按鈕 */}
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebar}
            className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100"
          >
            <Menu className="w-5 h-5" />
            <span className="font-medium">歷史對話</span>
          </Button>

          {/* 右側：關閉按鈕 */}
          <Button
            variant="ghost"
            size="icon"
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 hover:bg-gray-100"
          >
            <X className="w-5 h-5" />
          </Button>
        </header>

        {/* 主體內容區 */}
        <main className="flex-1 flex overflow-hidden relative">

          {/* 側邊欄遮罩（手機版） */}
          {isSidebarOpen && (
            <div
              className="fixed inset-0 bg-black/30 z-40 md:hidden"
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                setIsSidebarOpen(false)
              }}
              style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                pointerEvents: 'auto'
              }}
            />
          )}

          {/* 左側邊欄 */}
          <aside
            className={`transform transition-transform duration-300 ease-in-out fixed md:relative z-50 md:z-0 w-80 h-full bg-gray-50 border-r border-gray-200 flex flex-col ${
              isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
            }`}
            onClick={(e) => e.stopPropagation()}
            style={{
              transform: isSidebarOpen ? 'translateX(0)' : 'translateX(-100%)'
            }}
          >
            <div className="p-4 border-b bg-white flex items-center justify-between">
              <div>
                <h2 className="font-semibold text-gray-800">對話紀錄</h2>
                <p className="text-sm text-gray-500 mt-1">選擇要查看的對話</p>
              </div>
              {/* 手機版關閉按鈕 */}
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsSidebarOpen(false)}
                className="md:hidden text-gray-500 hover:text-gray-700"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            {/* 對話列表區域 */}
            <div className="flex-1 overflow-hidden">
              <ScrollArea className="h-full">
                <div className="p-4">
                  {/* 載入狀態 */}
                  {isLoading && (
                    <div className="text-center text-gray-500 py-8">
                      <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin" />
                      <p>載入對話記錄中...</p>
                    </div>
                  )}

                  {/* 錯誤狀態 */}
                  {error && (
                    <Alert className="mb-4">
                      <AlertCircle className="w-4 h-4" />
                      <AlertDescription>
                        {error}
                        <Button
                          variant="link"
                          className="p-0 ml-2 h-auto text-sm underline"
                          onClick={loadHistories}
                        >
                          重試
                        </Button>
                      </AlertDescription>
                    </Alert>
                  )}

                  {/* 空狀態 */}
                  {!isLoading && !error && chatHistories.length === 0 && (
                    <div className="text-center text-gray-500 py-8">
                      <History className="w-12 h-12 mx-auto mb-3 opacity-30" />
                      <p>尚無對話記錄</p>
                      <Button
                        variant="link"
                        className="p-0 mt-2 text-sm"
                        onClick={loadHistories}
                      >
                        重新整理
                      </Button>
                    </div>
                  )}

                  {/* 對話列表 */}
                  {!isLoading && chatHistories.length > 0 && (
                    <div className="space-y-2">
                      {chatHistories.map((history) => (
                        <Card
                          key={history.id}
                          className={`p-3 cursor-pointer transition-all hover:shadow-md ${
                            selectedHistory?.id === history.id
                              ? 'ring-2 ring-blue-200 bg-blue-50 border-blue-200'
                              : 'hover:bg-gray-50'
                          }`}
                          onClick={() => handleSelectHistory(history)}
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
                  )}
                </div>
              </ScrollArea>
            </div>
          </aside>

          {/* 右側主內容區 */}
          <section className="flex-1 flex flex-col bg-white relative z-10">
            {selectedHistory ? (
              <>
                {/* 對話標題 */}
                <div className="flex-shrink-0 p-4 border-b bg-white">
                  <h3 className="font-semibold text-gray-800">{selectedHistory.title}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {selectedHistory.startTime.toLocaleString('zh-TW', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>

                {/* 對話內容 */}
                <div className="flex-1 overflow-hidden">
                  <ScrollArea className="h-full">
                    <div className="p-4">
                      {/* 載入中 */}
                      {isDetailLoading && (
                        <div className="text-center text-gray-500 py-8">
                          <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin" />
                          <p>載入對話內容中...</p>
                        </div>
                      )}

                      {/* 對話訊息 */}
                      {!isDetailLoading && selectedDetail?.messages && (
                        <div className="space-y-4">
                          {selectedDetail.messages.map((message) => (
                            <div
                              key={message.id}
                              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
                            >
                              <div className={`flex items-start space-x-3 ${
                                message.role === 'user' ? 'flex-row-reverse space-x-reverse max-w-[85%] md:max-w-[70%]' : 'max-w-[85%] md:max-w-[70%]'
                              }`}>
                                {/* Avatar */}
                                <Avatar className="w-8 h-8 md:w-10 md:h-10 flex-shrink-0">
                                  {message.role === 'assistant' ? (
                                    <AvatarImage src={chatbotAvatar} alt="諮詢師頭像" />
                                  ) : null}
                                  <AvatarFallback
                                    className="text-white"
                                    style={{
                                      backgroundColor: message.role === 'user' ? 'var(--theme-accent)' : 'var(--theme-primary)'
                                    }}
                                  >
                                    {message.role === 'user' ? '我' : '諮'}
                                  </AvatarFallback>
                                </Avatar>

                                {/* Message Bubble */}
                                <div className={`relative px-3 md:px-4 py-2 md:py-3 rounded-xl shadow-sm overflow-hidden ${
                                  message.role === 'user'
                                    ? 'bg-gradient-to-r text-white rounded-br-sm'
                                    : 'bg-white border rounded-bl-sm'
                                }`}
                                style={{
                                  background: message.role === 'user'
                                    ? `linear-gradient(135deg, var(--theme-primary), var(--theme-secondary))`
                                    : undefined,
                                  borderColor: message.role === 'assistant' ? 'var(--theme-border)' : undefined
                                }}>
                                  {/* Message Content */}
                                  <div className={`text-sm md:text-base ${
                                    message.role === 'user' ? 'text-white' : 'text-gray-800'
                                  }`}>
                                    <div className="whitespace-pre-wrap">
                                      {message.content}
                                    </div>
                                  </div>

                                  {/* Timestamp */}
                                  <div className={`text-xs mt-2 ${
                                    message.role === 'user' ? 'text-white/70' : 'text-gray-400'
                                  }`}>
                                    {parseDateTime(message.created_at).toLocaleString('zh-TW', {
                                      hour: '2-digit',
                                      minute: '2-digit'
                                    })}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* 空對話 */}
                      {!isDetailLoading && selectedDetail &&
                       (!selectedDetail.messages || selectedDetail.messages.length === 0) && (
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
              /* 未選擇對話 */
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center text-gray-400">
                  <History className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <h3 className="text-lg font-medium mb-2">選擇對話記錄</h3>
                  <p className="text-sm">點擊左側的對話記錄以查看詳細內容</p>
                </div>
              </div>
            )}
          </section>

        </main>
      </div>
    </div>
  )
}