"""
Week 6: 메모리 관리, Tool 생성, Tool Agent
==============================================

이 모듈은 LangChain의 메모리 시스템과 도구(Tools) 기반 에이전트를 보여줍니다:
- ConversationMemory (여러 종류)
- Custom Tool 생성
- Tool Agent 구현
- 메모리 기반 상태 관리
"""

import json
import time
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class MemoryType(Enum):
    """메모리 유형"""
    BUFFER = "buffer"  # 최근 N개 메시지만 저장
    SUMMARY = "summary"  # 요약 기반
    ENTITY = "entity"  # 엔티티 기반
    VECTOR = "vector"  # 벡터 기반


@dataclass
class Message:
    """메시지 객체"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """메시지를 딕셔너리로 변환"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }


@dataclass
class ConversationContext:
    """대화 컨텍스트"""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def add_message(self, role: str, content: str) -> None:
        """메시지 추가"""
        message = Message(role=role, content=content)
        self.messages.append(message)

    def get_message_count(self) -> int:
        """총 메시지 개수 반환"""
        return len(self.messages)

    def get_last_n_messages(self, n: int) -> List[Message]:
        """마지막 N개 메시지 반환"""
        return self.messages[-n:] if n > 0 else []


class BufferMemory:
    """
    버퍼 메모리: 최근 N개의 메시지만 저장합니다.
    가장 간단하고 빠른 메모리 타입입니다.
    """

    def __init__(self, max_tokens: int = 1000):
        """
        BufferMemory 초기화

        Args:
            max_tokens (int): 최대 토큰 수
        """
        self.max_tokens = max_tokens
        self.messages: List[Message] = []
        self.token_count = 0

    def add_message(self, role: str, content: str) -> None:
        """
        메시지 추가

        Args:
            role (str): "user" 또는 "assistant"
            content (str): 메시지 내용
        """
        message = Message(role=role, content=content)
        self.messages.append(message)

        # 토큰 수 추정 (단어 수 기반)
        tokens = len(content.split())
        self.token_count += tokens

        # 토큰 초과 시 오래된 메시지 제거
        while self.token_count > self.max_tokens and self.messages:
            removed = self.messages.pop(0)
            self.token_count -= len(removed.content.split())

    def get_memory(self) -> str:
        """메모리 내용을 문자열로 반환"""
        if not self.messages:
            return "메모리가 비어있습니다."

        formatted = []
        for msg in self.messages:
            formatted.append(f"{msg.role.upper()}: {msg.content}")

        return "\n".join(formatted)

    def clear(self) -> None:
        """메모리 초기화"""
        self.messages = []
        self.token_count = 0


class SummaryMemory:
    """
    요약 메모리: 오래된 대화를 요약하여 저장합니다.
    메모리 효율성이 높지만 세부 정보 손실이 있습니다.
    """

    def __init__(self, summary_threshold: int = 5):
        """
        SummaryMemory 초기화

        Args:
            summary_threshold (int): 요약을 시작할 메시지 개수
        """
        self.summary_threshold = summary_threshold
        self.conversation_summary = ""
        self.recent_messages: List[Message] = []

    def add_message(self, role: str, content: str) -> None:
        """
        메시지 추가 및 요약 관리

        Args:
            role (str): "user" 또는 "assistant"
            content (str): 메시지 내용
        """
        message = Message(role=role, content=content)
        self.recent_messages.append(message)

        # 일정 개수를 넘으면 요약
        if len(self.recent_messages) > self.summary_threshold:
            self._summarize()

    def _summarize(self) -> None:
        """최근 메시지들을 요약"""
        if not self.recent_messages:
            return

        # 간단한 요약 시뮬레이션
        topics = set()
        for msg in self.recent_messages:
            words = msg.content.split()
            if len(words) > 3:
                topics.add(words[0])

        summary_topics = ", ".join(list(topics)[:3])
        new_summary = f"대화 요약: 최근 {len(self.recent_messages)}개 메시지에서 {summary_topics}에 대해 논의함"

        if self.conversation_summary:
            self.conversation_summary += " | " + new_summary
        else:
            self.conversation_summary = new_summary

        # 요약된 메시지는 최근 3개만 유지
        self.recent_messages = self.recent_messages[-3:]

    def get_memory(self) -> str:
        """메모리 내용을 문자열로 반환"""
        result = []

        if self.conversation_summary:
            result.append(f"대화 요약:\n{self.conversation_summary}")

        if self.recent_messages:
            result.append("\n최근 메시지:")
            for msg in self.recent_messages:
                result.append(f"  {msg.role.upper()}: {msg.content}")

        return "\n".join(result) if result else "메모리가 비어있습니다."


