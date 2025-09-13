import { useState } from 'react'
import { History, X } from 'lucide-react'
import { Button } from "./ui/button"
import { Card } from "./ui/card"
import { Avatar, AvatarImage, AvatarFallback } from "./ui/avatar"
import { ScrollArea } from "./ui/scroll-area"
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
  chatHistories: ChatHistory[]
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

export function ChatHistoryModal({ isOpen, onClose, chatHistories }: ChatHistoryModalProps) {
  const [selectedHistoryChat, setSelectedHistoryChat] = useState<ChatHistory | null>(null)

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm">
      {/* 全屏對話記錄面板 */}
      <div className="fixed inset-0 bg-white flex flex-col">
        {/* 標題欄 */}
        <div className="flex-shrink-0 flex items-center justify-between px-4 py-3 border-b bg-white">
          <div className="flex items-center space-x-2">
            <History className="w-5 h-5" style={{ color: 'var(--theme-primary)' }} />
            <h2 className="font-semibold text-gray-800">對話記錄</h2>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* 主要內容區域 */}
        <div className="flex-1 flex overflow-hidden">
          {/* 左側：對話記錄列表 */}
          <div className="w-1/3 border-r bg-gray-50/50 flex flex-col">
            <div className="flex-shrink-0 px-4 py-3 bg-gray-100/50 border-b">
              <h3 className="font-medium text-gray-800">歷史對話</h3>
            </div>
            <ScrollArea className="flex-1">
              <div className="p-4 space-y-2">
                {chatHistories.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <History className="w-12 h-12 mx-auto mb-3 opacity-30" />
                    <p>尚無對話記錄</p>
                  </div>
                ) : (
                  chatHistories.map((history) => (
                    <Card 
                      key={history.id}
                      className={`p-3 cursor-pointer transition-colors hover:bg-gray-100 ${
                        selectedHistoryChat?.id === history.id ? 'ring-2 ring-blue-200 bg-blue-50' : ''
                      }`}
                      onClick={() => setSelectedHistoryChat(history)}
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
                          {history.messages.length} 則對話
                        </p>
                      </div>
                    </Card>
                  ))
                )}
              </div>
            </ScrollArea>
          </div>
          
          {/* 右側：對話內容顯示 */}
          <div className="flex-1 flex flex-col bg-white">
            {selectedHistoryChat ? (
              <>
                {/* 對話詳情標題 */}
                <div className="flex-shrink-0 p-4 border-b bg-white">
                  <h3 className="font-semibold text-gray-800">{selectedHistoryChat.title}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {selectedHistoryChat.startTime.toLocaleDateString('zh-TW', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>

                {/* 對話訊息列表 */}
                <ScrollArea className="flex-1">
                  <div className="p-4 space-y-4">
                    {selectedHistoryChat.messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`flex max-w-[85%] ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3`}>
                          <Avatar className="w-7 h-7 flex-shrink-0">
                            {message.sender === 'counselor' ? (
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
                          
                          <div className={`flex flex-col ${message.sender === 'user' ? 'items-end' : 'items-start'}`}>
                            <div className="flex items-center mb-1 space-x-2">
                              <span className="text-xs text-gray-500 font-medium">
                                {message.senderName || (message.sender === 'user' ? '我' : '雄i聊')}
                              </span>
                              <span className="text-xs text-gray-400">{message.timestamp}</span>
                            </div>
                            
                            <div 
                              className={`max-w-full px-4 py-3 rounded-2xl ${
                                message.sender === 'user' 
                                  ? 'text-white rounded-br-md' 
                                  : 'bg-white border rounded-bl-md'
                              }`}
                              style={{
                                backgroundColor: message.sender === 'user' ? 'var(--theme-primary)' : undefined,
                                borderColor: message.sender === 'counselor' ? 'var(--theme-border)' : undefined
                              }}
                            >
                              <MarkdownRenderer content={message.content} />
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
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