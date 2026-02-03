# Week 20: Agent 구현 (스키마 인식, 쿼리 검증)

## 학습 목표
- 스키마 인식 기능을 갖춘 SQL Agent 구현
- 자동 쿼리 검증 및 실행 시스템 개발
- 에러 처리 및 재시도 메커니즘 구축
- Agent 아키텍처의 실제 구현 학습

## O'Reilly 리소스
- **"LLM Powered Applications"** - Aaron Tan
- **"Agents, Tools, and Frameworks"** - Multiple Contributors
- **"Enterprise Integration Patterns"** (Chapter 3-4) - Gregor Hohpe

## 핵심 개념

### 1. SQL Agent 아키텍처
```
┌─────────────────────────────────────────┐
│        사용자 자연어 입력                 │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        Agent Decision Loop               │
├──────────────────────────────────────────┤
│  1. Question 분석                        │
│  2. 필요한 Tool 선택 (SQL 생성, 검증)   │
│  3. Tool 실행                            │
│  4. 결과 검토 (성공? 재시도?)           │
│  5. 최종 답변 생성                       │
└──────────────────┬──────────────────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
┌────▼────┐  ┌────▼────┐  ┌────▼────┐
│ Schema  │  │SQL Gen  │  │ Query   │
│ Tool    │  │ Tool    │  │Executor │
└─────────┘  └─────────┘  └────────┘
     │             │             │
     └─────────────┼─────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        최종 결과 및 설명                 │
└──────────────────────────────────────────┘
```

### 2. 기본 SQL Agent 구현
```python
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import sqlite3

@dataclass
class QueryResult:
    """쿼리 실행 결과"""
    success: bool
    data: Optional[List[Dict]] = None
    error: Optional[str] = None
    sql: Optional[str] = None
    execution_time: Optional[float] = None

class SchemaAwareAgent:
    """스키마 인식 SQL Agent"""

    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.schema_info = self._extract_schema()
        self.query_history = []

    def _extract_schema(self) -> str:
        """데이터베이스 스키마 추출"""
        cursor = self.conn.cursor()

        # 모든 테이블 정보 추출
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]

        schema_info = "Database Schema:\n"
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            schema_info += f"\nTable: {table}\n"
            schema_info += "Columns:\n"
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                notnull = "NOT NULL" if col[3] else "NULL"
                schema_info += f"  - {col_name} ({col_type}, {notnull})\n"

        return schema_info

    def query(self, user_question: str) -> Dict[str, Any]:
        """자연어 질문을 처리하고 SQL을 생성/실행"""
        return {
            'question': user_question,
            'schema': self.schema_info,
            'steps': [
                self._understand_question(user_question),
                self._generate_sql(user_question),
                self._validate_sql(),
                self._execute_sql(),
                self._format_result()
            ]
        }

    def _understand_question(self, question: str) -> Dict:
        """질문 분석"""
        return {
            'step': 'Understanding Question',
            'input': question,
            'tables_needed': [],  # LLM으로 판단
            'operations': []      # SELECT, JOIN, GROUP BY 등
        }

    def _generate_sql(self, question: str) -> Dict:
        """SQL 생성 (LLM 호출)"""
        return {
            'step': 'Generate SQL',
            'prompt': self._build_prompt(question),
            'generated_sql': ""  # LLM 응답
        }

    def _validate_sql(self) -> Dict:
        """SQL 검증"""
        return {
            'step': 'Validate SQL',
            'syntax_valid': True,
            'schema_compatible': True,
            'warnings': []
        }

    def _execute_sql(self) -> QueryResult:
        """SQL 실행"""
        pass

    def _format_result(self) -> Dict:
        """결과 포맷팅"""
        pass

    def _build_prompt(self, question: str) -> str:
        """프롬프트 구성"""
        return f"""You are a SQL expert.

{self.schema_info}

Generate a SQL query to answer this question: {question}

Return only the SQL query, no explanation.
"""
```

