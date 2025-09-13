import React, { useRef, useState, useEffect } from 'react'
import { ChevronLeft, ChevronRight, ExternalLink, MessageCircle } from 'lucide-react'
import { InfoCard, CardLink } from '../../types/message'

interface InfoCardCarouselProps {
  cards: InfoCard[]
  onCommandClick: (command: string) => void
}

export function InfoCardCarousel({ cards, onCommandClick }: InfoCardCarouselProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const [canScrollLeft, setCanScrollLeft] = useState(false)
  const [canScrollRight, setCanScrollRight] = useState(false)

  // 檢查滾動狀態
  const checkScrollability = () => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current
      setCanScrollLeft(scrollLeft > 0)
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10)
    }
  }

  // 滾動處理
  const scroll = (direction: 'left' | 'right') => {
    if (scrollContainerRef.current) {
      const cardWidth = 280 // 卡片寬度
      const gap = 12 // 間隙
      const scrollAmount = cardWidth + gap
      const newScrollLeft = scrollContainerRef.current.scrollLeft +
        (direction === 'left' ? -scrollAmount : scrollAmount)

      scrollContainerRef.current.scrollTo({
        left: newScrollLeft,
        behavior: 'smooth'
      })
    }
  }

  useEffect(() => {
    checkScrollability()
    const container = scrollContainerRef.current
    if (container) {
      container.addEventListener('scroll', checkScrollability)
      window.addEventListener('resize', checkScrollability)

      return () => {
        container.removeEventListener('scroll', checkScrollability)
        window.removeEventListener('resize', checkScrollability)
      }
    }
  }, [cards])

  // 處理連結點擊
  const handleLinkClick = (link: CardLink, e: React.MouseEvent) => {
    if (link.type === 'command') {
      e.preventDefault()
      onCommandClick(link.action)
    }
    // URL類型會自動在新視窗開啟（由a標籤的target="_blank"處理）
  }

  return (
    <div className="info-card-carousel relative w-full max-w-full overflow-hidden">
      {/* 左滾動按鈕 */}
      {canScrollLeft && (
        <button
          onClick={() => scroll('left')}
          className="absolute left-1 top-1/2 -translate-y-1/2 z-10 bg-white/95 rounded-full p-1.5 shadow-lg hover:bg-white transition-all"
          aria-label="向左滾動"
        >
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </button>
      )}

      {/* 卡片容器 - 加入 overflow-x-auto 和 overflow-y-hidden 防止頁面滾動 */}
      <div
        ref={scrollContainerRef}
        className="flex gap-3 overflow-x-auto overflow-y-hidden scrollbar-hide py-2 px-1"
        style={{
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
          WebkitScrollbar: { display: 'none' },
          maxWidth: '100%',
          WebkitOverflowScrolling: 'touch' // iOS 平滑滾動
        }}
      >
        {cards.map((card) => {
          // 判斷是否只有一個連結（整張卡片可點擊）
          const isSingleLink = card.links.length === 1
          const singleLink = isSingleLink ? card.links[0] : null

          return (
            <div
              key={card.id}
              className={`flex-shrink-0 bg-white rounded-lg shadow-md hover:shadow-lg transition-all border ${
                card.style === 'highlight' ? 'border-blue-300' : 'border-gray-200'
              } ${isSingleLink ? 'cursor-pointer hover:scale-[1.02]' : ''}`}
              style={{
                width: '260px',
                minWidth: '260px',
                maxWidth: '80vw' // 在小螢幕上限制最大寬度
              }}
              onClick={isSingleLink && singleLink ? (e) => handleLinkClick(singleLink, e) : undefined}
            >
              {/* 卡片內容 */}
              <div className="p-4">
                {/* 標題 */}
                <h3 className="font-semibold text-lg text-gray-800 mb-2">
                  {card.title}
                </h3>

                {/* 描述 */}
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                  {card.description}
                </p>

                {/* 連結區域 */}
                <div className="space-y-2">
                  {isSingleLink && singleLink ? (
                    // 單一連結時，顯示為簡單的文字提示
                    <div className={`flex items-center justify-between px-3 py-2 rounded-md text-sm ${
                      singleLink.type === 'url'
                        ? 'bg-blue-50 text-blue-700'
                        : 'bg-purple-50 text-purple-700'
                    }`}>
                      <span className="flex items-center gap-2">
                        {singleLink.text}
                      </span>
                      {singleLink.type === 'url' ? (
                        <ExternalLink className="w-4 h-4" />
                      ) : (
                        <MessageCircle className="w-4 h-4" />
                      )}
                    </div>
                  ) : (
                    // 多個連結時，每個都是獨立的按鈕
                    card.links.map((link, linkIndex) => (
                      <a
                        key={linkIndex}
                        href={link.type === 'url' ? link.action : '#'}
                        target={link.type === 'url' ? '_blank' : undefined}
                        rel={link.type === 'url' ? 'noopener noreferrer' : undefined}
                        onClick={(e) => {
                          e.stopPropagation() // 防止觸發卡片點擊
                          handleLinkClick(link, e)
                        }}
                        className={`flex items-center justify-between px-3 py-2 rounded-md transition-colors text-sm ${
                          link.type === 'url'
                            ? 'bg-blue-50 hover:bg-blue-100 text-blue-700'
                            : 'bg-purple-50 hover:bg-purple-100 text-purple-700'
                        }`}
                      >
                        <span className="flex items-center gap-2">
                          {link.text}
                        </span>
                        {link.type === 'url' ? (
                          <ExternalLink className="w-4 h-4" />
                        ) : (
                          <MessageCircle className="w-4 h-4" />
                        )}
                      </a>
                    ))
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* 右滾動按鈕 */}
      {canScrollRight && (
        <button
          onClick={() => scroll('right')}
          className="absolute right-1 top-1/2 -translate-y-1/2 z-10 bg-white/95 rounded-full p-1.5 shadow-lg hover:bg-white transition-all"
          aria-label="向右滾動"
        >
          <ChevronRight className="w-5 h-5 text-gray-700" />
        </button>
      )}

      {/* 卡片數量指示器（手機版） */}
      <div className="flex justify-center mt-2 md:hidden">
        <div className="flex gap-1">
          {cards.map((_, index) => (
            <div
              key={index}
              className="w-1.5 h-1.5 rounded-full bg-gray-300"
            />
          ))}
        </div>
      </div>
    </div>
  )
}