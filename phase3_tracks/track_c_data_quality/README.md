# Track C: Data Quality Agent

> **목표**: 데이터 품질을 자동으로 검사하고 이상을 탐지하며 실시간 알림을 발송하는 AI Agent

## 🎯 최종 결과물

```
┌─────────────────────────────────────────────────────────────┐
│                   Data Quality Agent                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  데이터 파이프라인 ──────────────────────────────────────▶   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. 데이터 프로파일링                                 │   │
│  │  2. 스키마 검증                                       │   │
│  │  3. 품질 규칙 검사                                    │   │
│  │  4. 이상 탐지 (통계/ML)                               │   │
│  │  5. 품질 점수 계산                                    │   │
│  │  6. 원인 분석 (RCA)                                  │   │
│  │  7. 알림 발송                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  결과: 품질 리포트 + 알림 + 수정 제안 + 대시보드              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📅 주차별 학습 계획

### 월 5: 기초 구현

| 주차 | 주제 | 핵심 기술 | 실습 |
|------|------|----------|------|
| Week 17 | 품질 개념 | 6가지 차원 | 품질 프레임워크 |
| Week 18 | 프로파일링 | Great Expectations | 자동 검증 |
| Week 19 | 이상 탐지 | 통계, ML | 탐지 알고리즘 |
| Week 20 | LLM 품질 검사 | 의미적 검증 | 기본 Agent |

### 월 6: 고도화

| 주차 | 주제 | 핵심 기술 | 실습 |
|------|------|----------|------|
| Week 21 | 실시간 모니터링 | 스트리밍 | 대시보드 |
| Week 22 | 자동 해결 | RCA, 수정 제안 | 자동화 |
| Week 23 | 리니지 분석 | 영향 분석 | 전파 추적 |
| Week 24 | 통합 테스트 | 전체 통합 | Agent v1.0 |

---

## 📚 O'Reilly 리소스

| 도서 | 저자 | 학습 범위 |
|------|------|----------|
| [Data Quality in the Age of AI](https://www.oreilly.com/library/view/data-quality-in/9781098168698/) | Jeremy Stanley | 전체 |
| [Fundamentals of Data Engineering](https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/) | Joe Reis | Ch 8-9 |

---

## 🔧 핵심 기능

### 1. 데이터 품질 6가지 차원

| 차원 | 설명 | 검사 방법 |
|------|------|----------|
| **정확성** | 데이터가 실제 값과 일치 | 참조 데이터 비교 |
| **완전성** | 필수 데이터 존재 여부 | NULL/결측치 검사 |
| **일관성** | 데이터 간 모순 없음 | 교차 검증 |
| **적시성** | 데이터의 최신성 | 타임스탬프 검사 |
| **유효성** | 규칙/포맷 준수 | 정규식, 범위 검사 |
| **고유성** | 중복 데이터 없음 | 중복 탐지 |

### 2. 품질 규칙 예시

```python
QUALITY_RULES = {
    "email_valid": {
        "type": "format",
        "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$",
        "severity": "high"
    },
    "age_range": {
        "type": "range",
        "min": 0,
        "max": 150,
        "severity": "medium"
    },
    "not_null": {
        "type": "completeness",
        "columns": ["id", "created_at"],
        "severity": "critical"
    }
}
```

### 3. LLM 기반 의미적 검증

```python
def semantic_validation(data: pd.DataFrame, column: str) -> dict:
    """LLM을 활용한 의미적 데이터 검증"""

    prompt = f"""
    다음 데이터의 품질 이슈를 찾아주세요:

    컬럼: {column}
    샘플 데이터: {data[column].head(20).tolist()}

    다음을 검사하세요:
    1. 의미적 오류 (예: "주소" 컬럼에 이메일)
    2. 이상 패턴 (예: 갑자기 다른 형식)
    3. 잠재적 개인정보 노출

    JSON 형식으로 이슈 목록을 반환:
    """

    return llm_analyze(prompt)
```

### 4. 알림 시스템

```python
class AlertManager:
    def send_alert(self, issue: QualityIssue):
        if issue.severity == "critical":
            self.slack_alert(issue)
            self.email_alert(issue)
            self.pagerduty_alert(issue)
        elif issue.severity == "high":
            self.slack_alert(issue)
            self.email_alert(issue)
        else:
            self.slack_alert(issue)
```

---

## 💻 핵심 샘플 코드

```
samples/
├── quality_profiler.py      # 데이터 프로파일링
├── anomaly_detector.py      # 이상 탐지
├── rule_validator.py        # 규칙 기반 검증
├── semantic_checker.py      # LLM 의미 검증
├── alert_manager.py         # 알림 시스템
├── quality_dashboard.py     # Streamlit 대시보드
└── data_quality_agent/      # 통합 Agent
    ├── __init__.py
    ├── agent.py
    ├── tools/
    └── config.py
```

---

## ✅ Track C 완료 체크리스트

### 월 5 (기초)
- [ ] 품질 6차원 이해 및 검사 가능
- [ ] Great Expectations 활용 가능
- [ ] 통계/ML 기반 이상 탐지 가능
- [ ] 기본 Agent 프로토타입 완성

### 월 6 (고도화)
- [ ] 실시간 모니터링 구축 가능
- [ ] RCA 및 자동 수정 제안 가능
- [ ] 데이터 리니지 분석 가능
- [ ] Data Quality Agent v1.0 완성

---

[← Track B](../track_b_text_to_sql/README.md) | [Phase 4 →](../../phase4_project/README.md)
