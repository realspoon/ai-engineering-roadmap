# Week 24: 통합 테스트 및 Agent v1.0 완성

## 학습 목표
- 모든 컴포넌트 통합
- 엔드-투-엔드 테스트
- Data Quality Agent v1.0 릴리스 준비

## 1. DQ Agent 아키텍처 최종 설계

### 1.1 전체 시스템 아키텍처
```
┌────────────────────────────────────────────────────────────┐
│        Data Quality Agent v1.0                             │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Data Ingestion                                   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ - Database connectors                                │ │
│  │ - API adapters                                       │ │
│  │ - File parsers                                       │ │
│  │ - Streaming consumers (Kafka, Kinesis)              │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↓                                 │
│  Layer 2: Quality Assessment                              │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ - Profiling Engine (Week 18)                         │ │
│  │ - Anomaly Detection (Week 19)                        │ │
│  │ - Schema Validation                                  │ │
│  │ - Rule-based Validation                             │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↓                                 │
│  Layer 3: Intelligence & Analysis                         │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ - LLM Validation (Week 20)                           │ │
│  │ - Root Cause Analysis (Week 22)                      │ │
│  │ - Impact Analysis (Week 23)                          │ │
│  │ - Lineage Tracking (Week 23)                         │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↓                                 │
│  Layer 4: Action & Resolution                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ - Auto-repair Engine (Week 22)                       │ │
│  │ - Suggestion System (Week 22)                        │ │
│  │ - Alert Management                                   │ │
│  │ - Notification Channels                              │ │
│  └──────────────────────────────────────────────────────┘ │
│                          ↓                                 │
│  Layer 5: Monitoring & Reporting                          │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ - Real-time Dashboard (Week 21)                      │ │
│  │ - Metrics Storage                                    │ │
│  │ - Audit Logging                                      │ │
│  │ - Report Generation                                  │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

## 2. 통합 코드 구조

### 2.1 메인 DQ Agent 클래스
```python
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

