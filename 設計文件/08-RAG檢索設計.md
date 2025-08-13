# 08 - RAG 檢索設計文件

## 快速恢復指南
如果你忘記了這個模組，記住：這是知識庫檢索系統，使用向量資料庫儲存毒防服務、法律、醫療等資訊。透過語意檢索提供準確的參考資料，支援多語言，並根據個案階段調整檢索策略。

## 核心技術棧
- pgvector (PostgreSQL 向量擴充)
- OpenAI Embeddings (文字向量化)
- LangChain (檢索鏈)
- Elasticsearch (全文檢索備選)

## LLM 模型使用策略
- **向量嵌入**: 使用 text-embedding-3-small (成本效益最佳)
- **重排序**: 使用 gpt-4o-mini (快速評分)
- **摘要生成**: 使用 gpt-4o-mini (簡單摘要任務)

## 專案結構
```
rag/
├── __init__.py
├── embeddings.py       # 向量嵌入
├── indexer.py          # 文件索引
├── retriever.py        # 檢索器
├── reranker.py         # 重排序
├── chunker.py          # 文件分塊
├── data/               # 知識庫資料
│   ├── services/       # 服務資訊
│   ├── legal/          # 法律條文
│   ├── medical/        # 醫療知識
│   └── faqs/           # 常見問題
├── loaders/            # 資料載入器
│   ├── pdf_loader.py
│   ├── web_loader.py
│   └── db_loader.py
└── pipelines/          # 檢索管線
    ├── qa_pipeline.py
    └── summary_pipeline.py
```

## 1. 向量嵌入與索引

```python
# embeddings.py
from typing import List, Dict, Tuple
import numpy as np
from openai import OpenAI
from langchain.embeddings import OpenAIEmbeddings
import tiktoken

class EmbeddingService:
    """向量嵌入服務"""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        self.client = OpenAI()
        self.model = model
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # 向量維度
        self.dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        
        self.dimension = self.dimensions.get(model, 1536)
        
        # LangChain 整合
        self.langchain_embeddings = OpenAIEmbeddings(
            model=model,
            openai_api_key=self.client.api_key
        )
    
    async def embed_text(self, text: str) -> np.ndarray:
        """嵌入單一文本"""
        
        # 檢查 token 數量
        tokens = self.tokenizer.encode(text)
        if len(tokens) > 8191:  # OpenAI 限制
            text = self.tokenizer.decode(tokens[:8191])
        
        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        
        embedding = response.data[0].embedding
        return np.array(embedding)
    
    async def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[np.ndarray]:
        """批次嵌入"""
        
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            # 處理過長文本
            processed_batch = []
            for text in batch:
                tokens = self.tokenizer.encode(text)
                if len(tokens) > 8191:
                    text = self.tokenizer.decode(tokens[:8191])
                processed_batch.append(text)
            
            response = await self.client.embeddings.create(
                model=self.model,
                input=processed_batch
            )
            
            batch_embeddings = [
                np.array(item.embedding) 
                for item in response.data
            ]
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def calculate_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """計算餘弦相似度"""
        
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
```

## 2. 文件分塊策略

