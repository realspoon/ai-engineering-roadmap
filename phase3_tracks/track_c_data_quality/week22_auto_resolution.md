# Week 22: 자동 해결 (Auto Resolution & RCA)

## 학습 목표
- Root Cause Analysis (RCA) 기법 습득
- 자동 데이터 수정 알고리즘 학습
- 수정 제안 시스템 구현

## 1. Root Cause Analysis (RCA)

### 1.1 RCA의 정의 및 목적
```
RCA란?
- 데이터 품질 문제의 근본 원인을 찾는 프로세스
- 증상이 아닌 원인을 해결

RCA 필요성:
✓ 같은 문제 재발 방지
✓ 자동 수정 전략 수립
✓ 데이터 품질 지속적 개선
```

### 1.2 RCA 프로세스

```
문제 발견
    ↓
[Step 1] 데이터 수집
    - 발생 시간
    - 영향받은 데이터
    - 이전 상태
    ↓
[Step 2] 증상 분석
    - 패턴 인식
    - 스코프 정의
    ↓
[Step 3] 원인 가설 수립
    - 가능한 원인들 나열
    - 우선순위 지정
    ↓
[Step 4] 원인 검증
    - 데이터 기반 검증
    - 통계 분석
    ↓
[Step 5] 근본 원인 확인
    - 단일 원인 또는 다중 원인
    ↓
[Step 6] 해결 방안 수립
    - 단기 조치
    - 장기 개선
```

## 2. 데이터 품질 문제의 일반적인 원인들

### 2.1 원인 카테고리
```
1. 데이터 입력 오류
   - 사용자 입력 실수
   - 특수문자/인코딩 오류
   - NULL/공백 혼입

2. 시스템/ETL 오류
   - 파이프라인 실패
   - 데이터 타입 변환 오류
   - 데이터 소스 변경

3. 요구사항 변화
   - 스키마 변경
   - 비즈니스 규칙 변경
   - 데이터 포맷 변경

4. 외부 요인
   - API 변경
   - 데이터 제공자 변경
   - 시스템 통합 이슈
```

## 3. RCA 구현 - 패턴 분석

