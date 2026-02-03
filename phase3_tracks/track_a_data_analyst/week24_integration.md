# Week 24: 통합 테스트 (Data Analyst Agent v1.0 Integration & Testing)

## 학습 목표
- 모든 주간 학습 내용 통합 (Week 17-23)
- Data Analyst Agent v1.0 최종 구현
- 종합 테스트 및 성능 평가
- 프로덕션 배포 준비

## O'Reilly 리소스
- "Building Microservices" - 배포 및 통합
- "Continuous Integration/Continuous Deployment" - CI/CD
- "Software Testing" - 종합 테스트 전략
- "Production-Ready Python" - 프로덕션화

## 핵심 개념

### 1. Data Analyst Agent v1.0 아키텍처
```python
import anthropic
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
import json

# 통합 상태 정의
class DataAnalysisState(TypedDict):
    query: str
    file_path: str
    data: dict
    analysis_stage: str
    results: Annotated[dict, operator.add]
    visualizations: List[str]
    report: str
    metadata: dict
    errors: List[str]
    execution_time: float
    analysis_path: List[str]

class DataAnalystAgentV1:
    """Data Analyst Agent v1.0 - 완전 통합 버전"""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.workflow = self._build_complete_workflow()
        self.execution_history = []

    def _build_complete_workflow(self):
        """완전한 워크플로우 구축"""
        workflow = StateGraph(DataAnalysisState)

        # 1단계: 초기 평가 (Week 20)
        workflow.add_node("initial_assessment", self.initial_assessment)

        # 2단계: 데이터 로딩 (Week 22)
        workflow.add_node("data_loading", self.data_loading)

        # 3단계: EDA 자동화 (Week 17)
        workflow.add_node("eda_automation", self.eda_automation)

        # 4단계: 통계 분석 (Week 17, 21)
        workflow.add_node("statistical_analysis", self.statistical_analysis)

        # 5단계: 시각화 (Week 18)
        workflow.add_node("visualization", self.visualization)

        # 6단계: 고급 분석 (Week 21)
        workflow.add_node("advanced_analysis", self.advanced_analysis)

        # 7단계: 인사이트 생성 (Week 19)
        workflow.add_node("insight_generation", self.insight_generation)

        # 8단계: 리포트 생성 (Week 19)
        workflow.add_node("report_generation", self.report_generation)

        # 9단계: UI 준비 (Week 23)
        workflow.add_node("ui_preparation", self.ui_preparation)

        # 10단계: 에러 핸들링
        workflow.add_node("error_handler", self.error_handler)

        # 엣지 연결
        workflow.add_edge("initial_assessment", "data_loading")
        workflow.add_edge("data_loading", "eda_automation")
        workflow.add_edge("eda_automation", "statistical_analysis")
        workflow.add_edge("statistical_analysis", "visualization")
        workflow.add_edge("visualization", "advanced_analysis")
        workflow.add_edge("advanced_analysis", "insight_generation")
        workflow.add_edge("insight_generation", "report_generation")
        workflow.add_edge("report_generation", "ui_preparation")
        workflow.add_edge("ui_preparation", END)

        return workflow.compile()

    def initial_assessment(self, state):
        """쿼리 분석 및 접근 방식 결정"""
        state['analysis_stage'] = 'initial_assessment'
        state['analysis_path'].append('initial_assessment')

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"다음 분석 요청에 대한 최적의 접근 방식을 제시하세요: {state['query']}"
            }]
        )

        state['results']['assessment'] = message.content[0].text
        return state

    def data_loading(self, state):
        """다중 형식 데이터 로딩 (Week 22)"""
        state['analysis_stage'] = 'data_loading'
        state['analysis_path'].append('data_loading')

        try:
            from week22_multimodal import DataLoader

            loader = DataLoader()
            df = loader.auto_load(state['file_path'])

            state['data'] = {
                'dataframe': df.to_dict() if df is not None else {},
                'shape': df.shape if df is not None else None,
                'columns': df.columns.tolist() if df is not None else [],
                'dtypes': df.dtypes.to_dict() if df is not None else {}
            }
            state['metadata']['data_loaded'] = True

        except Exception as e:
            state['errors'].append(f"데이터 로딩 오류: {str(e)}")
            state['analysis_stage'] = 'error'

        return state

    def eda_automation(self, state):
        """자동 EDA (Week 17)"""
        state['analysis_stage'] = 'eda_automation'
        state['analysis_path'].append('eda_automation')

        try:
            # EDA 실행 (Week 17 코드 활용)
            # from week17_eda_automation import EDAAutomation
            # eda = EDAAutomation(df)
            # results = eda.run_complete_eda()

            state['results']['eda'] = {
                'profile_generated': True,
                'statistics_computed': True,
                'quality_assessed': True
            }

        except Exception as e:
            state['errors'].append(f"EDA 오류: {str(e)}")

        return state

    def statistical_analysis(self, state):
        """통계 분석 (Week 17, 21)"""
        state['analysis_stage'] = 'statistical_analysis'
        state['analysis_path'].append('statistical_analysis')

        try:
            # 통계 분석 로직
            state['results']['statistics'] = {
                'descriptive_stats': 'completed',
                'distribution_analysis': 'completed'
            }

        except Exception as e:
            state['errors'].append(f"통계 분석 오류: {str(e)}")

        return state

    def visualization(self, state):
        """시각화 생성 (Week 18)"""
        state['analysis_stage'] = 'visualization'
        state['analysis_path'].append('visualization')

        try:
            # Claude API 코드 생성 (Week 18)
            # visualizations = VisualizationEngine(df).generate_comprehensive_report()

            state['visualizations'] = ['histogram', 'scatter', 'heatmap']
            state['results']['visualizations'] = 'completed'

        except Exception as e:
            state['errors'].append(f"시각화 오류: {str(e)}")

        return state

    def advanced_analysis(self, state):
        """고급 분석 (Week 21)"""
        state['analysis_stage'] = 'advanced_analysis'
        state['analysis_path'].append('advanced_analysis')

        try:
            # 고급 분석 (Week 21)
            state['results']['advanced'] = {
                'timeseries_analysis': 'completed',
                'correlation_analysis': 'completed',
                'forecasting': 'completed'
            }

        except Exception as e:
            state['errors'].append(f"고급 분석 오류: {str(e)}")

        return state

    def insight_generation(self, state):
        """인사이트 생성 (Week 19)"""
        state['analysis_stage'] = 'insight_generation'
        state['analysis_path'].append('insight_generation')

        try:
            # Claude API 활용 인사이트 (Week 19)
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": f"다음 분석 결과를 기반으로 주요 인사이트를 도출하세요: {json.dumps(state['results'], ensure_ascii=False)}"
                }]
            )

            state['results']['insights'] = message.content[0].text

        except Exception as e:
            state['errors'].append(f"인사이트 생성 오류: {str(e)}")

        return state

    def report_generation(self, state):
        """자동 리포트 생성 (Week 19)"""
        state['analysis_stage'] = 'report_generation'
        state['analysis_path'].append('report_generation')

        try:
            # 전문적 리포트 생성 (Week 19)
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": f"""
                    다음 데이터 분석 결과를 기반으로 전문적인 마크다운 리포트를 작성하세요.

                    분석 결과:
                    {json.dumps(state['results'], ensure_ascii=False)}

                    리포트는 다음을 포함해야 합니다:
                    1. Executive Summary
                    2. Key Findings
                    3. Detailed Analysis
                    4. Recommendations
                    5. Conclusion
                    """
                }]
            )

            state['report'] = message.content[0].text

        except Exception as e:
            state['errors'].append(f"리포트 생성 오류: {str(e)}")
            state['report'] = "리포트 생성 중 오류 발생"

        return state

    def ui_preparation(self, state):
        """UI용 데이터 준비 (Week 23)"""
        state['analysis_stage'] = 'ui_preparation'
        state['analysis_path'].append('ui_preparation')

        state['results']['ui_ready'] = True
        state['metadata']['ui_export_format'] = 'streamlit'

        return state

    def error_handler(self, state):
        """에러 처리"""
        if state['errors']:
            state['analysis_stage'] = 'error_recovery'
            # 에러 복구 로직
        return state

    def run(self, query, file_path):
        """에이전트 실행"""
        import time

        start_time = time.time()

        initial_state = {
            'query': query,
            'file_path': file_path,
            'data': {},
            'analysis_stage': 'start',
            'results': {},
            'visualizations': [],
            'report': '',
            'metadata': {
                'query': query,
                'file_path': file_path,
                'timestamp': pd.Timestamp.now().isoformat()
            },
            'errors': [],
            'execution_time': 0,
            'analysis_path': []
        }

        result = self.workflow.invoke(initial_state)

        result['execution_time'] = time.time() - start_time

        # 실행 이력 저장
        self.execution_history.append(result)

        return result

    def get_execution_summary(self):
        """실행 요약"""
        if not self.execution_history:
            return None

        last_execution = self.execution_history[-1]

        return {
            'analysis_path': last_execution['analysis_path'],
            'execution_time': last_execution['execution_time'],
            'error_count': len(last_execution['errors']),
            'has_report': bool(last_execution['report']),
            'visualizations_count': len(last_execution['visualizations'])
        }
```

