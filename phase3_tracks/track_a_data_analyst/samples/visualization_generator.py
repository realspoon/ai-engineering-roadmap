"""
Visualization Generator Module
LLM 기반 차트 코드 자동 생성 및 시각화
"""

import pandas as pd
import json
from typing import Dict, Any, List, Tuple
import re
from enum import Enum


class ChartType(Enum):
    """차트 타입"""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    BOX = "box"
    PIE = "pie"
    HEATMAP = "heatmap"
    VIOLIN = "violin"


class VisualizationTemplate:
    """시각화 템플릿"""

    # Matplotlib 기본 템플릿
    MATPLOTLIB_TEMPLATES = {
        'line': '''
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('{data_source}')
fig, ax = plt.subplots(figsize=({width}, {height}))

ax.plot(df['{x_col}'], df['{y_col}'], marker='o', linewidth=2)
ax.set_xlabel('{x_label}', fontsize=12)
ax.set_ylabel('{y_label}', fontsize=12)
ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
''',
        'bar': '''
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('{data_source}')
fig, ax = plt.subplots(figsize=({width}, {height}))

ax.bar(df['{x_col}'], df['{y_col}'], color='steelblue')
ax.set_xlabel('{x_label}', fontsize=12)
ax.set_ylabel('{y_label}', fontsize=12)
ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()
''',
        'scatter': '''
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('{data_source}')
fig, ax = plt.subplots(figsize=({width}, {height}))

ax.scatter(df['{x_col}'], df['{y_col}'], alpha=0.6, s=100)
ax.set_xlabel('{x_label}', fontsize=12)
ax.set_ylabel('{y_label}', fontsize=12)
ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
''',
        'histogram': '''
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('{data_source}')
fig, ax = plt.subplots(figsize=({width}, {height}))

ax.hist(df['{column}'], bins=30, edgecolor='black', alpha=0.7)
ax.set_xlabel('{x_label}', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()
''',
        'pie': '''
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('{data_source}')
fig, ax = plt.subplots(figsize=({width}, {height}))

values = df['{y_col}']
labels = df['{x_col}']

ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
ax.set_title('{title}', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.show()
''',
        'heatmap': '''
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

df = pd.read_csv('{data_source}')
fig, ax = plt.subplots(figsize=({width}, {height}))

# 상관계수 행렬 계산
corr_matrix = df.corr(numeric_only=True)

sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
            center=0, square=True, ax=ax)
ax.set_title('{title}', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.show()
'''
    }

    # Plotly 기본 템플릿
    PLOTLY_TEMPLATES = {
        'line': '''
import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv('{data_source}')

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['{x_col}'],
    y=df['{y_col}'],
    mode='lines+markers',
    name='{y_label}'
))

fig.update_layout(
    title='{title}',
    xaxis_title='{x_label}',
    yaxis_title='{y_label}',
    width={width},
    height={height}
)

fig.show()
''',
        'bar': '''
import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv('{data_source}')

fig = go.Figure()
fig.add_trace(go.Bar(
    x=df['{x_col}'],
    y=df['{y_col}'],
    marker_color='steelblue'
))

fig.update_layout(
    title='{title}',
    xaxis_title='{x_label}',
    yaxis_title='{y_label}',
    width={width},
    height={height}
)

fig.show()
''',
        'scatter': '''
import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv('{data_source}')

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['{x_col}'],
    y=df['{y_col}'],
    mode='markers',
    marker=dict(size=10, opacity=0.6)
))

fig.update_layout(
    title='{title}',
    xaxis_title='{x_label}',
    yaxis_title='{y_label}',
    width={width},
    height={height}
)

fig.show()
'''
    }


