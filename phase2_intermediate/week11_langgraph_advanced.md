# Week 11: LangGraph 심화

## 🎯 학습 목표

1. Multi-Agent 시스템 구축
2. Checkpoint와 상태 지속성 활용
3. 복잡한 조건부 분기 구현
4. 그래프 시각화 및 디버깅

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Building Applications with AI Agents](https://www.oreilly.com/library/view/building-applications-with/9781098176495/) | Mariusz Skoneczko | Chapter 7-9 |
| 📚 Book | [Learning LangChain](https://www.oreilly.com/library/view/learning-langchain/9781098167271/) | Mayo Oshin | Chapter 11-12 |

---

## 📖 핵심 개념

### 1. Multi-Agent 아키텍처

여러 Agent가 협력하여 복잡한 작업을 해결합니다.

**구조:**

```
┌──────────────────────────────────────────┐
│          Orchestrator Agent               │
│      (작업 분배 및 결과 조정)             │
└────────────┬──────────────────┬──────────┘
             │                  │
      ┌──────▼──────┐    ┌──────▼──────┐
      │ Research    │    │ Analyst     │
      │ Agent       │    │ Agent       │
      └──────┬──────┘    └──────┬──────┘
             │                  │
      ┌──────▼──────┐    ┌──────▼──────┐
      │ Web Search  │    │ Data        │
      │ Tools       │    │ Processing  │
      │             │    │ Tools       │
      └─────────────┘    └─────────────┘
```

**Multi-Agent의 장점:**
- 역할 분담으로 복잡도 감소
- 각 Agent의 특화된 기능
- 병렬 처리 가능성
- 유지보수 및 확장성 향상

### 2. Checkpoint와 상태 지속성

Checkpoint는 **특정 시점의 상태를 저장**하여 복구 가능하게 합니다.

**Checkpoint의 용도:**
- 실패 시 복구
- 중단된 작업 재개
- 감사 추적 (Audit Trail)
- 상태 버전 관리

**구현:**

```python
# 메모리 기반 Checkpoint
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# 실행 중단 및 재개
config = {"configurable": {"thread_id": "user_123"}}

# 첫 번째 실행
result1 = graph.invoke(input1, config=config)

# 같은 thread로 재개
result2 = graph.invoke(input2, config=config)
```

**SQLite 기반 Checkpoint:**

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver(conn=sqlite3.connect("graph.db"))
graph = builder.compile(checkpointer=checkpointer)
```

| 저장소 | 용도 | 장점 | 단점 |
|--------|------|------|------|
| **Memory** | 개발/테스트 | 빠름, 간단 | 휘발성 |
| **SQLite** | 소규모 프로덕션 | 지속성, 쿼리 가능 | 확장성 제한 |
| **PostgreSQL** | 중규모 이상 | 확장성, 고가용성 | 설정 복잡 |

### 3. Reducer와 상태 업데이트

`Annotated`를 사용하여 상태 필드가 어떻게 병합되는지 정의합니다.

```python
from typing import Annotated
from operator import add

class GraphState(TypedDict):
    # 리스트에 추가 (누적)
    messages: Annotated[list, add]

    # 덮어쓰기 (기본)
    current_user: str

    # 커스텀 reducer
    scores: Annotated[dict, lambda x, y: {**x, **y}]
```

**내장 Reducer:**
- `add`: 리스트/숫자 누적
- `operator.setitem`: 딕셔너리 항목 업데이트
- 커스텀 함수: 복잡한 병합 로직

### 4. 조건부 분기 심화

**다중 조건 처리:**

```python
def route_to_agent(state: GraphState) -> list[str]:
    """
    여러 경로로 동시에 라우팅
    """
    paths = []

    if state["needs_research"]:
        paths.append("research_agent")

    if state["needs_analysis"]:
        paths.append("analysis_agent")

    if state["needs_feedback"]:
        paths.append("human_review")

    return paths

# 조건부 엣지 - 여러 경로
graph.add_conditional_edges(
    "orchestrator",
    route_to_agent,
    {
        "research_agent": "research_agent",
        "analysis_agent": "analysis_agent",
        "human_review": "human_review",
    }
)
```

### 5. 그래프 시각화

```python
from PIL import Image

# SVG로 그래프 구조 시각화
svg = graph.get_graph().draw_mermaid_png()
Image.open(io.BytesIO(svg)).show()

# 텍스트 기반 시각화
print(graph.get_graph().draw_ascii())
```

---

## 💻 실습 과제

### 과제 1: Multi-Agent 시스템 구축

**요청:** 제품 리뷰 분석 시스템

```python
# 필수 구현 항목:
# 1. Orchestrator: 작업 분배
# 2. Sentiment Agent: 감정 분석
# 3. Topic Agent: 주제 추출
# 4. Summary Agent: 요약 생성

# 예시 입력:
# "이 제품은 정말 좋았어요! 배송도 빠르고 품질도 우수합니다."
```

### 과제 2: Checkpoint 구현

```python
# 요구사항:
# 1. SQLiteSaver 설정
# 2. 같은 thread_id로 여러 번 실행
# 3. 중간 상태 확인
# 4. 재개 동작 검증

config = {"configurable": {"thread_id": "review_task_1"}}
```

### 과제 3: 상태 Reducer 설계

**시나리오:** 멀티 턴 대화 시스템

```python
# 요구사항:
# 1. messages 필드: 메시지 누적
# 2. context 필드: 문맥 정보 병합
# 3. scores 필드: 각 Agent의 점수 누적

# Annotated와 적절한 reducer 정의
```

### 과제 4: 복잡한 분기 로직

**요청:** 자동 버그 분류 시스템

```python
# 다음 조건에 따라 분기:
# - 버그 심각도 높음 → 즉시 할당
# - 심각도 중간 → 자동 분류 후 할당
# - 심각도 낮음 → 큐에 대기
# - 추가 정보 필요 → 사용자 피드백 요청

# 동시에 여러 경로 활성화 가능해야 함
```

### 과제 5: 그래프 디버깅

```python
# 요구사항:
# 1. 구축한 Multi-Agent 시스템 시각화
# 2. 실행 흐름 추적
# 3. 각 노드의 입출력 검사
# 4. 병목 지점 파악
```

---

## 📝 주요 패턴

### 패턴 1: Hierarchical Agent

```
┌─────────────────────┐
│   Main Orchestrator │
└──────────┬──────────┘
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
┌──────┐┌──────┐┌──────┐
│Sub-  ││Sub-  ││Sub-  │
│Agent1││Agent2││Agent3│
└──────┘└──────┘└──────┘
```

### 패턴 2: Map-Reduce Pattern

```
Input → Map (병렬 처리) → Reduce (결과 통합) → Output
```

### 패턴 3: Checkpoint with Retry

```
Node A → [성공?] → Node B
              ↓
          실패 → Checkpoint에서 복구 → Node A (재시도)
```

### 패턴 4: Streaming State Updates

```python
for event in graph.stream(input, config):
    print(f"노드: {event}")
    # 실시간으로 상태 업데이트 추적
```

---

## ✅ 주간 체크포인트

```
□ Multi-Agent 설계 및 구현 가능
□ Orchestrator와 Worker Agent 역할 구분
□ Checkpoint 설정 및 활용 가능
□ SQLite/메모리 Checkpoint 선택 기준 이해
□ 복잡한 조건부 분기 구현 가능
□ 그래프 시각화 및 디버깅 가능
□ 상태 Reducer 적절히 설계 가능
```

---

## 🔗 추가 리소스

- [LangGraph Checkpoint Documentation](https://langchain-ai.github.io/langgraph/concepts/checkpointer/)
- [LangGraph Multi-Agent Examples](https://langchain-ai.github.io/langgraph/tutorials/#multi-agent-systems)
- [State Management Patterns](https://langchain-ai.github.io/langgraph/concepts/low_level_conceptual_guide/)

---

[← Week 10](./week10_langgraph_intro.md) | [Week 12 →](./week12_agent_tools.md)