```python
# chunker.py
from typing import List, Dict
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter
)
import re

class DocumentChunker:
    """文件分塊器"""
    
    def __init__(self):
        # 不同類型文件的分塊策略
        self.strategies = {
            "legal": self._chunk_legal_document,
            "medical": self._chunk_medical_document,
            "service": self._chunk_service_info,
            "faq": self._chunk_faq,
            "general": self._chunk_general
        }
        
        # 預設分塊器
        self.default_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", "；", " "]
        )
        
        # Token 分塊器 (更精確)
        self.token_splitter = TokenTextSplitter(
            chunk_size=400,
            chunk_overlap=20
        )
    
    def chunk_document(
        self,
        text: str,
        doc_type: str = "general",
        metadata: Dict = None
    ) -> List[Dict]:
        """分塊文件"""
        
        strategy = self.strategies.get(doc_type, self._chunk_general)
        chunks = strategy(text)
        
        # 加入 metadata
        result = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                "content": chunk,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "doc_type": doc_type,
                "metadata": metadata or {}
            }
            
            # 計算摘要
            chunk_data["summary"] = self._generate_chunk_summary(chunk)
            
            result.append(chunk_data)
        
        return result
    
    def _chunk_legal_document(self, text: str) -> List[str]:
        """法律文件分塊 (保持條文完整性)"""
        
        chunks = []
        
        # 按條文分割
        articles = re.split(r'第[一二三四五六七八九十百千]+條', text)
        
        for article in articles:
            if not article.strip():
                continue
            
            # 如果條文太長，進一步分割
            if len(article) > 800:
                sub_chunks = self.default_splitter.split_text(article)
                chunks.extend(sub_chunks)
            else:
                chunks.append(article.strip())
        
        return chunks
    
    def _chunk_medical_document(self, text: str) -> List[str]:
        """醫療文件分塊 (保持段落完整性)"""
        
        # 先按段落分割
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            # 組合相關段落
            if len(current_chunk) + len(para) < 600:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_service_info(self, text: str) -> List[str]:
        """服務資訊分塊 (保持服務項目完整)"""
        
        chunks = []
        
        # 識別服務項目
        services = re.split(r'(?:服務項目|項目|服務)[:：]', text)
        
        for service in services:
            if not service.strip():
                continue
            
            # 提取服務細節
            details = self._extract_service_details(service)
            
            if details:
                chunks.append(details)
        
        return chunks if chunks else self.default_splitter.split_text(text)
    
    def _chunk_faq(self, text: str) -> List[str]:
        """FAQ 分塊 (Q&A 配對)"""
        
        chunks = []
        
        # 識別 Q&A 模式
        qa_pattern = r'[問Q][:：](.*?)[答A][:：](.*?)(?=[問Q][:：]|$)'
        matches = re.findall(qa_pattern, text, re.DOTALL)
        
        for question, answer in matches:
            qa_pair = f"問：{question.strip()}\n答：{answer.strip()}"
            chunks.append(qa_pair)
        
        # 如果沒有匹配到 Q&A 格式，使用預設分塊
        if not chunks:
            chunks = self.default_splitter.split_text(text)
        
        return chunks
    
    def _chunk_general(self, text: str) -> List[str]:
        """一般文件分塊"""
        return self.default_splitter.split_text(text)
    
    def _extract_service_details(self, text: str) -> str:
        """提取服務細節"""
        
        # 提取關鍵資訊
        patterns = {
            "名稱": r'名稱[:：](.*?)(?:\n|$)',
            "時間": r'時間[:：](.*?)(?:\n|$)',
            "地點": r'地點[:：](.*?)(?:\n|$)',
            "電話": r'電話[:：](.*?)(?:\n|$)',
            "費用": r'費用[:：](.*?)(?:\n|$)'
        }
        
        details = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                details[key] = match.group(1).strip()
        
        if details:
            return "\n".join([f"{k}: {v}" for k, v in details.items()])
        
        return text[:500] if len(text) > 500 else text
    
    def _generate_chunk_summary(self, chunk: str) -> str:
        """生成分塊摘要"""
        
        # 簡單摘要：取前100字元
        if len(chunk) > 100:
            return chunk[:100] + "..."
        return chunk
```

## 3. 文件索引器

