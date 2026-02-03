"""
Week 09: ReAct Agent and Plan-Execute Agent Implementation
ReAct (Reasoning + Acting) 패턴과 Plan-Execute 패턴을 구현한 에이전트
"""

import json
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


class ActionType(Enum):
    """에이전트가 수행할 수 있는 액션 타입"""
    SEARCH = "search"
    CALCULATE = "calculate"
    ANALYZE = "analyze"
    PLAN = "plan"
    EXECUTE = "execute"
    FINISH = "finish"


@dataclass
class Thought:
    """에이전트의 사고 과정"""
    content: str
    confidence: float
    reasoning: str


@dataclass
class Action:
    """에이전트의 액션"""
    type: ActionType
    tool: str
    input: Dict[str, Any]
    metadata: Dict[str, Any] = None


@dataclass
class Observation:
    """액션 수행 후 관찰 결과"""
    content: str
    action: Action
    success: bool
    timestamp: str


class Tool(ABC):
    """도구의 기본 클래스"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """도구 실행"""
        pass

    def get_info(self) -> Dict[str, str]:
        """도구 정보 반환"""
        return {
            "name": self.name,
            "description": self.description
        }


class SearchTool(Tool):
    """검색 도구"""

    def __init__(self):
        super().__init__(
            "search",
            "인터넷에서 정보를 검색합니다"
        )
        self.knowledge_base = {
            "python": "Python은 고수준의 프로그래밍 언어입니다",
            "ai": "인공지능은 기계 학습 기술을 사용합니다",
            "agent": "에이전트는 자율적으로 작동하는 시스템입니다"
        }

    def execute(self, query: str) -> str:
        """검색 쿼리 실행"""
        query = query.lower()
        for key, value in self.knowledge_base.items():
            if key in query:
                return f"검색 결과: {value}"
        return f"'{query}'에 대한 결과를 찾을 수 없습니다"


class CalculateTool(Tool):
    """계산 도구"""

    def __init__(self):
        super().__init__(
            "calculate",
            "수학 연산을 수행합니다"
        )

    def execute(self, expression: str) -> str:
        """수학 표현식 계산"""
        try:
            result = eval(expression, {"__builtins__": {}})
            return f"계산 결과: {result}"
        except Exception as e:
            return f"계산 오류: {str(e)}"


class AnalyzeTool(Tool):
    """분석 도구"""

    def __init__(self):
        super().__init__(
            "analyze",
            "데이터를 분석합니다"
        )

    def execute(self, data: str) -> str:
        """데이터 분석"""
        lines = data.split('\n')
        analysis = {
            "총 줄 수": len(lines),
            "평균 길이": sum(len(line) for line in lines) / len(lines) if lines else 0,
            "최대 길이": max(len(line) for line in lines) if lines else 0
        }
        return f"분석 결과: {json.dumps(analysis, ensure_ascii=False, indent=2)}"


class ReActAgent:
    """ReAct (Reasoning + Acting) 에이전트"""

    def __init__(self, name: str = "ReAct Agent"):
        self.name = name
        self.tools = {
            "search": SearchTool(),
            "calculate": CalculateTool(),
            "analyze": AnalyzeTool()
        }
        self.max_iterations = 10
        self.memory: List[Dict[str, Any]] = []

    def register_tool(self, tool: Tool) -> None:
        """도구 등록"""
        self.tools[tool.name] = tool

    def think(self, query: str, context: str = "") -> Thought:
        """사고 과정 실행"""
        reasoning = f"질문: {query}\n컨텍스트: {context}"
        confidence = 0.8
        content = f"{self.name}이(가) '{query}'에 대해 생각 중입니다"

        return Thought(
            content=content,
            confidence=confidence,
            reasoning=reasoning
        )

    def plan_action(self, thought: Thought) -> Action:
        """생각을 바탕으로 액션 계획"""
        # 간단한 액션 선택 로직
        if "검색" in thought.content or "정보" in thought.content:
            tool = "search"
        elif "계산" in thought.content or "수학" in thought.content:
            tool = "calculate"
        else:
            tool = "analyze"

        return Action(
            type=ActionType(tool),
            tool=tool,
            input={"query": thought.content},
            metadata={"thought_confidence": thought.confidence}
        )

    def execute_action(self, action: Action) -> Observation:
        """액션 실행"""
        import datetime

        tool = self.tools.get(action.tool)
        if not tool:
            return Observation(
                content=f"도구 '{action.tool}'을(를) 찾을 수 없습니다",
                action=action,
                success=False,
                timestamp=datetime.datetime.now().isoformat()
            )

        try:
            result = tool.execute(**action.input)
            success = True
        except Exception as e:
            result = f"실행 오류: {str(e)}"
            success = False

        return Observation(
            content=result,
            action=action,
            success=success,
            timestamp=datetime.datetime.now().isoformat()
        )

    def run(self, query: str) -> Dict[str, Any]:
        """에이전트 실행"""
        print(f"\n{'='*60}")
        print(f"ReAct Agent: {query}")
        print(f"{'='*60}\n")

        context = ""

        for iteration in range(self.max_iterations):
            print(f"[Iteration {iteration + 1}]")

            # 사고
            thought = self.think(query, context)
            print(f"Thought: {thought.content}")
            print(f"Confidence: {thought.confidence}")

            # 액션 계획
            action = self.plan_action(thought)
            print(f"Action: {action.tool}({json.dumps(action.input, ensure_ascii=False)})")

            # 액션 실행
            observation = self.execute_action(action)
            print(f"Observation: {observation.content}")

            # 메모리에 저장
            self.memory.append({
                "iteration": iteration,
                "thought": thought,
                "action": action,
                "observation": observation
            })

            # 컨텍스트 업데이트
            context += f"\n[Step {iteration}] {observation.content}"

            # 종료 조건
            if observation.success and iteration > 0:
                print(f"\nFinal Answer: {observation.content}")
                break

            print()

        return {
            "query": query,
            "memory": self.memory,
            "final_context": context
        }


class PlanExecuteAgent:
    """Plan-Execute 패턴 에이전트"""

    def __init__(self, name: str = "Plan-Execute Agent"):
        self.name = name
        self.tools = {
            "search": SearchTool(),
            "calculate": CalculateTool(),
            "analyze": AnalyzeTool()
        }
        self.plan: List[Action] = []
        self.execution_log: List[Dict[str, Any]] = []

    def generate_plan(self, query: str) -> List[Action]:
        """질문에 대한 계획 생성"""
        plan = []

        # 간단한 계획 생성 로직
        if "검색" in query:
            plan.append(Action(
                type=ActionType.SEARCH,
                tool="search",
                input={"query": query}
            ))

        if "계산" in query or "수학" in query:
            plan.append(Action(
                type=ActionType.CALCULATE,
                tool="calculate",
                input={"expression": "2 + 2"}
            ))

        if len(plan) == 0:
            plan.append(Action(
                type=ActionType.ANALYZE,
                tool="analyze",
                input={"data": query}
            ))

        plan.append(Action(
            type=ActionType.FINISH,
            tool="finish",
            input={}
        ))

        return plan

    def execute_plan(self, plan: List[Action]) -> List[Observation]:
        """생성된 계획 실행"""
        observations = []
        import datetime

        for step, action in enumerate(plan):
            if action.type == ActionType.FINISH:
                obs = Observation(
                    content="계획 실행 완료",
                    action=action,
                    success=True,
                    timestamp=datetime.datetime.now().isoformat()
                )
            else:
                tool = self.tools.get(action.tool)
                if not tool:
                    content = f"도구 '{action.tool}'을(를) 찾을 수 없습니다"
                    success = False
                else:
                    try:
                        content = tool.execute(**action.input)
                        success = True
                    except Exception as e:
                        content = f"실행 오류: {str(e)}"
                        success = False

                obs = Observation(
                    content=content,
                    action=action,
                    success=success,
                    timestamp=datetime.datetime.now().isoformat()
                )

            observations.append(obs)
            self.execution_log.append({
                "step": step,
                "action": action,
                "observation": obs
            })

        return observations

    def run(self, query: str) -> Dict[str, Any]:
        """에이전트 실행"""
        print(f"\n{'='*60}")
        print(f"Plan-Execute Agent: {query}")
        print(f"{'='*60}\n")

        # 계획 생성
        print("[Step 1: Plan Generation]")
        self.plan = self.generate_plan(query)
        print(f"생성된 계획 ({len(self.plan)}개 단계):")
        for i, action in enumerate(self.plan, 1):
            print(f"  {i}. {action.tool}({json.dumps(action.input, ensure_ascii=False)})")

        # 계획 실행
        print("\n[Step 2: Execution]")
        observations = self.execute_plan(self.plan)

        for step, obs in enumerate(observations, 1):
            print(f"\nStep {step} Result: {obs.content}")

        return {
            "query": query,
            "plan": self.plan,
            "execution_log": self.execution_log,
            "observations": observations
        }


def main():
    """메인 함수"""

    # ReAct Agent 테스트
    react_agent = ReActAgent()
    react_result = react_agent.run("Python에 대해 검색하고 분석해주세요")

    print("\n" + "="*60)
    print("ReAct Agent 결과 요약")
    print("="*60)
    print(f"쿼리: {react_result['query']}")
    print(f"실행 단계: {len(react_result['memory'])}")

    # Plan-Execute Agent 테스트
    print("\n")
    plan_execute_agent = PlanExecuteAgent()
    plan_result = plan_execute_agent.run("인공지능에 대해 검색하고 분석해주세요")

    print("\n" + "="*60)
    print("Plan-Execute Agent 결과 요약")
    print("="*60)
    print(f"쿼리: {plan_result['query']}")
    print(f"계획 단계: {len(plan_result['plan'])}")
    print(f"실행 로그: {len(plan_result['execution_log'])} 단계")


if __name__ == "__main__":
    main()
