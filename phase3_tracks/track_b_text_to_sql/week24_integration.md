# Week 24: 통합 테스트 (Agent v1.0 완성)

## 학습 목표
- 모든 컴포넌트를 통합한 완전한 Text-to-SQL Agent 구현
- 엔드-투-엔드 테스트 및 평가
- 성능 최적화 및 모니터링
- 프로덕션 배포 준비

## O'Reilly 리소스
- **"Building ML Systems that Matter"** - Gal Oshri, Gian Gabriel
- **"Production Ready Machine Learning"** - Andriy Burkov
- **"Designing Machine Learning Systems"** (Chapter 8-9) - Chip Huyen

## 핵심 개념

### 1. 통합 Agent 아키텍처
```python
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import sqlite3
import json

@dataclass
class AgentConfig:
    """Agent 설정"""
    db_path: str
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    max_retries: int = 3
    timeout: int = 30
    enable_rag: bool = True
    enable_caching: bool = True
    logging_level: str = "INFO"

class TextToSQLAgentV1:
    """완성된 Text-to-SQL Agent v1.0"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.db = sqlite3.connect(config.db_path)
        self.db.row_factory = sqlite3.Row

        # 컴포넌트 초기화
        self.schema_manager = SchemaManager(self.db)
        self.llm_client = LLMClient(config.model_name, config.temperature)
        self.query_validator = QueryValidator(self.schema_manager.get_schema())
        self.error_handler = ErrorHandler(config.max_retries)
        self.result_analyzer = ResultAnalyzer()

        # RAG 설정 (선택사항)
        if config.enable_rag:
            self.embedding_store = EmbeddingStore()
            self.schema_rag = SchemaRAG(self.embedding_store)
            self.fewshot_store = FewShotExampleStore(self.embedding_store)

        # 캐싱 설정 (선택사항)
        if config.enable_caching:
            self.query_cache = QueryCache()

        # 로깅
        self.logger = self._setup_logging(config.logging_level)

        # 메트릭
        self.metrics = AgentMetrics()

    def process_question(self, question: str) -> Dict[str, Any]:
        """질문 처리 완전 흐름"""
        start_time = datetime.now()
        self.logger.info(f"Processing question: {question}")

        # 1. 캐시 확인
        if self.config.enable_caching:
            cached_result = self.query_cache.get(question)
            if cached_result:
                self.logger.info("Returning cached result")
                self.metrics.record_cache_hit()
                return cached_result

        # 2. 프롬프트 생성
        prompt = self._build_prompt(question)

        # 3. 재시도 루프
        attempt = 0
        last_error = None

        while attempt < self.config.max_retries:
            try:
                # 4. SQL 생성 (LLM)
                generated_sql = self.llm_client.generate_sql(prompt)
                self.logger.debug(f"Generated SQL: {generated_sql}")

                # 5. SQL 검증
                validation = self.query_validator.validate(generated_sql)
                if not validation['valid']:
                    raise ValueError(f"Validation failed: {validation['errors']}")

                # 6. SQL 실행
                result = self._execute_query(generated_sql)

                # 7. 결과 분석 및 설명
                analysis = self.result_analyzer.analyze(result, generated_sql)

                # 8. 최종 응답 구성
                response = self._build_response(
                    question, generated_sql, result, analysis, attempt
                )

                # 9. 캐시 저장 및 메트릭 기록
                if self.config.enable_caching:
                    self.query_cache.set(question, response)

                self.metrics.record_success(
                    question, generated_sql, result, attempt,
                    (datetime.now() - start_time).total_seconds()
                )

                self.logger.info(f"Successfully processed question in {attempt + 1} attempt(s)")
                return response

            except Exception as e:
                last_error = e
                attempt += 1
                self.logger.warning(f"Attempt {attempt} failed: {str(e)}")

                if attempt < self.config.max_retries:
                    # 에러 기반 프롬프트 개선
                    prompt = self._improve_prompt(prompt, str(e))

        # 모든 재시도 실패
        self.metrics.record_failure(question, str(last_error), attempt)
        self.logger.error(f"Failed to process question after {attempt} attempts")

        return {
            'success': False,
            'question': question,
            'error': str(last_error),
            'attempts': attempt,
            'execution_time': (datetime.now() - start_time).total_seconds()
        }

    def _build_prompt(self, question: str) -> str:
        """프롬프트 구성"""
        components = []

        # 1. 시스템 메시지
        components.append(self._get_system_message())

        # 2. 스키마 정보
        if self.config.enable_rag:
            schema_context = self.schema_rag.retrieve_relevant_schema(question)
            components.append(schema_context['relevant_schema'])
        else:
            components.append(self.schema_manager.get_schema_description())

        # 3. Few-shot 예제
        if self.config.enable_rag:
            examples = self.fewshot_store.retrieve_similar_examples(question, top_k=3)
            components.append(self._format_examples(examples))

        # 4. 사용자 질문
        components.append(f"Question: {question}\nSQL Query:")

        return "\n\n".join(components)

    def _execute_query(self, sql: str) -> List[Dict]:
        """SQL 실행"""
        try:
            cursor = self.db.execute(sql)
            # Row를 Dict로 변환
            columns = [desc[0] for desc in cursor.description]
            result = []
            for row in cursor.fetchall():
                result.append(dict(zip(columns, row)))
            return result
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            raise

    def _build_response(self, question: str, sql: str, result: List[Dict],
                       analysis: Dict, attempts: int) -> Dict[str, Any]:
        """최종 응답 구성"""
        return {
            'success': True,
            'question': question,
            'sql': sql,
            'result': result[:100],  # 첫 100개 행만 반환
            'result_count': len(result),
            'explanation': analysis['narrative'],
            'insights': analysis['insights'],
            'visualization_url': analysis.get('visualization_url'),
            'recommendations': analysis['recommendations'],
            'statistics': analysis['statistics'],
            'attempts': attempts + 1,
            'execution_time': analysis.get('execution_time', 0),
            'timestamp': datetime.now().isoformat()
        }

    def _improve_prompt(self, original_prompt: str, error: str) -> str:
        """에러 기반 프롬프트 개선"""
        improvement = f"\n\nNote: Previous attempt failed with error: {error[:200]}\n"
        improvement += "Please ensure the SQL query is syntactically correct "
        improvement += "and uses only existing table and column names."
        return original_prompt + improvement

    def _get_system_message(self) -> str:
        """시스템 메시지"""
        return """You are an expert SQL database assistant. Your task is to:
1. Understand natural language questions about data
2. Generate accurate SQL queries based on the provided schema
3. Only use columns and tables that exist in the schema
4. Return only the SQL query, no explanation
5. Ensure the query is syntactically correct and optimized

Important constraints:
- Never modify the database (SELECT only, no INSERT/UPDATE/DELETE)
- Use appropriate JOINs for related tables
- Always include WHERE clauses to filter data efficiently
- Use proper aliases for clarity
- Limit results when appropriate"""

    def _format_examples(self, examples: List[Dict]) -> str:
        """예제 포맷팅"""
        formatted = "Examples:\n"
        for i, example in enumerate(examples, 1):
            formatted += f"{i}. Q: {example.get('question', '')}\n"
            formatted += f"   A: {example.get('sql', '')}\n\n"
        return formatted

    def _setup_logging(self, level: str):
        """로깅 설정"""
        import logging
        logger = logging.getLogger('TextToSQLAgent')
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

class QueryCache:
    """쿼리 캐시"""

    def __init__(self, db_path: str = "cache.db", ttl_hours: int = 24):
        self.db = sqlite3.connect(db_path)
        self.ttl_hours = ttl_hours
        self._init_cache_table()

    def _init_cache_table(self):
        """캐시 테이블 초기화"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS query_cache (
                question_hash TEXT PRIMARY KEY,
                question TEXT,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.commit()

    def get(self, question: str) -> Optional[Dict]:
        """캐시 조회"""
        import hashlib
        q_hash = hashlib.md5(question.encode()).hexdigest()

        cursor = self.db.execute(
            "SELECT response FROM query_cache WHERE question_hash = ?", (q_hash,)
        )
        row = cursor.fetchone()

        if row:
            return json.loads(row[0])
        return None

    def set(self, question: str, response: Dict):
        """캐시 저장"""
        import hashlib
        q_hash = hashlib.md5(question.encode()).hexdigest()

        self.db.execute(
            "INSERT OR REPLACE INTO query_cache (question_hash, question, response) "
            "VALUES (?, ?, ?)",
            (q_hash, question, json.dumps(response))
        )
        self.db.commit()

class AgentMetrics:
    """Agent 성능 메트릭"""

    def __init__(self):
        self.total_queries = 0
        self.successful_queries = 0
        self.failed_queries = 0
        self.cache_hits = 0
        self.average_attempts = 0
        self.average_execution_time = 0
        self.execution_times = []

    def record_success(self, question: str, sql: str, result: List[Dict],
                      attempts: int, execution_time: float):
        """성공 기록"""
        self.total_queries += 1
        self.successful_queries += 1
        self.execution_times.append(execution_time)
        self.average_execution_time = sum(self.execution_times) / len(self.execution_times)
        self.average_attempts = (
            (self.average_attempts * (self.total_queries - 1) + attempts) / self.total_queries
        )

    def record_failure(self, question: str, error: str, attempts: int):
        """실패 기록"""
        self.total_queries += 1
        self.failed_queries += 1

    def record_cache_hit(self):
        """캐시 히트 기록"""
        self.cache_hits += 1

    def get_summary(self) -> Dict:
        """메트릭 요약"""
        return {
            'total_queries': self.total_queries,
            'successful_queries': self.successful_queries,
            'failed_queries': self.failed_queries,
            'success_rate': (
                self.successful_queries / self.total_queries * 100
                if self.total_queries > 0 else 0
            ),
            'cache_hits': self.cache_hits,
            'average_attempts': self.average_attempts,
            'average_execution_time_ms': self.average_execution_time * 1000
        }
```

