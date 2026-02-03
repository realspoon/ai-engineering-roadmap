# Week 23: 결과 해석 (자연어 설명, 시각화)

## 학습 목표
- SQL 쿼리 결과를 자연어로 설명
- 결과 데이터 시각화
- 이상치 감지 및 설명
- 사용자 친화적 인사이트 도출

## O'Reilly 리소스
- **"Effective Data Visualization"** - Stephanie Evergreen
- **"The Grammar of Graphics"** - Leland Wilkinson
- **"Data Story Telling"** - Cole Nussbaumer Knaflic

## 핵심 개념

### 1. 결과 해석 시스템
```python
from typing import List, Dict, Any
import statistics

class ResultInterpreter:
    """SQL 쿼리 결과 해석"""

    def __init__(self):
        self.data = None
        self.metadata = {}

    def load_data(self, query_result: List[Dict],
                 query: str = "", column_types: Dict = None):
        """결과 데이터 로드"""
        self.data = query_result
        self.metadata = {
            'row_count': len(query_result),
            'column_count': len(query_result[0]) if query_result else 0,
            'query': query,
            'column_types': column_types or {}
        }

    def analyze_data(self) -> Dict[str, Any]:
        """데이터 분석"""
        if not self.data:
            return {'error': 'No data to analyze'}

        analysis = {
            'summary_stats': self._calculate_stats(),
            'data_quality': self._assess_quality(),
            'patterns': self._detect_patterns(),
            'anomalies': self._detect_anomalies()
        }

        return analysis

    def _calculate_stats(self) -> Dict:
        """통계 계산"""
        stats = {}

        for col_name in self.data[0].keys():
            values = [row[col_name] for row in self.data]

            # 숫자형 데이터 처리
            if all(isinstance(v, (int, float)) for v in values if v is not None):
                numeric_values = [v for v in values if v is not None]

                if numeric_values:
                    stats[col_name] = {
                        'type': 'numeric',
                        'count': len(numeric_values),
                        'min': min(numeric_values),
                        'max': max(numeric_values),
                        'mean': statistics.mean(numeric_values),
                        'median': statistics.median(numeric_values),
                        'stdev': statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
                    }
            else:
                # 문자열/범주형 데이터 처리
                non_null = [v for v in values if v is not None]
                unique_count = len(set(non_null))

                stats[col_name] = {
                    'type': 'categorical',
                    'count': len(non_null),
                    'unique': unique_count,
                    'null_count': len(values) - len(non_null)
                }

        return stats

    def _assess_quality(self) -> Dict:
        """데이터 품질 평가"""
        quality = {
            'missing_values': 0,
            'null_percentage': 0,
            'duplicate_rows': 0,
            'quality_score': 0
        }

        # NULL 값 개수
        total_cells = self.metadata['row_count'] * self.metadata['column_count']
        null_count = sum(
            1 for row in self.data
            for value in row.values()
            if value is None
        )

        quality['missing_values'] = null_count
        quality['null_percentage'] = (null_count / total_cells * 100) if total_cells > 0 else 0

        # 중복 행 감지
        unique_rows = len(set(tuple(row.items()) for row in self.data))
        quality['duplicate_rows'] = self.metadata['row_count'] - unique_rows

        # 품질 점수 (0-100)
        quality['quality_score'] = max(0, 100 - quality['null_percentage'])

        return quality

    def _detect_patterns(self) -> List[str]:
        """패턴 감지"""
        patterns = []

        for col_name in self.data[0].keys():
            values = [row[col_name] for row in self.data
                     if row[col_name] is not None]

            if not values:
                continue

            # 증가/감소 추세
            if all(isinstance(v, (int, float)) for v in values):
                if len(values) > 2:
                    diffs = [values[i] - values[i-1] for i in range(1, len(values))]
                    all_increasing = all(d > 0 for d in diffs)
                    all_decreasing = all(d < 0 for d in diffs)

                    if all_increasing:
                        patterns.append(f"'{col_name}' shows consistent increase")
                    elif all_decreasing:
                        patterns.append(f"'{col_name}' shows consistent decrease")

        return patterns

    def _detect_anomalies(self) -> List[Dict]:
        """이상치 감지 (IQR 방식)"""
        anomalies = []

        for col_name in self.data[0].keys():
            values = [row[col_name] for row in self.data
                     if isinstance(row[col_name], (int, float))]

            if len(values) < 4:
                continue

            sorted_vals = sorted(values)
            q1 = sorted_vals[len(sorted_vals) // 4]
            q3 = sorted_vals[3 * len(sorted_vals) // 4]
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            for row in self.data:
                val = row[col_name]
                if isinstance(val, (int, float)) and (val < lower_bound or val > upper_bound):
                    anomalies.append({
                        'column': col_name,
                        'value': val,
                        'type': 'outlier',
                        'bounds': (lower_bound, upper_bound)
                    })

        return anomalies

    def interpret_result(self) -> str:
        """결과를 자연어로 해석"""
        if not self.data:
            return "No data returned from query."

        interpretation = []

        # 기본 정보
        interpretation.append(
            f"The query returned {self.metadata['row_count']} rows "
            f"with {self.metadata['column_count']} columns."
        )

        # 통계 정보
        stats = self._calculate_stats()
        for col_name, col_stats in stats.items():
            if col_stats['type'] == 'numeric':
                interpretation.append(
                    f"'{col_name}' ranges from {col_stats['min']} to {col_stats['max']} "
                    f"with an average of {col_stats['mean']:.2f}."
                )
            else:
                interpretation.append(
                    f"'{col_name}' has {col_stats['unique']} unique values "
                    f"({col_stats['null_count']} missing)."
                )

        # 패턴
        patterns = self._detect_patterns()
        if patterns:
            interpretation.append("Notable patterns:")
            for pattern in patterns:
                interpretation.append(f"  - {pattern}")

        # 이상치
        anomalies = self._detect_anomalies()
        if anomalies:
            interpretation.append(f"Found {len(anomalies)} anomalies (outliers).")

        return "\n".join(interpretation)
```

