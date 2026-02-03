# Track B: Text-to-SQL Agent

> **목표**: 자연어 질문을 SQL로 변환하여 데이터베이스를 쿼리하고 결과를 해석하는 AI Agent

## 🎯 최종 결과물

```
┌─────────────────────────────────────────────────────────────┐
│                   Text-to-SQL Agent                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  사용자: "지난달 가장 많이 팔린 제품 Top 5를 알려줘"            │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. 자연어 질의 분석                                  │   │
│  │  2. 관련 테이블/컬럼 검색 (RAG)                       │   │
│  │  3. SQL 쿼리 생성                                    │   │
│  │  4. SQL 검증 및 최적화                               │   │
│  │  5. 쿼리 실행                                        │   │
│  │  6. 결과 해석 및 시각화                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  결과: SQL + 실행결과 + 자연어 설명 + 차트                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📅 주차별 학습 계획

### 월 5: 기초 구현

| 주차 | 주제 | 핵심 기술 | 실습 |
|------|------|----------|------|
| Week 17 | SQL 고급 | Window Functions, CTE | 복잡한 쿼리 작성 |
| Week 18 | 스키마 분석 | 메타데이터, ERD | 스키마 크롤러 |
| Week 19 | Text-to-SQL 기초 | 프롬프트 엔지니어링 | 기본 변환 |
| Week 20 | Agent 구현 | LangGraph | 기본 Agent |

### 월 6: 고도화

| 주차 | 주제 | 핵심 기술 | 실습 |
|------|------|----------|------|
| Week 21 | 고급 쿼리 | Multi-step, 분해 | 복잡한 질의 처리 |
| Week 22 | RAG 스키마 검색 | 임베딩, Few-shot | 대규모 스키마 |
| Week 23 | 결과 해석 | 자연어 설명 | 시각화 자동화 |
| Week 24 | 통합 테스트 | 전체 통합 | Agent v1.0 |

---

## 📚 O'Reilly 리소스

| 도서 | 저자 | 학습 범위 |
|------|------|----------|
| [Learning SQL, 3rd Ed](https://www.oreilly.com/library/view/learning-sql-3rd/9781492057604/) | Alan Beaulieu | Ch 8-15 |
| [SQL Cookbook, 2nd Ed](https://www.oreilly.com/library/view/sql-cookbook-2nd/9781492077435/) | Anthony Molinaro | Part 2-3 |
| [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) | Chip Huyen | Ch 6 |

---

## 💻 핵심 샘플 코드

### text_to_sql_agent.py

```python
"""Text-to-SQL Agent 핵심 구현"""

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

class TextToSQLState(TypedDict):
    question: str           # 자연어 질문
    schema_context: str     # 관련 스키마 정보
    sql_query: str          # 생성된 SQL
    query_result: list      # 쿼리 결과
    explanation: str        # 자연어 설명
    error: str              # 에러 메시지

def create_text_to_sql_agent():
    graph = StateGraph(TextToSQLState)

    # 노드
    graph.add_node("retrieve_schema", retrieve_relevant_schema)
    graph.add_node("generate_sql", generate_sql_query)
    graph.add_node("validate_sql", validate_and_fix_sql)
    graph.add_node("execute_sql", execute_query)
    graph.add_node("explain_result", explain_in_natural_language)

    # 엣지
    graph.add_edge(START, "retrieve_schema")
    graph.add_edge("retrieve_schema", "generate_sql")
    graph.add_edge("generate_sql", "validate_sql")
    graph.add_edge("validate_sql", "execute_sql")
    graph.add_edge("execute_sql", "explain_result")
    graph.add_edge("explain_result", END)

    return graph.compile()
```

---

## 🔧 핵심 기능

### 1. 스키마 인식 프롬프트

```python
SCHEMA_AWARE_PROMPT = """
당신은 SQL 전문가입니다. 자연어 질문을 SQL로 변환하세요.

## 데이터베이스 스키마
{schema}

## 테이블 관계
{relationships}

## 예시 쿼리
{few_shot_examples}

## 사용자 질문
{question}

## 생성할 SQL
```sql
"""
```

### 2. SQL 검증 및 수정

```python
def validate_sql(sql: str, schema: dict) -> tuple[bool, str]:
    """SQL 쿼리 검증 및 수정"""

    # 1. 문법 검사 (sqlparse)
    # 2. 테이블/컬럼 존재 확인
    # 3. SQL Injection 방지
    # 4. 쿼리 최적화 제안

    return is_valid, corrected_sql
```

### 3. 결과 해석

```
📊 쿼리 결과 해석

질문: "지난달 가장 많이 팔린 제품 Top 5"

결과:
| 순위 | 제품명      | 판매량  |
|-----|-----------|--------|
| 1   | iPhone 15 | 15,234 |
| 2   | Galaxy S24| 12,456 |
| ...

💡 인사이트:
- iPhone 15가 1위로 전월 대비 23% 증가
- 모바일 기기가 Top 5 중 4개 차지
```

---

## ✅ Track B 완료 체크리스트

### 월 5 (기초)
- [ ] 복잡한 SQL 쿼리 작성 가능
- [ ] 스키마 자동 분석 가능
- [ ] 기본 Text-to-SQL 변환 가능
- [ ] 기본 Agent 프로토타입 완성

### 월 6 (고도화)
- [ ] Multi-step 쿼리 분해 가능
- [ ] RAG 기반 스키마 검색 가능
- [ ] 결과 자연어 해석 및 시각화 가능
- [ ] Text-to-SQL Agent v1.0 완성

---

[← Track A](../track_a_data_analyst/README.md) | [Track C →](../track_c_data_quality/README.md)
