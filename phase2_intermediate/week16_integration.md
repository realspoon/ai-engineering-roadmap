# Week 16: 통합 프로젝트 - RAG Assistant

## 🎯 학습 목표

1. RAG 아키텍처 완전히 이해
2. 전체 시스템 통합
3. 프로덕션 수준의 구현
4. 실제 배포 및 운영

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Building Applications with AI Agents](https://www.oreilly.com/library/view/building-applications-with/9781098176495/) | Mariusz Skoneczko | Chapter 1-12 (종합) |
| 📚 Book | [Learning LangChain](https://www.oreilly.com/library/view/learning-langchain/9781098167271/) | Mayo Oshin | Chapter 1-12 (종합) |

---

## 📖 핵심 개념

### 1. RAG Assistant 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Assistant                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           User Interface Layer                       │  │
│  │  - Chat UI / API Gateway / Voice Input             │  │
│  └───────────────────┬────────────────────────────────┘  │
│                      │                                    │
│  ┌──────────────────▼────────────────────────────────┐  │
│  │         Orchestration Layer (LangGraph)           │  │
│  │  - ReAct Agent                                     │  │
│  │  - Multi-Agent Coordination                        │  │
│  │  - State Management                                │  │
│  └──────┬──────────────────────────────┬──────────────┘  │
│         │                              │                 │
│  ┌──────▼──────┐            ┌──────────▼────────┐        │
│  │ Retrieval   │            │ Generation        │        │
│  │ Pipeline    │            │ Pipeline          │        │
│  │             │            │                   │        │
│  │ 1. Query    │            │ 1. Prompt Build  │        │
│  │    Encode   │            │ 2. LLM Call      │        │
│  │ 2. Vector   │            │ 3. Post-Process  │        │
│  │    Search   │            │                   │        │
│  │ 3. Rerank   │            │                   │        │
│  └──────┬──────┘            └─────────┬────────┘        │
│         │                              │                 │
│  ┌──────▼──────────────────────────────▼────────┐       │
│  │         Data Layer                           │       │
│  │  - Vector DB (Pinecone/Weaviate)            │       │
│  │  - Document Storage (S3/PostgreSQL)         │       │
│  │  - Cache (Redis)                            │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────────┘
```

### 2. 전체 구현 계획

**Phase 1: 기본 RAG 파이프라인**

```python
# 1. 문서 수집 및 전처리
documents = load_documents(document_paths)
chunks = chunk_documents(documents, chunk_size=512)
embeddings = generate_embeddings(chunks)

# 2. 벡터 데이터베이스 구성
vector_db = VectorDB()
vector_db.index(chunks, embeddings)

# 3. 검색 및 검증
query = "사용자 질문"
retrieved_docs = vector_db.search(query, top_k=5)
reranked_docs = rerank(retrieved_docs, query)

# 4. 응답 생성
context = format_context(reranked_docs)
response = llm.generate(query, context)
```

**Phase 2: Agent 레이어 추가**

```python
# ReAct Agent 구현
class RAGAgent:
    def __init__(self, tools: list):
        self.tools = {tool.name: tool for tool in tools}
        self.llm = initialize_llm()

    async def invoke(self, query: str) -> str:
        thoughts = []
        actions = []
        observations = []

        for step in range(MAX_STEPS):
            # Thought: 현재 상황 분석
            thought = await self.think(
                query, actions, observations
            )
            thoughts.append(thought)

            # Action: 다음 행동 결정
            action = await self.decide_action(thought)
            actions.append(action)

            # Observation: 행동 실행
            if action.type == "search":
                obs = await self.search(action.query)
            elif action.type == "generate":
                obs = await self.generate(action.prompt)
            else:
                obs = "Unknown action"

            observations.append(obs)

            # Final answer 확인
            if action.type == "final_answer":
                return action.answer

        return "Unable to answer"
```

**Phase 3: 배포 및 모니터링**

```python
# FastAPI 애플리케이션
app = FastAPI()

@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    # 로깅 및 모니터링
    request_id = generate_request_id()
    logger.info(f"[{request_id}] 새 요청", extra={
        "user_id": request.user_id,
        "query": request.query
    })

    try:
        # RAG Assistant 호출
        response = await rag_assistant.invoke(
            request.query,
            context={"user_id": request.user_id}
        )

        logger.info(f"[{request_id}] 성공 응답")

        return ChatResponse(
            answer=response,
            request_id=request_id
        )

    except Exception as e:
        logger.error(f"[{request_id}] 에러 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="처리 오류")
```

### 3. 핵심 컴포넌트 구현

**Component 1: Document Processor**

```python
from typing import List
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def load_and_process(self, file_paths: List[str]) -> List[dict]:
        """문서 로드 및 청킹"""
        documents = []

        for path in file_paths:
            loader = PyPDFLoader(path)
            docs = loader.load()

            chunks = self.text_splitter.split_documents(docs)
            documents.extend(chunks)

        return documents

    def clean_and_validate(self, documents: List[dict]) -> List[dict]:
        """문서 정제 및 검증"""
        cleaned = []

        for doc in documents:
            # 정제
            text = doc.page_content.strip()
            text = " ".join(text.split())  # 공백 정규화

            # 검증
            if len(text) > 10:  # 최소 길이
                cleaned.append({
                    **doc,
                    "page_content": text
                })

        return cleaned
```

**Component 2: Retrieval Pipeline**

```python
from sentence_transformers import SentenceTransformer

class RetrievalPipeline:
    def __init__(self, vector_db, reranker=None):
        self.vector_db = vector_db
        self.reranker = reranker
        self.embedder = SentenceTransformer(
            'sentence-transformers/multilingual-mpnet-base-v2'
        )

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        rerank_top_k: int = 5
    ) -> List[dict]:
        """쿼리에 맞는 문서 검색"""

        # 1단계: 벡터 검색
        query_embedding = self.embedder.encode(query)
        initial_results = await self.vector_db.search(
            query_embedding,
            top_k=top_k
        )

        # 2단계: Reranking
        if self.reranker:
            reranked = await self.reranker.rerank(
                query,
                initial_results,
                top_k=rerank_top_k
            )
            return reranked

        return initial_results[:rerank_top_k]

    def format_context(self, documents: List[dict]) -> str:
        """검색된 문서를 프롬프트용 컨텍스트로 포맷"""
        context_parts = []

        for i, doc in enumerate(documents, 1):
            context_parts.append(
                f"[문서 {i}]\n"
                f"{doc['page_content']}\n"
            )

        return "\n".join(context_parts)
```

**Component 3: Response Generation**

```python
class ResponseGenerator:
    def __init__(self, llm, template: str = None):
        self.llm = llm
        self.template = template or self.default_template()

    def default_template(self) -> str:
        return """당신은 도움이 되는 어시스턴트입니다.
주어진 문맥을 기반으로 사용자의 질문에 답변하세요.

문맥:
{context}

질문: {question}

답변:"""

    async def generate(
        self,
        query: str,
        context: str,
        **kwargs
    ) -> str:
        """쿼리와 컨텍스트를 기반으로 응답 생성"""

        prompt = self.template.format(
            context=context,
            question=query
        )

        response = await self.llm.agenerate(prompt)

        # 후처리
        cleaned = response.strip()
        cleaned = self.remove_citations_if_needed(cleaned)

        return cleaned

    def remove_citations_if_needed(self, text: str) -> str:
        """원하면 인용 제거"""
        import re
        return re.sub(r'\[\d+\]', '', text)
```

### 4. 품질 보증 파이프라인

```python
class QualityAssurance:
    def __init__(self):
        self.metrics = {}

    async def evaluate_response(
        self,
        query: str,
        response: str,
        context: str
    ) -> dict:
        """응답 품질 평가"""

        scores = {}

        # 1. Relevance 점수
        scores['relevance'] = await self.score_relevance(
            query, response
        )

        # 2. Coherence 점수
        scores['coherence'] = await self.score_coherence(
            response
        )

        # 3. Factuality 점수
        scores['factuality'] = await self.score_factuality(
            response, context
        )

        # 4. 종합 점수
        scores['overall'] = sum(scores.values()) / len(scores)

        return scores

    async def should_flag_response(self, scores: dict) -> bool:
        """응답을 검토 대상으로 표시할지 판단"""
        return scores['overall'] < 0.6  # 60% 미만이면 검토 필요
```

---

## 💻 통합 프로젝트: RAG Assistant 전체 구현

### 요구사항

```
1. 시스템 설계 및 구현
   ✓ 문서 처리 파이프라인
   ✓ 검색 파이프라인
   ✓ 생성 파이프라인
   ✓ Agent 레이어

2. API 개발 (FastAPI)
   ✓ 채팅 엔드포인트
   ✓ 문서 업로드 엔드포인트
   ✓ 히스토리 조회 엔드포인트
   ✓ 헬스 체크

3. 배포
   ✓ Docker 컨테이너화
   ✓ docker-compose 구성
   ✓ 로깅 및 모니터링

4. 테스트 및 평가
   ✓ 단위 테스트
   ✓ 통합 테스트
   ✓ 성능 테스트
   ✓ 품질 평가

5. 문서화
   ✓ 아키텍처 문서
   ✓ API 문서
   ✓ 배포 가이드
   ✓ 운영 매뉴얼
```

### 최종 프로젝트 구조

```
rag-assistant/
├── src/
│   ├── main.py                 # FastAPI 애플리케이션
│   ├── models/
│   │   ├── request.py         # 요청 모델
│   │   └── response.py        # 응답 모델
│   ├── pipelines/
│   │   ├── document_processor.py
│   │   ├── retrieval.py
│   │   └── generation.py
│   ├── agents/
│   │   └── rag_agent.py
│   ├── utils/
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── cache.py
│   └── config.py
├── tests/
│   ├── test_pipelines.py
│   ├── test_agents.py
│   └── test_api.py
├── data/
│   └── documents/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### 핵심 파일 구현 예시

**main.py**

```python
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from src.pipelines import DocumentProcessor, RetrievalPipeline, ResponseGenerator
from src.agents import RAGAgent
from src.utils import logger, metrics

app = FastAPI(title="RAG Assistant", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 초기화
doc_processor = DocumentProcessor()
retrieval_pipeline = RetrievalPipeline(vector_db)
response_gen = ResponseGenerator(llm)
rag_agent = RAGAgent([retrieval_pipeline, response_gen])

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """채팅 엔드포인트"""
    try:
        response = await rag_agent.invoke(request.query)
        metrics.record_success()
        return ChatResponse(answer=response)
    except Exception as e:
        logger.error(str(e))
        metrics.record_error()
        raise

@app.post("/api/documents")
async def upload_document(file: UploadFile):
    """문서 업로드 엔드포인트"""
    # 구현
    pass

@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## ✅ 최종 체크포인트

```
프로젝트 완성도:
□ 전체 RAG 아키텍처 이해 및 설명 가능
□ 문서 처리 파이프라인 완전 구현
□ 검색 파이프라인 (벡터 검색 + Reranking) 구현
□ 생성 파이프라인 구현
□ ReAct Agent 통합
□ FastAPI REST API 완성
□ Docker 배포 준비 완료
□ 종합 테스트 (Unit/Integration/Performance) 완료
□ 모니터링 및 로깅 시스템 구축
□ 프로덕션 수준의 코드 품질

학습 목표 달성도:
□ LLM 애플리케이션 개발의 전체 사이클 이해
□ 아키텍처 설계 및 구현 능력
□ 프로덕션 배포 및 운영 능력
□ 성능 최적화 및 비용 관리 능력
□ 품질 보증 및 모니터링 능력
```

---

## 🔗 추가 학습 자료

- [LangChain RAG Examples](https://github.com/langchain-ai/langchain/tree/master/templates)
- [RAG Best Practices](https://docs.langchain.com/docs/modules/data_connection/)
- [Production RAG Systems](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/)
- [Multi-Agent Orchestration](https://langchain-ai.github.io/langgraph/tutorials/#multi-agent-systems)

---

## 🎓 Phase 2 완료

**다음 단계:**
- Phase 3: Advanced Topics (Fine-tuning, Custom Models)
- 실제 프로덕션 프로젝트 적용
- 커뮤니티 기여 및 오픈소스 참여
- 심화 과정 선택 (특정 도메인/기술 심화)

축하합니다! Phase 2를 완료하셨습니다. 이제 LLM 기반 애플리케이션을 설계, 구현, 배포할 수 있는 역량을 갖추셨습니다.

---

[← Week 15](./week15_deployment.md)