```python
# indexer.py
from typing import List, Dict, Optional
import asyncio
from datetime import datetime
from pgvector.asyncpg import register_vector

class DocumentIndexer:
    """文件索引器"""
    
    def __init__(self, db_helper, embedding_service, chunker):
        self.db = db_helper
        self.embedder = embedding_service
        self.chunker = chunker
    
    async def index_document(
        self,
        content: str,
        title: str,
        source: str,
        category: str,
        lang: str = "zh-TW",
        metadata: Dict = None
    ) -> Dict:
        """索引單一文件"""
        
        # 分塊
        chunks = self.chunker.chunk_document(
            content,
            doc_type=category,
            metadata=metadata
        )
        
        # 產生向量
        chunk_texts = [c["content"] for c in chunks]
        embeddings = await self.embedder.embed_batch(chunk_texts)
        
        # 儲存到資料庫
        indexed_ids = []
        
        async with self.db.get_session() as session:
            for chunk, embedding in zip(chunks, embeddings):
                doc = RagDocument(
                    title=title,
                    content=chunk["content"],
                    source=source,
                    category=category,
                    lang=lang,
                    embedding=embedding,
                    metadata={
                        **metadata,
                        "chunk_index": chunk["chunk_index"],
                        "total_chunks": chunk["total_chunks"],
                        "summary": chunk["summary"]
                    },
                    published_date=metadata.get("published_date"),
                    created_at=datetime.utcnow()
                )
                
                session.add(doc)
                await session.flush()
                indexed_ids.append(str(doc.id))
            
            await session.commit()
        
        return {
            "document_id": indexed_ids[0] if indexed_ids else None,
            "chunks_indexed": len(indexed_ids),
            "chunk_ids": indexed_ids
        }
    
    async def index_batch(
        self,
        documents: List[Dict],
        batch_size: int = 10
    ) -> Dict:
        """批次索引文件"""
        
        results = {
            "total": len(documents),
            "succeeded": 0,
            "failed": 0,
            "errors": []
        }
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            
            # 平行處理
            tasks = [
                self.index_document(**doc)
                for doc in batch
            ]
            
            batch_results = await asyncio.gather(
                *tasks,
                return_exceptions=True
            )
            
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    results["failed"] += 1
                    results["errors"].append({
                        "document": batch[j].get("title", "unknown"),
                        "error": str(result)
                    })
                else:
                    results["succeeded"] += 1
        
        return results
    
    async def update_document(
        self,
        document_id: str,
        content: str = None,
        metadata: Dict = None
    ) -> bool:
        """更新文件"""
        
        async with self.db.get_session() as session:
            doc = await session.get(RagDocument, document_id)
            
            if not doc:
                return False
            
            if content:
                # 重新產生向量
                embedding = await self.embedder.embed_text(content)
                doc.content = content
                doc.embedding = embedding
            
            if metadata:
                doc.metadata.update(metadata)
            
            doc.updated_at = datetime.utcnow()
            
            await session.commit()
            
        return True
    
    async def delete_document(self, document_id: str) -> bool:
        """刪除文件"""
        
        async with self.db.get_session() as session:
            doc = await session.get(RagDocument, document_id)
            
            if not doc:
                return False
            
            await session.delete(doc)
            await session.commit()
            
        return True
    
    async def reindex_all(self) -> Dict:
        """重新索引所有文件"""
        
        # 取得所有文件
        async with self.db.get_session() as session:
            result = await session.execute(
                select(RagDocument)
            )
            documents = result.scalars().all()
        
        results = {
            "total": len(documents),
            "reindexed": 0,
            "errors": []
        }
        
        for doc in documents:
            try:
                # 重新產生向量
                embedding = await self.embedder.embed_text(doc.content)
                
                async with self.db.get_session() as session:
                    doc.embedding = embedding
                    doc.updated_at = datetime.utcnow()
                    await session.commit()
                
                results["reindexed"] += 1
                
            except Exception as e:
                results["errors"].append({
                    "document_id": str(doc.id),
                    "error": str(e)
                })
        
        return results
```

## 4. 檢索器實作