### 2. 자연어 생성 (NLG)
```python
from enum import Enum

class QueryType(Enum):
    AGGREGATION = "aggregation"
    COMPARISON = "comparison"
    TREND = "trend"
    DISTRIBUTION = "distribution"
    RANKING = "ranking"

class NaturalLanguageGenerator:
    """자연어 생성기"""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict:
        """응답 템플릿 로드"""
        return {
            'aggregation': [
                "The total {metric} is {value}.",
                "We have {count} records with an average {metric} of {value}.",
                "The sum of {metric} across all records is {value}."
            ],
            'comparison': [
                "{item1} has {value1} {metric} compared to {item2}'s {value2}.",
                "{item1} outperforms {item2} by {diff} in {metric}.",
            ],
            'trend': [
                "There is a {direction} trend in {metric} over time.",
                "{metric} has been {direction} steadily from {start} to {end}.",
            ],
            'ranking': [
                "The top {count} {items} by {metric} are: {list}.",
                "{item} ranks #{rank} in {metric} with a value of {value}.",
            ]
        }

    def generate_narrative(self, data: List[Dict], query: str) -> str:
        """데이터 기반 설명 생성"""
        if not data:
            return "No results found."

        # 쿼리 타입 분석
        query_type = self._analyze_query_type(query)

        # 타입에 맞는 설명 생성
        if query_type == QueryType.AGGREGATION:
            return self._generate_aggregation_narrative(data)
        elif query_type == QueryType.RANKING:
            return self._generate_ranking_narrative(data)
        elif query_type == QueryType.COMPARISON:
            return self._generate_comparison_narrative(data)
        else:
            return self._generate_generic_narrative(data)

    def _analyze_query_type(self, query: str) -> QueryType:
        """쿼리 타입 분석"""
        query_upper = query.upper()

        if 'GROUP BY' in query_upper or 'COUNT' in query_upper or 'SUM' in query_upper:
            return QueryType.AGGREGATION
        elif 'ORDER BY' in query_upper and ('LIMIT' in query_upper or 'TOP' in query_upper):
            return QueryType.RANKING
        elif 'PARTITION BY' in query_upper or 'OVER' in query_upper:
            return QueryType.TREND
        else:
            return QueryType.COMPARISON

    def _generate_aggregation_narrative(self, data: List[Dict]) -> str:
        """집계 결과 설명"""
        if not data:
            return "No data available."

        first_row = data[0]
        narrative = []

        # 첫 번째 행 분석
        for key, value in first_row.items():
            if isinstance(value, (int, float)):
                narrative.append(f"The {key} is {value}.")
            else:
                narrative.append(f"The {key} is '{value}'.")

        # 전체 요약
        narrative.append(f"This analysis includes {len(data)} records.")

        return " ".join(narrative)

    def _generate_ranking_narrative(self, data: List[Dict]) -> str:
        """랭킹 결과 설명"""
        if not data:
            return "No ranking data available."

        narrative = [f"Here are the top {len(data)} results:"]

        for i, row in enumerate(data[:5], 1):
            items = [f"{k}: {v}" for k, v in row.items()]
            narrative.append(f"{i}. {', '.join(items)}")

        return "\n".join(narrative)

    def _generate_comparison_narrative(self, data: List[Dict]) -> str:
        """비교 결과 설명"""
        if len(data) < 2:
            return self._generate_generic_narrative(data)

        narrative = []
        first = data[0]
        second = data[1]

        for key in first.keys():
            v1 = first[key]
            v2 = second[key]

            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                diff = v1 - v2
                direction = "higher" if diff > 0 else "lower"
                narrative.append(
                    f"The first item's {key} is {abs(diff)} {direction} "
                    f"than the second."
                )

        return " ".join(narrative)

    def _generate_generic_narrative(self, data: List[Dict]) -> str:
        """일반적인 설명 생성"""
        narrative = f"The query returned {len(data)} result(s)."

        if len(data) <= 3:
            for i, row in enumerate(data, 1):
                items = [f"{k}: {v}" for k, v in row.items()]
                narrative += f"\n{i}. {', '.join(items)}"

        return narrative
```

