"""向量嵌入服務"""

from typing import List, Dict, Any, Optional
import numpy as np
from openai import AsyncOpenAI
import logging
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """嵌入結果"""
    text: str
    embedding: List[float]
    model: str
    usage: Dict[str, int]


class EmbeddingService:
    """向量嵌入服務"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-3-small"  # 成本效益最佳
        self.dimensions = 1536  # text-embedding-3-small 的維度
    
    async def embed_text(self, text: str) -> List[float]:
        """將文字轉換為向量嵌入"""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding for text (length: {len(text)})")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量將文字轉換為向量嵌入"""
        try:
            # OpenAI API 限制每次最多 2048 個輸入
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    encoding_format="float"
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Generated embeddings for batch {i//batch_size + 1}")
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    async def embed_with_metadata(self, text: str, metadata: Dict[str, Any] = None) -> EmbeddingResult:
        """將文字轉換為向量嵌入並返回完整結果"""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )
            
            result = EmbeddingResult(
                text=text,
                embedding=response.data[0].embedding,
                model=response.model,
                usage=response.usage.dict() if response.usage else {}
            )
            
            logger.info(f"Generated embedding with metadata for text (length: {len(text)})")
            return result
            
        except Exception as e:
            logger.error(f"Error generating embedding with metadata: {str(e)}")
            raise
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """計算兩個向量的餘弦相似度"""
        try:
            # 轉換為 numpy 數組
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # 計算餘弦相似度
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def get_embedding_dimensions(self) -> int:
        """取得嵌入向量的維度"""
        return self.dimensions
    
    def get_model_name(self) -> str:
        """取得使用的模型名稱"""
        return self.model

