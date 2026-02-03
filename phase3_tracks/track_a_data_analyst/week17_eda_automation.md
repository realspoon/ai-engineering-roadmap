# Week 17: EDA 자동화 (Exploratory Data Analysis Automation)

## 학습 목표
- Pandas Profiling을 활용한 자동 탐색적 데이터 분석 구현
- 통계 분석 자동화 (기술통계, 분포, 이상치 감지)
- Claude API를 활용한 EDA 리포트 자동 생성
- 데이터 품질 평가 자동화

## O'Reilly 리소스
- "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow" - Chapter 2: End-to-End ML Project
- "Python Data Analysis" - Pandas 심화
- "Statistical Rethinking" - 기술통계 이론
- O'Reilly Data Science Handbook - EDA 모범 사례

## 핵심 개념

### 1. Pandas Profiling
```python
import pandas as pd
from ydata_profiling import ProfileReport

# 기본 프로파일 생성
df = pd.read_csv('data.csv')
profile = ProfileReport(df, title="EDA Report")
profile.to_html("report.html")

# 상세 설정
profile = ProfileReport(
    df,
    title="Detailed EDA",
    explorative=True,
    missing_threshold=0.5,
    vars={'num': {'skewness_threshold': 2}}
)
```

### 2. 통계 분석 자동화
```python
import numpy as np
from scipy import stats

def auto_statistics(df):
    """자동 통계 분석"""
    stats_dict = {}

    for col in df.select_dtypes(include=[np.number]).columns:
        stats_dict[col] = {
            'mean': df[col].mean(),
            'median': df[col].median(),
            'std': df[col].std(),
            'skewness': df[col].skew(),
            'kurtosis': df[col].kurtosis(),
            'q1': df[col].quantile(0.25),
            'q3': df[col].quantile(0.75),
            'iqr': df[col].quantile(0.75) - df[col].quantile(0.25)
        }

    return stats_dict

# 이상치 감지 (IQR 방법)
def detect_outliers(df, threshold=1.5):
    """IQR 기반 이상치 감지"""
    outliers = {}
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - threshold * IQR
    upper_bound = Q3 + threshold * IQR

    for col in df.columns:
        outliers[col] = df[(df[col] < lower_bound[col]) |
                          (df[col] > upper_bound[col])].index.tolist()

    return outliers
```

### 3. 데이터 품질 평가
```python
def assess_data_quality(df):
    """데이터 품질 점수 계산"""
    quality_report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicates': len(df[df.duplicated()]),
        'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
        'data_types': df.dtypes.to_dict(),
        'completeness': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    }
    return quality_report
```

### 4. Claude API와 통합
```python
import anthropic

def generate_eda_insights(df, stats_dict):
    """Claude를 활용한 자동 인사이트 생성"""
    client = anthropic.Anthropic()

    # 데이터 요약
    summary = f"""
    Dataset shape: {df.shape}
    Columns: {df.columns.tolist()}
    Data types: {df.dtypes.to_dict()}
    Missing values: {df.isnull().sum().to_dict()}
    Statistics: {stats_dict}
    """

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"데이터 분석가로서 다음 데이터셋을 분석하고 주요 발견사항을 정리해주세요:\n{summary}"
            }
        ]
    )

    return message.content[0].text
```

## 실습 과제

### Task 1: 자동 EDA 파이프라인
```python
class EDAAutomation:
    def __init__(self, df):
        self.df = df
        self.profile = None
        self.stats = None
        self.quality = None

    def run_complete_eda(self):
        """전체 EDA 실행"""
        self.generate_profile()
        self.compute_statistics()
        self.assess_quality()
        return self.generate_report()

    def generate_profile(self):
        """Pandas Profiling 생성"""
        from ydata_profiling import ProfileReport
        self.profile = ProfileReport(self.df, title="Auto EDA")

    def compute_statistics(self):
        """통계 분석 수행"""
        self.stats = auto_statistics(self.df)
        self.outliers = detect_outliers(self.df)

    def assess_quality(self):
        """데이터 품질 평가"""
        self.quality = assess_data_quality(self.df)

    def generate_report(self):
        """리포트 생성"""
        return {
            'profile': self.profile,
            'statistics': self.stats,
            'quality': self.quality,
            'outliers': self.outliers
        }

# 사용 예시
eda = EDAAutomation(df)
results = eda.run_complete_eda()
```

### Task 2: 카테고리별 분석
- 수치형 변수: 분포 분석, 상관관계 행렬
- 범주형 변수: 빈도 분석, 카이제곱 검정
- 혼합형: 변수 간 관계 시각화

### Task 3: Claude API 통합
- EDA 결과를 Claude에 전달
- 자동 인사이트 생성
- 데이터 품질 이슈 자동 식별
- 권장사항 생성

## 주간 체크포인트

- [ ] Pandas Profiling으로 기본 EDA 구현
- [ ] 통계 분석 자동화 함수 작성
- [ ] 이상치 감지 알고리즘 구현
- [ ] 데이터 품질 평가 시스템 구축
- [ ] Claude API 통합 및 테스트
- [ ] 자동 리포트 생성 기능 완성
- [ ] 10개 이상의 다양한 데이터셋으로 테스트
- [ ] 주간 마일스톤 달성 확인

## 학습 성과 기준
- [ ] 다양한 유형의 데이터셋에서 완전한 EDA 생성
- [ ] Claude API를 활용한 자동 인사이트 정확도 > 80%
- [ ] 데이터 품질 이슈 자동 감지 정확도 > 85%