### 3. 쿼리 검증 시스템
```python
class QueryValidator:
    """SQL 쿼리 검증"""

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.validation_rules = []

    def validate(self, query: str) -> Dict[str, Any]:
        """쿼리 종합 검증"""
        return {
            'syntax': self._validate_syntax(query),
            'schema': self._validate_schema(query),
            'performance': self._check_performance(query),
            'security': self._check_security(query),
            'valid': all([
                self._validate_syntax(query),
                self._validate_schema(query),
                self._check_security(query)
            ])
        }

    def _validate_syntax(self, query: str) -> bool:
        """SQL 문법 검증"""
        try:
            # sqlparse 라이브러리 사용
            import sqlparse
            parsed = sqlparse.parse(query)
            return len(parsed) > 0 and parsed[0].get_type() in (
                'SELECT', 'INSERT', 'UPDATE', 'DELETE'
            )
        except:
            return False

    def _validate_schema(self, query: str) -> bool:
        """스키마 호환성 검증"""
        # 쿼리에 사용된 테이블/컬럼이 스키마에 존재하는지 확인
        import sqlparse

        parsed = sqlparse.parse(query)[0]
        tables_used = self._extract_tables(parsed)
        columns_used = self._extract_columns(parsed)

        for table in tables_used:
            if table.lower() not in self.schema.get('tables', {}):
                return False

        return True

    def _extract_tables(self, parsed_query) -> List[str]:
        """쿼리에서 테이블명 추출"""
        tables = []
        # 구현
        return tables

    def _extract_columns(self, parsed_query) -> List[str]:
        """쿼리에서 컬럼명 추출"""
        columns = []
        # 구현
        return columns

    def _check_performance(self, query: str) -> Dict:
        """성능 이슈 감지"""
        return {
            'has_select_star': '*' in query and 'SELECT *' in query.upper(),
            'has_join_without_on': 'JOIN' in query.upper() and 'ON' not in query.upper(),
            'has_subquery': '(' in query and 'SELECT' in query.upper()
        }

    def _check_security(self, query: str) -> bool:
        """SQL Injection 등 보안 검사"""
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER']
        for keyword in dangerous_keywords:
            if keyword in query.upper():
                return False
        return True
```

### 4. 에러 처리 및 재시도
```python
class ErrorHandler:
    """에러 처리 및 재시도 관리"""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_count = 0

    def handle_error(self, error: Exception, context: Dict) -> Dict:
        """에러 처리"""
        error_type = type(error).__name__

        if error_type == 'OperationalError':
            return self._handle_db_error(error, context)
        elif error_type == 'SyntaxError':
            return self._handle_syntax_error(error, context)
        else:
            return self._handle_unknown_error(error, context)

    def _handle_db_error(self, error: Exception, context: Dict) -> Dict:
        """데이터베이스 에러 처리"""
        error_msg = str(error)

        if 'no such table' in error_msg.lower():
            return {
                'type': 'table_not_found',
                'recovery': 'Check table name against schema',
                'retry': True
            }
        elif 'no such column' in error_msg.lower():
            return {
                'type': 'column_not_found',
                'recovery': 'Check column name against schema',
                'retry': True
            }
        else:
            return {
                'type': 'generic_db_error',
                'message': error_msg,
                'retry': False
            }

    def _handle_syntax_error(self, error: Exception, context: Dict) -> Dict:
        """SQL 문법 에러 처리"""
        return {
            'type': 'syntax_error',
            'recovery': 'Regenerate SQL with better prompt',
            'retry': True
        }

    def _handle_unknown_error(self, error: Exception, context: Dict) -> Dict:
        """미알려 에러 처리"""
        return {
            'type': 'unknown_error',
            'message': str(error),
            'retry': False
        }

    def should_retry(self) -> bool:
        """재시도 가능 여부"""
        return self.retry_count < self.max_retries
```

### 5. 통합 Agent 클래스
```python
class TextToSQLAgent:
    """완전한 Text-to-SQL Agent"""

    def __init__(self, db_path: str, llm_client):
        self.db = sqlite3.connect(db_path)
        self.llm = llm_client
        self.schema_agent = SchemaAwareAgent(self.db)
        self.validator = QueryValidator(self.schema_agent.schema_info)
        self.error_handler = ErrorHandler()

    def process_question(self, question: str) -> Dict[str, Any]:
        """질문 처리 전체 흐름"""
        attempt = 0
        last_error = None

        while attempt < 3:
            try:
                # 1. 프롬프트 생성
                prompt = self.schema_agent._build_prompt(question)

                # 2. SQL 생성 (LLM)
                generated_sql = self.llm.generate_sql(prompt)

                # 3. 검증
                validation = self.validator.validate(generated_sql)
                if not validation['valid']:
                    raise ValueError(f"Validation failed: {validation}")

                # 4. 실행
                result = self.db.execute(generated_sql).fetchall()

                return {
                    'success': True,
                    'question': question,
                    'sql': generated_sql,
                    'result': result,
                    'attempts': attempt + 1
                }

            except Exception as e:
                last_error = e
                attempt += 1
                if attempt < 3:
                    # 재시도 전 프롬프트 개선
                    question = self._improve_question(question, str(e))

        return {
            'success': False,
            'question': question,
            'error': str(last_error),
            'attempts': attempt
        }

    def _improve_question(self, question: str, error_msg: str) -> str:
        """에러 기반 질문 개선"""
        return f"{question} [Previous error: {error_msg}]"
```

