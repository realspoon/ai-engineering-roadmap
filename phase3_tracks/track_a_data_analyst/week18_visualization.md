# Week 18: 시각화 자동화 (Visualization Automation)

## 학습 목표
- Claude API를 활용한 자동 시각화 코드 생성
- Matplotlib과 Plotly를 활용한 정적/동적 차트 생성
- 데이터 특성에 맞는 최적의 시각화 자동 선택
- 인터랙티브 대시보드 기초 구축

## O'Reilly 리소스
- "Fundamentals of Data Visualization" - Edward Tufte 원칙
- "Interactive Data Visualization with Plotly in Python"
- "Matplotlib for Python Developers"
- O'Reilly Visual Analysis Best Practices

## 핵심 개념

### 1. Claude API를 활용한 코드 생성
```python
import anthropic

def generate_visualization_code(df, column_name, analysis_type):
    """Claude가 시각화 코드를 자동으로 생성"""
    client = anthropic.Anthropic()

    prompt = f"""
    주어진 데이터프레임 정보를 바탕으로 Python Matplotlib/Plotly 코드를 생성하세요.

    데이터프레임 정보:
    - 크기: {df.shape}
    - 컬럼 '{column_name}' 타입: {df[column_name].dtype}
    - 샘플 데이터: {df[column_name].head().tolist()}

    분석 유형: {analysis_type}

    다음 조건을 만족하는 완성된 Python 코드를 제공하세요:
    1. 필요한 라이브러리 import 포함
    2. 효과적인 시각화 선택
    3. 적절한 레이블과 제목
    4. 한국어 지원
    5. 저장 기능 포함
    """

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text
```

### 2. Matplotlib 자동 생성
```python
import matplotlib.pyplot as plt
import numpy as np

def auto_matplotlib_viz(df, column, viz_type='histogram'):
    """자동 matplotlib 시각화"""
    fig, ax = plt.subplots(figsize=(12, 6))

    if viz_type == 'histogram':
        ax.hist(df[column], bins=50, edgecolor='black', alpha=0.7)
        ax.set_title(f'{column} 분포도')
        ax.set_xlabel(column)
        ax.set_ylabel('빈도')

    elif viz_type == 'boxplot':
        ax.boxplot(df[column], vert=True)
        ax.set_title(f'{column} 박스플롯')
        ax.set_ylabel(column)

    elif viz_type == 'scatter':
        ax.scatter(df.index, df[column], alpha=0.6)
        ax.set_title(f'{column} 시계열 플롯')
        ax.set_xlabel('인덱스')
        ax.set_ylabel(column)

    elif viz_type == 'density':
        df[column].plot(kind='density', ax=ax)
        ax.set_title(f'{column} 확률밀도함수')

    plt.tight_layout()
    return fig

def create_correlation_heatmap(df):
    """상관관계 히트맵"""
    import seaborn as sns

    fig, ax = plt.subplots(figsize=(12, 10))
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr_matrix = df[numeric_cols].corr()

    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, square=True, ax=ax, cbar_kws={'label': '상관계수'})
    ax.set_title('변수 간 상관관계 행렬')
    plt.tight_layout()

    return fig
```

### 3. Plotly 인터랙티브 시각화
```python
import plotly.graph_objects as go
import plotly.express as px

def create_interactive_viz(df, column, viz_type='scatter'):
    """Plotly를 활용한 인터랙티브 시각화"""

    if viz_type == 'scatter':
        fig = px.scatter(df, x=df.index, y=column,
                        title=f'{column} 시각화',
                        labels={'y': column, 'x': '인덱스'},
                        hover_data=df.columns)

    elif viz_type == 'box':
        fig = px.box(df, y=column, title=f'{column} 박스플롯')

    elif viz_type == 'histogram':
        fig = px.histogram(df, x=column, nbins=50,
                          title=f'{column} 히스토그램')

    elif viz_type == 'violin':
        fig = px.violin(df, y=column, title=f'{column} 바이올린 플롯')

    fig.update_layout(
        hovermode='x unified',
        font=dict(family='Arial', size=12),
        title_font_size=16
    )

    return fig

def create_multi_series_plot(df, columns):
    """여러 시계열 데이터 플롯"""
    fig = go.Figure()

    for col in columns:
        fig.add_trace(go.Scatter(
            y=df[col],
            mode='lines',
            name=col,
            hovertemplate=f'{col}: %{{y:.2f}}<extra></extra>'
        ))

    fig.update_layout(
        title='다중 시계열 분석',
        xaxis_title='시간',
        yaxis_title='값',
        hovermode='x unified',
        height=500
    )

    return fig
```

### 4. 시각화 타입 자동 선택
```python
def recommend_visualization(df, column):
    """데이터 특성에 맞는 최적의 시각화 추천"""
    dtype = df[column].dtype
    n_unique = df[column].nunique()
    n_total = len(df)

    # 범주형 데이터
    if dtype == 'object' or n_unique <= 20:
        return {
            'primary': 'bar',
            'secondary': ['pie', 'count']
        }

    # 연속형 데이터 (적은 샘플)
    elif n_total < 100:
        return {
            'primary': 'scatter',
            'secondary': ['line', 'strip']
        }

    # 연속형 데이터 (많은 샘플)
    else:
        return {
            'primary': 'histogram',
            'secondary': ['density', 'box', 'violin']
        }
```

## 실습 과제

### Task 1: 시각화 자동 생성 엔진
```python
class VisualizationEngine:
    def __init__(self, df):
        self.df = df
        self.client = anthropic.Anthropic()

    def generate_viz(self, column, output_format='matplotlib'):
        """자동 시각화 생성"""
        viz_type = recommend_visualization(self.df, column)

        if output_format == 'matplotlib':
            return auto_matplotlib_viz(
                self.df, column,
                viz_type=viz_type['primary']
            )
        elif output_format == 'plotly':
            return create_interactive_viz(
                self.df, column,
                viz_type=viz_type['primary']
            )

    def generate_comprehensive_report(self, columns=None):
        """포괄적 시각화 리포트"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns

        visualizations = {}
        for col in columns[:5]:  # 처음 5개 컬럼
            visualizations[col] = self.generate_viz(col)

        return visualizations

    def generate_code_examples(self, column):
        """Claude가 코드 예제 생성"""
        return generate_visualization_code(
            self.df, column, 'exploratory'
        )
```

### Task 2: 다양한 시각화 유형 구현
- 단변량 분석: 히스토그램, 밀도함수, 박스플롯
- 이변량 분석: 산점도, 회귀선 포함
- 다변량 분석: 히트맵, 평행좌표 플롯
- 시계열: 라인 플롯, 캔들스틱

### Task 3: 대시보드 기초
- 여러 시각화를 한 페이지에 배치
- Plotly Subplots 활용
- 반응형 레이아웃 구현

## 주간 체크포인트

- [ ] Claude API 통합 시각화 코드 생성
- [ ] Matplotlib 자동 시각화 10개 이상 유형
- [ ] Plotly 인터랙티브 시각화 구현
- [ ] 시각화 타입 자동 추천 시스템
- [ ] 상관관계 히트맵 생성
- [ ] 다중 시계열 시각화
- [ ] 20개 이상의 다양한 차트 테스트
- [ ] 한국어 레이블 처리 완료

## 학습 성과 기준
- [ ] 데이터 특성에 맞는 최적 시각화 선택률 > 85%
- [ ] Claude 생성 코드 실행 성공률 > 90%
- [ ] 시각화 프로세싱 속도 < 2초/차트
