# Week 12: Agent 도구 생태계

## 🎯 학습 목표

1. Custom Tool 개발 및 등록
2. API 연동 방법 학습
3. Tool 체인과 선택 로직
4. Error Handling과 Fallback

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Learning LangChain](https://www.oreilly.com/library/view/learning-langchain/9781098167271/) | Mayo Oshin | Chapter 6-7 |
| 📚 Book | [Building Applications with AI Agents](https://www.oreilly.com/library/view/building-applications-with/9781098176495/) | Mariusz Skoneczko | Chapter 6 |

---

## 📖 핵심 개념

### 1. Tool이란?

Tool은 **Agent가 외부 기능에 접근할 수 있게 해주는 인터페이스**입니다.

**Tool의 특징:**
- 명확한 입출력 정의
- Agent가 이해할 수 있는 설명
- 에러 처리 기능
- 실행 결과 반환

**Tool의 종류:**

```
┌─────────────────────────────────────┐
│           Agent Tool                │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Search Tools               │   │
│  │  - 웹 검색                   │   │
│  │  - 문서 검색                 │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  API Tools                  │   │
│  │  - REST API 호출             │   │
│  │  - 데이터 조회               │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Computation Tools          │   │
│  │  - 계산 수행                 │   │
│  │  - 데이터 분석               │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Action Tools               │   │
│  │  - 파일 저장                 │   │
│  │  - DB 업데이트              │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### 2. Custom Tool 개발

**방법 1: @tool 데코레이터**

```python
from langchain.tools import tool

@tool
def calculator(expression: str) -> float:
    """
    수학 표현식을 계산합니다.

    Args:
        expression: 계산할 수학 식 (예: "2 + 2 * 3")

    Returns:
        계산 결과
    """
    return eval(expression)

# 사용
print(calculator.name)  # "calculator"
print(calculator.description)  # 위의 docstring
```

**방법 2: Tool 클래스**

```python
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    expression: str = Field(
        description="계산할 수학 식"
    )

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "수학 표현식을 계산합니다"
    args_schema = CalculatorInput

    def _run(self, expression: str) -> str:
        try:
            result = eval(expression)
            return f"결과: {result}"
        except Exception as e:
            return f"에러: {str(e)}"
```

**방법 3: 구조화된 Tool (권장)**

```python
from langchain_core.tools import tool
from typing import Annotated

@tool
def search_database(
    query: Annotated[str, "검색 쿼리"],
    limit: Annotated[int, "최대 결과 개수"] = 10
) -> str:
    """데이터베이스를 검색합니다."""
    # 구현
    pass
```

### 3. API 연동

**REST API 호출 Tool:**

```python
from langchain.tools import tool
import httpx

@tool
def fetch_weather(city: str) -> str:
    """
    도시의 날씨 정보를 조회합니다.

    Args:
        city: 도시 이름

    Returns:
        날씨 정보
    """
    async def get_weather():
        async with httpx.AsyncClient() as client:
            url = f"https://api.weather.com/v1/{city}"
            response = await client.get(url)
            return response.json()

    import asyncio
    result = asyncio.run(get_weather())
    return str(result)
```

**GraphQL API Tool:**

```python
@tool
def query_graphql(query: str) -> str:
    """GraphQL 쿼리를 실행합니다."""
    import httpx

    client = httpx.Client()
    response = client.post(
        "https://api.example.com/graphql",
        json={"query": query}
    )
    return response.json()
```

### 4. Tool Selection과 Chain

**Tool 선택 로직:**

```python
from langchain.agents import Tool

tools = [
    Tool(
        name="search",
        func=search_tool,
        description="인터넷 검색"
    ),
    Tool(
        name="calculator",
        func=calculator,
        description="계산 수행"
    ),
    Tool(
        name="email_sender",
        func=send_email,
        description="이메일 전송"
    ),
]

# Tool selection function
def select_tool(query: str) -> str:
    """
    쿼리에 따라 적절한 Tool 선택
    """
    if "계산" in query or "수학" in query:
        return "calculator"
    elif "검색" in query or "정보" in query:
        return "search"
    elif "보내" in query or "메일" in query:
        return "email_sender"
    else:
        return "search"  # 기본값
```

**Tool 매니페스트:**

```python
# Tool의 메타정보를 명확히 정의
tools_manifest = {
    "calculator": {
        "description": "수학 표현식 계산",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "계산식"
                }
            },
            "required": ["expression"]
        }
    },
    "search": {
        "description": "웹 검색",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색어"
                }
            },
            "required": ["query"]
        }
    }
}
```

### 5. Error Handling과 Fallback

```python
@tool
def robust_api_call(endpoint: str) -> str:
    """에러 처리가 있는 API 호출"""
    import httpx
    from tenacity import retry, stop_after_attempt, wait_exponential

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def call_api():
        try:
            response = httpx.get(endpoint, timeout=5.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "엔드포인트를 찾을 수 없음"}
            elif e.response.status_code == 429:
                raise  # 재시도
            else:
                return {"error": f"HTTP 에러: {e.status_code}"}
        except httpx.TimeoutException:
            return {"error": "요청 시간 초과"}
        except Exception as e:
            return {"error": f"예상치 못한 에러: {str(e)}"}

    return str(call_api())
