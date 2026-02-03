# Week 19: 인사이트 생성 (Insight Generation & Automated Reporting)

## 학습 목표
- Claude Code Interpreter를 활용한 데이터 분석 자동화
- 통계적 발견사항의 자동 해석 및 설명
- Claude API를 활용한 자동 리포트 생성
- 비즈니스 인사이트 추출 및 액션 아이템 도출

## O'Reilly 리소스
- "The Art of Statistics" - David Spiegelhalter
- "Storytelling with Data" - Cole Nussbaumer Knaflic
- "Causal Inference: The Mixtape"
- O'Reilly Data Storytelling Guide

## 핵심 개념

### 1. Code Interpreter를 활용한 분석
```python
import anthropic
import json

def run_analysis_with_code_interpreter(df, analysis_query):
    """Code Interpreter를 활용한 데이터 분석"""
    client = anthropic.Anthropic()

    # 데이터를 JSON으로 변환
    df_json = df.to_json(orient='records')

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        tools=[
            {
                "name": "python",
                "type": "tool",
                "description": "Python 코드 실행",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "실행할 Python 코드"
                        }
                    },
                    "required": ["code"]
                }
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"""
                다음 데이터셋에 대해 {analysis_query}를 수행하세요.

                데이터셋: {df_json[:2000]}

                Python 코드를 작성하여 분석을 수행하고 결과를 해석하세요.
                """
            }
        ]
    )

    return message
```

### 2. 자동 인사이트 추출
```python
class InsightGenerator:
    def __init__(self, df, client=None):
        self.df = df
        self.client = client or anthropic.Anthropic()
        self.insights = []

    def extract_statistical_insights(self):
        """통계적 인사이트 추출"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            data = self.df[col]

            # 기본 통계
            insight = {
                'column': col,
                'type': 'statistical',
                'metrics': {
                    'mean': float(data.mean()),
                    'median': float(data.median()),
                    'std': float(data.std()),
                    'skewness': float(data.skew()),
                    'kurtosis': float(data.kurtosis())
                }
            }

            # 해석
            interpretation = self._interpret_statistics(data)
            insight['interpretation'] = interpretation

            self.insights.append(insight)

        return self.insights

    def _interpret_statistics(self, data):
        """통계 결과 해석"""
        skewness = data.skew()
        kurtosis = data.kurtosis()

        interpretation = []

        # 왜도 해석
        if abs(skewness) < 0.5:
            interpretation.append("분포가 거의 대칭적입니다")
        elif skewness > 0.5:
            interpretation.append("데이터가 오른쪽으로 치우쳐 있습니다")
        else:
            interpretation.append("데이터가 왼쪽으로 치우쳐 있습니다")

        # 첨도 해석
        if kurtosis > 3:
            interpretation.append("꼬리가 두꺼운 분포입니다 (이상치 포함 가능)")
        else:
            interpretation.append("비교적 정상적인 분포입니다")

        return " ".join(interpretation)

    def extract_correlation_insights(self, threshold=0.5):
        """상관관계 인사이트"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        corr_matrix = self.df[numeric_cols].corr()

        insights = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > threshold:
                    insights.append({
                        'type': 'correlation',
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': float(corr_value),
                        'strength': self._correlation_strength(corr_value)
                    })

        return insights

    def _correlation_strength(self, corr_value):
        """상관계수 강도 판정"""
        abs_corr = abs(corr_value)
        if abs_corr > 0.7:
            return '강함'
        elif abs_corr > 0.4:
            return '중간'
        else:
            return '약함'

    def extract_anomaly_insights(self):
        """이상치 관련 인사이트"""
        from scipy import stats

        insights = []
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            z_scores = np.abs(stats.zscore(self.df[col].dropna()))
            anomalies = (z_scores > 3).sum()

            if anomalies > 0:
                insights.append({
                    'type': 'anomaly',
                    'column': col,
                    'count': int(anomalies),
                    'percentage': float(anomalies / len(self.df) * 100)
                })

        return insights
```