### 2. 엔드-투-엔드 테스트
```python
class AgentTestSuite:
    """Agent 테스트 스위트"""

    def __init__(self, agent: TextToSQLAgentV1):
        self.agent = agent
        self.results = []

    def run_test_suite(self) -> Dict:
        """테스트 스위트 실행"""
        test_cases = self._load_test_cases()

        results = {
            'total_tests': len(test_cases),
            'passed': 0,
            'failed': 0,
            'test_results': []
        }

        for test_case in test_cases:
            result = self._run_test_case(test_case)
            results['test_results'].append(result)

            if result['passed']:
                results['passed'] += 1
            else:
                results['failed'] += 1

        results['success_rate'] = results['passed'] / results['total_tests'] * 100

        return results

    def _load_test_cases(self) -> List[Dict]:
        """테스트 케이스 로드"""
        return [
            {
                'id': 'basic_select',
                'category': 'Basic',
                'question': 'Show all customers',
                'expected_sql': 'SELECT * FROM customers',
                'expected_columns': ['id', 'name', 'email']
            },
            {
                'id': 'join',
                'category': 'Join',
                'question': 'List customer names and their orders',
                'expected_sql': 'SELECT c.name, o.order_date FROM customers c JOIN orders o',
                'expected_columns': ['name', 'order_date']
            },
            {
                'id': 'aggregation',
                'category': 'Aggregation',
                'question': 'How many orders per customer?',
                'expected_sql': 'GROUP BY',
                'expected_columns': ['customer_id', 'count']
            },
            {
                'id': 'filter',
                'category': 'Filter',
                'question': 'Find orders from 2024',
                'expected_sql': 'WHERE',
                'expected_columns': None
            },
            {
                'id': 'sorting',
                'category': 'Sorting',
                'question': 'Top 10 customers by spending',
                'expected_sql': 'ORDER BY',
                'expected_columns': None
            }
        ]

    def _run_test_case(self, test_case: Dict) -> Dict:
        """단일 테스트 케이스 실행"""
        result = self.agent.process_question(test_case['question'])

        passed = (
            result['success'] and
            (test_case.get('expected_sql') in result.get('sql', '').upper())
        )

        return {
            'test_id': test_case['id'],
            'category': test_case['category'],
            'question': test_case['question'],
            'passed': passed,
            'success': result['success'],
            'sql_generated': result.get('sql', ''),
            'error': result.get('error', ''),
            'execution_time': result.get('execution_time', 0)
        }

    def generate_report(self, results: Dict) -> str:
        """테스트 리포트 생성"""
        report = "=== Text-to-SQL Agent v1.0 Test Report ===\n\n"

        report += f"Total Tests: {results['total_tests']}\n"
        report += f"Passed: {results['passed']}\n"
        report += f"Failed: {results['failed']}\n"
        report += f"Success Rate: {results['success_rate']:.1f}%\n\n"

        report += "=== Test Results by Category ===\n"
        categories = {}
        for test in results['test_results']:
            cat = test['category']
            if cat not in categories:
                categories[cat] = {'passed': 0, 'total': 0}
            categories[cat]['total'] += 1
            if test['passed']:
                categories[cat]['passed'] += 1

        for cat, counts in categories.items():
            rate = counts['passed'] / counts['total'] * 100
            report += f"{cat}: {counts['passed']}/{counts['total']} ({rate:.1f}%)\n"

        report += "\n=== Detailed Results ===\n"
        for test in results['test_results']:
            status = "PASS" if test['passed'] else "FAIL"
            report += f"\n[{status}] {test['test_id']}: {test['question']}\n"
            if not test['passed']:
                report += f"  Error: {test['error']}\n"
                report += f"  SQL: {test['sql_generated']}\n"

        return report
```

