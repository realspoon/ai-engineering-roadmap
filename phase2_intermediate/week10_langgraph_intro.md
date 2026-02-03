# Week 10: LangGraph 입문

## 🎯 학습 목표

1. LangGraph의 그래프 기반 접근법 이해
2. State Machine 개념 적용
3. StateGraph와 Node, Edge 구성
4. Human-in-the-loop 패턴 구현

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Learning LangChain](https://www.oreilly.com/library/view/learning-langchain/9781098167271/) | Mayo Oshin | Chapter 8-10 |
| 📚 Book | [Building Applications with AI Agents](https://www.oreilly.com/library/view/building-applications-with/9781098176495/) | Mariusz Skoneczko | Chapter 5-6 |

---

## 📖 핵심 개념

### 1. LangGraph란?

LangGraph는 LLM 애플리케이션을 **상태 기반 그래프**로 모델링하는 프레임워크입니다.

**기존 Chain의 한계:**
- 선형적 실행만 가능
- 조건부 분기가 복잡
- 상태 관리 어려움
- 재시도/복구 어려움

**LangGraph의 장점:**
- 순환 (Cycles) 지원
- 조건부 분기 용이
- 명시적 상태 관리
- Checkpoint로 복구 가능

### 2. LangGraph 핵심 구성요소

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph 구조                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                     State                            │   │
│  │  (그래프 전체에서 공유되는 상태 정보)                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐              │
│         ▼                 ▼                 ▼              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │
│  │   Node A    │   │   Node B    │   │   Node C    │      │
│  │  (분석기)    │   │  (생성기)    │   │  (검증기)    │      │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘      │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           ▼                                 │
│                    ┌─────────────┐                         │
│                    │    Edge     │                         │
│                    │ (조건부 분기)│                         │
│                    └─────────────┘                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. 핵심 컴포넌트

| 컴포넌트 | 설명 | 예시 |
|----------|------|------|
| **State** | 그래프 전체 상태 | `TypedDict` 또는 `Pydantic` |
| **Node** | 상태를 변경하는 함수 | LLM 호출, Tool 실행 |
| **Edge** | 노드 간 연결 | 조건부/무조건부 |
| **Conditional Edge** | 조건에 따른 분기 | 다음 노드 결정 |
| **START/END** | 그래프 시작/종료점 | 진입점, 종료점 |

### 4. State 설계 패턴

```python
from typing import TypedDict, Annotated
from operator import add

class AgentState(TypedDict):
    # 메시지 히스토리 (누적)
    messages: Annotated[list, add]

    # 현재 작업 단계
    current_step: str

    # 중간 결과물
    intermediate_results: dict

    # 최종 결과
    final_answer: str | None
```

---

## 💻 실습 과제

### 과제 1: 환경 설정

```bash
pip install langgraph langchain-openai
```

### 과제 2: 기본 StateGraph 구현

```python
from langgraph.graph import StateGraph, START, END

# 1. State 정의
class MyState(TypedDict):
    input: str
    output: str

# 2. 그래프 생성
graph = StateGraph(MyState)

# 3. 노드 추가
graph.add_node("process", process_function)

# 4. 엣지 연결
graph.add_edge(START, "process")
graph.add_edge("process", END)

# 5. 컴파일 및 실행
app = graph.compile()
result = app.invoke({"input": "Hello"})
```

### 과제 3: Conditional Edge 활용

```python
def route_decision(state: MyState) -> str:
    """상태에 따라 다음 노드 결정"""
    if state["needs_review"]:
        return "review_node"
    else:
        return "finalize_node"

graph.add_conditional_edges(
    "analyze_node",
    route_decision,
    {
        "review_node": "review_node",
        "finalize_node": "finalize_node"
    }
)
```

### 과제 4: Human-in-the-loop 구현

[샘플 코드 → week10_langgraph_basic.py](./samples/week10_langgraph_basic.py)

---

## 📝 주요 패턴

### 패턴 1: 선형 워크플로우

```
START → Node A → Node B → Node C → END
```

### 패턴 2: 조건부 분기

```
START → Analyze → [조건] → Path A → END
                        → Path B → END
```

### 패턴 3: 반복 (Loop)

```
START → Generate → Review → [통과?] → END
                         ↑    ↓
                         └────┘ (재생성)
```

### 패턴 4: Human-in-the-loop

```
START → Agent → [확인 필요?] → Human Review → Agent → END
                           ↓
                          END
```

---

## ✅ 주간 체크포인트

```
□ LangGraph의 장점과 사용 시점 설명 가능
□ State, Node, Edge 개념 이해
□ 기본 StateGraph 독립 구축 가능
□ Conditional Edge로 분기 로직 구현 가능
□ Human-in-the-loop 패턴 구현 가능
```

---

## 🔗 추가 리소스

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)

---

[← Week 9](./week09_agent_concepts.md) | [Week 11 →](./week11_langgraph_advanced.md)