### 3. 데이터 시각화
```python
import matplotlib.pyplot as plt
import pandas as pd

class DataVisualizer:
    """데이터 시각화"""

    def __init__(self, data: List[Dict]):
        self.data = data
        self.df = pd.DataFrame(data)

    def visualize(self, chart_type: str = 'auto',
                 x_col: str = None, y_col: str = None) -> str:
        """자동으로 적절한 시각화 선택"""

        if chart_type == 'auto':
            chart_type = self._suggest_chart_type()

        if chart_type == 'bar':
            return self._create_bar_chart(x_col, y_col)
        elif chart_type == 'line':
            return self._create_line_chart(x_col, y_col)
        elif chart_type == 'pie':
            return self._create_pie_chart(x_col, y_col)
        elif chart_type == 'scatter':
            return self._create_scatter_chart(x_col, y_col)
        elif chart_type == 'histogram':
            return self._create_histogram(y_col)
        else:
            return self._create_table_visualization()

    def _suggest_chart_type(self) -> str:
        """최적의 차트 타입 제안"""
        # 컬럼 개수와 타입 기반으로 제안
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        object_cols = self.df.select_dtypes(include=['object']).columns

        if len(object_cols) == 1 and len(numeric_cols) == 1:
            return 'bar'
        elif len(numeric_cols) >= 2:
            return 'scatter'
        elif len(object_cols) >= 1 and len(numeric_cols) == 1:
            return 'pie'
        else:
            return 'table'

    def _create_bar_chart(self, x_col: str = None, y_col: str = None) -> str:
        """막대 차트 생성"""
        if not x_col:
            x_col = self.df.columns[0]
        if not y_col:
            y_col = self.df.columns[1] if len(self.df.columns) > 1 else None

        fig, ax = plt.subplots(figsize=(10, 6))
        self.df.set_index(x_col)[y_col].plot(kind='bar', ax=ax)
        ax.set_title(f"{y_col} by {x_col}")
        ax.set_ylabel(y_col)
        ax.set_xlabel(x_col)

        return self._save_figure(fig)

    def _create_line_chart(self, x_col: str = None, y_col: str = None) -> str:
        """선 차트 생성"""
        if not x_col:
            x_col = self.df.columns[0]
        if not y_col:
            y_col = self.df.columns[1]

        fig, ax = plt.subplots(figsize=(10, 6))
        self.df.plot(x=x_col, y=y_col, ax=ax, kind='line')
        ax.set_title(f"{y_col} Trend")

        return self._save_figure(fig)

    def _create_pie_chart(self, x_col: str = None, y_col: str = None) -> str:
        """원형 차트 생성"""
        if not x_col:
            x_col = self.df.columns[0]
        if not y_col:
            y_col = self.df.columns[1]

        fig, ax = plt.subplots(figsize=(8, 8))
        self.df.set_index(x_col)[y_col].plot(kind='pie', ax=ax, autopct='%1.1f%%')
        ax.set_ylabel('')
        ax.set_title(f"Distribution of {y_col}")

        return self._save_figure(fig)

    def _create_scatter_chart(self, x_col: str = None, y_col: str = None) -> str:
        """산점도 생성"""
        if not x_col:
            x_col = self.df.columns[0]
        if not y_col:
            y_col = self.df.columns[1]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(self.df[x_col], self.df[y_col])
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} vs {x_col}")

        return self._save_figure(fig)

    def _create_histogram(self, y_col: str = None) -> str:
        """히스토그램 생성"""
        if not y_col:
            y_col = self.df.columns[0]

        fig, ax = plt.subplots(figsize=(10, 6))
        self.df[y_col].plot(kind='hist', ax=ax, bins=20)
        ax.set_title(f"Distribution of {y_col}")
        ax.set_xlabel(y_col)

        return self._save_figure(fig)

    def _create_table_visualization(self) -> str:
        """테이블 시각화"""
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.axis('tight')
        ax.axis('off')

        table = ax.table(cellText=self.df.values,
                        colLabels=self.df.columns,
                        cellLoc='center',
                        loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)

        return self._save_figure(fig)

    def _save_figure(self, fig) -> str:
        """그림 저장 및 경로 반환"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            fig.savefig(f.name, dpi=100, bbox_inches='tight')
            plt.close(fig)
            return f.name
```

