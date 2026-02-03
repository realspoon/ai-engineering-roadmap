# Week 9: Agent 개념과 설계 원칙

## 🎯 학습 목표

1. Agent의 정의와 동작 원리 이해
2. ReAct 패턴 학습 및 구현
3. Plan-Execute Agent 설계
4. Agent vs Chain의 차이점 파악

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Building Applications with AI Agents](https://www.oreilly.com/library/view/building-applications-with/9781098176495/) | Mariusz Skoneczko | Chapter 1-4 |
| 📚 Book | [Learning LangChain](https://www.oreilly.com/library/view/learning-langchain/9781098167271/) | Mayo Oshin | Chapter 5-7 |

---

## 📖 핵심 개념

### 1. Agent란?

Agent는 **자율적으로 상황을 판단하고 행동하는 AI 시스템**입니다.

**Chain과의 차이:**
- Chain: 사전 정의된 순서대로 실행 (정적)
- Agent: 상황에 따라 동적으로 다음 행동 결정 (동적)

**Agent의 특징:**
- Perception: 환경 관찰
- Reasoning: 상황 분석
- Planning: 행동 계획 수립
- Action: 실행

### 2. Agent 아키텍처

```
┌────────────────────────────────────────┐
│         사용자 질문                      │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│  LLM (Agent의 뇌)                      │
│  - 상황 분석                            │
│  - 다음 행동 결정                       │
└────────────┬───────────────────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌─────────┐      ┌──────────┐
│ 도구 실행  │      │최종 답변  │
│(Tool)    │      │생성      │
└────┬─────┘      └──────────┘
     │
     ▼
┌────────────────────────────────────────┐
│    실행 결과 (새로운 정보)               │
└────────┬───────────────────────────────┘
         │
         └──→ (다시 LLM으로 전달)
```

### 3. ReAct (Reasoning + Acting)

ReAct 패턴은 **사고(Reasoning)와 행동(Acting)을 반복**하는 방식입니다.

**ReAct의 단계:**
1. **Thought**: 현재 상황에 대한 분석
2. **Action**: 취할 행동 결정
3. **Observation**: 행동 결과 관찰
4. 반복: 최종 답에 도달할 때까지 반복

**예시:**

```
Thought: 사용자가 "파리의 인구는?"을 물었다. 웹 검색이 필요하다.
Action: search("Paris population")
Observation: Paris has 2.16 million inhabitants (2022)

Thought: 정보를 얻었다. 최종 답을 생성할 수 있다.
Answer: 파리의 인구는 약 216만 명입니다.
```

| 요소 | 설명 | 사용 시점 |
|------|------|----------|
| **Thought** | 현재 상황 분석 | 다음 행동 결정 전 |
| **Action** | 실행할 도구/명령 | Thought 이후 |
| **Observation** | 행동 결과 | 다음 Thought 전 |

### 4. Plan-Execute Agent

더 복잡한 작업을 위한 패턴입니다.

```
┌──────────────────────────────────────┐
│  초기 요청                             │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  Plan 수립 (LLM)                      │
│  - 전체 작업 분해                      │
│  - 하위 작업 순서 정의                 │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  각 하위 작업 실행 (ExecuteAgent)     │
│  - 도구 선택 및 실행                  │
│  - 결과 수집                          │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  결과 종합 및 최종 답변                 │
└──────────────────────────────────────┘
```

### 5. Agent 상태 관리

```python
class AgentState(TypedDict):
    # 초기 입력
    input: str

    # Agent의 사고 과정
    thoughts: list[str]

    # 실행한 도구들
    actions: list[dict]

    # 도구 실행 결과들
    observations: list[str]

    # 최종 답변
    final_answer: str | None

    # 반복 횟수
    step_count: int
```

---

## 💻 실습 과제

### 과제 1: ReAct 기본 구조 이해

다음 질문에 대해 ReAct 형식으로 작성하세요:

**질문:** "2024년 한국의 GDP 성장률은?"

**작성 형식:**
```
Thought: [현재 상황 분석]
Action: [취할 행동]
Observation: [행동 결과]
Thought: [다음 판단]
...
Final Answer: [최종 답변]
```

### 과제 2: Agent vs Chain 비교

다음 시나리오에서 Agent와 Chain 중 어떤 것이 더 적합한지 설명하세요:

1. 사용자 쿼리 → 템플릿 기반 답변
2. 사용자 쿼리 → 웹 검색 → 정보 통합 → 답변
3. 사용자 쿼리 → 문서 검색 → 동적 필터링 → 답변

### 과제 3: Agent 상태 설계

다음 작업을 위한 AgentState를 설계하세요:

**작업:** 사용자의 쇼핑 요청 처리 (상품 검색 → 가격 비교 → 추천)

필요한 상태 필드들을 정의하고, 각 필드의 용도를 설명하세요.

### 과제 4: Plan-Execute 패턴 설계

**요청:** "한국, 일본, 중국의 수도를 찾고, 각 수도의 인구를 비교하세요."

이 요청을 Plan-Execute 패턴으로 분해하세요:
1. Plan 단계: 어떤 하위 작업들로 분해할 것인가?
2. Execute 단계: 각 하위 작업을 어떻게 실행할 것인가?

---

## 📝 주요 패턴

### 패턴 1: 단순 ReAct Loop

```
Input → [Thought → Action → Observation] 반복 → Output
```

### 패턴 2: 조건부 Agent

```
Input → Agent → [도구 필요?] → 도구 실행 → Output
                           ↓
                        직접 생성
```

### 패턴 3: Multi-Agent (협력)

```
         ┌─ Agent A (검색 전문)
Input ──→├─ Agent B (분석 전문)
         └─ Agent C (작성 전문)
                ↓
            결과 통합 → Output
```

---

## ✅ 주간 체크포인트

```
□ Agent와 Chain의 차이점 설명 가능
□ ReAct 패턴 이해 및 예시 작성 가능
□ Thought-Action-Observation 사이클 이해
□ Plan-Execute 패턴으로 복잡한 작업 분해 가능
□ Agent 상태 설계 가능
□ Agent 적용 시기 판단 가능
```

---

## 🔗 추가 리소스

- [ReAct: Synergizing Reasoning and Acting in LLMs](https://arxiv.org/abs/2210.03629)
- [Agent Loop Documentation](https://python.langchain.com/docs/modules/agents/)
- [LangChain Agent Examples](https://github.com/langchain-ai/langchain/tree/master/examples/agents)

---

[← Week 8](./week08_chains_routing.md) | [Week 10 →](./week10_langgraph_intro.md)