### 3.1 이상 패턴 분석
```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class RCAEngine:
    def __init__(self):
        self.anomaly_history = []
        self.pattern_db = {}

    def analyze_root_cause(self, anomaly_data, historical_data):
        """근본 원인 분석"""
        causes = []

        # 1. 시간 기반 분석
        time_cause = self._analyze_temporal_pattern(
            anomaly_data, historical_data
        )
        if time_cause:
            causes.append(time_cause)

        # 2. 소스 기반 분석
        source_cause = self._analyze_source_pattern(
            anomaly_data, historical_data
        )
        if source_cause:
            causes.append(source_cause)

        # 3. 값 기반 분석
        value_cause = self._analyze_value_pattern(
            anomaly_data, historical_data
        )
        if value_cause:
            causes.append(value_cause)

        # 4. 의존성 분석
        dependency_cause = self._analyze_dependencies(
            anomaly_data, historical_data
        )
        if dependency_cause:
            causes.append(dependency_cause)

        # 근본 원인 결정
        root_cause = self._determine_root_cause(causes)

        return {
            'identified_causes': causes,
            'root_cause': root_cause,
            'confidence': self._calculate_confidence(causes),
            'affected_records': self._count_affected(anomaly_data),
            'recommendations': self._generate_recommendations(root_cause)
        }

    def _analyze_temporal_pattern(self, anomaly, historical):
        """시간 패턴 분석"""
        anomaly_time = anomaly.get('timestamp')
        if not anomaly_time:
            return None

        # 같은 시간대에 비슷한 문제가 있었는가?
        similar_issues = [
            h for h in historical
            if h.get('issue_type') == anomaly.get('issue_type')
            and self._same_time_period(h.get('timestamp'), anomaly_time)
        ]

        if len(similar_issues) > 2:
            return {
                'type': 'TEMPORAL_PATTERN',
                'description': f'Recurring issue at {anomaly_time.strftime("%H:%M")}',
                'instances': len(similar_issues),
                'likely_cause': 'Scheduled job or batch process'
            }

        return None

    def _analyze_source_pattern(self, anomaly, historical):
        """데이터 소스 패턴 분석"""
        anomaly_source = anomaly.get('source')

        # 같은 소스에서 반복되는 문제?
        source_issues = [
            h for h in historical
            if h.get('source') == anomaly_source
        ]

        if len(source_issues) > len([
            h for h in historical if h.get('source') != anomaly_source
        ]):
            return {
                'type': 'SOURCE_PATTERN',
                'description': f'Issue predominantly from source: {anomaly_source}',
                'instances': len(source_issues),
                'likely_cause': 'Data quality issue at source'
            }

        return None

    def _analyze_value_pattern(self, anomaly, historical):
        """값 패턴 분석"""
        anomaly_value = anomaly.get('value')

        # 같은 값으로 반복되는 문제?
        value_issues = [
            h for h in historical
            if h.get('value') == anomaly_value
        ]

        if len(value_issues) > 1:
            return {
                'type': 'VALUE_PATTERN',
                'description': f'Repeated value: {anomaly_value}',
                'instances': len(value_issues),
                'likely_cause': f'Default/placeholder value: {anomaly_value}'
            }

        return None

    def _analyze_dependencies(self, anomaly, historical):
        """의존성 분석"""
        # 다른 필드의 이상과 상관관계 있는가?
        correlated_anomalies = self._find_correlated_anomalies(
            anomaly, historical
        )

        if correlated_anomalies:
            return {
                'type': 'DEPENDENCY',
                'description': 'Correlated issues detected',
                'correlated_fields': correlated_anomalies,
                'likely_cause': 'Upstream data transformation issue'
            }

        return None

    def _same_time_period(self, time1, time2, tolerance_hours=1):
        """시간 범위 비교"""
        if not time1 or not time2:
            return False

        return abs((time1 - time2).total_seconds()) < tolerance_hours * 3600

    def _find_correlated_anomalies(self, anomaly, historical):
        """상관된 이상 찾기"""
        # 복잡한 상관성 분석
        pass

    def _determine_root_cause(self, causes):
        """근본 원인 결정"""
        if not causes:
            return None

        # 신뢰도가 가장 높은 원인 선택
        return max(causes, key=lambda x: x.get('instances', 0))

    def _calculate_confidence(self, causes):
        """신뢰도 계산"""
        if not causes:
            return 0

        total_instances = sum(c.get('instances', 0) for c in causes)
        max_instances = max(c.get('instances', 0) for c in causes)

        if total_instances == 0:
            return 0

        return min(100, (max_instances / max(1, total_instances)) * 100)

    def _count_affected(self, anomaly):
        """영향받은 레코드 수"""
        return anomaly.get('record_count', 1)

    def _generate_recommendations(self, root_cause):
        """권장사항 생성"""
        if not root_cause:
            return []

        recommendations = []

        cause_type = root_cause.get('type')

        if cause_type == 'TEMPORAL_PATTERN':
            recommendations.append({
                'action': 'SCHEDULE_MAINTENANCE',
                'timing': 'Off-peak hours',
                'priority': 'HIGH'
            })

        elif cause_type == 'SOURCE_PATTERN':
            recommendations.append({
                'action': 'CONTACT_SOURCE_OWNER',
                'description': 'Review data quality at source',
                'priority': 'HIGH'
            })

        elif cause_type == 'VALUE_PATTERN':
            recommendations.append({
                'action': 'ADD_VALIDATION_RULE',
                'description': 'Reject placeholder values',
                'priority': 'MEDIUM'
            })

        elif cause_type == 'DEPENDENCY':
            recommendations.append({
                'action': 'REVIEW_TRANSFORMATION',
                'description': 'Check upstream transformation logic',
                'priority': 'HIGH'
            })

        return recommendations
```

## 4. 자동 데이터 수정 (Auto-Fix)

