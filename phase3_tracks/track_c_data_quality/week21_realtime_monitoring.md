# Week 21: 실시간 모니터링 (Streaming & Dashboard)

## 학습 목표
- 스트리밍 데이터 품질 모니터링
- 실시간 대시보드 구축
- 알림 시스템 구현

## 1. 실시간 모니터링의 필요성

### 1.1 배치 vs 스트리밍
```
배치 처리 (Week 18-19):
✓ 정확도 높음
✓ 복잡한 분석 가능
✗ 지연 시간 (hours/days)
✗ 문제 발견 늦음

스트리밍 처리:
✓ 실시간 감지
✓ 즉각적인 대응
✗ 제한된 계산 능력
✗ 복잡한 구현
```

### 1.2 모니터링 아키텍처
```
┌─────────────┐
│ Data Source │
└──────┬──────┘
       │
       ↓
┌──────────────────┐
│  Stream Ingestion│ (Kafka, Kinesis)
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│ Quality Check    │
│ Engine (Real-time)
└──────┬───────────┘
       │
    ┌──┴──┬─────────┬────────┐
    ↓     ↓         ↓        ↓
  Store Dashboard Alert DB Archive
```

## 2. Apache Kafka를 활용한 스트리밍

### 2.1 Kafka 기본 설정
```python
from kafka import KafkaConsumer, KafkaProducer
import json
from datetime import datetime

class KafkaStreamMonitor:
    def __init__(self, bootstrap_servers=['localhost:9092']):
        self.bootstrap_servers = bootstrap_servers

    def create_consumer(self, topic):
        """Kafka Consumer 생성"""
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='dq-monitoring-group'
        )
        return consumer

    def create_producer(self):
        """Kafka Producer 생성"""
        producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda m: json.dumps(m).encode('utf-8')
        )
        return producer

    def consume_and_validate(self, input_topic, output_topic, validators):
        """스트림 데이터 검증"""
        consumer = self.create_consumer(input_topic)
        producer = self.create_producer()

        for message in consumer:
            data = message.value
            quality_metrics = self._validate(data, validators)

            # 결과 저장
            result = {
                'timestamp': datetime.now().isoformat(),
                'original_data': data,
                'quality_metrics': quality_metrics,
                'status': 'PASS' if quality_metrics['score'] > 80 else 'FAIL'
            }

            # 결과 송출
            producer.send(output_topic, result)

    def _validate(self, data, validators):
        """데이터 검증"""
        metrics = {}
        total_score = 0

        for validator_name, validator_func in validators.items():
            score = validator_func(data)
            metrics[validator_name] = score
            total_score += score

        metrics['score'] = total_score / len(validators)
        return metrics
```