## 실습 과제

### 과제 1: 기본 Agent 구현
```python
# 요구사항:
# 1. SchemaAwareAgent 완전 구현
# 2. 5개 이상의 테이블을 가진 샘플 DB 생성
# 3. Agent로 10개의 질문 처리
# 4. 성공/실패 비율 기록

def create_sample_db():
    """샘플 데이터베이스 생성"""
    # customers, orders, products, categories, reviews 테이블
    pass

agent = SchemaAwareAgent(db)
questions = [
    "Show all customers from USA",
    "What's the total revenue this year?",
    # ... 8개 더 추가
]

for q in questions:
    result = agent.query(q)
    print(result)
```

### 과제 2: 검증 시스템 구현
```python
# 요구사항:
# 1. QueryValidator 완전 구현
# 2. 20개의 SQL 쿼리 (유효/무효) 생성
# 3. 검증 정확도 측정
# 4. 경고/에러 메시지 개선

valid_queries = [
    "SELECT * FROM customers WHERE country = 'USA'",
    # ... 9개 더
]

invalid_queries = [
    "SELECT * FROM nonexistent_table",
    "SELECT col1 FROM table WHERE",
    # ... 9개 더
]

validator = QueryValidator(schema)
for query in valid_queries:
    assert validator.validate(query)['valid']

for query in invalid_queries:
    assert not validator.validate(query)['valid']
```

### 과제 3: 에러 처리 및 재시도
```python
# 요구사항:
# 1. ErrorHandler 완전 구현
# 2. 5가지 이상의 에러 시나리오 테스트
# 3. 자동 재시도 메커니즘 검증
# 4. 로깅 시스템 구현

error_scenarios = [
    "SELECT * FROM nonexistent_table",  # Table not found
    "SELECT wrong_col FROM customers",  # Column not found
    "INVALID SQL SYNTAX",               # Syntax error
    # ... 2개 더
]

handler = ErrorHandler()
for scenario in error_scenarios:
    result = handler.handle_error(Exception(scenario), {})
    print(f"Scenario: {scenario}")
    print(f"Recovery: {result}")
```

### 과제 4: 통합 Agent 테스트
```python
# 요구사항:
# 1. TextToSQLAgent 구현
# 2. 20개의 다양한 질문으로 테스트
# 3. 성공률 및 정확도 측정
# 4. 성능 분석 (응답 시간)

agent = TextToSQLAgent('ecommerce.db', llm_client)

test_cases = [
    {
        'question': 'Show top 10 customers by spending',
        'expected_tables': ['customers', 'orders']
    },
    # ... 19개 더
]

success_count = 0
for case in test_cases:
    result = agent.process_question(case['question'])
    if result['success']:
        success_count += 1

print(f"Success rate: {success_count}/{len(test_cases)}")
```

## 체크포인트

- [ ] SchemaAwareAgent 완전 구현 및 테스트
- [ ] QueryValidator 3가지 검증 메커니즘 완료
- [ ] ErrorHandler 5가지 이상의 에러 타입 처리
- [ ] 에러 재시도 메커니즘 동작 확인
- [ ] TextToSQLAgent 통합 구현 완료
- [ ] 20개 이상의 질문으로 Agent 테스트 완료
- [ ] 80% 이상의 성공률 달성

## 추가 학습 자료
- LangChain Agent: https://python.langchain.com/docs/modules/agents/
- SQL Parser: https://sqlparse.readthedocs.io/
- Agent Design Patterns: https://github.com/hwchase17/langchain