### 4.1 수정 전략
```python
class DataRepairEngine:
    def __init__(self):
        self.repair_rules = {}
        self.repair_history = []

    def auto_repair(self, anomaly_data, detected_issue):
        """자동 수정 실행"""
        issue_type = detected_issue['issue_type']

        if issue_type == 'NULL_VALUE':
            return self._repair_null_value(anomaly_data, detected_issue)

        elif issue_type == 'INVALID_FORMAT':
            return self._repair_format(anomaly_data, detected_issue)

        elif issue_type == 'DUPLICATE':
            return self._repair_duplicate(anomaly_data, detected_issue)

        elif issue_type == 'INCONSISTENT_VALUE':
            return self._repair_consistency(anomaly_data, detected_issue)

        elif issue_type == 'OUTLIER':
            return self._repair_outlier(anomaly_data, detected_issue)

        else:
            return None

    def _repair_null_value(self, data, issue):
        """NULL 값 수정"""
        field = issue.get('field')
        repair_strategies = [
            ('forward_fill', self._forward_fill),
            ('backward_fill', self._backward_fill),
            ('mean_imputation', self._mean_imputation),
            ('mode_imputation', self._mode_imputation),
        ]

        # 가장 적합한 전략 선택
        best_strategy = self._select_best_strategy(
            data, field, repair_strategies
        )

        repaired_value = best_strategy(data, field)

        return {
            'strategy': best_strategy.__name__,
            'original_value': None,
            'repaired_value': repaired_value,
            'confidence': 0.85
        }

    def _repair_format(self, data, issue):
        """형식 수정"""
        field = issue.get('field')
        value = data.get(field)
        target_format = issue.get('expected_format')

        # 형식 변환
        if target_format == 'email':
            repaired = self._normalize_email(value)
        elif target_format == 'phone':
            repaired = self._normalize_phone(value)
        elif target_format == 'date':
            repaired = self._normalize_date(value)
        else:
            repaired = value

        return {
            'strategy': 'FORMAT_CONVERSION',
            'original_value': value,
            'repaired_value': repaired,
            'confidence': 0.90 if repaired != value else 0.0
        }

    def _repair_duplicate(self, data, issue):
        """중복 제거"""
        # PK 기반으로 나중 값 유지 또는 병합
        return {
            'strategy': 'DUPLICATE_REMOVAL',
            'action': 'MARKED_FOR_DELETION',
            'confidence': 0.95
        }

    def _repair_consistency(self, data, issue):
        """일관성 수정"""
        field = issue.get('field')
        expected_value = issue.get('expected_value')

        # 비즈니스 규칙에 따라 수정
        repaired = self._apply_business_rule(
            data, field, expected_value
        )

        return {
            'strategy': 'CONSISTENCY_FIX',
            'original_value': data.get(field),
            'repaired_value': repaired,
            'confidence': 0.80
        }

    def _repair_outlier(self, data, issue):
        """이상치 수정"""
        field = issue.get('field')
        value = data.get(field)

        # 이상치 처리: 삭제, 경계값으로 변환, 또는 평균값으로 변환
        strategy = issue.get('outlier_treatment', 'MEDIAN')

        if strategy == 'MEDIAN':
            repaired = self._calculate_median(field)
        elif strategy == 'BOUNDARY':
            repaired = self._apply_boundary(field, value)
        elif strategy == 'DELETE':
            repaired = None

        return {
            'strategy': f'OUTLIER_{strategy}',
            'original_value': value,
            'repaired_value': repaired,
            'confidence': 0.75
        }

    def _forward_fill(self, data, field):
        """이전 값으로 채우기"""
        pass

    def _backward_fill(self, data, field):
        """이후 값으로 채우기"""
        pass

    def _mean_imputation(self, data, field):
        """평균값으로 채우기"""
        pass

    def _mode_imputation(self, data, field):
        """최빈값으로 채우기"""
        pass

    def _normalize_email(self, email):
        """이메일 정규화"""
        if isinstance(email, str):
            return email.lower().strip()
        return None

    def _normalize_phone(self, phone):
        """전화번호 정규화"""
        import re
        if isinstance(phone, str):
            return re.sub(r'\D', '', phone)
        return None

    def _normalize_date(self, date_str):
        """날짜 정규화"""
        from dateutil import parser
        try:
            return parser.parse(date_str).isoformat()
        except:
            return None

    def _select_best_strategy(self, data, field, strategies):
        """최적 전략 선택"""
        # 가장 적합한 전략 선택 로직
        return strategies[0][1]

    def _apply_business_rule(self, data, field, expected):
        """비즈니스 규칙 적용"""
        pass

    def _calculate_median(self, field):
        """중앙값 계산"""
        pass

    def _apply_boundary(self, field, value):
        """경계값 적용"""
        pass
```

## 5. 수정 제안 시스템