class QualitySeverity(Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"

@dataclass
class QualityIssue:
    issue_id: str
    issue_type: str
    severity: QualitySeverity
    field: str
    value: any
    expected_value: Optional[any]
    root_cause: Optional[str]
    suggested_fix: Optional[str]
    confidence: float
    timestamp: str

class DataQualityAgent:
    """
    Data Quality Agent v1.0
    모든 품질 관리 작업을 수행하는 통합 에이전트
    """

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()

        # 각 레이어 초기화
        self.ingestion = DataIngestionLayer(self.config)
        self.assessment = QualityAssessmentLayer(self.config)
        self.intelligence = IntelligenceLayer(self.config)
        self.action = ActionLayer(self.config)
        self.monitoring = MonitoringLayer(self.config)

        self.quality_issues = []
        self.metrics = {}

    def process_data(self, data_source: Dict) -> Dict:
        """
        데이터 품질 전체 처리 파이프라인
        """
        self.logger.info(f"Processing data from: {data_source['name']}")

        try:
            # 1. 데이터 수집
            raw_data = self.ingestion.ingest(data_source)
            self.logger.info(f"Ingested {len(raw_data)} records")

            # 2. 품질 평가
            quality_results = self.assessment.evaluate(raw_data, data_source)
            self.logger.info(f"Quality assessment complete")

            # 3. 문제 분석 및 지능형 검증
            analyzed_issues = []
            for issue in quality_results['issues']:
                analyzed = self.intelligence.analyze(issue, raw_data)
                analyzed_issues.append(analyzed)

            # 4. 조치 실행
            resolution_results = self.action.resolve(
                analyzed_issues, raw_data
            )

            # 5. 모니터링 및 리포팅
            metrics = self.monitoring.collect_metrics(
                quality_results, resolution_results
            )

            # 6. 결과 집계
            report = self._generate_report(
                quality_results, analyzed_issues,
                resolution_results, metrics
            )

            return {
                'status': 'SUCCESS',
                'data_source': data_source['name'],
                'quality_score': metrics['overall_quality_score'],
                'issues_found': len(analyzed_issues),
                'issues_resolved': len(resolution_results['resolved']),
                'report': report,
                'metrics': metrics
            }

        except Exception as e:
            self.logger.error(f"Error processing data: {str(e)}", exc_info=True)
            return {
                'status': 'ERROR',
                'error_message': str(e),
                'data_source': data_source['name']
            }

    def process_stream(self, stream_config: Dict):
        """
        스트리밍 데이터 실시간 처리
        """
        self.logger.info(f"Starting stream processing: {stream_config['name']}")

        consumer = self.ingestion.create_stream_consumer(stream_config)

        for batch in consumer:
            # 실시간 품질 평가
            quality_results = self.assessment.evaluate_stream(batch)

            # 임계값 초과시 즉시 조치
            if quality_results['quality_score'] < 80:
                self.logger.warning(
                    f"Low quality score: {quality_results['quality_score']}"
                )
                self.action.send_alert(
                    'LOW_QUALITY',
                    quality_results,
                    'HIGH'
                )

            # 메트릭 기록
            self.monitoring.record_stream_metrics(quality_results)

    def get_lineage(self, data_node: str) -> Dict:
        """
        데이터 리니지 조회
        """
        return self.intelligence.get_lineage(data_node)

    def analyze_impact(self, changed_node: str) -> Dict:
        """
        데이터 변경의 영향도 분석
        """
        return self.intelligence.analyze_impact(changed_node)

    def _load_config(self, config_path: str) -> Dict:
        """설정 로드"""
        import yaml
        if config_path:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """기본 설정"""
        return {
            'data_sources': [],
            'quality_rules': [],
            'alert_channels': [],
            'storage': 'postgresql'
        }

    def _setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('DataQualityAgent')

    def _generate_report(self, quality_results, issues,
                        resolution_results, metrics) -> str:
        """최종 리포트 생성"""
        report = f"""
========== DATA QUALITY REPORT ==========

Overall Quality Score: {metrics['overall_quality_score']:.1f}/100

Issues Found: {len(issues)}
  - Critical: {len([i for i in issues if i.severity == 'CRITICAL'])}
  - Warning: {len([i for i in issues if i.severity == 'WARNING'])}
  - Info: {len([i for i in issues if i.severity == 'INFO'])}

Issues Resolved: {len(resolution_results['resolved'])}
Requires Manual Review: {len(resolution_results['manual_review'])}

Quality Dimensions:
  - Accuracy: {metrics['accuracy']:.1f}%
  - Completeness: {metrics['completeness']:.1f}%
  - Consistency: {metrics['consistency']:.1f}%
  - Timeliness: {metrics['timeliness']:.1f}%
  - Validity: {metrics['validity']:.1f}%
  - Uniqueness: {metrics['uniqueness']:.1f}%

Timestamp: {metrics['timestamp']}

=========================================
"""
        return report
```

### 2.2 각 레이어 구현

```python
class DataIngestionLayer:
    """데이터 수집 레이어"""

    def __init__(self, config):
        self.config = config
        self.connectors = self._init_connectors()

    def ingest(self, data_source: Dict):
        """데이터 수집"""
        connector = self.connectors.get(data_source['type'])
        if not connector:
            raise ValueError(f"Unsupported source type: {data_source['type']}")

        return connector.fetch(data_source)

    def create_stream_consumer(self, stream_config):
        """스트리밍 소비자 생성"""
        pass

    def _init_connectors(self):
        """커넥터 초기화"""
        return {
            'postgresql': PostgresConnector(),
            'mysql': MySQLConnector(),
            'mongodb': MongoDBConnector(),
            'kafka': KafkaConnector(),
            'kinesis': KinesisConnector(),
            's3': S3Connector(),
            'gcs': GCSConnector()
        }


class QualityAssessmentLayer:
    """품질 평가 레이어"""

    def __init__(self, config):
        self.config = config
        self.profiler = DataProfiler()
        self.anomaly_detector = AnomalyDetectionEngine()
        self.validator = SchemaValidator()

    def evaluate(self, data, data_source) -> Dict:
        """전체 품질 평가"""
        results = {
            'issues': [],
            'metrics': {},
            'quality_score': 0
        }

        # 프로파일링
        profile = self.profiler.profile(data)
        results['metrics']['profile'] = profile

        # 유효성 검증
        schema_issues = self.validator.validate(data, data_source['schema'])
        results['issues'].extend(schema_issues)

        # 이상 탐지
        anomalies = self.anomaly_detector.detect(data)
        results['issues'].extend(anomalies)

        # 품질 점수 계산
        results['quality_score'] = self._calculate_quality_score(
            results['issues']
        )

        return results

    def evaluate_stream(self, batch):
        """스트림 품질 평가"""
        # 간소화된 평가 (성능 중시)
        pass

    def _calculate_quality_score(self, issues) -> float:
        """품질 점수 계산"""
        if not issues:
            return 100.0

        severity_weights = {
            'CRITICAL': 10,
            'WARNING': 5,
            'INFO': 1
        }

        total_weight = sum(
            severity_weights.get(i.severity.value, 0)
            for i in issues
        )

        return max(0, 100 - total_weight)


class IntelligenceLayer:
    """지능형 분석 레이어"""

    def __init__(self, config):
        self.config = config
        self.rca_engine = RCAEngine()
        self.lineage_tracker = DataLineageTracker()
        self.impact_analyzer = ImpactAnalysisEngine(self.lineage_tracker)
        self.llm_validator = LLMValidator(config.get('llm_api_key'))

    def analyze(self, issue: QualityIssue, data) -> QualityIssue:
        """문제 분석 및 근본 원인 파악"""
        # LLM 기반 의미적 검증
        if issue.issue_type in ['INVALID_FORMAT', 'INCONSISTENT_VALUE']:
            llm_validation = self.llm_validator.validate(
                issue.field, issue.value
            )
            issue.suggested_fix = llm_validation.get('suggestion')
            issue.confidence = llm_validation.get('confidence', issue.confidence)

        # RCA 분석
        rca_result = self.rca_engine.analyze_root_cause(issue, data)
        issue.root_cause = rca_result['root_cause']

        return issue

    def get_lineage(self, data_node: str) -> Dict:
        """리니지 조회"""
        return self.lineage_tracker.get_lineage(data_node)

    def analyze_impact(self, changed_node: str) -> Dict:
        """영향도 분석"""
        return self.impact_analyzer.analyze_impact(changed_node)


class ActionLayer:
    """조치 실행 레이어"""

    def __init__(self, config):
        self.config = config
        self.repair_engine = DataRepairEngine()
        self.alert_manager = AlertManager()
        self.notification_manager = NotificationManager()

    def resolve(self, issues: List[QualityIssue], data) -> Dict:
        """문제 해결"""
        results = {
            'resolved': [],
            'manual_review': [],
            'errors': []
        }

        for issue in issues:
            try:
                if issue.confidence > 0.8:
                    # 자동 수정
                    repair_result = self.repair_engine.auto_repair(
                        {issue.field: issue.value},
                        issue
                    )
                    results['resolved'].append({
                        'issue': issue,
                        'repair': repair_result
                    })
                else:
                    # 수동 검토 필요
                    results['manual_review'].append(issue)

            except Exception as e:
                results['errors'].append({
                    'issue': issue,
                    'error': str(e)
                })

        return results

    def send_alert(self, alert_type: str, data: Dict, priority: str):
        """알림 발송"""
        self.alert_manager.send_alert(
            alert_type=alert_type,
            data=data,
            priority=priority,
            channels=self.config.get('alert_channels', [])
        )


class MonitoringLayer:
    """모니터링 및 리포팅 레이어"""

    def __init__(self, config):
        self.config = config
        self.metrics_store = MetricsStore(config.get('storage'))
        self.dashboard = Dashboard()

    def collect_metrics(self, quality_results, resolution_results) -> Dict:
        """메트릭 수집"""
        metrics = {
            'overall_quality_score': quality_results['quality_score'],
            'accuracy': quality_results['metrics'].get('accuracy', 100),
            'completeness': quality_results['metrics'].get('completeness', 100),
            'consistency': quality_results['metrics'].get('consistency', 100),
            'timeliness': quality_results['metrics'].get('timeliness', 100),
            'validity': quality_results['metrics'].get('validity', 100),
            'uniqueness': quality_results['metrics'].get('uniqueness', 100),
            'issues_resolved': len(resolution_results['resolved']),
            'manual_reviews': len(resolution_results['manual_review']),
            'timestamp': datetime.now().isoformat()
        }

        # 메트릭 저장
        self.metrics_store.save(metrics)

        return metrics

    def record_stream_metrics(self, quality_results):
        """스트림 메트릭 기록"""
        self.metrics_store.save_stream_metric(quality_results)

    def get_dashboard(self) -> str:
        """대시보드 조회"""
        return self.dashboard.render(self.metrics_store)
```

## 3. 테스트 전략

### 3.1 단위 테스트 (Unit Tests)
```python
import unittest
from unittest.mock import Mock, patch

class TestDataQualityAgent(unittest.TestCase):
    """DQ Agent 단위 테스트"""

    def setUp(self):
        self.agent = DataQualityAgent()

    def test_data_ingestion(self):
        """데이터 수집 테스트"""
        mock_data = [{'id': 1, 'name': 'John'}]
        with patch.object(self.agent.ingestion, 'ingest', return_value=mock_data):
            result = self.agent.ingestion.ingest({'type': 'postgresql'})
            self.assertEqual(len(result), 1)

    def test_quality_assessment(self):
        """품질 평가 테스트"""
        data = [
            {'id': 1, 'email': 'test@example.com', 'age': 25},
            {'id': 2, 'email': 'invalid-email', 'age': -5}
        ]

        results = self.agent.assessment.evaluate(data, {
            'schema': {
                'id': 'int',
                'email': 'email',
                'age': 'int_range(0,150)'
            }
        })

        self.assertTrue(len(results['issues']) > 0)
        self.assertTrue(results['quality_score'] < 100)

    def test_root_cause_analysis(self):
        """RCA 테스트"""
        issue = QualityIssue(
            issue_id='test-1',
            issue_type='NULL_VALUE',
            severity=QualitySeverity.WARNING,
            field='email',
            value=None,
            expected_value='valid@example.com',
            root_cause=None,
            suggested_fix=None,
            confidence=0.5,
            timestamp=datetime.now().isoformat()
        )

        analyzed = self.agent.intelligence.analyze(issue, [])
        self.assertIsNotNone(analyzed.root_cause)

    def test_auto_repair(self):
        """자동 수정 테스트"""
        issue = QualityIssue(
            issue_id='test-1',
            issue_type='INVALID_FORMAT',
            severity=QualitySeverity.WARNING,
            field='email',
            value='INVALID EMAIL',
            expected_value=None,
            root_cause=None,
            suggested_fix=None,
            confidence=0.9,
            timestamp=datetime.now().isoformat()
        )

        results = self.agent.action.resolve([issue], {})
        self.assertTrue(len(results['resolved']) > 0)
```

### 3.2 통합 테스트 (Integration Tests)
```python
class TestDataQualityAgentIntegration(unittest.TestCase):
    """통합 테스트"""

    @classmethod
    def setUpClass(cls):
        cls.test_config = 'test_config.yaml'
        cls.agent = DataQualityAgent(cls.test_config)

    def test_end_to_end_pipeline(self):
        """엔드-투-엔드 파이프라인 테스트"""
        data_source = {
            'name': 'test_source',
            'type': 'postgresql',
            'connection': 'test_db',
            'schema': {
                'id': 'int',
                'email': 'email',
                'age': 'int'
            }
        }

        result = self.agent.process_data(data_source)

        self.assertEqual(result['status'], 'SUCCESS')
        self.assertTrue('quality_score' in result)
        self.assertTrue('report' in result)

    def test_streaming_pipeline(self):
        """스트리밍 파이프라인 테스트"""
        stream_config = {
            'name': 'test_stream',
            'type': 'kafka',
            'topic': 'test_topic'
        }

        # 스트리밍 처리 시작
        # (실제 테스트에서는 모의 데이터 사용)
        pass
```

### 3.3 성능 테스트 (Performance Tests)
```python
import time

class TestDataQualityAgentPerformance(unittest.TestCase):
    """성능 테스트"""

    def test_throughput(self):
        """처리량 테스트"""
        agent = DataQualityAgent()

        # 1000개 레코드 처리
        large_data = [
            {'id': i, 'value': i * 2.5}
            for i in range(1000)
        ]

        start_time = time.time()
        results = agent.assessment.evaluate(large_data, {})
        elapsed = time.time() - start_time

        # 1000개당 1초 이내에 처리
        self.assertTrue(elapsed < 1.0)

    def test_latency(self):
        """지연시간 테스트"""
        agent = DataQualityAgent()

        single_record = {'id': 1, 'value': 10}

        start_time = time.time()
        results = agent.assessment.evaluate([single_record], {})
        elapsed = time.time() - start_time

        # 단일 레코드 처리 50ms 이내
        self.assertTrue(elapsed < 0.05)
```

## 4. 배포 설정

### 4.1 Docker 배포
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드
COPY . .

# 설정 파일
COPY config/ /etc/dq-agent/

# 건강 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 포트 노출
EXPOSE 8000

# 실행
CMD ["python", "agent_server.py"]
```

### 4.2 K8s 배포
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dq-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dq-agent
  template:
    metadata:
      labels:
        app: dq-agent
    spec:
      containers:
      - name: dq-agent
        image: dq-agent:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: CONFIG_PATH
          value: /etc/dq-agent/config.yaml
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: dq-agent-service
spec:
  selector:
    app: dq-agent
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

## 5. 릴리스 체크리스트

### 5.1 기능 검증
- [ ] 모든 7개 컴포넌트 통합 완료
- [ ] 단위 테스트 커버리지 > 80%
- [ ] 통합 테스트 모두 통과
- [ ] 성능 기준 달성 (1000 records/sec)
- [ ] 문서 작성 완료

### 5.2 운영 준비
- [ ] 모니터링 설정
- [ ] 알림 채널 구성
- [ ] 로깅 설정
- [ ] 백업/복구 계획
- [ ] 운영 매뉴얼 작성

### 5.3 배포 준비
- [ ] Docker 이미지 빌드 및 테스트
- [ ] K8s 설정 검증
- [ ] 헬스 체크 구현
- [ ] 무중단 배포 전략
- [ ] 롤백 계획

## 6. 파일 구조
```
data-quality-agent/
├── src/
│   ├── agent.py                 # 메인 에이전트
│   ├── layers/
│   │   ├── ingestion.py        # 데이터 수집
│   │   ├── assessment.py       # 품질 평가
│   │   ├── intelligence.py     # 지능 분석
│   │   ├── action.py           # 조치 실행
│   │   └── monitoring.py       # 모니터링
│   ├── modules/
│   │   ├── profiler.py         # 프로파일링
│   │   ├── anomaly.py          # 이상 탐지
│   │   ├── llm_validator.py    # LLM 검증
│   │   ├── rca.py              # RCA 엔진
│   │   ├── lineage.py          # 리니지 추적
│   │   └── repair.py           # 자동 수정
│   └── api/
│       ├── server.py           # API 서버
│       └── routes.py           # API 라우트
├── tests/
│   ├── unit/
│   ├── integration/
│   └── performance/
├── config/
│   ├── default.yaml
│   └── test.yaml
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── docs/
│   └── api.md
├── requirements.txt
└── README.md
```

## 7. 평가 기준

- [ ] 모든 컴포넌트 통합
- [ ] 단위/통합 테스트 완료
- [ ] 성능 기준 달성
- [ ] 문서화 완료
- [ ] 배포 준비 완료
- [ ] v1.0 릴리스

## 8. 다음 단계 (Phase 4)

- 프로덕션 배포 및 모니터링
- 사용자 피드백 수집
- 지속적 개선
- v1.1 로드맵 수립
