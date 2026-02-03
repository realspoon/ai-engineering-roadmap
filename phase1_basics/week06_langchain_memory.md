# Week 6: LangChain Memory & Tools

## 🎯 학습 목표

1. Conversation Memory 구현 및 활용
2. Custom Tool 생성
3. Tool을 활용하는 Agent 기초
4. 외부 API 연동

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Learning LangChain](https://www.oreilly.com/library/view/learning-langchain/9781098167271/) | Mayo Oshin | Chapter 5-7 |
| 📚 Book | [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) | Chip Huyen | Chapter 5-6 |

---

## 📖 핵심 개념

### 1. Memory 유형

| Memory 유형 | 설명 | 사용 시점 |
|-------------|------|----------|
| **ConversationBufferMemory** | 전체 대화 저장 | 짧은 대화 |
| **ConversationBufferWindowMemory** | 최근 N개 대화만 | 긴 대화 |
| **ConversationSummaryMemory** | 요약 저장 | 매우 긴 대화 |
| **ConversationTokenBufferMemory** | 토큰 제한 | 비용 관리 |

### 2. Memory 구현

```python
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain

memory = ConversationBufferMemory()
llm = ChatOpenAI(model="gpt-4o-mini")

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 대화
conversation.predict(input="안녕하세요, 저는 김철수입니다.")
conversation.predict(input="제 이름이 뭐라고 했죠?")  # 기억함!
```

### 3. Custom Tool 생성

```python
from langchain.tools import tool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="검색할 키워드")

@tool("web_search", args_schema=SearchInput)
def web_search(query: str) -> str:
    """웹에서 정보를 검색합니다."""
    # 실제 검색 로직
    return f"'{query}'에 대한 검색 결과..."

# Tool 정보 확인
print(web_search.name)        # web_search
print(web_search.description) # 웹에서 정보를 검색합니다.
print(web_search.args)        # {'query': {'description': '검색할 키워드'}}
```

### 4. Tool을 사용하는 Agent

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

tools = [web_search, calculator, weather_api]

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 도구를 사용할 수 있는 AI 어시스턴트입니다."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({"input": "서울 날씨 알려줘"})
```

---

## 💻 실습 과제

### 과제 1: Memory가 있는 챗봇

```python
# 요구사항:
# 1. 사용자 이름 기억
# 2. 이전 대화 맥락 유지
# 3. 요약 기반 장기 메모리
```

### 과제 2: Custom Tool 3개 생성

- 날씨 API Tool
- 계산기 Tool
- 웹 검색 Tool

### 과제 3: Tool Agent 구현

[샘플 코드 → week06_memory_tools.py](./samples/week06_memory_tools.py)

---

## ✅ 주간 체크포인트

```
□ 4가지 Memory 유형의 차이 설명 가능
□ ConversationBufferMemory 구현 가능
□ Custom Tool 생성 가능 (Pydantic 스키마 포함)
□ Tool을 사용하는 기본 Agent 구현 가능
□ 외부 API를 Tool로 연동 가능
```

---

[← Week 5](./week05_langchain_intro.md) | [Week 7 →](./week07_rag_basics.md)
