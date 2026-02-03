"""
Week 11: Multi-Agent System, Supervisor Pattern, and Checkpoint Implementation
여러 에이전트를 조율하는 Supervisor 패턴과 Checkpoint를 구현한 다중 에이전트 시스템
"""

import json
import uuid
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod


class AgentRole(Enum):
    """에이전트의 역할"""
    PLANNER = "planner"
    EXECUTOR = "executor"
    ANALYZER = "analyzer"
    REVIEWER = "reviewer"
    SUPERVISOR = "supervisor"


class TaskStatus(Enum):
    """작업 상태"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Task:
    """작업 정의"""
    id: str
    description: str
    assigned_to: str
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['status'] = self.status.value
        return data


@dataclass
class Checkpoint:
    """작업 체크포인트"""
    id: str
    task_id: str
    agent_id: str
    status: str
    state: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)


class Agent(ABC):
    """에이전트의 기본 클래스"""

    def __init__(self, agent_id: str, name: str, role: AgentRole):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.tasks: List[Task] = []
        self.checkpoints: List[Checkpoint] = []
        self.state: Dict[str, Any] = {}

    @abstractmethod
    def execute_task(self, task: Task) -> str:
        """작업 실행"""
        pass

    def save_checkpoint(self, task_id: str, state: Dict[str, Any], message: str = "") -> Checkpoint:
        """체크포인트 저장"""
        checkpoint = Checkpoint(
            id=str(uuid.uuid4()),
            task_id=task_id,
            agent_id=self.agent_id,
            status="saved",
            state=state,
            message=message
        )
        self.checkpoints.append(checkpoint)
        return checkpoint

    def load_checkpoint(self, task_id: str) -> Optional[Checkpoint]:
        """체크포인트 로드"""
        for checkpoint in reversed(self.checkpoints):
            if checkpoint.task_id == task_id:
                return checkpoint
        return None

    def get_info(self) -> Dict[str, Any]:
        """에이전트 정보"""
        return {
            "id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "tasks_count": len(self.tasks),
            "checkpoints_count": len(self.checkpoints)
        }


class PlannerAgent(Agent):
    """계획을 수립하는 에이전트"""

    def __init__(self, agent_id: str = None):
        agent_id = agent_id or str(uuid.uuid4())
        super().__init__(agent_id, "Planner", AgentRole.PLANNER)

    def execute_task(self, task: Task) -> str:
        """작업 계획 수립"""
        plan = {
            "goal": task.description,
            "subtasks": [
                "요구사항 분석",
                "리소스 할당",
                "타임라인 설정",
                "위험 평가"
            ],
            "timeline": "3일",
            "resources": ["팀원 2명", "도구 3개"]
        }

        result = f"계획 완료: {json.dumps(plan, ensure_ascii=False, indent=2)}"

        # 체크포인트 저장
        self.save_checkpoint(task.id, {"plan": plan}, "계획 수립 완료")

        return result


class ExecutorAgent(Agent):
    """작업을 실행하는 에이전트"""

    def __init__(self, agent_id: str = None):
        agent_id = agent_id or str(uuid.uuid4())
        super().__init__(agent_id, "Executor", AgentRole.EXECUTOR)

    def execute_task(self, task: Task) -> str:
        """작업 실행"""
        steps = [
            "1단계: 환경 설정",
            "2단계: 필요 라이브러리 설치",
            "3단계: 메인 로직 구현",
            "4단계: 통합 테스트"
        ]

        result = f"작업 실행: {', '.join(steps)}"

        # 체크포인트 저장
        self.save_checkpoint(task.id, {"steps": steps}, "작업 실행 진행 중")

        return result


class AnalyzerAgent(Agent):
    """작업 결과를 분석하는 에이전트"""

    def __init__(self, agent_id: str = None):
        agent_id = agent_id or str(uuid.uuid4())
        super().__init__(agent_id, "Analyzer", AgentRole.ANALYZER)

    def execute_task(self, task: Task) -> str:
        """작업 분석"""
        analysis = {
            "성능": "양호",
            "오류율": "0.5%",
            "응답시간": "평균 150ms",
            "품질점수": 8.5
        }

        result = f"분석 완료: {json.dumps(analysis, ensure_ascii=False, indent=2)}"

        # 체크포인트 저장
        self.save_checkpoint(task.id, {"analysis": analysis}, "분석 완료")

        return result


class ReviewerAgent(Agent):
    """작업을 검토하는 에이전트"""

    def __init__(self, agent_id: str = None):
        agent_id = agent_id or str(uuid.uuid4())
        super().__init__(agent_id, "Reviewer", AgentRole.REVIEWER)

    def execute_task(self, task: Task) -> str:
        """작업 검토"""
        review = {
            "상태": "승인됨",
            "의견": "요구사항 충족",
            "개선사항": [
                "성능 최적화 고려",
                "문서화 개선"
            ],
            "승인자": self.name
        }

        result = f"검토 완료: {json.dumps(review, ensure_ascii=False, indent=2)}"

        # 체크포인트 저장
        self.save_checkpoint(task.id, {"review": review}, "검토 완료")

        return result


class SupervisorAgent:
    """여러 에이전트를 조율하는 감독 에이전트"""

    def __init__(self, supervisor_id: str = None):
        self.supervisor_id = supervisor_id or str(uuid.uuid4())
        self.name = "Supervisor"
        self.agents: Dict[AgentRole, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        self.execution_history: List[Dict[str, Any]] = []

    def register_agent(self, agent: Agent) -> None:
        """에이전트 등록"""
        self.agents[agent.role] = agent
        print(f"✓ {agent.name} 에이전트 등록 (ID: {agent.agent_id})")

    def create_task(self, description: str, agent_role: AgentRole,
                   dependencies: List[str] = None) -> Task:
        """작업 생성"""
        task = Task(
            id=str(uuid.uuid4()),
            description=description,
            assigned_to=agent_role.value,
            dependencies=dependencies or []
        )
        self.tasks[task.id] = task
        self.task_queue.append(task.id)
        return task

    def can_execute_task(self, task: Task) -> bool:
        """작업 실행 가능 여부 확인"""
        # 의존성이 완료되었는지 확인
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """작업 실행"""
        task = self.tasks.get(task_id)
        if not task:
            return {"status": "error", "message": "작업을 찾을 수 없습니다"}

        if not self.can_execute_task(task):
            task.status = TaskStatus.BLOCKED
            return {"status": "blocked", "message": "의존성 작업 대기 중"}

        # 할당된 에이전트 찾기
        agent = None
        for agent_role, agent_obj in self.agents.items():
            if agent_role.value == task.assigned_to:
                agent = agent_obj
                break

        if not agent:
            task.status = TaskStatus.FAILED
            return {"status": "error", "message": f"할당된 에이전트를 찾을 수 없습니다: {task.assigned_to}"}

        # 작업 실행
        task.status = TaskStatus.IN_PROGRESS

        try:
            result = agent.execute_task(task)
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now().isoformat()

            execution_record = {
                "task_id": task_id,
                "agent": agent.name,
                "status": "success",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            task.status = TaskStatus.FAILED
            result = f"오류: {str(e)}"
            execution_record = {
                "task_id": task_id,
                "agent": agent.name,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

        self.execution_history.append(execution_record)
        return execution_record

    def run_workflow(self, tasks_description: str) -> Dict[str, Any]:
        """워크플로우 실행"""
        print(f"\n{'='*60}")
        print(f"Supervisor: Multi-Agent 워크플로우 실행")
        print(f"{'='*60}\n")

        # 작업 생성
        print("작업 정의:")
        task1 = self.create_task("프로젝트 계획 수립", AgentRole.PLANNER)
        print(f"  1. {task1.description}")

        task2 = self.create_task("계획에 따라 구현", AgentRole.EXECUTOR, [task1.id])
        print(f"  2. {task2.description} (의존성: 작업 1)")

        task3 = self.create_task("구현 결과 분석", AgentRole.ANALYZER, [task2.id])
        print(f"  3. {task3.description} (의존성: 작업 2)")

        task4 = self.create_task("최종 검토", AgentRole.REVIEWER, [task3.id])
        print(f"  4. {task4.description} (의존성: 작업 3)")

        # 작업 실행
        print("\n작업 실행 순서:")
        for task_id in self.task_queue:
            print(f"\n[작업 실행: {self.tasks[task_id].id[:8]}...]")
            result = self.execute_task(task_id)
            print(f"  상태: {result['status']}")
            if 'result' in result:
                print(f"  결과: {result['result'][:100]}...")

        # 최종 요약
        completed_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)

        return {
            "total_tasks": len(self.tasks),
            "completed": completed_count,
            "failed": failed_count,
            "execution_history": self.execution_history
        }

    def get_agent_stats(self) -> Dict[str, Any]:
        """에이전트 통계"""
        stats = {
            "supervisor_id": self.supervisor_id,
            "registered_agents": len(self.agents),
            "agents": {}
        }

        for role, agent in self.agents.items():
            stats["agents"][agent.name] = {
                "role": role.value,
                "id": agent.agent_id,
                "tasks_count": len(agent.tasks),
                "checkpoints_count": len(agent.checkpoints)
            }

        return stats

    def save_state(self) -> Dict[str, Any]:
        """전체 상태 저장"""
        return {
            "supervisor_id": self.supervisor_id,
            "timestamp": datetime.now().isoformat(),
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "execution_history": self.execution_history,
            "agent_stats": self.get_agent_stats()
        }

    def load_state(self, state: Dict[str, Any]) -> None:
        """상태 복원"""
        print(f"상태 복원: {state['timestamp']}")
        # 실제 구현에서는 상태를 복원하는 로직


def main():
    """메인 함수"""

    # Supervisor 생성
    supervisor = SupervisorAgent()

    # 에이전트 등록
    planner = PlannerAgent()
    executor = ExecutorAgent()
    analyzer = AnalyzerAgent()
    reviewer = ReviewerAgent()

    supervisor.register_agent(planner)
    supervisor.register_agent(executor)
    supervisor.register_agent(analyzer)
    supervisor.register_agent(reviewer)

    # 워크플로우 실행
    workflow_result = supervisor.run_workflow("AI 에이전트 시스템 개발")

    # 결과 출력
    print("\n" + "="*60)
    print("Multi-Agent 시스템 완료 요약")
    print("="*60)
    print(f"전체 작업: {workflow_result['total_tasks']}")
    print(f"완료된 작업: {workflow_result['completed']}")
    print(f"실패한 작업: {workflow_result['failed']}")

    # 에이전트 통계
    print("\n에이전트 통계:")
    stats = supervisor.get_agent_stats()
    for agent_name, agent_info in stats["agents"].items():
        print(f"  {agent_name}: {agent_info['checkpoints_count']}개 체크포인트")

    # 상태 저장
    print("\n상태 저장:")
    saved_state = supervisor.save_state()
    print(f"  시간: {saved_state['timestamp']}")
    print(f"  작업 수: {len(saved_state['tasks'])}")


if __name__ == "__main__":
    main()