### 3. 배포 준비
```python
class AgentDeploymentManager:
    """Agent 배포 관리"""

    def __init__(self, agent: TextToSQLAgentV1):
        self.agent = agent
        self.deployment_info = {}

    def prepare_for_deployment(self) -> Dict:
        """배포 준비"""
        return {
            'health_check': self._run_health_checks(),
            'performance_baseline': self._establish_performance_baseline(),
            'documentation': self._generate_documentation(),
            'deployment_checklist': self._create_checklist()
        }

    def _run_health_checks(self) -> Dict:
        """헬스 체크"""
        checks = {
            'database_connection': self._check_db_connection(),
            'llm_connection': self._check_llm_connection(),
            'schema_integrity': self._check_schema_integrity(),
            'cache_system': self._check_cache_system()
        }

        all_passed = all(checks.values())
        checks['overall_status'] = 'HEALTHY' if all_passed else 'NEEDS_ATTENTION'

        return checks

    def _check_db_connection(self) -> bool:
        """DB 연결 확인"""
        try:
            cursor = self.agent.db.execute("SELECT 1")
            return cursor.fetchone() is not None
        except:
            return False

    def _check_llm_connection(self) -> bool:
        """LLM 연결 확인"""
        try:
            # 간단한 프롬프트로 테스트
            response = self.agent.llm_client.generate_sql("SELECT 1")
            return response is not None
        except:
            return False

    def _check_schema_integrity(self) -> bool:
        """스키마 무결성 확인"""
        try:
            schema = self.agent.schema_manager.get_schema()
            return schema is not None and len(schema) > 0
        except:
            return False

    def _check_cache_system(self) -> bool:
        """캐시 시스템 확인"""
        if not self.agent.config.enable_caching:
            return True

        try:
            # 캐시 테스트
            test_key = "health_check_test"
            test_value = {"test": "data"}
            self.agent.query_cache.set(test_key, test_value)
            retrieved = self.agent.query_cache.get(test_key)
            return retrieved == test_value
        except:
            return False

    def _establish_performance_baseline(self) -> Dict:
        """성능 기준선 설정"""
        # 샘플 질문들로 벤치마크 실행
        sample_questions = [
            "How many customers do we have?",
            "What is the total revenue?",
            "Show recent orders",
            "Top 5 products by sales",
            "Monthly revenue trend"
        ]

        times = []
        for q in sample_questions:
            result = self.agent.process_question(q)
            times.append(result.get('execution_time', 0))

        return {
            'sample_size': len(sample_questions),
            'min_time_ms': min(times) * 1000,
            'max_time_ms': max(times) * 1000,
            'avg_time_ms': (sum(times) / len(times)) * 1000,
            'p95_time_ms': sorted(times)[int(len(times) * 0.95)] * 1000
        }

    def _generate_documentation(self) -> str:
        """문서 생성"""
        doc = """# Text-to-SQL Agent v1.0 Deployment Guide

## Overview
This is a production-ready Text-to-SQL Agent that converts natural language questions
to SQL queries and provides intelligent results with explanations.

## Features
- Natural language to SQL conversion
- Query validation and optimization
- Automatic error recovery with retry logic
- RAG-based schema awareness
- Result analysis and explanation
- Query caching for performance

## Configuration
See AgentConfig class for all available options.

## API Usage
```python
agent = TextToSQLAgentV1(config)
result = agent.process_question("Your question here")
```

## Monitoring
Monitor the following metrics:
- Success rate
- Average execution time
- Cache hit rate
- Error patterns

## Troubleshooting
See logs for detailed error information.
"""
        return doc

    def _create_checklist(self) -> List[str]:
        """배포 체크리스트"""
        return [
            "All health checks passed",
            "Performance baselines established",
            "Logging configured",
            "Monitoring alerts set up",
            "Documentation reviewed",
            "Backup strategy confirmed",
            "Incident response plan prepared",
            "User access controls configured",
            "Rate limiting configured",
            "Staging environment tested"
        ]

    def generate_deployment_report(self) -> str:
        """배포 리포트 생성"""
        prep = self.prepare_for_deployment()

        report = "=== Agent Deployment Readiness Report ===\n\n"

        # 헬스 체크 결과
        report += "=== Health Checks ===\n"
        for check, status in prep['health_check'].items():
            status_str = "PASS" if status else "FAIL"
            report += f"{check}: {status_str}\n"

        # 성능 베이스라인
        report += "\n=== Performance Baseline ===\n"
        perf = prep['performance_baseline']
        report += f"Average execution time: {perf['avg_time_ms']:.2f}ms\n"
        report += f"P95 execution time: {perf['p95_time_ms']:.2f}ms\n"

        # 체크리스트
        report += "\n=== Deployment Checklist ===\n"
        for i, item in enumerate(prep['deployment_checklist'], 1):
            report += f"{i}. {item}\n"

        return report
```