### 2.2 구체적인 스트림 검증 예제
```python
class StreamQualityValidator:
    def __init__(self):
        self.window_size = 100  # 슬라이딩 윈도우 크기
        self.data_buffer = []

    def validate_stream(self, stream_data):
        """스트림 데이터 품질 검증"""
        self.data_buffer.append(stream_data)

        # 윈도우 크기 유지
        if len(self.data_buffer) > self.window_size:
            self.data_buffer.pop(0)

        return {
            'completeness': self._check_completeness(stream_data),
            'validity': self._check_validity(stream_data),
            'consistency': self._check_consistency(),
            'timeliness': self._check_timeliness(stream_data),
            'anomaly': self._detect_anomaly()
        }

    def _check_completeness(self, data):
        """완전성 확인"""
        required_fields = ['id', 'timestamp', 'value']
        missing = [f for f in required_fields if f not in data or data[f] is None]
        return 100 * (1 - len(missing) / len(required_fields))

    def _check_validity(self, data):
        """유효성 확인"""
        checks = []

        # 타입 확인
        if isinstance(data.get('id'), int):
            checks.append(True)

        # 범위 확인
        value = data.get('value')
        if value is not None and -1000 <= value <= 1000:
            checks.append(True)

        return 100 * (sum(checks) / len(checks)) if checks else 0

    def _check_consistency(self):
        """일관성 확인"""
        if len(self.data_buffer) < 2:
            return 100

        # 포맷 일관성 체크
        consistent = 0
        for i in range(1, len(self.data_buffer)):
            if self._same_format(self.data_buffer[i-1], self.data_buffer[i]):
                consistent += 1

        return 100 * (consistent / (len(self.data_buffer) - 1))

    def _check_timeliness(self, data):
        """적시성 확인"""
        from datetime import datetime, timedelta

        timestamp = data.get('timestamp')
        if timestamp is None:
            return 0

        try:
            data_time = datetime.fromisoformat(timestamp)
            delay = (datetime.now() - data_time).total_seconds()

            # 5분 이내면 100점
            if delay < 300:
                return 100
            # 1시간 이내면 50점
            elif delay < 3600:
                return 50
            # 그 이상이면 0점
            else:
                return 0
        except:
            return 0

    def _detect_anomaly(self):
        """이상 탐지"""
        if len(self.data_buffer) < 10:
            return 100  # 데이터 부족

        values = [d.get('value') for d in self.data_buffer if d.get('value') is not None]

        if not values:
            return 100

        # 최근 값이 윈도우의 평균과 3-sigma 범위를 벗어나면 이상
        mean = np.mean(values[:-1])
        std = np.std(values[:-1])

        if abs(values[-1] - mean) > 3 * std:
            return 0  # 이상
        else:
            return 100  # 정상

    def _same_format(self, data1, data2):
        """데이터 형식 비교"""
        return set(data1.keys()) == set(data2.keys())
```

## 3. AWS Kinesis를 활용한 실시간 모니터링

### 3.1 Kinesis Consumer 구현
```python
import boto3
import json
from datetime import datetime

class KinesisQualityMonitor:
    def __init__(self, region_name='us-east-1'):
        self.kinesis = boto3.client('kinesis', region_name=region_name)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region_name)

    def start_monitoring(self, stream_name, validator):
        """Kinesis 스트림 모니터링 시작"""
        response = self.kinesis.describe_stream(StreamName=stream_name)
        shard_ids = [shard['ShardId'] for shard in response['StreamDescription']['Shards']]

        for shard_id in shard_ids:
            self._process_shard(stream_name, shard_id, validator)

    def _process_shard(self, stream_name, shard_id, validator):
        """Shard 처리"""
        shard_iterator_response = self.kinesis.get_shard_iterator(
            StreamName=stream_name,
            ShardId=shard_id,
            ShardIteratorType='LATEST'
        )

        shard_iterator = shard_iterator_response['ShardIterator']

        while shard_iterator:
            response = self.kinesis.get_records(
                ShardIterator=shard_iterator,
                Limit=100
            )

            # 레코드 처리
            for record in response['Records']:
                data = json.loads(record['Data'])
                metrics = validator.validate_stream(data)

                # CloudWatch에 메트릭 저장
                self._publish_metrics(stream_name, metrics)

                # 알림 확인
                if metrics['score'] < 80:
                    self._send_alert(stream_name, metrics)

            shard_iterator = response.get('NextShardIterator')

    def _publish_metrics(self, stream_name, metrics):
        """CloudWatch에 메트릭 발행"""
        self.cloudwatch.put_metric_data(
            Namespace='DataQuality',
            MetricData=[
                {
                    'MetricName': 'QualityScore',
                    'Value': metrics['score'],
                    'Unit': 'Percent',
                    'Dimensions': [
                        {'Name': 'StreamName', 'Value': stream_name}
                    ],
                    'Timestamp': datetime.now()
                }
            ]
        )

    def _send_alert(self, stream_name, metrics):
        """알림 발송"""
        sns = boto3.client('sns')
        sns.publish(
            TopicArn='arn:aws:sns:...',
            Subject=f'Data Quality Alert: {stream_name}',
            Message=json.dumps(metrics, indent=2)
        )
```