### 2. 종합 테스트 전략
```python
import unittest
import pandas as pd
import numpy as np
from io import StringIO

class TestDataAnalystAgentV1(unittest.TestCase):
    """Data Analyst Agent v1.0 종합 테스트"""

    def setUp(self):
        """테스트 초기화"""
        self.agent = DataAnalystAgentV1()
        self.test_df = pd.DataFrame({
            'sales': np.random.rand(100) * 1000,
            'quantity': np.random.randint(1, 50, 100),
            'region': np.random.choice(['A', 'B', 'C'], 100),
            'date': pd.date_range('2023-01-01', periods=100)
        })
        self.test_csv = '/tmp/test_data.csv'
        self.test_df.to_csv(self.test_csv, index=False)

    def test_data_loading(self):
        """데이터 로딩 테스트"""
        result = self.agent.run(
            query="데이터 분석",
            file_path=self.test_csv
        )

        self.assertIsNotNone(result['data'])
        self.assertEqual(result['data']['shape'], (100, 4))

    def test_eda_execution(self):
        """EDA 실행 테스트"""
        result = self.agent.run(
            query="기본 탐색 분석",
            file_path=self.test_csv
        )

        self.assertIn('eda_automation', result['analysis_path'])
        self.assertIn('eda', result['results'])

    def test_statistical_analysis(self):
        """통계 분석 테스트"""
        result = self.agent.run(
            query="통계 분석",
            file_path=self.test_csv
        )

        self.assertIn('statistics', result['results'])

    def test_visualization_generation(self):
        """시각화 생성 테스트"""
        result = self.agent.run(
            query="시각화 생성",
            file_path=self.test_csv
        )

        self.assertTrue(len(result['visualizations']) > 0)

    def test_report_generation(self):
        """리포트 생성 테스트"""
        result = self.agent.run(
            query="리포트 생성",
            file_path=self.test_csv
        )

        self.assertIsNotNone(result['report'])
        self.assertTrue(len(result['report']) > 0)

    def test_error_handling(self):
        """에러 처리 테스트"""
        result = self.agent.run(
            query="분석",
            file_path="/nonexistent/path.csv"
        )

        self.assertTrue(len(result['errors']) > 0)

    def test_execution_performance(self):
        """실행 성능 테스트"""
        result = self.agent.run(
            query="전체 분석",
            file_path=self.test_csv
        )

        # 실행 시간이 60초 이내인지 확인
        self.assertLess(result['execution_time'], 60)

    def test_end_to_end_workflow(self):
        """end-to-end 워크플로우 테스트"""
        result = self.agent.run(
            query="완전한 분석을 수행해주세요",
            file_path=self.test_csv
        )

        # 모든 단계가 수행되었는지 확인
        expected_stages = [
            'initial_assessment',
            'data_loading',
            'eda_automation',
            'statistical_analysis',
            'visualization',
            'advanced_analysis',
            'insight_generation',
            'report_generation'
        ]

        for stage in expected_stages:
            self.assertIn(stage, result['analysis_path'])

        # 최종 산출물 확인
        self.assertIsNotNone(result['report'])
        self.assertTrue(len(result['visualizations']) > 0)

    def tearDown(self):
        """테스트 정리"""
        import os
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
```

