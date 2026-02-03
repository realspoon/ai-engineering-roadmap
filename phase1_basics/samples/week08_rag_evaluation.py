"""
Week 8: RAG 평가, Multi-Query Retriever, Hybrid Search
========================================================

이 모듈은 RAG(Retrieval-Augmented Generation) 시스템의 평가 및 고급 검색 기법을 보여줍니다:
- RAGAS (RAG Assessment) 메트릭
- Multi-Query Retriever
- Hybrid Search (키워드 + 의미론적)
- 검색 성능 측정
- 평가 결과 분석
"""

import json
import time
import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod


class RetrievalMetric(Enum):
    """검색 메트릭"""
    PRECISION = "precision"  # 관련성 있는 문서 비율
    RECALL = "recall"  # 검색된 관련 문서 비율
    F1_SCORE = "f1_score"  # Precision과 Recall의 조화평균
    MRR = "mrr"  # Mean Reciprocal Rank
    NDCG = "ndcg"  # Normalized Discounted Cumulative Gain


@dataclass
class Document:
    """문서 객체"""
    id: str
    content: str
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """검색 결과"""
    document: Document
    score: float  # 0~1 사이의 점수
    rank: int


@dataclass
class QueryContext:
    """쿼리 컨텍스트"""
    query: str
    relevant_doc_ids: List[str]  # 정답 문서 ID 리스트


@dataclass
class RAGEvaluation:
    """RAG 평가 결과"""
    query: str
    retrieved_docs: List[Document]
    metrics: Dict[str, float]
    explanation: str


class DocumentStore:
    """
    문서 저장소입니다.
    검색 대상이 되는 문서들을 관리합니다.
    """

    def __init__(self):
        """DocumentStore 초기화"""
        self.documents: Dict[str, Document] = {}
        self.document_embeddings: Dict[str, List[float]] = {}

    def add_document(self, doc: Document) -> None:
        """
        문서 추가

        Args:
            doc (Document): 추가할 문서
        """
        self.documents[doc.id] = doc
        # 간단한 임베딩 시뮬레이션
        self.document_embeddings[doc.id] = self._simulate_embedding(doc.content)

    def add_documents(self, docs: List[Document]) -> None:
        """
        여러 문서 추가

        Args:
            docs (List[Document]): 추가할 문서 리스트
        """
        for doc in docs:
            self.add_document(doc)

    def _simulate_embedding(self, text: str) -> List[float]:
        """
        텍스트 임베딩을 시뮬레이션합니다.
        실제로는 BERT, OpenAI 등의 임베딩 모델을 사용합니다.

        Args:
            text (str): 텍스트

        Returns:
            List[float]: 임베딩 벡터 (간단한 예제용)
        """
        words = text.split()
        # 간단한 해시 기반 벡터 생성
        vector = [float(hash(word) % 100) / 100 for word in words[:10]]
        # 길이 고정 (10차원)
        while len(vector) < 10:
            vector.append(0.0)
        return vector[:10]

    def get_document(self, doc_id: str) -> Optional[Document]:
        """
        문서 조회

        Args:
            doc_id (str): 문서 ID

        Returns:
            Optional[Document]: 문서 객체
        """
        return self.documents.get(doc_id)

    def list_all_documents(self) -> List[Document]:
        """
        모든 문서 반환

        Returns:
            List[Document]: 문서 리스트
        """
        return list(self.documents.values())


