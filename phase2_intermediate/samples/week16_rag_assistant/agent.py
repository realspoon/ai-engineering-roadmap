"""
Week 16: RAG Assistant - Agent Module
RAG (Retrieval-Augmented Generation) 에이전트의 핵심 구현
"""

import os
import json
import hashlib
import pickle
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import logging

from .config import Config, get_config


logger = logging.getLogger(__name__)


@dataclass
class Document:
    """문서 정의"""
    id: str
    content: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at
        }


@dataclass
class Chunk:
    """문서 청크"""
    id: str
    document_id: str
    content: str
    position: int
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "position": self.position,
            "metadata": self.metadata
        }


@dataclass
class RetrievalResult:
    """검색 결과"""
    chunk: Chunk
    similarity_score: float
    rank: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk": self.chunk.to_dict(),
            "similarity_score": self.similarity_score,
            "rank": self.rank
        }


class Embedder(ABC):
    """임베더 기본 클래스"""

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """텍스트를 임베딩"""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """배치 임베딩"""
        pass


class SimpleEmbedder(Embedder):
    """간단한 임베더 (해시 기반)"""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed(self, text: str) -> List[float]:
        """해시 기반 임베딩"""
        hash_obj = hashlib.md5(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)

        embedding = []
        for i in range(self.dimension):
            embedding.append(float((hash_int >> i) & 1))

        # 정규화
        norm = sum(x ** 2 for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]

        return embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """배치 임베딩"""
        return [self.embed(text) for text in texts]


class VectorDB(ABC):
    """벡터 데이터베이스 기본 클래스"""

    @abstractmethod
    def add(self, chunk: Chunk) -> None:
        """청크 추가"""
        pass

    @abstractmethod
    def search(self, embedding: List[float], top_k: int) -> List[Tuple[Chunk, float]]:
        """유사도 검색"""
        pass

    @abstractmethod
    def delete(self, chunk_id: str) -> None:
        """청크 삭제"""
        pass


class SimpleVectorDB(VectorDB):
    """간단한 벡터 데이터베이스 (인메모리)"""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.chunks: Dict[str, Chunk] = {}
        self.embeddings: Dict[str, List[float]] = {}

    def add(self, chunk: Chunk) -> None:
        """청크 추가"""
        if chunk.embedding is None:
            raise ValueError("Chunk must have an embedding")

        self.chunks[chunk.id] = chunk
        self.embeddings[chunk.id] = chunk.embedding

    def search(self, embedding: List[float], top_k: int) -> List[Tuple[Chunk, float]]:
        """코사인 유사도 검색"""
        if not self.chunks:
            return []

        scores = []
        for chunk_id, stored_embedding in self.embeddings.items():
            similarity = self._cosine_similarity(embedding, stored_embedding)
            scores.append((self.chunks[chunk_id], similarity))

        # 유사도로 정렬
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_k]

    def delete(self, chunk_id: str) -> None:
        """청크 삭제"""
        if chunk_id in self.chunks:
            del self.chunks[chunk_id]
            del self.embeddings[chunk_id]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """코사인 유사도 계산"""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_v1 = sum(a ** 2 for a in v1) ** 0.5
        norm_v2 = sum(b ** 2 for b in v2) ** 0.5

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return dot_product / (norm_v1 * norm_v2)


