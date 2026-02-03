# Week 20: 분석 파이프라인 (LangGraph-based Agent Pipeline)

## 학습 목표
- LangGraph를 활용한 멀티 스텝 에이전트 파이프라인 구축
- 상태 관리 및 조건부 라우팅 구현
- 재시도 로직 및 에러 핸들링
- 기본적인 Data Analyst Agent v0.1 구현

## O'Reilly 리소스
- "LangChain & LLM Applications" - 에이전트 패턴
- "System Design Interview" - 파이프라인 설계
- "Designing Data-Intensive Applications" - 상태 관리
- LangGraph 공식 문서

## 핵심 개념

### 1. LangGraph 기초
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator

# 상태 정의
class AnalysisState(TypedDict):
    query: str
    data: dict
    current_step: str
    results: Annotated[dict, operator.add]
    analysis_path: List[str]
    errors: List[str]

# 그래프 구축
workflow = StateGraph(AnalysisState)

# 노드 정의
def load_data_node(state):
    """데이터 로드 노드"""
    state['current_step'] = 'load_data'
    state['analysis_path'].append('load_data')
    state['data'] = {'loaded': True}
    return state

def analyze_node(state):
    """분석 노드"""
    state['current_step'] = 'analyze'
    state['analysis_path'].append('analyze')
    state['results']['analysis'] = 'completed'
    return state

# 엣지 추가
workflow.add_node("load_data", load_data_node)
workflow.add_node("analyze", analyze_node)
workflow.add_edge("load_data", "analyze")
workflow.add_edge("analyze", END)

# 그래프 컴파일
graph = workflow.compile()
```

### 2. 조건부 라우팅
```python
from langgraph.graph import StateGraph, END

def route_based_data_type(state):
    """데이터 타입에 따른 라우팅"""
    data_type = state.get('data_type', 'unknown')

    if data_type == 'timeseries':
        return "timeseries_analysis"
    elif data_type == 'categorical':
        return "categorical_analysis"
    else:
        return "general_analysis"

def route_based_quality(state):
    """데이터 품질에 따른 라우팅"""
    quality_score = state.get('data_quality_score', 0)

    if quality_score > 0.8:
        return "proceed_analysis"
    else:
        return "data_cleaning"

# 조건부 엣지 추가
workflow.add_conditional_edges(
    "assess_data",
    route_based_data_type,
    {
        "timeseries_analysis": "timeseries_node",
        "categorical_analysis": "categorical_node",
        "general_analysis": "general_node"
    }
)

workflow.add_conditional_edges(
    "data_quality_check",
    route_based_quality,
    {
        "proceed_analysis": "analysis_node",
        "data_cleaning": "cleaning_node"
    }
)
```

### 3. 재시도 로직 및 에러 핸들링
```python
import time
from functools import wraps
from typing import Callable