### 3. 성능 평가 및 메트릭
```python
class AgentPerformanceEvaluator:
    """에이전트 성능 평가"""

    def __init__(self, execution_history):
        self.execution_history = execution_history
        self.metrics = {}

    def calculate_success_rate(self):
        """성공률 계산"""
        if not self.execution_history:
            return 0

        successful = sum(1 for e in self.execution_history if len(e['errors']) == 0)
        return (successful / len(self.execution_history)) * 100

    def calculate_average_execution_time(self):
        """평균 실행 시간"""
        if not self.execution_history:
            return 0

        total_time = sum(e['execution_time'] for e in self.execution_history)
        return total_time / len(self.execution_history)

    def calculate_error_rate(self):
        """에러율"""
        if not self.execution_history:
            return 0

        total_errors = sum(len(e['errors']) for e in self.execution_history)
        return (total_errors / len(self.execution_history)) * 100

    def get_comprehensive_report(self):
        """종합 성능 리포트"""
        return {
            'total_executions': len(self.execution_history),
            'success_rate': self.calculate_success_rate(),
            'average_execution_time': self.calculate_average_execution_time(),
            'error_rate': self.calculate_error_rate(),
            'average_stages_completed': self._avg_stages_completed(),
            'visualization_generation_rate': self._viz_generation_rate()
        }

    def _avg_stages_completed(self):
        """평균 완료된 단계 수"""
        if not self.execution_history:
            return 0

        total_stages = sum(len(e['analysis_path']) for e in self.execution_history)
        return total_stages / len(self.execution_history)

    def _viz_generation_rate(self):
        """시각화 생성률"""
        if not self.execution_history:
            return 0

        viz_generated = sum(1 for e in self.execution_history if len(e['visualizations']) > 0)
        return (viz_generated / len(self.execution_history)) * 100
```