class DocumentProcessor:
    """문서 처리기"""

    def __init__(self, config: Config = None):
        self.config = config or get_config()

    def load_documents(self, directory: str) -> List[Document]:
        """디렉토리에서 문서 로드"""
        documents = []

        if not os.path.exists(directory):
            logger.warning(f"Directory not found: {directory}")
            return documents

        for filename in os.listdir(directory):
            if filename.endswith(('.txt', '.md', '.pdf')):
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    doc_id = hashlib.md5(filename.encode()).hexdigest()
                    document = Document(
                        id=doc_id,
                        content=content,
                        source=filename,
                        metadata={"path": filepath, "size": len(content)}
                    )
                    documents.append(document)
                    logger.info(f"Loaded document: {filename}")
                except Exception as e:
                    logger.error(f"Error loading document {filename}: {str(e)}")

        return documents

    def chunk_documents(self, documents: List[Document]) -> List[Chunk]:
        """문서를 청크로 분할"""
        chunks = []
        chunk_size = self.config.rag.chunk_size
        chunk_overlap = self.config.rag.chunk_overlap

        for doc in documents:
            chunks_for_doc = self._chunk_text(
                doc.content,
                chunk_size,
                chunk_overlap
            )

            for position, chunk_content in enumerate(chunks_for_doc):
                chunk_id = hashlib.md5(
                    f"{doc.id}_{position}".encode()
                ).hexdigest()

                chunk = Chunk(
                    id=chunk_id,
                    document_id=doc.id,
                    content=chunk_content,
                    position=position,
                    metadata={"source": doc.source, "doc_id": doc.id}
                )
                chunks.append(chunk)

        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """텍스트를 청크로 분할"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            if chunk.strip():
                chunks.append(chunk)

            start += chunk_size - overlap

        return chunks


class RAGAgent:
    """RAG 에이전트"""

    def __init__(self, config: Config = None):
        self.config = config or get_config()
        self.embedder = SimpleEmbedder(
            dimension=self.config.vector_db.dimension
        )
        self.vector_db = SimpleVectorDB(
            dimension=self.config.vector_db.dimension
        )
        self.document_processor = DocumentProcessor(self.config)
        self.documents: Dict[str, Document] = {}
        self.chunks: Dict[str, Chunk] = {}
        self.cache: Dict[str, List[RetrievalResult]] = {}

        logger.info("RAG Agent initialized")

    def add_documents(self, documents: List[Document]) -> int:
        """문서 추가"""
        # 문서 저장
        for doc in documents:
            self.documents[doc.id] = doc

        # 청크 생성
        chunks = self.document_processor.chunk_documents(documents)

        # 임베딩 및 벡터 DB에 추가
        for chunk in chunks:
            embedding = self.embedder.embed(chunk.content)
            chunk.embedding = embedding
            self.vector_db.add(chunk)
            self.chunks[chunk.id] = chunk

        logger.info(f"Added {len(documents)} documents with {len(chunks)} chunks")
        return len(chunks)

    def load_documents_from_directory(self, directory: str = None) -> int:
        """디렉토리에서 문서 로드"""
        if directory is None:
            directory = self.config.documents_dir

        documents = self.document_processor.load_documents(directory)
        return self.add_documents(documents)

    def retrieve(self, query: str, top_k: int = None) -> List[RetrievalResult]:
        """쿼리에 대한 관련 청크 검색"""
        if top_k is None:
            top_k = self.config.rag.top_k

        # 캐시 확인
        cache_key = hashlib.md5(f"{query}_{top_k}".encode()).hexdigest()
        if self.config.rag.enable_cache and cache_key in self.cache:
            logger.debug(f"Cache hit for query: {query}")
            return self.cache[cache_key]

        # 쿼리 임베딩
        query_embedding = self.embedder.embed(query)

        # 벡터 검색
        search_results = self.vector_db.search(query_embedding, top_k)

        # 결과를 RetrievalResult로 변환
        results = []
        for rank, (chunk, similarity) in enumerate(search_results, 1):
            if similarity >= self.config.rag.similarity_threshold:
                result = RetrievalResult(
                    chunk=chunk,
                    similarity_score=similarity,
                    rank=rank
                )
                results.append(result)

        # 캐시 저장
        if self.config.rag.enable_cache:
            self.cache[cache_key] = results

        logger.info(f"Retrieved {len(results)} documents for query: {query}")
        return results

    def generate_context(self, query: str) -> str:
        """쿼리를 기반으로 컨텍스트 생성"""
        retrieval_results = self.retrieve(query)

        context_parts = []
        context_parts.append("## 관련 문서:\n")

        for result in retrieval_results:
            part = f"### {result.chunk.metadata.get('source', 'Unknown')} (유사도: {result.similarity_score:.2f})\n"
            part += result.chunk.content[:500]
            if len(result.chunk.content) > 500:
                part += "...\n"

            context_parts.append(part)

        return "\n".join(context_parts)

    def generate_response(self, query: str) -> Dict[str, Any]:
        """쿼리에 대한 응답 생성"""
        # 컨텍스트 생성
        context = self.generate_context(query)

        # 응답 생성 (간단한 구현)
        response = f"질문: {query}\n\n{context}\n\n응답: 위의 문서를 기반으로 한 답변입니다."

        return {
            "query": query,
            "response": response,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }

    def get_stats(self) -> Dict[str, Any]:
        """에이전트 통계"""
        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "cache_size": len(self.cache),
            "vector_db_dimension": self.config.vector_db.dimension,
            "retrieval_top_k": self.config.rag.top_k,
            "chunk_size": self.config.rag.chunk_size
        }

    def clear_cache(self) -> None:
        """캐시 초기화"""
        cache_size = len(self.cache)
        self.cache.clear()
        logger.info(f"Cleared {cache_size} cache entries")


def main():
    """테스트 함수"""
    print("="*60)
    print("RAG Agent Demo")
    print("="*60)

    # 에이전트 초기화
    agent = RAGAgent()

    # 샘플 문서 생성
    print("\n[Adding Sample Documents]")
    sample_docs = [
        Document(
            id="doc_001",
            content="Python은 고수준의 프로그래밍 언어입니다. 간단한 문법과 강력한 기능을 제공합니다.",
            source="python_intro.txt"
        ),
        Document(
            id="doc_002",
            content="머신러닝은 데이터를 기반으로 모델이 자동으로 학습하는 기술입니다.",
            source="ml_basics.txt"
        ),
        Document(
            id="doc_003",
            content="RAG는 Retrieval-Augmented Generation의 약자입니다. 검색과 생성을 결합합니다.",
            source="rag_definition.txt"
        )
    ]

    chunks_added = agent.add_documents(sample_docs)
    print(f"Added {len(sample_docs)} documents ({chunks_added} chunks)")

    # 검색 테스트
    print("\n[Retrieval Test]")
    query = "Python에 대해"
    results = agent.retrieve(query, top_k=3)
    print(f"Query: {query}")
    print(f"Retrieved {len(results)} results:")
    for result in results:
        print(f"  - {result.chunk.metadata.get('source')}: {result.similarity_score:.3f}")

    # 응답 생성 테스트
    print("\n[Response Generation]")
    response = agent.generate_response("머신러닝이란?")
    print(f"Query: {response['query']}")
    print(f"Response (first 200 chars): {response['response'][:200]}...")

    # 통계
    print("\n[Agent Statistics]")
    stats = agent.get_stats()
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