```python
# retriever.py
from typing import List, Dict, Optional, Tuple
import numpy as np
from sqlalchemy import select, and_, or_

class RAGRetriever:
    """RAG 檢索器"""
    
    def __init__(self, db_helper, embedding_service):
        self.db = db_helper
        self.embedder = embedding_service
        
        # 檢索參數
        self.default_k = 5
        self.similarity_threshold = 0.7
    
    async def retrieve(
        self,
        query: str,
        k: int = None,
        filters: Dict = None,
        rerank: bool = True
    ) -> List[Dict]:
        """檢索相關文件"""
        
        k = k or self.default_k
        
        # 產生查詢向量
        query_embedding = await self.embedder.embed_text(query)
        
        # 向量檢索
        results = await self._vector_search(
            query_embedding,
            k=k * 3 if rerank else k,  # 如果要重排序，先取更多結果
            filters=filters
        )
        
        # 重排序
        if rerank and results:
            results = await self._rerank_results(
                query,
                results,
                k=k
            )
        
        # 後處理
        return self._postprocess_results(results)
    
    async def _vector_search(
        self,
        query_embedding: np.ndarray,
        k: int,
        filters: Dict = None
    ) -> List[Tuple[Dict, float]]:
        """向量相似度搜尋"""
        
        async with self.db.get_session() as session:
            # 建立查詢
            query = select(
                RagDocument,
                RagDocument.embedding.cosine_distance(query_embedding).label("distance")
            )
            
            # 應用過濾條件
            if filters:
                conditions = []
                
                if "category" in filters:
                    conditions.append(
                        RagDocument.category == filters["category"]
                    )
                
                if "lang" in filters:
                    conditions.append(
                        RagDocument.lang == filters["lang"]
                    )
                
                if "source" in filters:
                    conditions.append(
                        RagDocument.source == filters["source"]
                    )
                
                if conditions:
                    query = query.where(and_(*conditions))
            
            # 按相似度排序
            query = query.order_by("distance").limit(k)
            
            # 執行查詢
            result = await session.execute(query)
            rows = result.all()
            
            # 轉換結果
            results = []
            for doc, distance in rows:
                similarity = 1 - distance  # 轉換為相似度
                
                if similarity >= self.similarity_threshold:
                    results.append((
                        {
                            "id": str(doc.id),
                            "title": doc.title,
                            "content": doc.content,
                            "source": doc.source,
                            "category": doc.category,
                            "metadata": doc.metadata,
                            "published_date": doc.published_date
                        },
                        similarity
                    ))
            
            return results
    
    async def _rerank_results(
        self,
        query: str,
        results: List[Tuple[Dict, float]],
        k: int
    ) -> List[Tuple[Dict, float]]:
        """重排序結果"""
        
        # 使用交叉編碼器或其他重排序模型
        reranker = CrossEncoderReranker()
        
        # 準備輸入
        documents = [r[0]["content"] for r in results]
        
        # 計算重排序分數
        scores = await reranker.score(query, documents)
        
        # 結合原始相似度和重排序分數
        combined_results = []
        for i, (doc, similarity) in enumerate(results):
            # 加權組合
            final_score = 0.3 * similarity + 0.7 * scores[i]
            combined_results.append((doc, final_score))
        
        # 重新排序
        combined_results.sort(key=lambda x: x[1], reverse=True)
        
        return combined_results[:k]
    
    def _postprocess_results(
        self,
        results: List[Tuple[Dict, float]]
    ) -> List[Dict]:
        """後處理結果"""
        
        processed = []
        
        for doc, score in results:
            # 加入相關性分數
            doc["relevance_score"] = round(score, 3)
            
            # 處理 metadata
            if doc.get("metadata"):
                # 提取重要資訊
                doc["chunk_index"] = doc["metadata"].get("chunk_index", 0)
                doc["total_chunks"] = doc["metadata"].get("total_chunks", 1)
            
            # 截斷過長內容
            if len(doc["content"]) > 1000:
                doc["content_truncated"] = doc["content"][:1000] + "..."
                doc["is_truncated"] = True
            else:
                doc["content_truncated"] = doc["content"]
                doc["is_truncated"] = False
            
            processed.append(doc)
        
        return processed
    
    async def hybrid_search(
        self,
        query: str,
        k: int = None,
        filters: Dict = None
    ) -> List[Dict]:
        """混合檢索 (向量 + 關鍵字)"""
        
        k = k or self.default_k
        
        # 向量檢索
        vector_results = await self.retrieve(
            query,
            k=k,
            filters=filters,
            rerank=False
        )
        
        # 關鍵字檢索
        keyword_results = await self._keyword_search(
            query,
            k=k,
            filters=filters
        )
        
        # 合併結果
        merged = self._merge_results(
            vector_results,
            keyword_results,
            k=k
        )
        
        return merged
    
    async def _keyword_search(
        self,
        query: str,
        k: int,
        filters: Dict = None
    ) -> List[Dict]:
        """關鍵字搜尋"""
        
        async with self.db.get_session() as session:
            # 使用 PostgreSQL 全文搜尋
            search_query = select(RagDocument).where(
                RagDocument.content.match(query)
            )
            
            if filters:
                if "category" in filters:
                    search_query = search_query.where(
                        RagDocument.category == filters["category"]
                    )
                
                if "lang" in filters:
                    search_query = search_query.where(
                        RagDocument.lang == filters["lang"]
                    )
            
            search_query = search_query.limit(k)
            
            result = await session.execute(search_query)
            documents = result.scalars().all()
            
            return [
                {
                    "id": str(doc.id),
                    "title": doc.title,
                    "content": doc.content,
                    "source": doc.source,
                    "category": doc.category,
                    "relevance_score": 0.5  # 預設分數
                }
                for doc in documents
            ]
    
    def _merge_results(
        self,
        vector_results: List[Dict],
        keyword_results: List[Dict],
        k: int
    ) -> List[Dict]:
        """合併檢索結果"""
        
        # 使用 ID 去重
        seen_ids = set()
        merged = []
        
        # 交替加入結果
        for i in range(max(len(vector_results), len(keyword_results))):
            if i < len(vector_results):
                doc = vector_results[i]
                if doc["id"] not in seen_ids:
                    merged.append(doc)
                    seen_ids.add(doc["id"])
            
            if i < len(keyword_results):
                doc = keyword_results[i]
                if doc["id"] not in seen_ids:
                    merged.append(doc)
                    seen_ids.add(doc["id"])
            
            if len(merged) >= k:
                break
        
        return merged[:k]
```