## 실습 과제

### 과제 1: 통합 Agent 구현
```python
# 요구사항:
# 1. TextToSQLAgentV1 완전 구현
# 2. 모든 이전 컴포넌트 통합
# 3. 설정 기반 동작 (RAG, 캐싱 토글)
# 4. 완전한 에러 처리 및 로깅

config = AgentConfig(
    db_path='ecommerce.db',
    model_name='gpt-3.5-turbo',
    enable_rag=True,
    enable_caching=True
)

agent = TextToSQLAgentV1(config)

# 테스트
questions = [
    "Show all customers",
    "What's the total revenue?",
    "Top 10 products by sales",
    # ... 추가 질문들
]

for q in questions:
    result = agent.process_question(q)
    print(f"Q: {q}")
    print(f"Success: {result['success']}")
    print(f"SQL: {result.get('sql', '')}")
    print()
```

### 과제 2: 엔드-투-엔드 테스트
```python
# 요구사항:
# 1. AgentTestSuite 완전 구현
# 2. 20개 이상의 테스트 케이스 작성
# 3. 카테고리별 테스트 (기본, JOIN, 집계, 필터, 정렬)
# 4. 테스트 리포트 생성

suite = AgentTestSuite(agent)
results = suite.run_test_suite()
report = suite.generate_report(results)

print(report)

# 예상 결과: 80% 이상의 성공률
```