### 5.1 사용자 대면 수정 제안
```python
class RepairSuggestionEngine:
    def __init__(self, llm_api_key=None):
        self.llm_api_key = llm_api_key
        self.suggestion_history = []

    def suggest_repair(self, anomaly_data, issue_type, confidence=None):
        """수정 제안 생성"""
        suggestions = []

        # 자동 수정 시도
        auto_repair = self._generate_auto_repair(
            anomaly_data, issue_type
        )
        if auto_repair and auto_repair.get('confidence', 0) > 0.8:
            suggestions.append({
                'type': 'AUTO_FIX',
                'suggestion': auto_repair,
                'priority': 'HIGH',
                'action': 'APPLY_AUTOMATICALLY'
            })

        # 고신뢰도 수정 제안
        high_confidence = self._generate_suggestions(
            anomaly_data, issue_type, min_confidence=0.7
        )
        for suggestion in high_confidence:
            suggestions.append({
                'type': 'SUGGESTED_FIX',
                'suggestion': suggestion,
                'priority': 'MEDIUM',
                'action': 'REQUIRES_APPROVAL'
            })

        # 저신뢰도 제안
        low_confidence = self._generate_suggestions(
            anomaly_data, issue_type, max_confidence=0.7
        )
        for suggestion in low_confidence:
            suggestions.append({
                'type': 'OPTION',
                'suggestion': suggestion,
                'priority': 'LOW',
                'action': 'MANUAL_SELECTION'
            })

        return suggestions

    def _generate_auto_repair(self, data, issue_type):
        """자동 수정 생성"""
        engine = DataRepairEngine()
        return engine.auto_repair(
            data,
            {'issue_type': issue_type}
        )

    def _generate_suggestions(self, data, issue_type,
                             min_confidence=0, max_confidence=1):
        """수정 제안 생성"""
        suggestions = []

        # 여러 수정 옵션 생성
        options = {
            'NULL_VALUE': [
                {'method': 'Mean Imputation', 'description': '평균값으로 채우기'},
                {'method': 'Forward Fill', 'description': '이전 값으로 채우기'},
                {'method': 'Delete Record', 'description': '레코드 삭제'}
            ],
            'INVALID_FORMAT': [
                {'method': 'Auto-normalize', 'description': '자동 정규화'},
                {'method': 'Manual Entry', 'description': '수동 입력'}
            ],
            'DUPLICATE': [
                {'method': 'Keep First', 'description': '첫 번째 유지'},
                {'method': 'Keep Latest', 'description': '최신값 유지'},
                {'method': 'Merge', 'description': '병합'}
            ]
        }

        for option in options.get(issue_type, []):
            confidence = self._estimate_confidence(data, option)
            if min_confidence <= confidence <= max_confidence:
                suggestions.append({
                    'method': option['method'],
                    'description': option['description'],
                    'confidence': confidence
                })

        return suggestions

    def _estimate_confidence(self, data, option):
        """신뢰도 추정"""
        # 복잡한 신뢰도 계산 로직
        return 0.75

    def record_user_choice(self, anomaly_id, chosen_suggestion):
        """사용자 선택 기록"""
        self.suggestion_history.append({
            'anomaly_id': anomaly_id,
            'chosen': chosen_suggestion,
            'timestamp': datetime.now()
        })

        # 향후 제안 개선에 활용
        self._update_suggestion_model()

    def _update_suggestion_model(self):
        """제안 모델 업데이트"""
        # 사용자 피드백 기반 모델 재학습
        pass
```

## 6. 수정 효과 평가

### 6.1 수정 전후 비교
```python
class RepairImpactAnalysis:
    def __init__(self):
        self.repair_records = []

    def evaluate_repair(self, original_data, repaired_data,
                       issue_type, repair_method):
        """수정 효과 평가"""
        before_quality = self._calculate_quality_score(original_data)
        after_quality = self._calculate_quality_score(repaired_data)
        improvement = after_quality - before_quality

        # 수정 타당성 검사
        is_valid = self._validate_repair(
            original_data, repaired_data, issue_type
        )

        return {
            'issue_type': issue_type,
            'repair_method': repair_method,
            'quality_before': before_quality,
            'quality_after': after_quality,
            'improvement': improvement,
            'is_valid': is_valid,
            'success_rate': self._estimate_success_rate(
                repair_method, issue_type
            )
        }

    def _calculate_quality_score(self, data):
        """품질 점수 계산"""
        score = 0
        # 다차원 품질 평가
        return score

    def _validate_repair(self, original, repaired, issue_type):
        """수정 타당성 검증"""
        # 수정된 데이터가 규칙 위반하지 않는지 확인
        return True

    def _estimate_success_rate(self, repair_method, issue_type):
        """성공률 추정"""
        # 과거 기록 기반 성공률 계산
        return 0.85
```

## 7. 실습 프로젝트

### 7.1 프로젝트: 종합 자동 해결 시스템
```
1. RCA 엔진 구현
2. 자동 수정 규칙 수립
3. 수정 제안 시스템 구현
4. 사용자 피드백 수집
5. 수정 효과 평가
6. 모니터링 및 개선
```

## 8. 평가 기준

- [ ] RCA 프로세스 이해
- [ ] 패턴 분석 구현
- [ ] 자동 수정 알고리즘
- [ ] 수정 제안 시스템
- [ ] 피드백 루프 구현
- [ ] 프로젝트 완료

## 9. 주요 고려사항

| 항목 | 설명 |
|------|------|
| 정확성 | 잘못된 수정보다 안하는 게 낫다 |
| 감사 추적 | 모든 수정 기록 유지 |
| 승인 프로세스 | 중요한 수정은 승인 필요 |
| 롤백 | 수정 실패시 원상복구 가능 |

## 10. 참고 자료

- "Root Cause Analysis" - 린 리스키 (Lean Riskski)
- 5-Why 분석법
- 피셔본(Fishbone) 다이어그램