## 5. 重排序器

```python
# reranker.py
from typing import List, Tuple
from sentence_transformers import CrossEncoder
import torch

class CrossEncoderReranker:
    """交叉編碼器重排序"""
    
    def __init__(self, model_name: str = None, use_llm: bool = False):
        self.use_llm = use_llm
        
        if use_llm:
            # 使用 GPT-4o-mini 進行重排序
            from langchain.chat_models import ChatOpenAI
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                max_tokens=100
            )
        elif model_name:
            self.model = CrossEncoder(model_name)
        else:
            # 使用預設的中文重排序模型
            self.model = CrossEncoder(
                'cross-encoder/ms-marco-MiniLM-L-6-v2',
                max_length=512
            )
    
    async def score(
        self,
        query: str,
        documents: List[str]
    ) -> List[float]:
        """計算重排序分數"""
        
        if self.use_llm:
            # 使用 GPT-4o-mini 評分
            scores = []
            for doc in documents:
                prompt = f"""
                查詢: {query[:200]}
                文件: {doc[:500]}
                
                請評估文件與查詢的相關性，回傳0-1的分數：
                """
                response = await self.llm.ainvoke(prompt)
                try:
                    score = float(response.content.strip())
                    scores.append(min(max(score, 0), 1))  # 限制在[0,1]
                except:
                    scores.append(0.5)  # 預設分數
            return scores
        else:
            # 使用交叉編碼器
            pairs = [[query, doc] for doc in documents]
            
            with torch.no_grad():
                scores = self.model.predict(pairs)
            
            scores = torch.sigmoid(torch.tensor(scores)).tolist()
            
            return scores
    
    async def rerank(
        self,
        query: str,
        documents: List[Dict],
        k: int = None
    ) -> List[Dict]:
        """重排序文件"""
        
        if not documents:
            return []
        
        # 提取文本
        texts = [doc.get("content", "") for doc in documents]
        
        # 計算分數
        scores = await self.score(query, texts)
        
        # 組合結果
        ranked = []
        for doc, score in zip(documents, scores):
            doc["rerank_score"] = score
            ranked.append(doc)
        
        # 排序
        ranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        if k:
            ranked = ranked[:k]
        
        return ranked

class DiversityReranker:
    """多樣性重排序"""
    
    def __init__(self, lambda_param: float = 0.5):
        self.lambda_param = lambda_param  # 相關性與多樣性的權衡
    
    async def rerank(
        self,
        documents: List[Dict],
        k: int = None
    ) -> List[Dict]:
        """基於 MMR (Maximal Marginal Relevance) 的重排序"""
        
        if not documents:
            return []
        
        k = k or len(documents)
        
        # 提取向量
        embeddings = [doc.get("embedding") for doc in documents]
        scores = [doc.get("relevance_score", 0) for doc in documents]
        
        selected = []
        selected_indices = []
        remaining_indices = list(range(len(documents)))
        
        # 選擇第一個文件 (最相關的)
        first_idx = scores.index(max(scores))
        selected.append(documents[first_idx])
        selected_indices.append(first_idx)
        remaining_indices.remove(first_idx)
        
        # 迭代選擇
        while len(selected) < k and remaining_indices:
            mmr_scores = []
            
            for idx in remaining_indices:
                # 相關性分數
                relevance = scores[idx]
                
                # 計算與已選文件的最大相似度
                max_similarity = 0
                for sel_idx in selected_indices:
                    if embeddings[idx] is not None and embeddings[sel_idx] is not None:
                        similarity = self._cosine_similarity(
                            embeddings[idx],
                            embeddings[sel_idx]
                        )
                        max_similarity = max(max_similarity, similarity)
                
                # MMR 分數
                mmr = self.lambda_param * relevance - (1 - self.lambda_param) * max_similarity
                mmr_scores.append(mmr)
            
            # 選擇 MMR 最高的文件
            best_idx = remaining_indices[mmr_scores.index(max(mmr_scores))]
            selected.append(documents[best_idx])
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)
        
        return selected
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """計算餘弦相似度"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
```