class BaseRetriever(ABC):
    """검색기의 기본 클래스"""

    def __init__(self, document_store: DocumentStore):
        """
        BaseRetriever 초기화

        Args:
            document_store (DocumentStore): 문서 저장소
        """
        self.document_store = document_store

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        문서 검색

        Args:
            query (str): 쿼리
            top_k (int): 반환할 문서 개수

        Returns:
            List[SearchResult]: 검색 결과
        """
        pass


class KeywordRetriever(BaseRetriever):
    """
    키워드 기반 검색기입니다.
    쿼리 키워드와 문서의 겹침 정도로 점수를 매깁니다.
    """

    def retrieve(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        키워드 기반 검색 수행

        Args:
            query (str): 쿼리
            top_k (int): 반환할 문서 개수

        Returns:
            List[SearchResult]: 검색 결과
        """
        query_words = set(query.lower().split())
        results = []

        for doc in self.document_store.list_all_documents():
            doc_words = set(doc.content.lower().split())
            # Jaccard 유사도 계산
            intersection = len(query_words & doc_words)
            union = len(query_words | doc_words)
            score = intersection / union if union > 0 else 0.0

            if score > 0:
                results.append(SearchResult(
                    document=doc,
                    score=score,
                    rank=0
                ))

        # 점수 기준 정렬
        results.sort(key=lambda x: x.score, reverse=True)

        # 순위 할당
        for i, result in enumerate(results[:top_k]):
            result.rank = i + 1

        return results[:top_k]