## 4. 대시보드 구축 (Streamlit)

### 4.1 Streamlit 대시보드
```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

class DQDashboard:
    def __init__(self):
        st.set_page_config(
            page_title="Data Quality Dashboard",
            layout="wide"
        )

    def render(self, metrics_db):
        """대시보드 렌더링"""
        st.title("Data Quality Monitoring Dashboard")

        # 1. 전체 요약
        self._render_summary(metrics_db)

        # 2. 시간별 트렌드
        self._render_trends(metrics_db)

        # 3. 데이터 소스별 상태
        self._render_source_status(metrics_db)

        # 4. 이상 탐지 결과
        self._render_anomalies(metrics_db)

    def _render_summary(self, metrics_db):
        """요약 정보 표시"""
        st.header("Overall Quality Score")

        # 최근 1시간 평균
        recent = metrics_db.get_recent_metrics(hours=1)
        avg_score = recent['score'].mean()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Current Score", f"{avg_score:.1f}%")

        with col2:
            pass_rate = (recent['status'] == 'PASS').mean() * 100
            st.metric("Pass Rate", f"{pass_rate:.1f}%")

        with col3:
            alert_count = (recent['score'] < 80).sum()
            st.metric("Alerts", alert_count)

        with col4:
            total_records = len(recent)
            st.metric("Records Processed", total_records)

    def _render_trends(self, metrics_db):
        """시간별 트렌드 표시"""
        st.header("Quality Score Trend")

        # 최근 24시간 데이터
        hourly_data = metrics_db.get_hourly_metrics(hours=24)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_data['timestamp'],
            y=hourly_data['score'],
            mode='lines+markers',
            name='Quality Score'
        ))

        fig.update_layout(
            title="Quality Score Over Time",
            xaxis_title="Time",
            yaxis_title="Score (%)",
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_source_status(self, metrics_db):
        """데이터 소스별 상태"""
        st.header("Data Source Status")

        sources = metrics_db.get_sources()

        status_data = []
        for source in sources:
            recent = metrics_db.get_recent_metrics(
                source=source, hours=1
            )
            avg_score = recent['score'].mean()
            pass_count = (recent['status'] == 'PASS').sum()
            total = len(recent)

            status_data.append({
                'Source': source,
                'Score': f"{avg_score:.1f}%",
                'Pass Rate': f"{pass_count/total*100:.1f}%",
                'Status': 'OK' if avg_score > 80 else 'WARNING'
            })

        df = pd.DataFrame(status_data)
        st.dataframe(df, use_container_width=True)

    def _render_anomalies(self, metrics_db):
        """이상 탐지 결과"""
        st.header("Detected Anomalies")

        recent_anomalies = metrics_db.get_anomalies(hours=24)

        if len(recent_anomalies) > 0:
            st.warning(f"Found {len(recent_anomalies)} anomalies in the last 24 hours")

            with st.expander("View Details"):
                for _, anomaly in recent_anomalies.iterrows():
                    st.write(f"- {anomaly['timestamp']}: {anomaly['description']}")
        else:
            st.success("No anomalies detected in the last 24 hours")
```