def retry_with_backoff(max_retries=3, backoff_factor=2):
    """재시도 데코레이터"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor ** attempt
                        time.sleep(wait_time)
                    else:
                        raise

        return wrapper
    return decorator

# 에러 핸들링이 포함된 노드
def robust_analysis_node(state):
    """강건한 분석 노드"""
    try:
        result = perform_analysis(state['data'])
        state['results'] = result
        return state
    except ValueError as e:
        state['errors'].append(f"분석 오류: {str(e)}")
        state['current_step'] = 'error'
        return state
    except Exception as e:
        state['errors'].append(f"예상치 못한 오류: {str(e)}")
        state['current_step'] = 'fatal_error'
        return state

# 에러 복구 노드
def error_recovery_node(state):
    """에러 복구"""
    state['current_step'] = 'recovery'
    # 정제된 데이터로 재시도
    state['data'] = clean_data(state['data'])
    return state
```

### 4. Data Analyst Agent v0.1 기본 구조
```python
from langgraph.graph import StateGraph, END
import anthropic

class DataAnalystAgentV0:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        """에이전트 워크플로우 구성"""
        workflow = StateGraph(AnalysisState)

        # 노드들
        workflow.add_node("initial_assessment", self.initial_assessment)
        workflow.add_node("data_loading", self.data_loading)
        workflow.add_node("eda", self.eda)
        workflow.add_node("statistical_analysis", self.statistical_analysis)
        workflow.add_node("visualization", self.visualization)
        workflow.add_node("report_generation", self.report_generation)
        workflow.add_node("error_handler", self.error_handler)

        # 엣지
        workflow.add_edge("initial_assessment", "data_loading")
        workflow.add_edge("data_loading", "eda")
        workflow.add_edge("eda", "statistical_analysis")
        workflow.add_edge("statistical_analysis", "visualization")
        workflow.add_edge("visualization", "report_generation")
        workflow.add_edge("report_generation", END)

        return workflow.compile()

    def initial_assessment(self, state):
        """초기 평가"""
        state['current_step'] = 'initial_assessment'
        state['analysis_path'].append('initial_assessment')

        # Claude에 쿼리 분석 요청
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"다음 분석 요청을 분석하세요: {state['query']}"
            }]
        )

        state['assessment'] = message.content[0].text
        return state

    def data_loading(self, state):
        """데이터 로딩"""
        state['current_step'] = 'data_loading'
        state['analysis_path'].append('data_loading')
        # 데이터 로딩 로직
        return state

    def eda(self, state):
        """탐색적 데이터 분석"""
        state['current_step'] = 'eda'
        state['analysis_path'].append('eda')
        # EDA 로직
        return state

    def statistical_analysis(self, state):
        """통계 분석"""
        state['current_step'] = 'statistical_analysis'
        state['analysis_path'].append('statistical_analysis')
        # 통계 분석 로직
        return state

    def visualization(self, state):
        """시각화"""
        state['current_step'] = 'visualization'
        state['analysis_path'].append('visualization')
        # 시각화 로직
        return state

    def report_generation(self, state):
        """리포트 생성"""
        state['current_step'] = 'report_generation'
        state['analysis_path'].append('report_generation')
        # 리포트 생성 로직
        return state

    def error_handler(self, state):
        """에러 처리"""
        state['current_step'] = 'error_handling'
        return state

    def run(self, query, data=None):
        """에이전트 실행"""
        initial_state = {
            'query': query,
            'data': data or {},
            'current_step': 'start',
            'results': {},
            'analysis_path': [],
            'errors': []
        }

        return self.workflow.invoke(initial_state)
```

## 실습 과제

### Task 1: 기본 LangGraph 파이프라인
- 5개 단계의 기본 파이프라인 구축
- 조건부 라우팅 구현
- 상태 추적 및 로깅

### Task 2: 에러 핸들링 강화
- 재시도 로직 구현
- 에러 복구 메커니즘
- 로깅 및 모니터링

### Task 3: Data Analyst Agent v0.1
```python
# 사용 예시
agent = DataAnalystAgentV0()

result = agent.run(
    query="고객 데이터의 주요 트렌드를 분석해주세요",
    data={
        'file_path': 'customer_data.csv',
        'format': 'csv'
    }
)

print(f"분석 경로: {result['analysis_path']}")
print(f"현재 상태: {result['current_step']}")
print(f"결과: {result['results']}")
if result['errors']:
    print(f"에러: {result['errors']}")
```

## 주간 체크포인트

- [ ] LangGraph 기본 개념 이해
- [ ] 3단계 이상의 파이프라인 구축
- [ ] 조건부 라우팅 구현
- [ ] 에러 핸들링 및 재시도 로직
- [ ] State 관리 및 추적
- [ ] Data Analyst Agent v0.1 기본 구조
- [ ] 5개 이상의 시나리오로 테스트
- [ ] 파이프라인 실행 기록 저장

## 학습 성과 기준
- [ ] 파이프라인 실행 성공률 > 95%
- [ ] 에러 복구율 > 80%
- [ ] 상태 추적 정확도 100%
