# Week 7: RAG (Retrieval-Augmented Generation) 기초

## 🎯 학습 목표

1. RAG 아키텍처와 필요성 이해
2. Embedding과 Vector Database 개념 습득
3. 문서 로딩 → 청킹 → 임베딩 파이프라인 구축
4. 기본 RAG 시스템 구현

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [RAG-Driven Generative AI](https://www.oreilly.com/library/view/rag-driven-generative-ai/9781836200918/) | Denis Rothman | Chapter 1-4 |
| 📚 Book | [Unlocking Data with Generative AI and RAG](https://www.oreilly.com/library/view/unlocking-data-with/9781835887905/) | Kelby Zorgdrager | Chapter 1-5 |
| 🎬 Video | [Practical Retrieval Augmented Generation (RAG)](https://www.oreilly.com/library/view/practical-retrieval-augmented/9780135414378/) | Sinan Ozdemir | Part 1-2 |

---

## 📖 핵심 개념

### 1. RAG가 필요한 이유

| 문제 | RAG의 해결 |
|------|-----------|
| **할루시네이션** | 외부 문서 기반 답변으로 정확도 향상 |
| **지식 한계** | 최신 정보, 도메인 지식 주입 가능 |
| **프라이버시** | 내부 문서를 안전하게 활용 |
| **비용** | Fine-tuning 없이 지식 확장 |

### 2. RAG 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      RAG 파이프라인                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Indexing Phase - 오프라인]                                 │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ Document │ → │  Text    │ → │ Chunking │ → │ Embedding│ │
│  │ Loading  │   │ Extract  │   │          │   │          │ │
│  └──────────┘   └──────────┘   └──────────┘   └────┬─────┘ │
│                                                     │       │
│                                               ┌─────▼─────┐ │
│                                               │  Vector   │ │
│                                               │   Store   │ │
│                                               └─────┬─────┘ │
│                                                     │       │
│  [Query Phase - 온라인]                              │       │
│                                                     │       │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐        │       │
│  │  User    │ → │  Query   │ → │ Semantic │ ───────┘       │
│  │  Query   │   │ Embedding│   │  Search  │                │
│  └──────────┘   └──────────┘   └────┬─────┘                │
│                                      │                      │
│                               ┌──────▼──────┐              │
│                               │  Retrieved  │              │
│                               │   Context   │              │
│                               └──────┬──────┘              │
│                                      │                      │
│  ┌──────────┐   ┌──────────┐   ┌────▼─────┐               │
│  │ Response │ ← │   LLM    │ ← │  Prompt  │               │
│  │          │   │          │   │ + Context│               │
│  └──────────┘   └──────────┘   └──────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. 핵심 컴포넌트

| 컴포넌트 | 역할 | 예시 |
|----------|------|------|
| **Document Loader** | 다양한 형식의 문서 로딩 | PDF, DOCX, HTML, CSV |
| **Text Splitter** | 문서를 청크로 분할 | RecursiveCharacterTextSplitter |
| **Embedding Model** | 텍스트를 벡터로 변환 | OpenAI, Cohere, HuggingFace |
| **Vector Store** | 벡터 저장 및 검색 | Chroma, Pinecone, Weaviate |
| **Retriever** | 관련 문서 검색 | Similarity, MMR |

### 4. 청킹 전략

```python
# 1. 고정 크기 청킹
chunks = split_by_characters(text, chunk_size=1000, overlap=200)

# 2. 의미 기반 청킹
chunks = split_by_sentences(text, max_sentences=5)

# 3. 구조 기반 청킹
chunks = split_by_headers(text)  # 마크다운 헤더 기준
```

---

## 💻 실습 과제

### 과제 1: 환경 설정

```bash
pip install langchain langchain-openai langchain-community
pip install chromadb sentence-transformers
pip install pypdf docx2txt unstructured
```

### 과제 2: Document Loader 실습

```python
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader
)

# PDF 로딩
pdf_loader = PyPDFLoader("document.pdf")
pages = pdf_loader.load()

# 텍스트 파일 로딩
text_loader = TextLoader("document.txt")
docs = text_loader.load()
```

### 과제 3: RAG 파이프라인 구축

[샘플 코드 → week07_rag_pipeline.py](./samples/week07_rag_pipeline.py)

### 과제 4: Vector Store 비교

| Vector Store | 특징 | 사용 시점 |
|--------------|------|----------|
| **Chroma** | 로컬, 간편한 설정 | 프로토타입, 소규모 |
| **Pinecone** | 클라우드, 확장성 | 프로덕션, 대규모 |
| **Weaviate** | 하이브리드 검색 | 복잡한 쿼리 필요 |
| **FAISS** | 빠른 속도, 로컬 | 대량 벡터, 오프라인 |

---

## 📝 주요 패턴

### 패턴 1: 기본 RAG

```python
# 1. 인덱싱
vectorstore = Chroma.from_documents(docs, embedding)

# 2. 검색 + 생성
retriever = vectorstore.as_retriever(k=4)
chain = create_retrieval_chain(retriever, qa_chain)
```

### 패턴 2: Contextual Compression

```python
# 검색 결과를 압축하여 관련 부분만 추출
compressor = LLMChainExtractor.from_llm(llm)
retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)
```

### 패턴 3: Multi-Query Retriever

```python
# 하나의 질문을 여러 관점으로 변환하여 검색
retriever = MultiQueryRetriever.from_llm(
    retriever=base_retriever,
    llm=llm
)
```

---

## ✅ 주간 체크포인트

```
□ RAG가 필요한 이유와 장점 설명 가능
□ Embedding의 개념과 작동 원리 이해
□ Vector Similarity Search 개념 이해
□ 기본 RAG 파이프라인 독립 구축 가능
□ 다양한 청킹 전략의 장단점 비교 가능
```

---

## 🔗 추가 리소스

- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Pinecone Learning Center](https://www.pinecone.io/learn/)

---

[← Week 6](./week06_langchain_memory.md) | [Week 8 →](./week08_rag_advanced.md)