class VisualizationAnalyzer:
    """시각화 추천 분석"""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    def analyze_column(self, column: str) -> Dict[str, Any]:
        """컬럼 분석"""
        if column not in self.df.columns:
            raise ValueError(f"컬럼을 찾을 수 없습니다: {column}")

        col_data = self.df[column]
        dtype = col_data.dtype
        unique_count = col_data.nunique()

        info = {
            'column_name': column,
            'dtype': str(dtype),
            'unique_values': unique_count,
            'missing_count': col_data.isna().sum(),
            'missing_percentage': (col_data.isna().sum() / len(col_data)) * 100
        }

        return info

    def recommend_chart(self, x_col: str = None, y_col: str = None) -> List[Dict[str, Any]]:
        """차트 타입 추천"""
        recommendations = []

        # 단일 컬럼 분석
        if x_col and not y_col:
            col_info = self.analyze_column(x_col)

            if col_info['dtype'] in ['int64', 'float64']:
                recommendations.append({
                    'chart_type': ChartType.HISTOGRAM.value,
                    'description': '분포 확인',
                    'config': {'column': x_col}
                })
                recommendations.append({
                    'chart_type': ChartType.BOX.value,
                    'description': '이상치 확인',
                    'config': {'column': x_col}
                })
            else:
                recommendations.append({
                    'chart_type': ChartType.BAR.value,
                    'description': '카테고리 분포',
                    'config': {'column': x_col}
                })

        # 두 컬럼 비교
        elif x_col and y_col:
            x_info = self.analyze_column(x_col)
            y_info = self.analyze_column(y_col)

            x_is_numeric = x_info['dtype'] in ['int64', 'float64']
            y_is_numeric = y_info['dtype'] in ['int64', 'float64']

            if x_is_numeric and y_is_numeric:
                recommendations.append({
                    'chart_type': ChartType.SCATTER.value,
                    'description': '변수 관계',
                    'config': {'x_col': x_col, 'y_col': y_col}
                })
                recommendations.append({
                    'chart_type': ChartType.LINE.value,
                    'description': '추세',
                    'config': {'x_col': x_col, 'y_col': y_col}
                })
            elif not x_is_numeric and y_is_numeric:
                recommendations.append({
                    'chart_type': ChartType.BAR.value,
                    'description': '카테고리별 값',
                    'config': {'x_col': x_col, 'y_col': y_col}
                })
            elif x_is_numeric and not y_is_numeric:
                recommendations.append({
                    'chart_type': ChartType.BOX.value,
                    'description': '분포 비교',
                    'config': {'x_col': y_col, 'y_col': x_col}
                })

        return recommendations

    def get_column_statistics(self, column: str) -> Dict[str, Any]:
        """컬럼 통계"""
        col_data = self.df[column]

        stats = {
            'column': column,
            'count': len(col_data),
            'unique': col_data.nunique()
        }

        if col_data.dtype in ['int64', 'float64']:
            stats.update({
                'mean': float(col_data.mean()),
                'std': float(col_data.std()),
                'min': float(col_data.min()),
                'max': float(col_data.max())
            })

        return stats