### 3. 자동 리포트 생성
```python
def generate_auto_report(df, insights, analysis_name):
    """Claude API를 활용한 자동 리포트 생성"""
    client = anthropic.Anthropic()

    # 인사이트를 텍스트로 변환
    insights_text = json.dumps(insights, indent=2, ensure_ascii=False)

    prompt = f"""
    다음 분석 결과를 기반으로 전문적인 데이터 분석 리포트를 작성하세요:

    분석명: {analysis_name}
    데이터셋 크기: {df.shape}
    분석 결과:
    {insights_text}

    리포트는 다음을 포함해야 합니다:
    1. 요약 (Executive Summary)
    2. 주요 발견사항 (Key Findings)
    3. 상세 분석 (Detailed Analysis)
    4. 권장사항 (Recommendations)
    5. 다음 단계 (Next Steps)

    마크다운 형식으로 작성하고, 전문적이고 명확한 표현을 사용하세요.
    """

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text
```

### 4. 비즈니스 액션 아이템 도출
```python
def derive_action_items(insights, domain_context):
    """비즈니스 액션 아이템 도출"""
    client = anthropic.Anthropic()

    insights_summary = json.dumps(insights, indent=2, ensure_ascii=False)

    prompt = f"""
    다음 분석 인사이트를 기반으로 비즈니스 액션 아이템을 도출하세요:

    도메인: {domain_context}
    인사이트:
    {insights_summary}

    각 액션 아이템에 대해:
    1. 우선순위 (높음/중간/낮음)
    2. 예상 영향 (고/중/저)
    3. 구현 기간 (일주일/한달/분기)
    4. 책임자
    5. 성공 지표

    JSON 형식으로 반환하세요.
    """

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return json.loads(message.content[0].text)
```

## 실습 과제

### Task 1: 완전한 인사이트 생성 파이프라인
```python
class InsightPipeline:
    def __init__(self, df):
        self.df = df
        self.generator = InsightGenerator(df)

    def run_complete_analysis(self):
        """전체 분석 실행"""
        statistical_insights = self.generator.extract_statistical_insights()
        correlation_insights = self.generator.extract_correlation_insights()
        anomaly_insights = self.generator.extract_anomaly_insights()

        all_insights = {
            'statistical': statistical_insights,
            'correlation': correlation_insights,
            'anomaly': anomaly_insights
        }

        # 리포트 생성
        report = generate_auto_report(
            self.df, all_insights, "자동 데이터 분석 리포트"
        )

        # 액션 아이템 도출
        action_items = derive_action_items(
            all_insights, "일반 비즈니스"
        )

        return {
            'insights': all_insights,
            'report': report,
            'action_items': action_items
        }

    def save_results(self, output_path):
        """결과 저장"""
        results = self.run_complete_analysis()
        with open(f'{output_path}/report.md', 'w') as f:
            f.write(results['report'])
        with open(f'{output_path}/insights.json', 'w') as f:
            json.dump(results['insights'], f, ensure_ascii=False, indent=2)
        with open(f'{output_path}/action_items.json', 'w') as f:
            json.dump(results['action_items'], f, ensure_ascii=False, indent=2)
```

### Task 2: 다양한 도메인별 분석
- 금융 데이터: 변동성, 트렌드, 리스크 분석
- 마케팅 데이터: 고객 세분화, 효율성 분석
- 운영 데이터: 병목 지점, 최적화 기회

### Task 3: 리포트 자동화
- 마크다운 형식의 전문적 리포트
- PDF 자동 생성
- 이메일 자동 배포

## 주간 체크포인트

- [ ] Code Interpreter 통합 분석 구현
- [ ] 통계 인사이트 자동 추출
- [ ] 상관관계 분석 및 해석
- [ ] 이상치 감지 및 보고
- [ ] Claude API 리포트 생성
- [ ] 액션 아이템 자동 도출
- [ ] 5개 이상의 데이터셋으로 테스트
- [ ] 리포트 품질 검증

## 학습 성과 기준
- [ ] 생성된 리포트 전문성 평가 > 8/10
- [ ] 액션 아이템의 실용성 > 80%
- [ ] 리포트 생성 시간 < 5분/분석