```

**Fallback 패턴:**

```python
def tool_with_fallback(query: str) -> str:
    """기본 tool 실패 시 fallback 실행"""
    try:
        return primary_tool(query)
    except PrimaryToolError:
        print("Primary tool 실패, fallback 실행")
        return fallback_tool(query)
```

---

## 💻 실습 과제

### 과제 1: Custom Tool 개발

```python
# 요구사항:
# 1. 도시 이름을 받아 위도/경도 반환하는 Tool
# 2. Docstring으로 명확한 설명
# 3. 입력 검증 포함

# 예시:
# geocoding_tool("Seoul") → {"lat": 37.57, "lon": 126.98}
```

### 과제 2: API 연동 Tool

```python
# 요구사항:
# 1. 공개 API 선택 (JSONPlaceholder, OpenWeather 등)
# 2. 해당 API와 연동하는 Tool 작성
# 3. 적절한 파라미터와 응답 처리

# 예시 API: https://jsonplaceholder.typicode.com/
# Tool: 특정 사용자의 정보 조회
```

### 과제 3: Tool Selection Logic

```python
# 요구사항:
# 1. 최소 3개의 Tool 정의
# 2. 사용자 쿼리에 따라 적절한 Tool 선택
# 3. Tool 선택 이유 설명

# 테스트 쿼리들:
# - "파리의 날씨를 알려줘"
# - "2024년 가장 영화는?"
# - "이 파일을 저장해줘"
```

### 과제 4: Error Handling

```python
# 요구사항:
# 1. 불안정한 API를 호출하는 Tool 작성
# 2. 다양한 에러 케이스 처리
#    - 타임아웃
#    - 404 Not Found
#    - 500 Server Error
#    - 네트워크 에러
# 3. 재시도 로직 구현 (tenacity 라이브러리)
```

### 과제 5: Tool 체인 구축

```python
# 요구사항:
# 1. 3-4개의 Tool을 순차적으로 호출
# 2. 이전 Tool의 결과를 다음 Tool의 입력으로 사용

# 예시 워크플로우:
# 1. 도시명 입력
# 2. Geocoding Tool: 위도/경도 얻기
# 3. Weather Tool: 좌표로 날씨 조회
# 4. Formatter Tool: 결과를 사람이 읽기 좋게 정렬
```

---

## 📝 주요 패턴

### 패턴 1: Simple Tool

```python
@tool
def simple_tool(input: str) -> str:
    """Tool 설명"""
    return process(input)
```

### 패턴 2: Tool with State

```python
class StatefulTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.state = {}

    def _run(self, input: str) -> str:
        self.state[input] = process(input)
        return self.state[input]
```

### 패턴 3: Tool Chain

```python
result1 = tool1(input)
result2 = tool2(result1)
result3 = tool3(result2)
```

### 패턴 4: Parallel Tools

```python
# 여러 Tool을 병렬로 실행
import asyncio

async def run_parallel():
    results = await asyncio.gather(
        tool1_async(input),
        tool2_async(input),
        tool3_async(input)
    )
    return results
```

---

## ✅ 주간 체크포인트

```
□ Custom Tool 개발 가능
□ @tool 데코레이터와 BaseTool 클래스 차이 이해
□ API 연동 Tool 작성 가능
□ Tool Selection 로직 구현 가능
□ 에러 처리 및 재시도 로직 구현 가능
□ Tool 체인 구축 가능
□ Tool 매니페스트 작성 가능
```

---

## 🔗 추가 리소스

- [LangChain Tools Documentation](https://python.langchain.com/docs/modules/tools/)
- [Tool Examples](https://github.com/langchain-ai/langchain/tree/master/examples/tools)
- [Custom Tool Integration](https://python.langchain.com/docs/modules/tools/custom_tools/)
- [Tenacity Retry Library](https://tenacity.readthedocs.io/)

---

[← Week 11](./week11_langgraph_advanced.md) | [Week 13 →](./week13_app_design.md)