## 6. 檢索管線

```python
# pipelines/qa_pipeline.py
from typing import Dict, List, Optional
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class QAPipeline:
    """問答檢索管線"""
    
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
        
        # 定義 prompt 模板
        self.prompt_template = """
請根據以下參考資料回答問題。如果資料中沒有相關資訊，請誠實說明。

參考資料：
{context}

問題：{question}

請用繁體中文回答，並註明資訊來源。
回答：
        """
        
        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )
    
    async def answer(
        self,
        question: str,
        user_profile: Dict = None,
        filters: Dict = None
    ) -> Dict:
        """回答問題"""
        
        # 根據使用者檔案調整檢索
        if user_profile:
            filters = self._adjust_filters(user_profile, filters)
        
        # 檢索相關文件
        documents = await self.retriever.retrieve(
            question,
            k=5,
            filters=filters
        )
        
        if not documents:
            return {
                "answer": "抱歉，我沒有找到相關資訊來回答您的問題。",
                "sources": [],
                "confidence": 0.0
            }
        
        # 準備上下文
        context = self._prepare_context(documents)
        
        # 生成答案
        prompt_text = self.prompt.format(
            context=context,
            question=question
        )
        
        response = await self.llm.ainvoke(prompt_text)
        
        # 提取來源
        sources = self._extract_sources(documents)
        
        # 計算信心度
        confidence = self._calculate_confidence(documents)
        
        return {
            "answer": response,
            "sources": sources,
            "confidence": confidence,
            "documents_used": len(documents)
        }
    
    def _adjust_filters(
        self,
        user_profile: Dict,
        filters: Dict = None
    ) -> Dict:
        """根據使用者檔案調整過濾條件"""
        
        filters = filters or {}
        
        # 語言偏好
        if "lang" not in filters:
            filters["lang"] = user_profile.get("lang", "zh-TW")
        
        # 根據階段調整類別
        stage = user_profile.get("stage")
        if stage and "category" not in filters:
            stage_categories = {
                "assessment": ["medical", "service"],
                "treatment": ["medical", "legal", "service"],
                "recovery": ["service", "employment", "social"]
            }
            filters["categories"] = stage_categories.get(stage, [])
        
        return filters
    
    def _prepare_context(self, documents: List[Dict]) -> str:
        """準備上下文"""
        
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            source_info = f"[來源 {i}: {doc.get('title', '未知')} - {doc.get('source', '')}]"
            content = doc.get('content_truncated', doc.get('content', ''))
            
            context_parts.append(f"{source_info}\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _extract_sources(self, documents: List[Dict]) -> List[Dict]:
        """提取來源資訊"""
        
        sources = []
        seen = set()
        
        for doc in documents:
            source_key = f"{doc.get('title')}:{doc.get('source')}"
            
            if source_key not in seen:
                sources.append({
                    "title": doc.get("title"),
                    "source": doc.get("source"),
                    "url": doc.get("metadata", {}).get("url"),
                    "date": doc.get("published_date")
                })
                seen.add(source_key)
        
        return sources
    
    def _calculate_confidence(self, documents: List[Dict]) -> float:
        """計算答案信心度"""
        
        if not documents:
            return 0.0
        
        # 基於相關性分數
        scores = [doc.get("relevance_score", 0) for doc in documents]
        avg_score = sum(scores) / len(scores)
        
        # 基於文件數量
        doc_factor = min(len(documents) / 3, 1.0)
        
        # 綜合信心度
        confidence = avg_score * 0.7 + doc_factor * 0.3
        
        return min(confidence, 1.0)
```

