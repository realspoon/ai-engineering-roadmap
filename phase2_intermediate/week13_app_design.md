# Week 13: LLM 애플리케이션 설계

## 🎯 학습 목표

1. LLM 애플리케이션 아키텍처 설계
2. 확장성과 성능 최적화
3. 비용 최적화 전략
4. 시스템 모니터링 설계

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Building Applications with AI Agents](https://www.oreilly.com/library/view/building-applications-with/9781098176495/) | Mariusz Skoneczko | Chapter 10-11 |
| 📚 Book | [Prompt Engineering for Generative AI](https://www.oreilly.com/library/view/prompt-engineering-for/9781098176532/) | James Phoenix, Mike Taylor | Chapter 1-3 |

---

## 📖 핵심 개념

### 1. LLM 애플리케이션 아키텍처

**전형적인 3계층 구조:**

```
┌─────────────────────────────────────────────────────┐
│              Presentation Layer                     │
│  (UI, API Gateway, ChatBot Interface)              │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│           Application Layer                         │
│  ┌──────────────────────────────────────────────┐   │
│  │ Application Logic                            │   │
│  │ - Request Processing                         │   │
│  │ - Context Management                         │   │
│  │ - LangGraph/LangChain Orchestration         │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │ Middleware                                   │   │
│  │ - Logging, Monitoring                        │   │
│  │ - Rate Limiting, Caching                     │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│            Infrastructure Layer                     │
│  ┌──────────────┐  ┌──────────────┐               │
│  │  LLM API     │  │  Vector DB   │               │
│  │  (OpenAI)    │  │  (Pinecone)  │               │
│  └──────────────┘  └──────────────┘               │
│  ┌──────────────┐  ┌──────────────┐               │
│  │  Cache Layer │  │  Observability              │
│  │  (Redis)     │  │  (DataDog)   │               │
│  └──────────────┘  └──────────────┘               │
└──────────────────────────────────────────────────────┘
```

### 2. 아키텍처 패턴

**패턴 1: Simple RAG**

```
User Query → Retrieval → LLM → Response
```

**패턴 2: Agent with Tools**

```
User Query → Agent → [Tool Selection]
                      ├→ Tool 1
                      ├→ Tool 2
                      └→ Tool 3
                           ↓
                    Result Synthesis → Response
```

**패턴 3: Multi-Agent Orchestration**

```
          User Request
                 │
          Orchestrator Agent
          │      │       │
     Research Analysis Writer
       Agent    Agent    Agent
          │      │       │
      Results Combine   Final Response
```

**패턴 4: Hybrid Search**

```
Query
  ├→ Keyword Search → Results
  ├→ Semantic Search → Results
  └→ Hybrid Ranking → Top-K Results → LLM
```

### 3. 확장성 설계

**수평 확장 (Horizontal Scaling):**

```python
# 로드 밸런싱 설정
from fastapi import FastAPI
from typing import Callable

app = FastAPI()

# 요청 큐 기반 처리
import asyncio
from queue import Queue

request_queue = Queue()

async def worker():
    while True:
        request = await asyncio.get_event_loop().run_in_executor(
            None, request_queue.get
        )
        result = await process_request(request)
        await send_response(result)

# 여러 워커 실행
for _ in range(4):  # 4개 워커
    asyncio.create_task(worker())
```

**수직 확장 (Vertical Scaling):**

```python
# 배치 처리로 효율성 증대
async def batch_process(requests: list[str]) -> list[str]:
    """
    여러 요청을 한 번에 처리
    """
    batch_size = 32

    results = []
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i + batch_size]

        # 배치 처리 (LLM API 효율성 증대)
        responses = await llm.batch(batch)
        results.extend(responses)

    return results
```

### 4. 비용 최적화

**전략 1: 모델 선택**

```python
# 비용 기반 모델 선택
LOW_COST_MODELS = {
    "simple_query": "gpt-3.5-turbo",  # $0.0005/1K tokens
    "complex_query": "gpt-4",          # $0.003/1K tokens
}

def select_model(query_complexity: str) -> str:
    if query_complexity == "simple":
        return LOW_COST_MODELS["simple_query"]
    else:
        return LOW_COST_MODELS["complex_query"]
```

**전략 2: 캐싱**

```python
import hashlib
from typing import Any

class ResponseCache:
    def __init__(self):
        self.cache = {}
        self.hit_count = 0
        self.miss_count = 0

    def get_key(self, prompt: str) -> str:
        """프롬프트의 해시 계산"""
        return hashlib.md5(prompt.encode()).hexdigest()

    def get(self, prompt: str) -> Any | None:
        key = self.get_key(prompt)
        if key in self.cache:
            self.hit_count += 1
            return self.cache[key]
        self.miss_count += 1
        return None

    def set(self, prompt: str, response: Any):
        key = self.get_key(prompt)
        self.cache[key] = response

    @property
    def hit_rate(self) -> float:
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0
```

**전략 3: 토큰 최적화**

```python
class TokenOptimizer:
    @staticmethod
    def compress_prompt(prompt: str, max_tokens: int = 4000) -> str:
        """긴 프롬프트 압축"""
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_tokens,
            chunk_overlap=200
        )
        chunks = splitter.split_text(prompt)
        # 가장 관련성 높은 청크만 선택
        return chunks[0]

    @staticmethod
    def estimate_cost(prompt: str, model: str) -> float:
        """토큰 기반 비용 추정"""
        token_count = len(prompt.split())  # 대략적 계산
        rates = {
            "gpt-3.5-turbo": 0.0005,  # 1K 토큰당 $0.0005
            "gpt-4": 0.003,
        }
        return (token_count / 1000) * rates.get(model, 0)
```

**전략 4: 배치 처리로 비용 절감**

```python
# 개별 요청 처리 (비효율적)
costs_individual = []
for query in queries:
    cost = estimate_cost(query, "gpt-4")
    costs_individual.append(cost)

total_individual = sum(costs_individual)

# 배치 처리 (효율적)
combined_query = "\n".join(queries)
total_batch = estimate_cost(combined_query, "gpt-4")

print(f"개별: ${total_individual:.4f}")
print(f"배치: ${total_batch:.4f}")
print(f"절감: {(total_individual - total_batch) / total_individual * 100:.1f}%")
```

### 5. 모니터링과 관찰성 (Observability)

```python
from datetime import datetime
import time

class ApplicationMetrics:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_latency = 0
        self.token_usage = 0

    def record_request(self, duration: float, tokens: int, success: bool):
        self.request_count += 1
        if not success:
            self.error_count += 1
        self.total_latency += duration
        self.token_usage += tokens

    @property
    def average_latency(self) -> float:
        return self.total_latency / self.request_count if self.request_count > 0 else 0

    @property
    def error_rate(self) -> float:
        return self.error_count / self.request_count if self.request_count > 0 else 0

    @property
    def cost_estimate(self, model: str = "gpt-4") -> float:
        # gpt-4: $0.03/1K input tokens, $0.06/1K output tokens
        return (self.token_usage / 1000) * 0.03

# 사용 예시
metrics = ApplicationMetrics()

start = time.time()
try:
    result = llm.invoke(prompt)
    duration = time.time() - start
    metrics.record_request(duration, token_count, success=True)
except Exception as e:
    duration = time.time() - start
    metrics.record_request(duration, 0, success=False)
```

---

## 💻 실습 과제

### 과제 1: 아키텍처 설계

**시나리오:** 멀티 테넌트 고객 지원 챗봇

```
요구사항:
1. 각 고객은 독립적인 컨텍스트 필요
2. 최대 동시 사용자: 1000명
3. 응답 시간 목표: 2초 이내
4. 가용성: 99.9% (SLA)

아키텍처 다이어그램을 그리고 설명하세요:
- 각 계층의 역할
- 확장성 전략
- 캐싱 전략
- 모니터링 포인트
```

### 과제 2: 비용 최적화 분석

```python
# 요구사항:
# 1. 3개 모델 선택 (gpt-3.5-turbo, gpt-4, Claude)
# 2. 샘플 쿼리 10개로 각 모델의 비용 계산
# 3. 캐싱이 적용될 경우 비용 절감 분석
# 4. 최적의 모델 선택 기준 제시

sample_queries = [
    "파리의 인구는?",
    "Python의 GIL이란?",
    # ... 8개 더
]
```

### 과제 3: 캐싱 전략

```python
# 요구사항:
# 1. ResponseCache 클래스 확장
# 2. TTL (Time To Live) 지원
# 3. LRU (Least Recently Used) 캐시 정책
# 4. 캐시 히트율 분석

# 테스트:
# - 1000개 요청 생성
# - 30% 중복 요청
# - 히트율과 지연시간 개선 측정
```

### 과제 4: 성능 모니터링

```python
# 요구사항:
# 1. 주요 메트릭 정의
# 2. 메트릭 수집 로직
# 3. 이상 감지 (Anomaly Detection)
# 4. 대시보드 시각화

# 메트릭들:
# - 응답 시간 분포
# - 에러율 추이
# - 토큰 사용량
# - 비용 추이
```

### 과제 5: 확장성 시뮬레이션

```python
# 요구사항:
# 1. 부하 테스트 시나리오 작성
# 2. 워커 수에 따른 성능 변화 측정
# 3. 병목 지점 파악
# 4. 확장 전략 제시

# 테스트 시나리오:
# - 초기: 100 요청/초
# - 증가: 1000 요청/초
# - 최고: 5000 요청/초
```

---

## 📝 주요 패턴

### 패턴 1: Request-Response

```python
@app.post("/api/generate")
async def generate(prompt: str):
    result = await llm.invoke(prompt)
    return {"result": result}
```

### 패턴 2: Async Pipeline

```python
async def pipeline(query: str):
    # 1단계: 검색
    context = await retrieve(query)

    # 2단계: 생성
    response = await generate(query, context)

    # 3단계: 검증
    validated = await validate(response)

    return validated
```

### 패턴 3: Streaming Response

```python
@app.post("/api/stream")
async def stream_generate(prompt: str):
    async def event_generator():
        async for token in llm.stream(prompt):
            yield f"data: {token}\n\n"

    return StreamingResponse(event_generator())
```

---

## ✅ 주간 체크포인트

```
□ 3계층 아키텍처 설명 가능
□ RAG, Agent 등 다양한 패턴 이해
□ 확장성 설계 가능
□ 비용 최적화 전략 수립 가능
□ 캐싱 구현 가능
□ 모니터링 시스템 설계 가능
□ 성능 최적화 기법 적용 가능
```

---

## 🔗 추가 리소스

- [Building LLM Applications](https://www.deeplearning.ai/short-courses/building-systems-with-chatgpt/)
- [Production LLM Systems](https://github.com/microsoft/guidance)
- [LLM Observability Best Practices](https://docs.langchain.com/docs/modules/agents/tools/langsmith_integration)
- [Scaling LLM Applications](https://www.anyscale.com/blog/scaling-llms)

---

[← Week 12](./week12_agent_tools.md) | [Week 14 →](./week14_evaluation.md)
