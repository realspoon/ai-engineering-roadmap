# Week 8: RAG 심화와 평가

## 🎯 학습 목표

1. 고급 Retrieval 전략 학습
2. RAG 시스템 평가 방법론
3. Hybrid Search 구현
4. 월 2 통합 프로젝트: Q&A 챗봇

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [RAG-Driven Generative AI](https://www.oreilly.com/library/view/rag-driven-generative-ai/9781836200918/) | Denis Rothman | Chapter 5-8 |
| 📚 Book | [A Simple Guide to Retrieval Augmented Generation](https://learning.oreilly.com/library/view/-/9781633435858/) | Rani Horev | Chapter 4-6 |

---

## 📖 핵심 개념

### 1. 고급 Retrieval 전략

| 전략 | 설명 | 장점 |
|------|------|------|
| **Multi-Query** | 질문을 여러 버전으로 변환 | 검색 범위 확대 |
| **Self-Query** | 메타데이터 필터 자동 생성 | 정밀한 필터링 |
| **Parent Document** | 작은 청크 검색 → 큰 문서 반환 | 컨텍스트 보존 |
| **Ensemble** | 여러 검색기 결과 결합 | 정확도 향상 |

### 2. Hybrid Search

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# 키워드 기반 검색 (BM25)
bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 4

# 의미 기반 검색 (Vector)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# 앙상블 (Hybrid)
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.4, 0.6]  # BM25 40%, Vector 60%
)
```

### 3. RAG 평가 지표

| 지표 | 설명 | 측정 방법 |
|------|------|----------|
| **Faithfulness** | 답변이 컨텍스트에 충실한가 | LLM 판정 |
| **Answer Relevance** | 답변이 질문에 관련되는가 | LLM 판정 |
| **Context Relevance** | 검색된 문서가 관련되는가 | LLM 판정 |
| **Context Recall** | 정답에 필요한 정보가 검색되었나 | Ground Truth 비교 |

### 4. RAGAS 평가 프레임워크

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

# 평가 데이터셋 준비
eval_dataset = {
    "question": questions,
    "answer": answers,
    "contexts": contexts,
    "ground_truths": ground_truths
}

# 평가 실행
result = evaluate(
    dataset=eval_dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
)
print(result)
```

---

## 💻 실습 과제

### 과제 1: Multi-Query Retriever 구현

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm
)
```

### 과제 2: RAG 평가 파이프라인

[샘플 코드 → week08_rag_evaluation.py](./samples/week08_rag_evaluation.py)

### 과제 3: 🎯 월 2 통합 프로젝트 - 회사 문서 Q&A 챗봇

**요구사항:**
- 회사 문서 (PDF, TXT) 인덱싱
- 자연어 질의응답
- 출처 표시
- 대화 히스토리 유지
- 답변 품질 평가

**산출물:**
- 동작하는 Q&A 챗봇
- 평가 리포트 (RAGAS 점수)

---

## ✅ 주간 체크포인트

```
□ Multi-Query Retriever 구현 가능
□ Hybrid Search 구현 가능
□ RAGAS로 RAG 시스템 평가 가능
□ RAG 평가 4가지 지표 설명 가능
□ 월 2 통합 프로젝트 완성
```

---

## 🏆 Phase 1 완료!

Phase 1을 완료하셨습니다! 다음을 달성했습니다:
- LLM API 활용 능력
- Prompt Engineering 기법
- LangChain 기본 활용
- RAG 시스템 구축 및 평가

[Phase 2로 이동 →](../phase2_intermediate/README.md)

---

[← Week 7](./week07_rag_basics.md) | [Phase 2 →](../phase2_intermediate/README.md)