## 7. 資料載入器

```python
# loaders/web_loader.py
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List

class WebLoader:
    """網頁載入器"""
    
    async def load_url(self, url: str) -> Dict:
        """載入網頁內容"""
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
        
        # 解析 HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除 script 和 style
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 提取文字
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # 提取 metadata
        metadata = {
            "url": url,
            "title": soup.title.string if soup.title else "",
            "description": self._get_meta_description(soup)
        }
        
        return {
            "content": text,
            "metadata": metadata
        }
    
    def _get_meta_description(self, soup) -> str:
        """提取 meta description"""
        
        meta = soup.find("meta", attrs={"name": "description"})
        if meta:
            return meta.get("content", "")
        return ""

class KnowledgeBaseLoader:
    """知識庫批次載入"""
    
    def __init__(self, indexer):
        self.indexer = indexer
        self.loaders = {
            "pdf": PDFLoader(),
            "web": WebLoader(),
            "csv": CSVLoader()
        }
    
    async def load_knowledge_base(self, config_path: str) -> Dict:
        """載入整個知識庫"""
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        results = {
            "total": 0,
            "succeeded": 0,
            "failed": 0,
            "errors": []
        }
        
        for source in config["sources"]:
            try:
                # 根據類型載入
                loader = self.loaders.get(source["type"])
                
                if source["type"] == "web":
                    content_data = await loader.load_url(source["url"])
                elif source["type"] == "pdf":
                    content_data = await loader.load_pdf(source["path"])
                else:
                    continue
                
                # 索引文件
                await self.indexer.index_document(
                    content=content_data["content"],
                    title=source.get("title", ""),
                    source=source.get("source", ""),
                    category=source.get("category", "general"),
                    lang=source.get("lang", "zh-TW"),
                    metadata=content_data.get("metadata", {})
                )
                
                results["succeeded"] += 1
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "source": source,
                    "error": str(e)
                })
            
            results["total"] += 1
        
        return results
```

## 8. 測試與評估