### 4. 통합 결과 해석기
```python
class Comprehensi ResultAnalyzer:
    """결과 분석 및 인사이트 제공"""

    def __init__(self, query: str, result: List[Dict]):
        self.query = query
        self.result = result
        self.interpreter = ResultInterpreter()
        self.nlg = NaturalLanguageGenerator()
        self.visualizer = DataVisualizer(result) if result else None

    def analyze_and_explain(self) -> Dict:
        """종합 분석 및 설명"""
        self.interpreter.load_data(self.result, self.query)

        return {
            'summary': self._generate_summary(),
            'narrative': self.nlg.generate_narrative(self.result, self.query),
            'insights': self._extract_insights(),
            'visualization': self._generate_visualization(),
            'statistics': self.interpreter.analyze_data(),
            'recommendations': self._generate_recommendations()
        }

    def _generate_summary(self) -> str:
        """요약 생성"""
        if not self.result:
            return "Query returned no results."

        return (f"Query returned {len(self.result)} rows with "
                f"{len(self.result[0])} columns.")

    def _extract_insights(self) -> List[str]:
        """인사이트 추출"""
        insights = []

        analysis = self.interpreter.analyze_data()

        # 이상치에 대한 인사이트
        anomalies = analysis.get('anomalies', [])
        if anomalies:
            insights.append(f"Found {len(anomalies)} anomalies that may need investigation.")

        # 데이터 품질 인사이트
        quality = analysis.get('data_quality', {})
        if quality.get('null_percentage', 0) > 10:
            insights.append(
                f"Data quality concern: {quality['null_percentage']:.1f}% missing values"
            )

        # 패턴 인사이트
        patterns = analysis.get('patterns', [])
        for pattern in patterns:
            insights.append(f"Pattern detected: {pattern}")

        return insights

    def _generate_visualization(self) -> str:
        """시각화 생성"""
        if not self.visualizer:
            return None

        try:
            return self.visualizer.visualize()
        except:
            return None

    def _generate_recommendations(self) -> List[str]:
        """권장사항 제공"""
        recommendations = []

        analysis = self.interpreter.analyze_data()

        # 데이터 품질 기반 권장
        quality = analysis.get('data_quality', {})
        if quality.get('duplicate_rows', 0) > 0:
            recommendations.append(
                "Consider removing duplicate rows for better analysis."
            )

        # 이상치 기반 권장
        anomalies = analysis.get('anomalies', [])
        if len(anomalies) > len(self.result) * 0.1:
            recommendations.append(
                "High number of outliers detected. Investigate data quality."
            )

        return recommendations
```

## 실습 과제

### 과제 1: 결과 해석기 구현
```python
# 요구사항:
# 1. ResultInterpreter 완전 구현
# 2. 5개의 서로 다른 데이터셋으로 테스트
# 3. 통계, 품질, 패턴, 이상치 모두 감지
# 4. 자동 인사이트 생성

test_datasets = [
    # 정상 데이터
    [{'id': i, 'value': 100 + i*10} for i in range(10)],
    # 이상치 포함
    [{'id': i, 'value': 100 + i*10} for i in range(10)] + [{'id': 99, 'value': 9999}],
    # NULL 값 포함
    [{'id': i, 'value': 100 + i*10 if i % 2 == 0 else None} for i in range(10)],
    # 중복 데이터
    [{'id': i, 'value': 100} for i in range(5)] * 2,
]

for i, data in enumerate(test_datasets):
    print(f"\n=== Dataset {i+1} ===")
    interpreter = ResultInterpreter()
    interpreter.load_data(data)
    analysis = interpreter.analyze_data()
    print(interpreter.interpret_result())
```

