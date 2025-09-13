import React from 'react'
import DOMPurify from 'dompurify'

interface RichTextRendererProps {
  content: string
}

export function RichTextRenderer({ content }: RichTextRendererProps) {
  // 配置DOMPurify以允許安全的HTML標籤
  const cleanHTML = DOMPurify.sanitize(content, {
    ALLOWED_TAGS: ['b', 'strong', 'br', 'a', 'ul', 'li', 'ol', 'p', 'span', 'div'],
    ALLOWED_ATTR: ['href', 'target', 'rel', 'class'],
    ADD_ATTR: ['target'], // 確保連結在新視窗開啟
  })

  // 處理連結，確保外部連結在新視窗開啟
  const processedHTML = cleanHTML.replace(
    /<a\s+href=/g,
    '<a target="_blank" rel="noopener noreferrer" href='
  )

  return (
    <div
      className="rich-text-content"
      dangerouslySetInnerHTML={{ __html: processedHTML }}
      style={{
        lineHeight: '1.6',
        wordBreak: 'break-word',
      }}
    />
  )
}

// 為富文本內容添加樣式
export const richTextStyles = `
  .rich-text-content {
    font-size: inherit;
    color: inherit;
  }

  .rich-text-content b,
  .rich-text-content strong {
    font-weight: 600;
  }

  .rich-text-content a {
    color: #2563eb;
    text-decoration: underline;
    transition: color 0.2s;
  }

  .rich-text-content a:hover {
    color: #1d4ed8;
  }

  .rich-text-content ul,
  .rich-text-content ol {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
  }

  .rich-text-content li {
    margin: 0.25rem 0;
  }

  .rich-text-content br {
    display: block;
    content: "";
    margin: 0.25rem 0;
  }
`