### 과제 3: 배포 준비
```python
# 요구사항:
# 1. AgentDeploymentManager 구현
# 2. 모든 헬스 체크 통과
# 3. 성능 베이스라인 설정
# 4. 배포 리포트 생성

manager = AgentDeploymentManager(agent)
report = manager.generate_deployment_report()

print(report)

# 모든 헬스 체크가 PASS 상태여야 함
```

### 과제 4: 성능 모니터링
```python
# 요구사항:
# 1. AgentMetrics를 사용한 모니터링
# 2. 1000개의 다양한 질문 처리
# 3. 메트릭 수집 및 분석
# 4. 성능 보고서 생성

# 성능 테스트 실행
test_questions = load_performance_test_set()  # 1000개

for q in test_questions:
    agent.process_question(q)

# 메트릭 조회
metrics = agent.metrics.get_summary()
print(metrics)

# 예상: 85% 이상의 성공률, 평균 응답 시간 < 3초
```

## 체크포인트

- [ ] TextToSQLAgentV1 완전 구현 및 통합
- [ ] 모든 이전 주차 컴포넌트 통합 완료
- [ ] 에러 처리 및 재시도 메커니즘 동작
- [ ] 캐싱 시스템 동작 확인
- [ ] AgentTestSuite 구현 및 20개 이상의 테스트 케이스 작성
- [ ] 80% 이상의 테스트 성공률 달성
- [ ] AgentDeploymentManager 구현 완료
- [ ] 모든 헬스 체크 통과
- [ ] 성능 베이스라인 설정 (평균 응답 시간 < 3초)
- [ ] 배포 리포트 생성 완료
- [ ] 프로덕션 배포 준비 완료

## 최종 성과

### Agent v1.0 완성 요구사항
1. 자연어를 SQL로 변환 가능
2. 복잡한 다단계 쿼리 처리 가능
3. RAG를 통한 스키마 인식
4. 결과 분석 및 자연어 설명
5. 자동 에러 복구 및 재시도
6. 결과 시각화
7. 성능 모니터링
8. 프로덕션 배포 가능

## 추가 학습 자료
- MLOps Best Practices: https://ml-ops.systems/
- Production ML Guide: https://madewithml.com/
- Agent Frameworks: https://python.langchain.com/docs/modules/agents/
- Monitoring ML Systems: https://github.com/evidentlyai/evidently