class EntityMemory:
    """
    엔티티 메모리: 대화에서 추출한 주요 엔티티(개념, 사람 등)를 저장합니다.
    특정 정보에 대한 쿼리 성능이 높습니다.
    """

    def __init__(self):
        """EntityMemory 초기화"""
        self.entities: Dict[str, Any] = {}
        self.message_history: List[Message] = []

    def add_message(self, role: str, content: str) -> None:
        """
        메시지 추가 및 엔티티 추출

        Args:
            role (str): "user" 또는 "assistant"
            content (str): 메시지 내용
        """
        message = Message(role=role, content=content)
        self.message_history.append(message)

        # 엔티티 추출 (간단한 규칙 기반)
        self._extract_entities(content)

    def _extract_entities(self, text: str) -> None:
        """텍스트에서 엔티티 추출"""
        words = text.split()

        for word in words:
            if word.isupper() and len(word) > 1:
                # 대문자 단어를 엔티티로 취급
                self.entities[word] = self.entities.get(word, 0) + 1

        # 특정 패턴 추출 (예: "이름: XXX")
        if "이름:" in text:
            parts = text.split("이름:")
            if len(parts) > 1:
                name = parts[1].strip().split()[0]
                self.entities["person_name"] = name

    def get_entity(self, entity_name: str) -> Optional[Any]:
        """
        특정 엔티티 조회

        Args:
            entity_name (str): 엔티티 이름

        Returns:
            Optional[Any]: 엔티티 값
        """
        return self.entities.get(entity_name)

    def get_memory(self) -> str:
        """메모리 내용을 문자열로 반환"""
        if not self.entities:
            return "추출된 엔티티가 없습니다."

        result = ["주요 엔티티:"]
        for entity, value in self.entities.items():
            result.append(f"  {entity}: {value}")

        return "\n".join(result)


@dataclass
class Tool:
    """
    Tool 정의
    """
    name: str
    description: str
    func: Callable
    input_schema: Dict[str, Any]

    def execute(self, **kwargs) -> str:
        """
        도구 실행

        Returns:
            str: 실행 결과
        """
        try:
            result = self.func(**kwargs)
            return str(result)
        except Exception as e:
            return f"오류: {str(e)}"