```python
# test_rag.py
import unittest
from datetime import datetime

class TestRAG(unittest.TestCase):
    
    async def test_embedding_generation(self):
        """測試向量生成"""
        
        embedder = EmbeddingService()
        
        text = "高雄市毒品防制局提供24小時諮詢服務"
        embedding = await embedder.embed_text(text)
        
        self.assertEqual(len(embedding), 1536)
        self.assertTrue(all(isinstance(x, float) for x in embedding))
    
    async def test_document_chunking(self):
        """測試文件分塊"""
        
        chunker = DocumentChunker()
        
        # 測試 FAQ 分塊
        faq_text = """
        問：戒毒需要多久時間？
        答：戒毒是一個長期的過程，通常需要至少3-6個月的密集治療。
        
        問：有哪些戒毒方法？
        答：包括藥物治療、心理諮商、團體治療等多種方法。
        """
        
        chunks = chunker.chunk_document(faq_text, doc_type="faq")
        
        self.assertEqual(len(chunks), 2)
        self.assertIn("戒毒需要多久時間", chunks[0]["content"])
    
    async def test_retrieval_accuracy(self):
        """測試檢索準確性"""
        
        retriever = RAGRetriever(db_helper, embedder)
        
        # 測試查詢
        query = "美沙冬替代療法的申請流程"
        
        results = await retriever.retrieve(
            query,
            k=5,
            filters={"category": "medical"}
        )
        
        self.assertTrue(len(results) > 0)
        self.assertTrue(all(r["relevance_score"] > 0.7 for r in results))
    
    async def test_multilingual_retrieval(self):
        """測試多語言檢索"""
        
        retriever = RAGRetriever(db_helper, embedder)
        
        # 中文查詢
        zh_results = await retriever.retrieve(
            "戒毒服務",
            filters={"lang": "zh-TW"}
        )
        
        # 英文查詢
        en_results = await retriever.retrieve(
            "addiction treatment",
            filters={"lang": "en"}
        )
        
        self.assertTrue(len(zh_results) > 0)
        self.assertTrue(len(en_results) > 0)
    
    async def test_qa_pipeline(self):
        """測試問答管線"""
        
        pipeline = QAPipeline(retriever, llm)
        
        question = "高雄市有哪些戒毒機構？"
        
        answer = await pipeline.answer(
            question,
            user_profile={"lang": "zh-TW", "stage": "treatment"}
        )
        
        self.assertIn("answer", answer)
        self.assertIn("sources", answer)
        self.assertGreater(answer["confidence"], 0.5)

# 評估指標
class RAGEvaluator:
    """RAG 系統評估"""
    
    def evaluate_retrieval(
        self,
        test_queries: List[Dict]
    ) -> Dict:
        """評估檢索效果"""
        
        metrics = {
            "precision_at_k": [],
            "recall_at_k": [],
            "mrr": [],  # Mean Reciprocal Rank
            "map": []   # Mean Average Precision
        }
        
        for query_data in test_queries:
            query = query_data["query"]
            relevant_docs = query_data["relevant_docs"]
            
            # 執行檢索
            results = self.retriever.retrieve(query, k=10)
            retrieved_ids = [r["id"] for r in results]
            
            # 計算指標
            precision = self._calculate_precision(
                retrieved_ids,
                relevant_docs
            )
            recall = self._calculate_recall(
                retrieved_ids,
                relevant_docs
            )
            mrr = self._calculate_mrr(
                retrieved_ids,
                relevant_docs
            )
            
            metrics["precision_at_k"].append(precision)
            metrics["recall_at_k"].append(recall)
            metrics["mrr"].append(mrr)
        
        # 計算平均值
        return {
            "avg_precision": np.mean(metrics["precision_at_k"]),
            "avg_recall": np.mean(metrics["recall_at_k"]),
            "avg_mrr": np.mean(metrics["mrr"])
        }
```

## 關鍵記憶點
1. **必須**定期更新知識庫索引，確保資訊時效性
2. **記得**根據使用者階段和語言調整檢索策略
3. **注意**文件分塊要保持語意完整性
4. **重要**使用重排序提升檢索準確度