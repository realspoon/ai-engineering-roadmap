# Track A: Data Analyst Agent

> **목표**: 자연어로 데이터 분석을 요청하면 자동으로 분석, 시각화, 인사이트를 생성하는 AI Agent

## 🎯 최종 결과물

```
┌─────────────────────────────────────────────────────────────┐
│                  Data Analyst Agent                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  사용자: "지난 분기 매출 트렌드를 분석해줘"                     │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. 질의 분석 → 의도 파악                             │   │
│  │  2. 데이터 로딩 → 전처리                              │   │
│  │  3. 분석 계획 수립                                    │   │
│  │  4. 분석 코드 생성 및 실행                            │   │
│  │  5. 시각화 생성                                       │   │
│  │  6. 인사이트 도출                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  결과: 차트 + 핵심 인사이트 + 추가 분석 제안                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📅 주차별 학습 계획

### 월 5: 기초 구현

| 주차 | 주제 | 파일 | 실습 |
|------|------|------|------|
| Week 17 | [EDA 자동화](./week17_eda_automation.md) | pandas, 통계 | 자동 EDA 리포트 |
| Week 18 | [시각화 자동화](./week18_visualization.md) | matplotlib, plotly | 차트 코드 생성 |
| Week 19 | [인사이트 생성](./week19_insight_generation.md) | Code Interpreter | 자동 리포트 |
| Week 20 | [분석 파이프라인](./week20_pipeline.md) | LangGraph | 기본 Agent |

### 월 6: 고도화

| 주차 | 주제 | 파일 | 실습 |
|------|------|------|------|
| Week 21 | [고급 분석](./week21_advanced_analysis.md) | 시계열, 예측 | 고급 분석 모듈 |
| Week 22 | [멀티모달](./week22_multimodal.md) | PDF, 이미지 | 파일 처리 |
| Week 23 | [UI 구축](./week23_ui.md) | Streamlit | 대화형 UI |
| Week 24 | [통합 테스트](./week24_integration.md) | 전체 통합 | Agent v1.0 |

---

## 📚 O'Reilly 리소스

| 도서 | 저자 | 학습 범위 |
|------|------|----------|
| [Python for Data Analysis, 3rd Ed](https://www.oreilly.com/library/view/python-for-data/9781098104023/) | Wes McKinney | 전체 |
| [Python Data Science Handbook, 2nd Ed](https://www.oreilly.com/library/view/python-data-science/9781098121211/) | Jake VanderPlas | Ch 4-5 |
| [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) | Chip Huyen | Ch 6 |
| [Building Applications with AI Agents](https://www.oreilly.com/library/view/building-applications-with/9781098176495/) | Mariusz Skoneczko | Ch 9-10 |

---

## 💻 샘플 코드

```
samples/
├── data_loader.py           # 다양한 형식 데이터 로딩
├── eda_automation.py        # 자동 EDA
├── visualization_generator.py # 차트 코드 생성
├── insight_extractor.py     # 인사이트 추출
├── analysis_agent.py        # 분석 Agent (LangGraph)
├── streamlit_app.py         # 대화형 UI
└── data_analyst_agent/      # 통합 Agent
    ├── __init__.py
    ├── agent.py
    ├── tools/
    │   ├── analysis_tool.py
    │   ├── visualization_tool.py
    │   └── insight_tool.py
    └── config.py
```

---

## 🔧 핵심 기능

### 1. 자연어 질의 분석

```python
# 입력
"지난 분기 매출 데이터에서 가장 성장한 제품군을 찾아줘"

# Agent 분석
{
    "intent": "comparative_analysis",
    "time_range": "last_quarter",
    "metric": "sales",
    "aggregation": "by_product_category",
    "ranking": "top_growth"
}
```

### 2. 자동 분석 계획

```python
analysis_plan = [
    {"step": 1, "action": "load_data", "params": {"file": "sales.csv"}},
    {"step": 2, "action": "filter_date", "params": {"range": "Q3 2025"}},
    {"step": 3, "action": "group_by", "params": {"column": "product_category"}},
    {"step": 4, "action": "calculate_growth", "params": {"metric": "sales"}},
    {"step": 5, "action": "rank", "params": {"by": "growth_rate", "order": "desc"}},
    {"step": 6, "action": "visualize", "params": {"chart_type": "bar"}},
    {"step": 7, "action": "generate_insight", "params": {}}
]
```

### 3. 시각화 코드 자동 생성

```python
# Agent가 생성하는 코드
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
df_growth.plot(kind='bar', x='category', y='growth_rate', ax=ax)
ax.set_title('제품군별 분기 성장률')
ax.set_xlabel('제품군')
ax.set_ylabel('성장률 (%)')
plt.tight_layout()
```

### 4. 인사이트 생성

```
📊 분석 결과

1. 핵심 발견
   - '전자제품' 카테고리가 45% 성장으로 1위
   - '의류' 카테고리는 -12%로 유일하게 감소

2. 주요 원인 분석
   - 신제품 출시 효과 (전자제품)
   - 계절적 요인 (의류)

3. 추천 액션
   - 전자제품 재고 확보 검토
   - 의류 프로모션 전략 수립
```

---

## ✅ Track A 완료 체크리스트

### 월 5 (기초)
- [ ] 자동 EDA 리포트 생성 가능
- [ ] 데이터 유형별 최적 차트 추천 가능
- [ ] LLM 기반 인사이트 생성 가능
- [ ] 기본 분석 Agent 프로토타입 완성

### 월 6 (고도화)
- [ ] 시계열/상관관계 분석 가능
- [ ] 다양한 파일 형식 처리 가능
- [ ] Streamlit UI 구축 완료
- [ ] Data Analyst Agent v1.0 완성

---

[← Phase 3 목록](../README.md) | [Track B →](../track_b_text_to_sql/README.md)
