"""文件切塊服務"""

from typing import List, Dict, Any, Optional
import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """文件塊"""
    content: str
    chunk_index: int
    metadata: Dict[str, Any]
    start_char: int
    end_char: int


class DocumentChunker:
    """文件切塊器"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        """將文字切塊"""
        if not text or not text.strip():
            return []
        
        metadata = metadata or {}
        chunks = []
        
        # 清理文字
        cleaned_text = self._clean_text(text)
        
        # 按段落分割
        paragraphs = self._split_by_paragraphs(cleaned_text)
        
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for paragraph in paragraphs:
            # 如果加入這個段落會超過大小限制
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                # 保存當前塊
                chunk = Chunk(
                    content=current_chunk.strip(),
                    chunk_index=chunk_index,
                    metadata=metadata.copy(),
                    start_char=current_start,
                    end_char=current_start + len(current_chunk)
                )
                chunks.append(chunk)
                
                # 開始新塊，保留重疊部分
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + paragraph
                current_start = chunk.end_char - len(overlap_text)
                chunk_index += 1
            else:
                current_chunk += paragraph
        
        # 處理最後一個塊
        if current_chunk.strip():
            chunk = Chunk(
                content=current_chunk.strip(),
                chunk_index=chunk_index,
                metadata=metadata.copy(),
                start_char=current_start,
                end_char=current_start + len(current_chunk)
            )
            chunks.append(chunk)
        
        logger.info(f"Chunked text into {len(chunks)} chunks")
        return chunks
    
    def chunk_document(self, title: str, content: str, source: str, 
                      category: str, lang: str = "zh-TW", 
                      published_date: str = None) -> List[Chunk]:
        """切塊文件"""
        metadata = {
            "title": title,
            "source": source,
            "category": category,
            "lang": lang,
            "published_date": published_date
        }
        
        # 將標題加入內容
        full_content = f"標題: {title}\n\n{content}"
        
        return self.chunk_text(full_content, metadata)
    
    def _clean_text(self, text: str) -> str:
        """清理文字"""
        # 移除多餘的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符但保留中文標點
        text = re.sub(r'[^\w\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef.,!?;:()（）【】「」『』""''""''，。！？；：]', '', text)
        
        return text.strip()
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """按段落分割文字"""
        # 按換行符分割
        paragraphs = re.split(r'\n\s*\n', text)
        
        # 過濾空段落
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def _get_overlap_text(self, text: str) -> str:
        """取得重疊文字"""
        if len(text) <= self.overlap:
            return text
        
        # 從文字末尾取重疊部分
        overlap_text = text[-self.overlap:]
        
        # 嘗試在句子邊界切斷
        sentence_endings = ['。', '！', '？', '.', '!', '?']
        for ending in sentence_endings:
            if ending in overlap_text:
                # 找到最後一個句子結束符號
                last_ending = overlap_text.rfind(ending)
                if last_ending > self.overlap // 2:  # 確保重疊足夠
                    return overlap_text[last_ending + 1:]
        
        return overlap_text
    
    def chunk_by_sentences(self, text: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        """按句子切塊"""
        if not text or not text.strip():
            return []
        
        metadata = metadata or {}
        chunks = []
        
        # 按句子分割
        sentences = self._split_by_sentences(text)
        
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                # 保存當前塊
                chunk = Chunk(
                    content=current_chunk.strip(),
                    chunk_index=chunk_index,
                    metadata=metadata.copy(),
                    start_char=current_start,
                    end_char=current_start + len(current_chunk)
                )
                chunks.append(chunk)
                
                # 開始新塊
                current_chunk = sentence
                current_start = chunk.end_char
                chunk_index += 1
            else:
                current_chunk += sentence
        
        # 處理最後一個塊
        if current_chunk.strip():
            chunk = Chunk(
                content=current_chunk.strip(),
                chunk_index=chunk_index,
                metadata=metadata.copy(),
                start_char=current_start,
                end_char=current_start + len(current_chunk)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """按句子分割文字"""
        # 中文和英文句子結束符號
        sentence_endings = ['。', '！', '？', '.', '!', '?']
        
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in sentence_endings:
                sentences.append(current_sentence)
                current_sentence = ""
        
        # 添加最後一個句子（如果存在）
        if current_sentence.strip():
            sentences.append(current_sentence)
        
        return [s.strip() for s in sentences if s.strip()]