class SemanticRetriever(BaseRetriever):
    """
    의미론적 검색기입니다.
    임베딩 벡터의 유사도를 기반으로 검색합니다.
    """

    def retrieve(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        의미론적 검색 수행

        Args:
            query (str): 쿼리
            top_k (int): 반환할 문서 개수

        Returns:
            List[SearchResult]: 검색 결과
        """
        query_embedding = self.document_store._simulate_embedding(query)
        results = []

        for doc in self.document_store.list_all_documents():
            doc_embedding = self.document_store.document_embeddings.get(doc.id, [])
            # 코사인 유사도 계산
            score = self._cosine_similarity(query_embedding, doc_embedding)

            if score > 0:
                results.append(SearchResult(
                    document=doc,
                    score=score,
                    rank=0
                ))

        # 점수 기준 정렬
        results.sort(key=lambda x: x.score, reverse=True)

        # 순위 할당
        for i, result in enumerate(results[:top_k]):
            result.rank = i + 1

        return results[:top_k]

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        코사인 유사도 계산

        Args:
            vec1 (List[float]): 벡터 1
            vec2 (List[float]): 벡터 2

        Returns:
            float: 유사도 (0~1)
        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)


class HybridRetriever(BaseRetriever):
    """
    하이브리드 검색기입니다.
    키워드 검색과 의미론적 검색을 결합합니다.
    """

    def __init__(
        self,
        document_store: DocumentStore,
        keyword_weight: float = 0.5,
        semantic_weight: float = 0.5,
    ):
        """
        HybridRetriever 초기화

        Args:
            document_store (DocumentStore): 문서 저장소
            keyword_weight (float): 키워드 검색 가중치
            semantic_weight (float): 의미론적 검색 가중치
        """
        super().__init__(document_store)
        self.keyword_retriever = KeywordRetriever(document_store)
        self.semantic_retriever = SemanticRetriever(document_store)
        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight

    def retrieve(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        하이브리드 검색 수행

        Args:
            query (str): 쿼리
            top_k (int): 반환할 문서 개수

        Returns:
            List[SearchResult]: 검색 결과
        """
        # 각 검색기에서 결과 획득
        keyword_results = self.keyword_retriever.retrieve(query, top_k=top_k)
        semantic_results = self.semantic_retriever.retrieve(query, top_k=top_k)

        # 점수 정규화 및 가중 합산
        combined_scores: Dict[str, float] = {}

        for result in keyword_results:
            combined_scores[result.document.id] = (
                self.keyword_weight * result.score
            )

        for result in semantic_results:
            doc_id = result.document.id
            if doc_id in combined_scores:
                combined_scores[doc_id] += self.semantic_weight * result.score
            else:
                combined_scores[doc_id] = self.semantic_weight * result.score

        # 합산 점수로 정렬
        sorted_docs = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        results = []
        for i, (doc_id, score) in enumerate(sorted_docs[:top_k]):
            doc = self.document_store.get_document(doc_id)
            if doc:
                results.append(SearchResult(
                    document=doc,
                    score=score,
                    rank=i + 1
                ))

        return results


class MultiQueryRetriever(BaseRetriever):
    """
    다중 쿼리 검색기입니다.
    원본 쿼리를 여러 형태로 변환한 후 검색을 수행합니다.
    """

    def __init__(self, document_store: DocumentStore):
        """
        MultiQueryRetriever 초기화

        Args:
            document_store (DocumentStore): 문서 저장소
        """
        super().__init__(document_store)
        self.base_retriever = HybridRetriever(document_store)

    def _generate_alternative_queries(self, query: str) -> List[str]:
        """
        대체 쿼리 생성

        Args:
            query (str): 원본 쿼리

        Returns:
            List[str]: 대체 쿼리 리스트
        """
        queries = [query]

        # 쿼리 변형 1: 동의어 기반
        synonym_map = {
            "빠른": "신속한",
            "좋은": "우수한",
            "배우다": "학습하다",
        }

        modified_query = query
        for word, synonym in synonym_map.items():
            if word in modified_query:
                modified_query = modified_query.replace(word, synonym)
        if modified_query != query:
            queries.append(modified_query)

        # 쿼리 변형 2: 역순
        words = query.split()
        if len(words) > 1:
            reversed_query = " ".join(reversed(words))
            queries.append(reversed_query)

        # 쿼리 변형 3: 질문 형태
        question_query = f"{query}는 무엇인가?"
        queries.append(question_query)

        return queries

    def retrieve(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        다중 쿼리 검색 수행

        Args:
            query (str): 쿼리
            top_k (int): 반환할 문서 개수

        Returns:
            List[SearchResult]: 검색 결과
        """
        # 대체 쿼리 생성
        alternative_queries = self._generate_alternative_queries(query)

        print(f"\n🔍 다중 쿼리 검색:")
        print(f"  원본 쿼리: {query}")
        print(f"  대체 쿼리:")
        for q in alternative_queries[1:]:
            print(f"    - {q}")

        # 각 쿼리로 검색 수행
        combined_results: Dict[str, SearchResult] = {}

        for q in alternative_queries:
            results = self.base_retriever.retrieve(q, top_k=top_k)
            for result in results:
                doc_id = result.document.id
                if doc_id in combined_results:
                    # 기존 결과의 점수 증가
                    combined_results[doc_id].score += result.score
                else:
                    combined_results[doc_id] = result

        # 합산 점수로 정렬
        final_results = sorted(
            combined_results.values(),
            key=lambda x: x.score,
            reverse=True
        )

        # 순위 재할당
        for i, result in enumerate(final_results[:top_k]):
            result.rank = i + 1

        return final_results[:top_k]


class RAGASEvaluator:
    """
    RAGAS (RAG Assessment) 평가기입니다.
    RAG 시스템의 성능을 측정합니다.
    """

    def __init__(self, retriever: BaseRetriever):
        """
        RAGASEvaluator 초기화

        Args:
            retriever (BaseRetriever): 검색기
        """
        self.retriever = retriever

    def calculate_precision(
        self,
        retrieved_doc_ids: List[str],
        relevant_doc_ids: List[str],
    ) -> float:
        """
        Precision 계산: 검색된 문서 중 관련성 있는 문서의 비율

        Args:
            retrieved_doc_ids (List[str]): 검색된 문서 ID
            relevant_doc_ids (List[str]): 관련성 있는 문서 ID

        Returns:
            float: Precision 값 (0~1)
        """
        if not retrieved_doc_ids:
            return 0.0

        relevant_set = set(relevant_doc_ids)
        retrieved_set = set(retrieved_doc_ids)
        intersection = len(retrieved_set & relevant_set)

        return intersection / len(retrieved_doc_ids)

    def calculate_recall(
        self,
        retrieved_doc_ids: List[str],
        relevant_doc_ids: List[str],
    ) -> float:
        """
        Recall 계산: 관련성 있는 문서 중 검색된 문서의 비율

        Args:
            retrieved_doc_ids (List[str]): 검색된 문서 ID
            relevant_doc_ids (List[str]): 관련성 있는 문서 ID

        Returns:
            float: Recall 값 (0~1)
        """
        if not relevant_doc_ids:
            return 0.0

        relevant_set = set(relevant_doc_ids)
        retrieved_set = set(retrieved_doc_ids)
        intersection = len(retrieved_set & relevant_set)

        return intersection / len(relevant_doc_ids)

    def calculate_f1_score(
        self,
        precision: float,
        recall: float,
    ) -> float:
        """
        F1 Score 계산

        Args:
            precision (float): Precision 값
            recall (float): Recall 값

        Returns:
            float: F1 Score (0~1)
        """
        if precision + recall == 0:
            return 0.0

        return 2 * (precision * recall) / (precision + recall)

    def calculate_mrr(
        self,
        retrieved_doc_ids: List[str],
        relevant_doc_ids: List[str],
    ) -> float:
        """
        MRR (Mean Reciprocal Rank) 계산

        Args:
            retrieved_doc_ids (List[str]): 검색된 문서 ID (순서 있음)
            relevant_doc_ids (List[str]): 관련성 있는 문서 ID

        Returns:
            float: MRR 값 (0~1)
        """
        relevant_set = set(relevant_doc_ids)

        for i, doc_id in enumerate(retrieved_doc_ids):
            if doc_id in relevant_set:
                return 1.0 / (i + 1)

        return 0.0

    def calculate_ndcg(
        self,
        search_results: List[SearchResult],
        relevant_doc_ids: List[str],
    ) -> float:
        """
        NDCG (Normalized Discounted Cumulative Gain) 계산

        Args:
            search_results (List[SearchResult]): 검색 결과
            relevant_doc_ids (List[str]): 관련성 있는 문서 ID

        Returns:
            float: NDCG 값 (0~1)
        """
        relevant_set = set(relevant_doc_ids)

        # DCG 계산
        dcg = 0.0
        for i, result in enumerate(search_results):
            relevance = 1.0 if result.document.id in relevant_set else 0.0
            dcg += relevance / math.log2(i + 2)

        # IDCG 계산 (이상적인 순서)
        num_relevant = len(relevant_set)
        idcg = 0.0
        for i in range(min(num_relevant, len(search_results))):
            idcg += 1.0 / math.log2(i + 2)

        # NDCG 계산
        if idcg == 0:
            return 0.0

        return dcg / idcg

    def evaluate(
        self,
        query: str,
        relevant_doc_ids: List[str],
        top_k: int = 5,
    ) -> RAGEvaluation:
        """
        RAG 시스템 평가

        Args:
            query (str): 쿼리
            relevant_doc_ids (List[str]): 관련성 있는 문서 ID
            top_k (int): 평가할 상위 문서 개수

        Returns:
            RAGEvaluation: 평가 결과
        """
        # 검색 수행
        search_results = self.retriever.retrieve(query, top_k=top_k)
        retrieved_doc_ids = [r.document.id for r in search_results]

        # 메트릭 계산
        precision = self.calculate_precision(retrieved_doc_ids, relevant_doc_ids)
        recall = self.calculate_recall(retrieved_doc_ids, relevant_doc_ids)
        f1_score = self.calculate_f1_score(precision, recall)
        mrr = self.calculate_mrr(retrieved_doc_ids, relevant_doc_ids)
        ndcg = self.calculate_ndcg(search_results, relevant_doc_ids)

        metrics = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1_score, 3),
            "mrr": round(mrr, 3),
            "ndcg": round(ndcg, 3),
        }

        # 평가 설명
        retrieved_set = set(retrieved_doc_ids)
        relevant_set = set(relevant_doc_ids)
        correct = len(retrieved_set & relevant_set)

        explanation = (
            f"검색 결과: {len(search_results)}개 | "
            f"관련 문서: {correct}/{len(relevant_doc_ids)} "
            f"({metrics['recall']*100:.0f}% 찾음)"
        )

        return RAGEvaluation(
            query=query,
            retrieved_docs=search_results,
            metrics=metrics,
            explanation=explanation,
        )


def example_document_store():
    """DocumentStore 예제"""
    print("\n" + "=" * 70)
    print("예제 1: Document Store")
    print("=" * 70)

    store = DocumentStore()

    # 샘플 문서 추가
    docs = [
        Document(
            id="doc1",
            content="파이썬은 높은 수준의 프로그래밍 언어입니다.",
            source="wiki"
        ),
        Document(
            id="doc2",
            content="기계학습은 인공지능의 한 분야입니다.",
            source="textbook"
        ),
        Document(
            id="doc3",
            content="자연어처리는 텍스트 분석에 사용됩니다.",
            source="blog"
        ),
    ]

    store.add_documents(docs)

    print(f"\n✓ {len(store.list_all_documents())}개 문서 저장됨")
    for doc in store.list_all_documents():
        print(f"  - {doc.id}: {doc.content[:30]}...")


def example_keyword_retriever():
    """KeywordRetriever 예제"""
    print("\n" + "=" * 70)
    print("예제 2: Keyword Retriever")
    print("=" * 70)

    # 문서 저장소 준비
    store = DocumentStore()
    docs = [
        Document(id="doc1", content="파이썬 프로그래밍 언어"),
        Document(id="doc2", content="자바 프로그래밍 튜토리얼"),
        Document(id="doc3", content="파이썬 데이터 분석"),
        Document(id="doc4", content="웹 개발 가이드"),
    ]
    store.add_documents(docs)

    # 키워드 검색 수행
    retriever = KeywordRetriever(store)
    results = retriever.retrieve("파이썬 프로그래밍", top_k=3)

    print(f"\n🔍 검색어: '파이썬 프로그래밍'")
    print(f"{'─'*70}")
    for result in results:
        print(f"순위 {result.rank}: {result.document.content}")
        print(f"  점수: {result.score:.3f}")


def example_hybrid_retriever():
    """HybridRetriever 예제"""
    print("\n" + "=" * 70)
    print("예제 3: Hybrid Retriever")
    print("=" * 70)

    # 문서 저장소 준비
    store = DocumentStore()
    docs = [
        Document(id="doc1", content="기계학습은 데이터에서 패턴을 학습합니다"),
        Document(id="doc2", content="딥러닝은 신경망을 사용한 기계학습입니다"),
        Document(id="doc3", content="자연어처리는 언어 이해에 중점입니다"),
        Document(id="doc4", content="컴퓨터 비전은 이미지 분석에 사용됩니다"),
    ]
    store.add_documents(docs)

    # 하이브리드 검색 수행
    retriever = HybridRetriever(store, keyword_weight=0.4, semantic_weight=0.6)
    results = retriever.retrieve("기계학습 알고리즘", top_k=3)

    print(f"\n🔀 하이브리드 검색: '기계학습 알고리즘'")
    print(f"{'─'*70}")
    for result in results:
        print(f"순위 {result.rank}: {result.document.content}")
        print(f"  점수: {result.score:.3f}")


def example_multi_query_retriever():
    """MultiQueryRetriever 예제"""
    print("\n" + "=" * 70)
    print("예제 4: Multi-Query Retriever")
    print("=" * 70)

    # 문서 저장소 준비
    store = DocumentStore()
    docs = [
        Document(id="doc1", content="신속한 알고리즘 개발 방법"),
        Document(id="doc2", content="효율적인 코드 최적화 기법"),
        Document(id="doc3", content="성능 개선 전략"),
        Document(id="doc4", content="시스템 설계 원칙"),
    ]
    store.add_documents(docs)

    # 다중 쿼리 검색 수행
    retriever = MultiQueryRetriever(store)
    results = retriever.retrieve("빠른 개발", top_k=3)

    print(f"\n{'─'*70}")
    print(f"결과:")
    for result in results:
        print(f"순위 {result.rank}: {result.document.content}")
        print(f"  점수: {result.score:.3f}")


def example_ragas_evaluation():
    """RAGAS 평가 예제"""
    print("\n" + "=" * 70)
    print("예제 5: RAGAS 평가")
    print("=" * 70)

    # 문서 저장소 준비
    store = DocumentStore()
    docs = [
        Document(id="doc1", content="자연어처리 기초 개념"),
        Document(id="doc2", content="자연어처리 응용 기술"),
        Document(id="doc3", content="머신러닝 알고리즘"),
        Document(id="doc4", content="데이터 과학 입문"),
        Document(id="doc5", content="파이썬 프로그래밍"),
    ]
    store.add_documents(docs)

    # 평가기 준비
    retriever = HybridRetriever(store)
    evaluator = RAGASEvaluator(retriever)

    # 테스트 쿼리들
    test_queries = [
        ("자연어처리", ["doc1", "doc2"]),
        ("머신러닝", ["doc3"]),
        ("프로그래밍", ["doc5"]),
    ]

    print(f"\n{'─'*70}")
    results = []

    for query, relevant_docs in test_queries:
        evaluation = evaluator.evaluate(query, relevant_docs, top_k=3)
        results.append(evaluation)

        print(f"\n🎯 쿼리: '{query}'")
        print(f"  {evaluation.explanation}")
        print(f"  메트릭:")
        for metric, value in evaluation.metrics.items():
            print(f"    - {metric}: {value}")

    # 전체 요약
    print(f"\n{'─'*70}")
    print("📊 전체 평가 요약:")
    avg_metrics = {
        "precision": sum(r.metrics["precision"] for r in results) / len(results),
        "recall": sum(r.metrics["recall"] for r in results) / len(results),
        "f1_score": sum(r.metrics["f1_score"] for r in results) / len(results),
        "ndcg": sum(r.metrics["ndcg"] for r in results) / len(results),
    }

    for metric, value in avg_metrics.items():
        print(f"  평균 {metric}: {round(value, 3)}")


def example_retriever_comparison():
    """검색기 비교 예제"""
    print("\n" + "=" * 70)
    print("예제 6: 검색기 비교")
    print("=" * 70)

    # 문서 저장소 준비
    store = DocumentStore()
    docs = [
        Document(id="doc1", content="인공지능 개요"),
        Document(id="doc2", content="자연언어 처리 기초"),
        Document(id="doc3", content="컴퓨터 비전 응용"),
        Document(id="doc4", content="강화학습 알고리즘"),
    ]
    store.add_documents(docs)

    # 여러 검색기 비교
    query = "자연언어"
    top_k = 2

    print(f"\n🔍 검색어: '{query}'")
    print(f"{'─'*70}")

    # 1. 키워드 검색
    print("\n1️⃣ 키워드 검색 결과:")
    keyword_retriever = KeywordRetriever(store)
    keyword_results = keyword_retriever.retrieve(query, top_k=top_k)
    for result in keyword_results:
        print(f"  {result.document.content} (점수: {result.score:.3f})")

    # 2. 의미론적 검색
    print("\n2️⃣ 의미론적 검색 결과:")
    semantic_retriever = SemanticRetriever(store)
    semantic_results = semantic_retriever.retrieve(query, top_k=top_k)
    for result in semantic_results:
        print(f"  {result.document.content} (점수: {result.score:.3f})")

    # 3. 하이브리드 검색
    print("\n3️⃣ 하이브리드 검색 결과:")
    hybrid_retriever = HybridRetriever(store)
    hybrid_results = hybrid_retriever.retrieve(query, top_k=top_k)
    for result in hybrid_results:
        print(f"  {result.document.content} (점수: {result.score:.3f})")

    # 4. 다중 쿼리 검색
    print("\n4️⃣ 다중 쿼리 검색 결과:")
    multi_retriever = MultiQueryRetriever(store)
    multi_results = multi_retriever.retrieve(query, top_k=top_k)
    for result in multi_results:
        print(f"  {result.document.content} (점수: {result.score:.3f})")


if __name__ == "__main__":
    """메인 실행 영역"""

    print("\n" + "#" * 70)
    print("# Week 8: RAG 평가, Multi-Query Retriever, Hybrid Search")
    print("#" * 70)

    # 예제 1: DocumentStore
    example_document_store()

    # 예제 2: KeywordRetriever
    example_keyword_retriever()

    # 예제 3: HybridRetriever
    example_hybrid_retriever()

    # 예제 4: MultiQueryRetriever
    example_multi_query_retriever()

    # 예제 5: RAGAS 평가
    example_ragas_evaluation()

    # 예제 6: 검색기 비교
    example_retriever_comparison()

    print("\n" + "#" * 70)
    print("# 모든 예제 완료")
    print("#" * 70)