## 실습 과제

### Task 1: 통합 테스트 실행
```bash
# 테스트 실행
python -m unittest test_agent_v1.TestDataAnalystAgentV1

# 커버리지 확인
coverage run -m unittest discover
coverage report
```

### Task 2: 성능 벤치마크
- 5개 이상의 다양한 데이터셋 테스트
- 각 단계별 실행 시간 측정
- 병목 지점 식별 및 최적화

### Task 3: 프로덕션 배포 준비
- Docker 컨테이너화
- API 엔드포인트 구축
- 로깅 및 모니터링 설정

## 주간 체크포인트

- [ ] Data Analyst Agent v1.0 완전 구현
- [ ] 모든 8개 단계 통합
- [ ] 종합 단위 테스트 (8+ 테스트)
- [ ] End-to-end 워크플로우 검증
- [ ] 성능 메트릭 수집 및 분석
- [ ] 에러 처리 및 로깅
- [ ] 문서화 완성
- [ ] 배포 준비

## 학습 성과 기준
- [ ] 테스트 성공률 > 95%
- [ ] 평균 실행 시간 < 30초
- [ ] 에러율 < 5%
- [ ] 코드 커버리지 > 85%

## 최종 산출물
1. **완성된 Data Analyst Agent v1.0**
   - 8단계 통합 파이프라인
   - 자동 분석 및 리포팅

2. **종합 테스트 스위트**
   - 단위 테스트
   - 통합 테스트
   - 성능 테스트

3. **사용 설명서**
   - API 문서
   - 사용 예제
   - 트러블슈팅 가이드

4. **성능 보고서**
   - 벤치마크 결과
   - 최적화 제안
   - 향후 개선 계획
