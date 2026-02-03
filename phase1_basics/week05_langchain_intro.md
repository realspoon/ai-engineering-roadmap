# Week 5: LangChain 시작하기

## 🎯 학습 목표

1. LangChain 프레임워크 구조 이해
2. 기본 컴포넌트 (LLMs, Prompts, Chains) 활용
3. PromptTemplate과 Output Parser 활용
4. Sequential Chain 구축

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Learning LangChain](https://www.oreilly.com/library/view/learning-langchain/9781098167271/) | Mayo Oshin | Chapter 1-4 |
| 📚 Book | [Building LLM Powered Applications](https://www.oreilly.com/library/view/building-llm-powered/9781835462317/) | Valentina Alto | Chapter 1-3 |

---

## 📖 핵심 개념

### 1. LangChain 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    LangChain 구조                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │  Model  │    │ Prompt  │    │  Chain  │    │  Agent  │  │
│  │ I/O     │    │Templates│    │         │    │         │  │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘  │
│       │              │              │              │        │
│       └──────────────┴──────────────┴──────────────┘        │
│                          │                                  │
│                    ┌─────┴─────┐                            │
│                    │  Memory   │                            │
│                    └─────┬─────┘                            │
│                          │                                  │
│            ┌─────────────┼─────────────┐                    │
│            │             │             │                    │
│       ┌────┴────┐  ┌─────┴─────┐  ┌────┴────┐              │
│       │ Vector  │  │  Document │  │  Tools  │              │
│       │ Stores  │  │  Loaders  │  │         │              │
│       └─────────┘  └───────────┘  └─────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. 핵심 컴포넌트

| 컴포넌트 | 설명 | 예시 |
|----------|------|------|
| **ChatModel** | LLM과의 인터페이스 | ChatOpenAI, ChatAnthropic |
| **PromptTemplate** | 동적 프롬프트 생성 | 변수 삽입 가능한 템플릿 |
| **OutputParser** | LLM 출력 구조화 | JSON, Pydantic 파싱 |
| **Chain** | 컴포넌트 연결 | LCEL (LangChain Expression Language) |
| **Memory** | 대화 히스토리 관리 | ConversationBufferMemory |

### 3. LCEL (LangChain Expression Language)

```python
# 기본 Chain 구성
chain = prompt | model | output_parser

# 파이프 연산자로 컴포넌트 연결
# prompt → model → output_parser 순서로 실행
```

---

## 💻 실습 과제

### 과제 1: LangChain 설치 및 기본 설정

```bash
pip install langchain langchain-openai langchain-anthropic
pip install langchain-community langchain-core
```

### 과제 2: PromptTemplate 생성

```python
from langchain_core.prompts import ChatPromptTemplate

# 기본 템플릿
template = ChatPromptTemplate.from_messages([
    ("system", "당신은 {role} 전문가입니다."),
    ("human", "{question}")
])

# 변수 주입
prompt = template.invoke({
    "role": "데이터 분석",
    "question": "판다스에서 결측치를 처리하는 방법은?"
})
```

### 과제 3: Sequential Chain 구현

[샘플 코드 → week05_langchain_chains.py](./samples/week05_langchain_chains.py)

### 과제 4: Output Parser 활용

```python
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

class Analysis(BaseModel):
    summary: str
    key_points: list[str]
    recommendation: str

parser = JsonOutputParser(pydantic_object=Analysis)
```

---

## 📝 주요 패턴

### 패턴 1: 기본 Chain

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

model = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_template("Translate to Korean: {text}")

chain = prompt | model
result = chain.invoke({"text": "Hello, world!"})
```

### 패턴 2: 분기 Chain (RunnableBranch)

```python
from langchain_core.runnables import RunnableBranch

branch = RunnableBranch(
    (lambda x: "code" in x["type"], code_chain),
    (lambda x: "data" in x["type"], data_chain),
    default_chain
)
```

### 패턴 3: 병렬 처리 (RunnableParallel)

```python
from langchain_core.runnables import RunnableParallel

parallel = RunnableParallel(
    summary=summary_chain,
    keywords=keyword_chain,
    sentiment=sentiment_chain
)
```

---

## ✅ 주간 체크포인트

```
□ LangChain의 핵심 컴포넌트 5가지 설명 가능
□ PromptTemplate으로 동적 프롬프트 생성 가능
□ LCEL 문법으로 Chain 구성 가능
□ OutputParser로 구조화된 출력 생성 가능
□ Sequential Chain 독립 구축 가능
```

---

## 🔗 추가 리소스

- [LangChain Documentation](https://python.langchain.com/docs/)
- [LCEL Cookbook](https://python.langchain.com/docs/expression_language/cookbook/)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)

---

[← Week 4](./week04_prompt_advanced.md) | [Week 6 →](./week06_langchain_memory.md)