### 과제 2: 자연어 생성기 구현
```python
# 요구사항:
# 1. NaturalLanguageGenerator 완전 구현
# 2. 4가지 쿼리 타입별 설명 생성
# 3. 템플릿 기반 설명 커스터마이징
# 4. 동적 설명 생성

queries_and_data = [
    {
        'query': 'SELECT category, SUM(amount) FROM orders GROUP BY category',
        'data': [
            {'category': 'Electronics', 'total': 5000},
            {'category': 'Books', 'total': 2000},
        ]
    },
    {
        'query': 'SELECT customer_name, total_spending FROM customers ORDER BY total_spending DESC LIMIT 5',
        'data': [
            {'customer_name': 'Alice', 'total_spending': 10000},
            {'customer_name': 'Bob', 'total_spending': 8000},
        ]
    },
    # 추가 사례들
]

nlg = NaturalLanguageGenerator()
for case in queries_and_data:
    narrative = nlg.generate_narrative(case['data'], case['query'])
    print(narrative)
    print()
```

### 과제 3: 데이터 시각화 구현
```python
# 요구사항:
# 1. DataVisualizer 완전 구현
# 2. 5가지 차트 타입 생성 (bar, line, pie, scatter, histogram)
# 3. 자동 차트 타입 선택
# 4. 결과 이미지 저장 및 표시

visualization_cases = [
    {
        'name': 'Sales by Category',
        'data': [
            {'category': 'Electronics', 'sales': 5000},
            {'category': 'Books', 'sales': 2000},
            {'category': 'Clothing', 'sales': 3000},
        ],
        'chart_type': 'bar'
    },
    {
        'name': 'Monthly Trend',
        'data': [
            {'month': 'Jan', 'revenue': 5000},
            {'month': 'Feb', 'revenue': 6000},
            {'month': 'Mar', 'revenue': 5500},
        ],
        'chart_type': 'line'
    },
    # 추가 사례들
]

for case in visualization_cases:
    visualizer = DataVisualizer(case['data'])
    chart_path = visualizer.visualize(chart_type=case['chart_type'])
    print(f"{case['name']}: {chart_path}")
```

### 과제 4: 통합 결과 분석기
```python
# 요구사항:
# 1. ComprehensiResultAnalyzer 완전 구현
# 2. 실제 SQL 쿼리 및 결과 처리
# 3. 요약, 설명, 인사이트, 시각화, 권장사항 모두 생성
# 4. JSON 형식으로 결과 출력

test_queries = [
    {
        'query': 'SELECT * FROM sales WHERE date > "2024-01-01"',
        'result': [
            {'date': '2024-01-05', 'amount': 1000, 'category': 'A'},
            {'date': '2024-01-10', 'amount': 1200, 'category': 'B'},
            # 추가 데이터
        ]
    },
    # 추가 쿼리들
]

for case in test_queries:
    analyzer = ComprehensiResultAnalyzer(case['query'], case['result'])
    full_analysis = analyzer.analyze_and_explain()

    import json
    print(json.dumps({
        'summary': full_analysis['summary'],
        'narrative': full_analysis['narrative'],
        'insights': full_analysis['insights'],
        'recommendations': full_analysis['recommendations']
    }, ensure_ascii=False, indent=2))
```

## 체크포인트

- [ ] ResultInterpreter 완전 구현 및 테스트
- [ ] 4가지 데이터 분석 (통계, 품질, 패턴, 이상치) 구현
- [ ] NaturalLanguageGenerator 구현 완료
- [ ] 4가지 쿼리 타입별 자연어 설명 생성 가능
- [ ] DataVisualizer 5가지 차트 타입 구현
- [ ] 자동 차트 타입 선택 알고리즘 동작
- [ ] ComprehensiResultAnalyzer 통합 구현 완료
- [ ] 10개 이상의 쿼리 결과 완전 분석 완료

## 추가 학습 자료
- Matplotlib Guide: https://matplotlib.org/stable/users/index
- Plotly Interactive: https://plotly.com/python/
- Data Storytelling: https://www.oreilly.com/library/view/storytelling-with-data/9781119002253/
- NLG Techniques: https://github.com/karpukhin/retriever