class ToolRegistry:
    """
    Tool을 등록하고 관리하는 클래스입니다.
    """

    def __init__(self):
        """ToolRegistry 초기화"""
        self.tools: Dict[str, Tool] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        func: Callable,
        input_schema: Dict[str, Any],
    ) -> None:
        """
        도구 등록

        Args:
            name (str): 도구 이름
            description (str): 도구 설명
            func (Callable): 실행할 함수
            input_schema (Dict): 입력 스키마
        """
        tool = Tool(
            name=name,
            description=description,
            func=func,
            input_schema=input_schema,
        )
        self.tools[name] = tool
        print(f"✓ 도구 등록: {name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """
        도구 조회

        Args:
            name (str): 도구 이름

        Returns:
            Optional[Tool]: 도구 객체
        """
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        등록된 모든 도구 목록 반환

        Returns:
            List[Dict]: 도구 정보 리스트
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in self.tools.values()
        ]

    def execute_tool(self, name: str, **kwargs) -> str:
        """
        도구 실행

        Args:
            name (str): 도구 이름
            **kwargs: 도구 입력 파라미터

        Returns:
            str: 실행 결과
        """
        tool = self.get_tool(name)
        if not tool:
            return f"오류: '{name}' 도구를 찾을 수 없습니다."

        return tool.execute(**kwargs)


class ToolAgent:
    """
    도구를 사용하는 에이전트입니다.
    메모리를 유지하면서 도구를 활용하여 작업을 수행합니다.
    """

    def __init__(self, memory_type: MemoryType = MemoryType.BUFFER):
        """
        ToolAgent 초기화

        Args:
            memory_type (MemoryType): 메모리 타입
        """
        self.memory_type = memory_type
        self.conversation_context = ConversationContext(
            session_id=self._generate_session_id()
        )

        # 메모리 초기화
        if memory_type == MemoryType.BUFFER:
            self.memory = BufferMemory()
        elif memory_type == MemoryType.SUMMARY:
            self.memory = SummaryMemory()
        elif memory_type == MemoryType.ENTITY:
            self.memory = EntityMemory()
        else:
            self.memory = BufferMemory()

        # 도구 레지스트리
        self.tool_registry = ToolRegistry()
        self.action_history: List[Dict[str, Any]] = []

    def _generate_session_id(self) -> str:
        """세션 ID 생성"""
        return f"session_{int(time.time() * 1000)}"

    def register_tools(self) -> None:
        """표준 도구들을 등록합니다."""
        print(f"\n{'='*60}")
        print("🔧 도구 등록")
        print(f"{'='*60}\n")

        # 도구 1: 계산
        def calculator(expression: str) -> float:
            """수학식 계산"""
            try:
                return eval(expression)
            except:
                return 0.0

        self.tool_registry.register_tool(
            name="calculator",
            description="수학 식을 계산하는 도구",
            func=calculator,
            input_schema={"expression": "string"},
        )

        # 도구 2: 시간 조회
        def get_current_time() -> str:
            """현재 시간 반환"""
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.tool_registry.register_tool(
            name="get_time",
            description="현재 시간을 조회하는 도구",
            func=get_current_time,
            input_schema={},
        )

        # 도구 3: 정보 검색 (시뮬레이션)
        def search_info(query: str) -> str:
            """정보 검색"""
            results = {
                "python": "프로그래밍 언어",
                "langchain": "LLM 애플리케이션 프레임워크",
                "ai": "인공지능",
            }
            return results.get(query.lower(), "검색 결과 없음")

        self.tool_registry.register_tool(
            name="search",
            description="정보를 검색하는 도구",
            func=search_info,
            input_schema={"query": "string"},
        )

        # 도구 4: 메모리 저장
        def save_to_memory(key: str, value: str) -> str:
            """메모리에 정보 저장"""
            self.conversation_context.metadata[key] = value
            return f"저장됨: {key}={value}"

        self.tool_registry.register_tool(
            name="save_memory",
            description="메모리에 정보를 저장하는 도구",
            func=save_to_memory,
            input_schema={"key": "string", "value": "string"},
        )

        print("✓ 모든 도구 등록 완료\n")

    def add_user_message(self, content: str) -> None:
        """
        사용자 메시지 추가

        Args:
            content (str): 메시지 내용
        """
        self.memory.add_message("user", content)
        self.conversation_context.add_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        """
        어시스턴트 메시지 추가

        Args:
            content (str): 메시지 내용
        """
        self.memory.add_message("assistant", content)
        self.conversation_context.add_message("assistant", content)

    def think_and_act(self, user_input: str) -> str:
        """
        사용자 입력을 받아 도구를 사용하여 처리합니다.

        Args:
            user_input (str): 사용자 입력

        Returns:
            str: 결과 메시지
        """
        print(f"\n📨 사용자 입력: {user_input}")
        self.add_user_message(user_input)

        # 도구 선택 및 실행
        actions = []

        # 계산 요청 처리
        if "계산" in user_input or "+" in user_input or "-" in user_input:
            result = self.tool_registry.execute_tool("calculator", expression="2+3")
            actions.append({"tool": "calculator", "result": result})

        # 시간 조회 처리
        if "시간" in user_input or "지금" in user_input:
            result = self.tool_registry.execute_tool("get_time")
            actions.append({"tool": "get_time", "result": result})

        # 검색 처리
        if "검색" in user_input or "찾" in user_input:
            query = user_input.split("검색")[1].strip() if "검색" in user_input else "ai"
            result = self.tool_registry.execute_tool("search", query=query)
            actions.append({"tool": "search", "result": result})

        # 응답 생성
        if actions:
            response = self._generate_response(user_input, actions)
        else:
            response = "요청을 처리할 수 있는 도구를 찾지 못했습니다."

        # 히스토리 저장
        self.action_history.append({
            "input": user_input,
            "actions": actions,
            "response": response,
            "timestamp": time.time(),
        })

        self.add_assistant_message(response)
        return response

    def _generate_response(self, user_input: str, actions: List[Dict]) -> str:
        """
        도구 실행 결과 기반 응답 생성

        Args:
            user_input (str): 사용자 입력
            actions (List[Dict]): 실행한 도구 액션

        Returns:
            str: 생성된 응답
        """
        responses = []
        for action in actions:
            responses.append(f"{action['tool']}: {action['result']}")

        return f"처리 결과: {' | '.join(responses)}"

    def show_memory(self) -> None:
        """현재 메모리 상태 출력"""
        print(f"\n{'='*60}")
        print("📚 메모리 상태")
        print(f"{'='*60}\n")
        print(self.memory.get_memory())

    def show_tools(self) -> None:
        """등록된 도구 목록 출력"""
        print(f"\n{'='*60}")
        print("🔧 등록된 도구")
        print(f"{'='*60}\n")

        tools = self.tool_registry.list_tools()
        for tool in tools:
            print(f"• {tool['name']}: {tool['description']}")

    def get_session_summary(self) -> Dict[str, Any]:
        """세션 요약 반환"""
        return {
            "session_id": self.conversation_context.session_id,
            "memory_type": self.memory_type.value,
            "total_messages": self.conversation_context.get_message_count(),
            "total_actions": len(self.action_history),
            "registered_tools": len(self.tool_registry.tools),
        }


def example_buffer_memory():
    """BufferMemory 예제"""
    print("\n" + "=" * 70)
    print("예제 1: Buffer Memory")
    print("=" * 70)

    memory = BufferMemory(max_tokens=50)

    print("\n메시지 추가:")
    memory.add_message("user", "안녕하세요")
    memory.add_message("assistant", "반갑습니다")
    memory.add_message("user", "오늘 날씨가 좋네요")
    memory.add_message("assistant", "정말 좋은 날씨입니다")

    print("\n메모리 상태:")
    print(memory.get_memory())


def example_summary_memory():
    """SummaryMemory 예제"""
    print("\n" + "=" * 70)
    print("예제 2: Summary Memory")
    print("=" * 70)

    memory = SummaryMemory(summary_threshold=3)

    messages = [
        ("user", "파이썬에 대해 알려주세요"),
        ("assistant", "파이썬은 프로그래밍 언어입니다"),
        ("user", "장점은 뭐가 있나요?"),
        ("assistant", "쉽고 배우기 좋습니다"),
        ("user", "어디에 사용되나요?"),
        ("assistant", "웹, 데이터 분석, AI 등에 사용됩니다"),
    ]

    print("\n메시지 추가:")
    for role, content in messages:
        memory.add_message(role, content)
        print(f"  {role}: {content[:30]}...")

    print("\n메모리 상태:")
    print(memory.get_memory())


def example_entity_memory():
    """EntityMemory 예제"""
    print("\n" + "=" * 70)
    print("예제 3: Entity Memory")
    print("=" * 70)

    memory = EntityMemory()

    messages = [
        ("user", "제 이름: John Smith입니다"),
        ("user", "저는 Python과 JavaScript를 사용합니다"),
        ("assistant", "반갑습니다, John"),
    ]

    print("\n메시지 추가:")
    for role, content in messages:
        memory.add_message(role, content)
        print(f"  {role}: {content}")

    print("\n메모리 상태:")
    print(memory.get_memory())

    print("\n엔티티 조회:")
    if isinstance(memory, EntityMemory):
        for key in ["Python", "JavaScript", "person_name"]:
            value = memory.get_entity(key)
            if value:
                print(f"  {key}: {value}")


def example_tool_agent():
    """ToolAgent 예제"""
    print("\n" + "=" * 70)
    print("예제 4: Tool Agent with Memory")
    print("=" * 70)

    agent = ToolAgent(memory_type=MemoryType.BUFFER)
    agent.register_tools()
    agent.show_tools()

    # 도구를 사용한 상호작용
    interactions = [
        "2 + 3을 계산해주세요",
        "지금 몇 시인가요?",
        "파이썬에 대해 검색해주세요",
    ]

    print(f"\n{'='*60}")
    print("🤖 Agent 상호작용")
    print(f"{'='*60}")

    for user_input in interactions:
        response = agent.think_and_act(user_input)
        print(f"✓ 응답: {response}")

    agent.show_memory()

    print(f"\n{'='*60}")
    print("📊 세션 요약")
    print(f"{'='*60}\n")
    summary = agent.get_session_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def example_multiple_memory_types():
    """여러 메모리 타입 비교 예제"""
    print("\n" + "=" * 70)
    print("예제 5: 메모리 타입 비교")
    print("=" * 70)

    memory_types = [MemoryType.BUFFER, MemoryType.SUMMARY, MemoryType.ENTITY]

    for memory_type in memory_types:
        print(f"\n{'─'*60}")
        print(f"메모리 타입: {memory_type.value.upper()}")
        print(f"{'─'*60}")

        agent = ToolAgent(memory_type=memory_type)
        agent.register_tools()

        # 여러 상호작용 수행
        interactions = [
            "제 이름은 Alice입니다",
            "2 + 5를 계산해주세요",
            "시간을 알려주세요",
        ]

        for interaction in interactions:
            response = agent.think_and_act(interaction)

        agent.show_memory()


if __name__ == "__main__":
    """메인 실행 영역"""

    print("\n" + "#" * 70)
    print("# Week 6: 메모리 관리, Tool 생성, Tool Agent")
    print("#" * 70)

    # 예제 1: Buffer Memory
    example_buffer_memory()

    # 예제 2: Summary Memory
    example_summary_memory()

    # 예제 3: Entity Memory
    example_entity_memory()

    # 예제 4: Tool Agent
    example_tool_agent()

    # 예제 5: 메모리 타입 비교
    example_multiple_memory_types()

    print("\n" + "#" * 70)
    print("# 모든 예제 완료")
    print("#" * 70)
