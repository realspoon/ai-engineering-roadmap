"""
Insight Extractor Module
데이터에서 자동으로 인사이트 추출 및 분석
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from collections import Counter
import json


class InsightType:
    """인사이트 타입 정의"""
    TREND = "trend"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    DISTRIBUTION = "distribution"
    OUTLIER = "outlier"
    COMPOSITION = "composition"
    COMPARISON = "comparison"
    PATTERN = "pattern"


class InsightGenerator:
    """인사이트 자동 생성"""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        self.insights = []

    def generate_all_insights(self) -> List[Dict[str, Any]]:
        """모든 인사이트 생성"""
        self.insights = []

        # 각 종류의 인사이트 생성
        self._generate_distribution_insights()
        self._generate_outlier_insights()
        self._generate_correlation_insights()
        self._generate_composition_insights()
        self._generate_comparison_insights()
        self._generate_pattern_insights()

        # 인사이트를 신뢰도 순으로 정렬
        self.insights.sort(key=lambda x: x['confidence'], reverse=True)

        return self.insights

    def _generate_distribution_insights(self) -> None:
        """분포 인사이트 생성"""
        for col in self.numeric_cols:
            data = self.df[col].dropna()

            if len(data) < 3:
                continue

            # 왜도(Skewness) 분석
            skewness = data.skew()
            if abs(skewness) > 1:
                direction = "우측" if skewness > 0 else "좌측"
                insight = {
                    'type': InsightType.DISTRIBUTION,
                    'title': f'{col}: {direction} 왜곡 분포',
                    'description': f'{col}의 분포가 {direction}으로 왜곡되어 있습니다. 왜도값: {skewness:.2f}',
                    'metric': col,
                    'value': float(skewness),
                    'severity': 'medium' if abs(skewness) > 2 else 'low',
                    'confidence': min(0.95, abs(skewness) / 3)
                }
                self.insights.append(insight)

            # 첨도(Kurtosis) 분석
            kurtosis = data.kurtosis()
            if abs(kurtosis) > 3:
                tail_type = "두터운 꼬리" if kurtosis > 0 else "가는 꼬리"
                insight = {
                    'type': InsightType.DISTRIBUTION,
                    'title': f'{col}: {tail_type} 분포',
                    'description': f'{col}의 분포가 {tail_type}를 가지고 있습니다. 첨도값: {kurtosis:.2f}',
                    'metric': col,
                    'value': float(kurtosis),
                    'severity': 'medium',
                    'confidence': 0.8
                }
                self.insights.append(insight)

    def _generate_outlier_insights(self) -> None:
        """이상치 인사이트 생성"""
        for col in self.numeric_cols:
            data = self.df[col].dropna()

            if len(data) < 4:
                continue

            # IQR 방식 이상치 탐지
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = data[(data < lower_bound) | (data > upper_bound)]

            if len(outliers) > 0:
                outlier_percentage = (len(outliers) / len(data)) * 100

                insight = {
                    'type': InsightType.OUTLIER,
                    'title': f'{col}: 이상치 {len(outliers)}개 발견',
                    'description': f'{col}에서 {outlier_percentage:.1f}%의 이상치를 발견했습니다. '
                                  f'범위: [{lower_bound:.2f}, {upper_bound:.2f}]',
                    'metric': col,
                    'outlier_count': len(outliers),
                    'outlier_percentage': outlier_percentage,
                    'outlier_values': outliers.nlargest(5).tolist(),
                    'severity': 'high' if outlier_percentage > 5 else 'medium',
                    'confidence': 0.9
                }
                self.insights.append(insight)

    def _generate_correlation_insights(self) -> None:
        """상관관계 인사이트 생성"""
        if len(self.numeric_cols) < 2:
            return

        corr_matrix = self.df[self.numeric_cols].corr()

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]

                if abs(corr_value) > 0.7:
                    col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                    relationship = "양의" if corr_value > 0 else "음의"

                    insight = {
                        'type': InsightType.CORRELATION,
                        'title': f'{col1}와 {col2}: 강한 {relationship} 상관관계',
                        'description': f'{col1}과 {col2} 사이에 강한 {relationship} 상관관계가 있습니다. '
                                      f'상관계수: {corr_value:.3f}',
                        'variable1': col1,
                        'variable2': col2,
                        'correlation': float(corr_value),
                        'severity': 'low',
                        'confidence': min(0.99, (abs(corr_value) - 0.7) / 0.3 * 0.2 + 0.8)
                    }
                    self.insights.append(insight)

    def _generate_composition_insights(self) -> None:
        """구성 인사이트 생성"""
        for col in self.categorical_cols:
            value_counts = self.df[col].value_counts()

            if len(value_counts) == 0:
                continue

            # 가장 많은 카테고리
            top_value = value_counts.index[0]
            top_percentage = (value_counts.iloc[0] / len(self.df)) * 100

            if top_percentage > 50:
                insight = {
                    'type': InsightType.COMPOSITION,
                    'title': f'{col}: 한 카테고리 편중',
                    'description': f'{col}에서 "{top_value}"가 {top_percentage:.1f}%를 차지합니다. 클래스 불균형이 있습니다.',
                    'metric': col,
                    'dominant_category': top_value,
                    'dominant_percentage': float(top_percentage),
                    'severity': 'medium',
                    'confidence': 0.85
                }
                self.insights.append(insight)

            # 카테고리 다양성
            n_categories = len(value_counts)
            if n_categories > 20:
                insight = {
                    'type': InsightType.COMPOSITION,
                    'title': f'{col}: 높은 카테고리 다양성',
                    'description': f'{col}에는 {n_categories}개의 서로 다른 값이 있습니다.',
                    'metric': col,
                    'category_count': n_categories,
                    'severity': 'low',
                    'confidence': 0.8
                }
                self.insights.append(insight)

    def _generate_comparison_insights(self) -> None:
        """비교 인사이트 생성"""
        if not self.numeric_cols or not self.categorical_cols:
            return

        # 첫 번째 범주형 컬럼으로 그룹화
        group_col = self.categorical_cols[0]
        numeric_col = self.numeric_cols[0]

        groups = self.df.groupby(group_col)[numeric_col].agg(['mean', 'std', 'count'])

        if len(groups) > 1:
            # 최대값과 최소값 비교
            max_group = groups['mean'].idxmax()
            min_group = groups['mean'].idxmin()
            max_val = groups.loc[max_group, 'mean']
            min_val = groups.loc[min_group, 'mean']
            difference = max_val - min_val

            if difference > 0:
                percentage_diff = (difference / min_val) * 100

                insight = {
                    'type': InsightType.COMPARISON,
                    'title': f'{group_col}별 {numeric_col} 차이',
                    'description': f'{group_col}에 따라 {numeric_col}에 큰 차이가 있습니다. '
                                  f'{max_group}은 {min_group}보다 {percentage_diff:.1f}% 높습니다.',
                    'groupby': group_col,
                    'metric': numeric_col,
                    'max_group': max_group,
                    'max_value': float(max_val),
                    'min_group': min_group,
                    'min_value': float(min_val),
                    'difference_percentage': float(percentage_diff),
                    'severity': 'low',
                    'confidence': 0.8
                }
                self.insights.append(insight)

    def _generate_pattern_insights(self) -> None:
        """패턴 인사이트 생성"""
        # 결측치 패턴
        missing_data = self.df.isnull().sum()
        total_missing = missing_data.sum()

        if total_missing > 0:
            missing_percentage = (total_missing / (len(self.df) * len(self.df.columns))) * 100

            cols_with_missing = missing_data[missing_data > 0]
            if len(cols_with_missing) > 0:
                insight = {
                    'type': InsightType.PATTERN,
                    'title': '결측데이터 감지',
                    'description': f'전체 데이터의 {missing_percentage:.2f}%가 결측입니다. '
                                  f'{len(cols_with_missing)}개 컬럼에 결측이 있습니다.',
                    'total_missing_cells': int(total_missing),
                    'missing_columns': cols_with_missing.to_dict(),
                    'severity': 'medium' if missing_percentage > 5 else 'low',
                    'confidence': 0.95
                }
                self.insights.append(insight)

        # 중복행 패턴
        duplicate_count = self.df.duplicated().sum()
        if duplicate_count > 0:
            dup_percentage = (duplicate_count / len(self.df)) * 100

            insight = {
                'type': InsightType.PATTERN,
                'title': '중복행 감지',
                'description': f'데이터에 {duplicate_count}개의 중복행이 있습니다 ({dup_percentage:.2f}%).',
                'duplicate_rows': int(duplicate_count),
                'duplicate_percentage': float(dup_percentage),
                'severity': 'medium' if dup_percentage > 1 else 'low',
                'confidence': 0.95
            }
            self.insights.append(insight)

    def get_insights_by_type(self, insight_type: str) -> List[Dict[str, Any]]:
        """특정 타입의 인사이트만 반환"""
        return [i for i in self.insights if i['type'] == insight_type]

    def get_high_confidence_insights(self, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """높은 신뢰도의 인사이트만 반환"""
        return [i for i in self.insights if i['confidence'] >= threshold]

    def get_critical_insights(self) -> List[Dict[str, Any]]:
        """심각도 높은 인사이트만 반환"""
        return [i for i in self.insights if i.get('severity') == 'high']


class InsightNarrativeGenerator:
    """인사이트 자연어 서술 생성"""

    def __init__(self, insights: List[Dict[str, Any]]):
        self.insights = insights

    def generate_summary(self) -> str:
        """인사이트 요약 생성"""
        if not self.insights:
            return "발견된 인사이트가 없습니다."

        lines = []
        lines.append(f"총 {len(self.insights)}개의 인사이트를 발견했습니다.\n")

        # 타입별 정리
        by_type = {}
        for insight in self.insights:
            itype = insight['type']
            by_type[itype] = by_type.get(itype, 0) + 1

        lines.append("인사이트 분류:")
        for itype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  - {itype}: {count}개")

        return '\n'.join(lines)

    def generate_detailed_report(self) -> str:
        """상세 인사이트 리포트 생성"""
        lines = []
        lines.append("=" * 50)
        lines.append("데이터 인사이트 상세 리포트")
        lines.append("=" * 50)
        lines.append("")

        # 신뢰도 기준 정렬
        sorted_insights = sorted(self.insights, key=lambda x: x['confidence'], reverse=True)

        for i, insight in enumerate(sorted_insights[:10], 1):  # 상위 10개만
            lines.append(f"[{i}] {insight['title']}")
            lines.append(f"    타입: {insight['type']}")
            lines.append(f"    설명: {insight['description']}")
            lines.append(f"    신뢰도: {insight['confidence']:.1%}")
            lines.append(f"    심각도: {insight.get('severity', 'N/A')}")
            lines.append("")

        return '\n'.join(lines)

    def generate_executive_summary(self) -> str:
        """경영진 요약 생성"""
        lines = []
        lines.append("데이터 분석 Executive Summary")
        lines.append("-" * 40)

        # 가장 중요한 인사이트들
        high_confidence = self.get_critical_insights()

        if high_confidence:
            lines.append("\n주요 발견사항:")
            for insight in high_confidence[:3]:
                lines.append(f"• {insight['title']}")
                lines.append(f"  {insight['description']}")

        return '\n'.join(lines)

    def get_critical_insights(self) -> List[Dict[str, Any]]:
        """중요 인사이트 추출"""
        critical = [i for i in self.insights if i.get('severity') in ['high', 'critical']]
        return sorted(critical, key=lambda x: x['confidence'], reverse=True)


class InsightManager:
    """인사이트 관리 클래스"""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.generator = InsightGenerator(df)
        self.insights = []

    def analyze(self) -> Dict[str, Any]:
        """전체 분석 실행"""
        self.insights = self.generator.generate_all_insights()

        narrative_gen = InsightNarrativeGenerator(self.insights)

        return {
            'total_insights': len(self.insights),
            'insights': self.insights,
            'summary': narrative_gen.generate_summary(),
            'critical_insights': narrative_gen.get_critical_insights(),
            'detailed_report': narrative_gen.generate_detailed_report()
        }

    def get_insights_for_action(self) -> List[Dict[str, Any]]:
        """실행 가능한 인사이트 반환"""
        actionable = [
            i for i in self.insights
            if i['confidence'] > 0.8 and i.get('severity') in ['high', 'medium']
        ]
        return sorted(actionable, key=lambda x: x['confidence'], reverse=True)


# 사용 예제
if __name__ == "__main__":
    import numpy as np

    # 샘플 데이터셋
    np.random.seed(42)
    sample_df = pd.DataFrame({
        'age': np.concatenate([
            np.random.normal(35, 10, 90),
            [100, 120, 150, 180, 200, 5, 2]  # 이상치
        ]),
        'salary': np.random.normal(50000, 15000, 97),
        'experience': np.random.normal(10, 5, 97),
        'department': np.random.choice(['Sales', 'IT', 'HR'], 97),
        'performance': np.random.choice(['A', 'B', 'C', 'A', 'A'], 97)  # 불균형
    })

    # 일부 결측치 추가
    sample_df.loc[np.random.choice(sample_df.index, 5), 'age'] = np.nan

    # 인사이트 분석
    print("=== 데이터 인사이트 분석 ===\n")
    manager = InsightManager(sample_df)
    result = manager.analyze()

    print(result['summary'])
    print("\n" + result['detailed_report'])

    print("\n" + "=" * 50)
    print("실행 가능한 인사이트:")
    for insight in manager.get_insights_for_action()[:5]:
        print(f"• {insight['title']}")