class CodeGenerator:
    """차트 코드 생성"""

    def __init__(self, template_type: str = 'matplotlib'):
        self.template_type = template_type.lower()

        if self.template_type == 'matplotlib':
            self.templates = VisualizationTemplate.MATPLOTLIB_TEMPLATES
        elif self.template_type == 'plotly':
            self.templates = VisualizationTemplate.PLOTLY_TEMPLATES
        else:
            raise ValueError(f"지원하지 않는 라이브러리: {template_type}")

    def generate_code(self, chart_type: str, data_source: str,
                      config: Dict[str, Any], **kwargs) -> str:
        """차트 코드 생성"""
        if chart_type not in self.templates:
            raise ValueError(f"지원하지 않는 차트: {chart_type}")

        template = self.templates[chart_type]

        # 기본값 설정
        params = {
            'data_source': data_source,
            'width': kwargs.get('width', 10),
            'height': kwargs.get('height', 6),
            'title': kwargs.get('title', f'{chart_type.capitalize()} Chart'),
            'x_label': kwargs.get('x_label', 'X Axis'),
            'y_label': kwargs.get('y_label', 'Y Axis'),
        }

        # config에서 컬럼명 추출
        params.update(config)

        # 템플릿에 파라미터 적용
        code = template.format(**params)

        return code

    def generate_multiple_charts(self, data_source: str,
                                 df: pd.DataFrame) -> Dict[str, str]:
        """여러 차트 자동 생성"""
        analyzer = VisualizationAnalyzer(df)
        generated_codes = {}

        # 각 수치형 컬럼에 대해 히스토그램 생성
        for col in analyzer.numeric_cols[:3]:  # 처음 3개만
            try:
                code = self.generate_code(
                    'histogram',
                    data_source,
                    {'column': col},
                    title=f'{col} Distribution',
                    x_label=col
                )
                generated_codes[f'histogram_{col}'] = code
            except Exception as e:
                print(f"코드 생성 실패 {col}: {str(e)}")

        # 수치형 컬럼 쌍에 대해 산점도 생성
        if len(analyzer.numeric_cols) >= 2:
            x_col, y_col = analyzer.numeric_cols[0], analyzer.numeric_cols[1]
            try:
                code = self.generate_code(
                    'scatter',
                    data_source,
                    {'x_col': x_col, 'y_col': y_col},
                    title=f'{x_col} vs {y_col}',
                    x_label=x_col,
                    y_label=y_col
                )
                generated_codes[f'scatter_{x_col}_vs_{y_col}'] = code
            except Exception as e:
                print(f"코드 생성 실패: {str(e)}")

        return generated_codes


class VisualizationOrchestrator:
    """시각화 전체 조정"""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.analyzer = VisualizationAnalyzer(df)

    def create_visualization_plan(self, data_source: str,
                                   library: str = 'matplotlib') -> Dict[str, Any]:
        """시각화 계획 생성"""
        generator = CodeGenerator(library)

        plan = {
            'data_source': data_source,
            'library': library,
            'dataset_info': {
                'rows': len(self.df),
                'columns': len(self.df.columns),
                'numeric_columns': self.analyzer.numeric_cols,
                'categorical_columns': self.analyzer.categorical_cols
            },
            'recommended_charts': [],
            'generated_codes': {}
        }

        # 수치형 컬럼별 추천
        for col in self.analyzer.numeric_cols[:3]:
            recommendations = self.analyzer.recommend_chart(col)
            for rec in recommendations:
                plan['recommended_charts'].append({
                    'chart_type': rec['chart_type'],
                    'description': rec['description'],
                    'config': rec['config']
                })

        # 코드 생성
        for chart_rec in plan['recommended_charts'][:5]:  # 처음 5개만
            try:
                code = generator.generate_code(
                    chart_rec['chart_type'],
                    data_source,
                    chart_rec['config']
                )
                key = f"{chart_rec['chart_type']}"
                if key in plan['generated_codes']:
                    key = f"{key}_{len(plan['generated_codes'])}"
                plan['generated_codes'][key] = code
            except Exception as e:
                print(f"코드 생성 실패: {str(e)}")

        return plan


# 사용 예제
if __name__ == "__main__":
    import numpy as np

    # 샘플 데이터셋
    np.random.seed(42)
    sample_df = pd.DataFrame({
        'age': np.random.normal(35, 10, 100),
        'salary': np.random.normal(50000, 15000, 100),
        'years': np.random.normal(10, 5, 100),
        'department': np.random.choice(['Sales', 'IT', 'HR'], 100)
    })

    # 시각화 계획 생성
    print("=== 시각화 계획 생성 ===\n")
    orchestrator = VisualizationOrchestrator(sample_df)
    plan = orchestrator.create_visualization_plan('/data/sample.csv')

    print(f"라이브러리: {plan['library']}")
    print(f"추천 차트 수: {len(plan['recommended_charts'])}")
    print(f"생성된 코드: {len(plan['generated_codes'])}개\n")

    # 첫 번째 생성 코드 출력
    if plan['generated_codes']:
        first_code_key = list(plan['generated_codes'].keys())[0]
        print(f"=== {first_code_key} ===")
        print(plan['generated_codes'][first_code_key])
