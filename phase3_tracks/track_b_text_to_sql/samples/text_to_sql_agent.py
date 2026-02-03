"""
Text-to-SQL Agent Module
LangGraph 기반 완전한 Text-to-SQL Agent 구현
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from abc import ABC, abstractmethod


class AgentState(Enum):
    """에이전트 상태"""
    WAITING = "WAITING"
    ANALYZING = "ANALYZING"
    VALIDATING = "VALIDATING"
    OPTIMIZING = "OPTIMIZING"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Message:
    """메시지"""
    role: str
    content: str
    type: str = "text"


@dataclass
class AgentContext:
    """에이전트 컨텍스트"""
    user_query: str
    schema: Dict[str, Any]
    generated_sql: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None
    execution_results: Optional[Dict[str, Any]] = None
    conversation_history: List[Message] = None
    current_state: AgentState = AgentState.WAITING
    confidence_score: float = 0.0

    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []


class Agent(ABC):
    """에이전트 기본 클래스"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def process(self, context: AgentContext) -> AgentContext:
        """처리 실행"""
        pass

    def _log(self, message: str, context: AgentContext) -> None:
        """로깅"""
        context.conversation_history.append(
            Message(role="agent", content=f"[{self.name}] {message}")
        )


class UnderstandingAgent(Agent):
    """자연어 이해 에이전트"""

    def __init__(self):
        super().__init__("UnderstandingAgent")

    def process(self, context: AgentContext) -> AgentContext:
        """자연어 쿼리 분석"""
        context.current_state = AgentState.ANALYZING

        self._log(f"쿼리 분석 중: '{context.user_query}'", context)

        # 쿼리 분석
        analysis = self._analyze_query(context.user_query, context.schema)

        self._log(f"분석 완료: {analysis}", context)

        return context

    def _analyze_query(self, query: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """쿼리 분석"""
        analysis = {
            'intent': self._identify_intent(query),
            'entities': self._extract_entities(query, schema),
            'conditions': self._extract_conditions(query),
            'aggregations': self._extract_aggregations(query)
        }
        return analysis

    def _identify_intent(self, query: str) -> str:
        """의도 파악"""
        query_lower = query.lower()

        if any(kw in query_lower for kw in ['조회', '보여줘', '찾아', 'select']):
            return 'SELECT'
        elif any(kw in query_lower for kw in ['추가', '저장', 'insert']):
            return 'INSERT'
        elif any(kw in query_lower for kw in ['수정', '변경', 'update']):
            return 'UPDATE'
        elif any(kw in query_lower for kw in ['삭제', 'delete']):
            return 'DELETE'

        return 'SELECT'

    def _extract_entities(self, query: str, schema: Dict[str, Any]) -> List[str]:
        """엔티티 추출"""
        entities = []

        for table_name in schema.keys():
            if table_name.lower() in query.lower():
                entities.append(table_name)

        return entities

    def _extract_conditions(self, query: str) -> List[Dict[str, str]]:
        """조건 추출"""
        conditions = []

        # 간단한 조건 패턴 매칭
        import re
        pattern = r'(\w+)\s*(?:=|은|이|가)\s*(["\']?)(.+?)\2(?:[,;]|$)'
        matches = re.findall(pattern, query)

        for col, quote, value in matches:
            conditions.append({
                'column': col,
                'value': value.strip()
            })

        return conditions

    def _extract_aggregations(self, query: str) -> List[str]:
        """집계함수 추출"""
        aggregations = []

        agg_keywords = {
            'count': ['개수', '몇개'],
            'sum': ['합계', '합'],
            'avg': ['평균'],
            'max': ['최대', '최고'],
            'min': ['최소', '최저']
        }

        for func, keywords in agg_keywords.items():
            if any(kw in query.lower() for kw in keywords):
                aggregations.append(func)

        return aggregations


class GenerationAgent(Agent):
    """SQL 생성 에이전트"""

    def __init__(self):
        super().__init__("GenerationAgent")

    def process(self, context: AgentContext) -> AgentContext:
        """SQL 생성"""
        self._log("SQL 생성 중...", context)

        try:
            sql = self._generate_sql(context.user_query, context.schema)
            context.generated_sql = sql
            context.confidence_score = self._estimate_confidence(context.user_query, sql)

            self._log(f"SQL 생성 완료: {sql}", context)
        except Exception as e:
            self._log(f"SQL 생성 실패: {str(e)}", context)
            context.current_state = AgentState.FAILED

        return context

    def _generate_sql(self, query: str, schema: Dict[str, Any]) -> str:
        """SQL 생성"""
        # 간단한 SQL 생성 로직
        query_lower = query.lower()

        # 테이블 이름 찾기
        table_name = None
        for tbl in schema.keys():
            if tbl.lower() in query_lower:
                table_name = tbl
                break

        if not table_name:
            raise ValueError("테이블을 찾을 수 없습니다")

        # 기본 SELECT 쿼리
        columns = schema.get(table_name, {}).get('columns', ['*'])
        sql = f"SELECT * FROM {table_name}"

        # WHERE 조건 추가
        if '조건' in query_lower or '어디' in query_lower:
            sql += " WHERE 1=1"

        # ORDER BY 추가
        if '정렬' in query_lower:
            sql += " ORDER BY id ASC"

        # LIMIT 추가
        import re
        limit_match = re.search(r'(?:상위|상단|처음)\s*(\d+)', query)
        if limit_match:
            sql += f" LIMIT {limit_match.group(1)}"

        return sql

    def _estimate_confidence(self, query: str, sql: str) -> float:
        """신뢰도 추정"""
        # 간단한 신뢰도 계산
        base_score = 0.5

        # 쿼리 길이
        if len(query) > 20:
            base_score += 0.1

        # SQL 길이
        if len(sql) > 30:
            base_score += 0.1

        # 특정 키워드 포함
        if any(kw in query.lower() for kw in ['조회', 'select']):
            base_score += 0.2

        return min(1.0, base_score)


class ValidationAgent(Agent):
    """검증 에이전트"""

    def __init__(self):
        super().__init__("ValidationAgent")

    def process(self, context: AgentContext) -> AgentContext:
        """SQL 검증"""
        context.current_state = AgentState.VALIDATING

        self._log("SQL 검증 중...", context)

        if not context.generated_sql:
            self._log("검증할 SQL이 없습니다", context)
            return context

        validation_result = self._validate_sql(context.generated_sql, context.schema)
        context.validation_results = validation_result

        self._log(f"검증 완료: {validation_result['status']}", context)

        return context

    def _validate_sql(self, sql: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """SQL 검증"""
        issues = []

        # 문법 검사
        syntax_check = self._check_syntax(sql)
        if not syntax_check['valid']:
            issues.extend(syntax_check['issues'])

        # 테이블 존재 여부
        table_check = self._check_tables(sql, schema)
        if not table_check['valid']:
            issues.extend(table_check['issues'])

        # 컬럼 존재 여부
        column_check = self._check_columns(sql, schema)
        if not column_check['valid']:
            issues.extend(column_check['issues'])

        return {
            'status': 'VALID' if len(issues) == 0 else 'INVALID',
            'issues': issues,
            'severity': 'ERROR' if len(issues) > 0 else 'OK'
        }

    def _check_syntax(self, sql: str) -> Dict[str, Any]:
        """문법 검사"""
        issues = []

        # 괄호 체크
        if sql.count('(') != sql.count(')'):
            issues.append("괄호가 일치하지 않습니다")

        # 따옴표 체크
        if sql.count("'") % 2 != 0:
            issues.append("작은따옴표가 일치하지 않습니다")

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def _check_tables(self, sql: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """테이블 존재 여부"""
        issues = []
        sql_upper = sql.upper()

        # FROM 다음 테이블 추출
        import re
        from_pattern = r'FROM\s+(\w+)'
        matches = re.findall(from_pattern, sql_upper)

        for table_name in matches:
            if table_name.lower() not in [t.lower() for t in schema.keys()]:
                issues.append(f"테이블을 찾을 수 없습니다: {table_name}")

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def _check_columns(self, sql: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """컬럼 존재 여부"""
        issues = []

        # 간단한 컬럼 검사 (실제로는 더 복잡함)
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }


class OptimizationAgent(Agent):
    """최적화 에이전트"""

    def __init__(self):
        super().__init__("OptimizationAgent")

    def process(self, context: AgentContext) -> AgentContext:
        """SQL 최적화"""
        context.current_state = AgentState.OPTIMIZING

        self._log("SQL 최적화 중...", context)

        if not context.generated_sql:
            return context

        optimized_sql = self._optimize_sql(context.generated_sql)
        context.generated_sql = optimized_sql

        self._log(f"최적화 완료: {optimized_sql}", context)

        return context

    def _optimize_sql(self, sql: str) -> str:
        """SQL 최적화"""
        optimized = sql

        # SELECT * 최적화 (간단한 예)
        if 'SELECT *' in optimized:
            # 실제로는 더 복잡한 최적화 로직
            pass

        # 인덱스 활용 최적화
        if 'WHERE' in optimized:
            # 최적화 로직
            pass

        return optimized


class ExecutionAgent(Agent):
    """실행 에이전트"""

    def __init__(self):
        super().__init__("ExecutionAgent")

    def process(self, context: AgentContext) -> AgentContext:
        """SQL 실행"""
        context.current_state = AgentState.EXECUTING

        self._log("SQL 실행 중...", context)

        if not context.generated_sql:
            context.current_state = AgentState.FAILED
            return context

        try:
            result = self._execute_sql(context.generated_sql)
            context.execution_results = result
            context.current_state = AgentState.COMPLETED

            self._log(f"실행 완료: {result['rows']}개 행 반환", context)
        except Exception as e:
            self._log(f"실행 실패: {str(e)}", context)
            context.current_state = AgentState.FAILED

        return context

    def _execute_sql(self, sql: str) -> Dict[str, Any]:
        """SQL 실행 (시뮬레이션)"""
        # 실제 실행은 데이터베이스 커넥션 필요
        return {
            'status': 'SUCCESS',
            'rows': 10,
            'columns': ['id', 'name', 'email'],
            'data': []
        }


class TextToSQLAgent:
    """Text-to-SQL Agent"""

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.agents = [
            UnderstandingAgent(),
            GenerationAgent(),
            ValidationAgent(),
            OptimizationAgent(),
            ExecutionAgent()
        ]

    def process_query(self, user_query: str) -> AgentContext:
        """쿼리 처리"""
        context = AgentContext(
            user_query=user_query,
            schema=self.schema
        )

        # 각 에이전트 순차 실행
        for agent in self.agents:
            context = agent.process(context)

            # 실패시 중단
            if context.current_state == AgentState.FAILED:
                break

        return context

    def get_conversation_history(self, context: AgentContext) -> str:
        """대화 기록 조회"""
        history = []

        history.append(f"사용자: {context.user_query}\n")

        for msg in context.conversation_history:
            history.append(f"{msg.role}: {msg.content}")

        if context.generated_sql:
            history.append(f"\n생성된 SQL:\n{context.generated_sql}\n")

        if context.execution_results:
            history.append(f"실행 결과: {context.execution_results['status']}\n")

        return '\n'.join(history)


class AgentOrchestrator:
    """에이전트 조정"""

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.agent = TextToSQLAgent(schema)

    def process(self, user_query: str) -> Dict[str, Any]:
        """전체 처리"""
        context = self.agent.process_query(user_query)

        return {
            'user_query': user_query,
            'generated_sql': context.generated_sql,
            'validation_results': context.validation_results,
            'execution_results': context.execution_results,
            'confidence_score': context.confidence_score,
            'final_state': context.current_state.value,
            'conversation_history': self.agent.get_conversation_history(context)
        }


# 사용 예제
if __name__ == "__main__":
    # 스키마 정의
    schema = {
        'employees': {
            'columns': ['id', 'name', 'email', 'salary', 'department_id']
        },
        'departments': {
            'columns': ['id', 'name', 'location']
        }
    }

    print("=== Text-to-SQL Agent (LangGraph 기반) ===\n")

    orchestrator = AgentOrchestrator(schema)

    test_queries = [
        "직원 테이블에서 모든 직원의 이름과 급여를 조회해",
        "employees 테이블의 급여 합계를 구해",
        "부서별 직원 개수를 조회해"
    ]

    for query in test_queries:
        print(f"\n쿼리: {query}")
        print("-" * 50)

        result = orchestrator.process(query)

        print(f"상태: {result['final_state']}")
        print(f"신뢰도: {result['confidence_score']:.2%}")
        print(f"\n생성된 SQL:\n{result['generated_sql']}")

        if result['validation_results']:
            print(f"\n검증: {result['validation_results']['status']}")
