import React, { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { ChevronLeft, ChevronRight, X, ZoomIn } from 'lucide-react'
import { ImageContent } from '../../types/message'

interface ImageGalleryProps {
  images: ImageContent[]
}

export function ImageGallery({ images }: ImageGalleryProps) {
  const [selectedImage, setSelectedImage] = useState<number | null>(null)
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
      const scrollAmount = 200
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
  }, [images])

  // 鍵盤導航
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (selectedImage !== null) {
        if (e.key === 'Escape') {
          setSelectedImage(null)
        } else if (e.key === 'ArrowLeft' && selectedImage > 0) {
          setSelectedImage(selectedImage - 1)
        } else if (e.key === 'ArrowRight' && selectedImage < images.length - 1) {
          setSelectedImage(selectedImage + 1)
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [selectedImage, images.length])

  return (
    <>
      {/* 圖片橫向滾動容器 - 加入 overflow-hidden 防止橫向滾動 */}
      <div className="image-gallery-container relative w-full max-w-full overflow-hidden">
        {/* 左滾動按鈕 */}
        {canScrollLeft && (
          <button
            onClick={() => scroll('left')}
            className="absolute left-2 md:left-0 top-1/2 -translate-y-1/2 z-10 bg-white/95 rounded-full p-1 shadow-md hover:bg-white transition-colors"
            aria-label="向左滾動"
          >
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          </button>
        )}

        {/* 圖片容器 - 加入 overflow-y-hidden */}
        <div
          ref={scrollContainerRef}
          className="flex gap-2 overflow-x-auto overflow-y-hidden scrollbar-hide py-2 px-1"
          style={{
            scrollbarWidth: 'none',
            msOverflowStyle: 'none',
            WebkitScrollbar: { display: 'none' },
            maxWidth: '100%',
            WebkitOverflowScrolling: 'touch' // iOS 平滑滾動
          }}
        >
          {images.map((image, index) => (
            <div
              key={index}
              className="flex-shrink-0 relative group cursor-pointer"
              onClick={() => setSelectedImage(index)}
            >
              {/* 圖片 */}
              <div className="relative overflow-hidden rounded-lg">
                <img
                  src={image.url}
                  alt={image.alt || `圖片 ${index + 1}`}
                  className="h-32 md:h-40 w-48 md:w-auto object-cover transition-transform duration-300 group-hover:scale-105"
                  loading="lazy"
                />

                {/* 放大圖示 */}
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                  <ZoomIn className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>

              {/* 圖片說明 */}
              {image.caption && (
                <p className="text-xs text-gray-600 mt-1 w-48 md:max-w-[200px] truncate">
                  {image.caption}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* 右滾動按鈕 */}
        {canScrollRight && (
          <button
            onClick={() => scroll('right')}
            className="absolute right-2 md:right-0 top-1/2 -translate-y-1/2 z-10 bg-white/95 rounded-full p-1 shadow-md hover:bg-white transition-colors"
            aria-label="向右滾動"
          >
            <ChevronRight className="w-5 h-5 text-gray-700" />
          </button>
        )}
      </div>

      {/* Lightbox 放大檢視 - 使用 Portal 渲染到 body */}
      {selectedImage !== null && createPortal(
        <div
          className="fixed inset-0 z-[9999] bg-black/90 flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
          style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0 }}
        >
          {/* 關閉按鈕 */}
          <button
            onClick={() => setSelectedImage(null)}
            className="absolute top-4 right-4 text-white/80 hover:text-white transition-colors z-[10000]"
            aria-label="關閉"
          >
            <X className="w-8 h-8" />
          </button>

          {/* 上一張按鈕 */}
          {selectedImage > 0 && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                setSelectedImage(selectedImage - 1)
              }}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-white/80 hover:text-white transition-colors z-[10000]"
              aria-label="上一張"
            >
              <ChevronLeft className="w-10 h-10" />
            </button>
          )}

          {/* 下一張按鈕 */}
          {selectedImage < images.length - 1 && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                setSelectedImage(selectedImage + 1)
              }}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-white/80 hover:text-white transition-colors z-[10000]"
              aria-label="下一張"
            >
              <ChevronRight className="w-10 h-10" />
            </button>
          )}

          {/* 圖片展示 - 只有圖片區域阻止關閉 */}
          <div className="flex flex-col items-center justify-center gap-4">
            {/* 圖片本身 - 只有這個元素阻止點擊關閉 */}
            <img
              src={images[selectedImage].url}
              alt={images[selectedImage].alt || `圖片 ${selectedImage + 1}`}
              className="rounded-lg shadow-2xl cursor-default"
              onClick={(e) => e.stopPropagation()}
              style={{
                maxWidth: '85vw',
                maxHeight: '70vh',
                width: 'auto',
                height: 'auto',
                objectFit: 'contain'
              }}
            />

            {/* 圖片說明和計數 - 不阻止點擊關閉 */}
            <div className="text-center text-white px-4">
              {images[selectedImage].caption && (
                <p className="text-lg mb-2 font-medium drop-shadow-md">
                  {images[selectedImage].caption}
                </p>
              )}
              <p className="text-sm text-white/80 drop-shadow-md">
                {selectedImage + 1} / {images.length}
              </p>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  )
}