### 4.2 Grafana와의 통합
```python
class GrafanaIntegration:
    def __init__(self, grafana_url, api_key):
        self.grafana_url = grafana_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {'Authorization': f'Bearer {api_key}'}
        )

    def create_dashboard(self, dashboard_config):
        """Grafana 대시보드 생성"""
        response = self.session.post(
            f"{self.grafana_url}/api/dashboards/db",
            json={
                "dashboard": dashboard_config,
                "overwrite": True
            }
        )
        return response.json()

    def add_metric_to_dashboard(self, dashboard_id, metric_name, query):
        """메트릭 추가"""
        # Grafana API를 통해 메트릭 추가
        pass

    def create_alert_rule(self, metric_name, threshold):
        """알림 규칙 생성"""
        alert_config = {
            "uid": None,
            "title": f"Alert: {metric_name} < {threshold}",
            "condition": f"B",
            "data": [
                {
                    "refId": "A",
                    "queryType": "",
                    "model": {
                        "expr": f'dq_{metric_name}',
                        "interval": "",
                        "legendFormat": ""
                    },
                    "datasourceUid": "prometheus-uid",
                    "relativeTimeRange": {
                        "from": 600,
                        "to": 0
                    }
                },
                {
                    "refId": "B",
                    "queryType": "",
                    "expression": f"$A < {threshold}",
                    "datasourceUid": "-100",
                    "conditions": [
                        {
                            "evaluator": {"params": [], "type": "gt"},
                            "operator": {"type": "and"},
                            "query": {"params": ["A"]},
                            "type": "query"
                        }
                    ]
                }
            ]
        }

        response = self.session.post(
            f"{self.grafana_url}/api/v1/rules",
            json=alert_config
        )
        return response.json()
```

## 5. 알림 시스템 (Alert System)

### 5.1 다중 채널 알림
```python
class AlertManager:
    def __init__(self):
        self.alert_rules = []
        self.notification_channels = {}

    def add_notification_channel(self, channel_type, config):
        """알림 채널 추가"""
        if channel_type == 'email':
            self.notification_channels['email'] = EmailNotifier(config)
        elif channel_type == 'slack':
            self.notification_channels['slack'] = SlackNotifier(config)
        elif channel_type == 'webhook':
            self.notification_channels['webhook'] = WebhookNotifier(config)

    def add_alert_rule(self, rule):
        """알림 규칙 추가"""
        self.alert_rules.append(rule)

    def check_and_alert(self, metrics):
        """메트릭 확인 및 알림"""
        for rule in self.alert_rules:
            if rule.should_trigger(metrics):
                alert_message = rule.generate_message(metrics)
                self._send_alerts(alert_message, rule.channels)

    def _send_alerts(self, message, channels):
        """알림 발송"""
        for channel in channels:
            if channel in self.notification_channels:
                self.notification_channels[channel].send(message)


class AlertRule:
    def __init__(self, name, condition, severity, channels):
        self.name = name
        self.condition = condition  # lambda 함수
        self.severity = severity  # CRITICAL, WARNING, INFO
        self.channels = channels

    def should_trigger(self, metrics):
        """알림 조건 확인"""
        return self.condition(metrics)

    def generate_message(self, metrics):
        """알림 메시지 생성"""
        return f"[{self.severity}] {self.name}\n{json.dumps(metrics, indent=2)}"


class SlackNotifier:
    def __init__(self, config):
        self.webhook_url = config['webhook_url']

    def send(self, message):
        """Slack으로 알림 발송"""
        payload = {
            "text": message,
            "attachments": [
                {
                    "color": "danger",
                    "title": "Data Quality Alert"
                }
            ]
        }
        requests.post(self.webhook_url, json=payload)


class EmailNotifier:
    def __init__(self, config):
        self.smtp_server = config['smtp_server']
        self.recipients = config['recipients']

    def send(self, message):
        """이메일로 알림 발송"""
        # 이메일 발송 로직
        pass
```

## 6. 실습 프로젝트

### 6.1 프로젝트: 실시간 주식 데이터 품질 모니터링
```
1. Kafka 클러스터 구성
2. 실시간 데이터 스트림 설정
3. 품질 검증 엔진 구현
4. Streamlit 대시보드 구축
5. 알림 시스템 구현
6. 성능 최적화
```

## 7. 평가 기준

- [ ] Kafka/Kinesis 기본 설정
- [ ] 스트림 품질 검증 구현
- [ ] Streamlit 대시보드 구축
- [ ] 알림 시스템 구현
- [ ] 성능 최적화
- [ ] 프로젝트 완료

## 8. 참고 자료

- Apache Kafka 공식 문서
- AWS Kinesis 개발자 가이드
- Streamlit 문서
- Grafana 알림 설정
