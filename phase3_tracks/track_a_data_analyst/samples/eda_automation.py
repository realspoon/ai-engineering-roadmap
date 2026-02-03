"""
EDA Automation Module
자동 탐색적 데이터 분석, 통계 분석, 데이터 프로파일링
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
import warnings
from scipy import stats
from sklearn.preprocessing import StandardScaler
import json

warnings.filterwarnings('ignore')


class StatisticalAnalyzer:
    """통계 분석 클래스"""

    @staticmethod
    def calculate_descriptive_stats(data: pd.Series) -> Dict[str, float]:
        """기술통계 계산"""
        return {
            'count': len(data),
            'mean': float(data.mean()),
            'std': float(data.std()),
            'min': float(data.min()),
            '25%': float(data.quantile(0.25)),
            '50%': float(data.quantile(0.50)),
            '75%': float(data.quantile(0.75)),
            'max': float(data.max()),
            'variance': float(data.var()),
            'skewness': float(data.skew()),
            'kurtosis': float(data.kurtosis())
        }

    @staticmethod
    def detect_outliers(data: pd.Series, method: str = 'iqr') -> Dict[str, Any]:
        """이상치 탐지"""
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = data[(data < lower_bound) | (data > upper_bound)]

        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(data.dropna()))
            outliers = data[z_scores > 3]

        else:
            raise ValueError(f"지원하지 않는 방법: {method}")

        return {
            'method': method,
            'outlier_count': len(outliers),
            'outlier_percentage': (len(outliers) / len(data)) * 100,
            'outlier_indices': outliers.index.tolist(),
            'outlier_values': outliers.tolist()
        }

    @staticmethod
    def test_normality(data: pd.Series) -> Dict[str, Any]:
        """정규성 검정 (Shapiro-Wilk)"""
        data_clean = data.dropna()

        if len(data_clean) < 3:
            return {'error': '정규성 검정을 위해 최소 3개 이상의 데이터 필요'}

        stat, p_value = stats.shapiro(data_clean)

        return {
            'test': 'Shapiro-Wilk',
            'statistic': float(stat),
            'p_value': float(p_value),
            'is_normal': p_value > 0.05,
            'interpretation': '정규분포를 따릅니다' if p_value > 0.05 else '정규분포를 따르지 않습니다'
        }

    @staticmethod
    def calculate_correlation(df: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
        """상관계수 계산"""
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.corr(method=method)


class DataProfiler:
    """데이터 프로파일링 클래스"""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.profile = {}

    def generate_profile(self) -> Dict[str, Any]:
        """전체 데이터 프로파일 생성"""
        profile = {
            'dataset_info': self._get_dataset_info(),
            'column_profiles': self._profile_columns(),
            'missing_data': self._analyze_missing_data(),
            'duplicates': self._analyze_duplicates(),
            'memory_usage': self._get_memory_usage()
        }

        self.profile = profile
        return profile

    def _get_dataset_info(self) -> Dict[str, Any]:
        """데이터셋 기본 정보"""
        return {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'column_names': self.df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        }

    def _profile_columns(self) -> Dict[str, Any]:
        """각 컬럼별 프로파일"""
        profiles = {}

        for col in self.df.columns:
            col_data = self.df[col]
            dtype = col_data.dtype

            profile_info = {
                'dtype': str(dtype),
                'non_null_count': int(col_data.notna().sum()),
                'null_count': int(col_data.isna().sum()),
                'unique_values': int(col_data.nunique()),
                'missing_percentage': float((col_data.isna().sum() / len(col_data)) * 100)
            }

            # 수치형 데이터
            if dtype in ['int64', 'float64']:
                stats = StatisticalAnalyzer.calculate_descriptive_stats(col_data)
                profile_info['statistics'] = stats

                # 이상치 탐지
                outliers = StatisticalAnalyzer.detect_outliers(col_data)
                profile_info['outliers'] = outliers

            # 범주형 데이터
            elif dtype == 'object':
                value_counts = col_data.value_counts()
                profile_info['top_values'] = value_counts.head(10).to_dict()
                profile_info['cardinality'] = len(value_counts)

            profiles[col] = profile_info

        return profiles

    def _analyze_missing_data(self) -> Dict[str, Any]:
        """결측치 분석"""
        missing_data = self.df.isnull().sum()
        missing_percent = (missing_data / len(self.df)) * 100

        missing_info = {
            'total_missing_cells': int(missing_data.sum()),
            'total_cells': int(self.df.shape[0] * self.df.shape[1]),
            'missing_percentage': float((missing_data.sum() / (self.df.shape[0] * self.df.shape[1])) * 100),
            'by_column': {}
        }

        for col in missing_data[missing_data > 0].index:
            missing_info['by_column'][col] = {
                'missing_count': int(missing_data[col]),
                'missing_percentage': float(missing_percent[col])
            }

        return missing_info

    def _analyze_duplicates(self) -> Dict[str, Any]:
        """중복 행 분석"""
        total_duplicates = self.df.duplicated().sum()

        return {
            'total_duplicate_rows': int(total_duplicates),
            'duplicate_percentage': float((total_duplicates / len(self.df)) * 100),
            'duplicate_count_by_column': {}
        }

    def _get_memory_usage(self) -> Dict[str, float]:
        """메모리 사용량"""
        memory_usage = self.df.memory_usage(deep=True)

        return {
            'total_memory_mb': float(memory_usage.sum() / 1024**2),
            'by_column': {col: float(mem / 1024**2) for col, mem in memory_usage.items()}
        }


class EDAAutomation:
    """자동 EDA 클래스"""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.profiler = DataProfiler(df)
        self.analyzer = StatisticalAnalyzer()

    def run_complete_eda(self) -> Dict[str, Any]:
        """전체 EDA 실행"""
        eda_report = {
            'data_profile': self.profiler.generate_profile(),
            'statistical_analysis': self._run_statistical_analysis(),
            'correlation_analysis': self._run_correlation_analysis(),
            'distribution_analysis': self._run_distribution_analysis(),
            'recommendations': self._generate_recommendations()
        }

        return eda_report

    def _run_statistical_analysis(self) -> Dict[str, Any]:
        """통계 분석 실행"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        stats_result = {}
        for col in numeric_cols:
            stats_result[col] = {
                'descriptive_stats': self.analyzer.calculate_descriptive_stats(self.df[col]),
                'normality_test': self.analyzer.test_normality(self.df[col]),
                'outlier_analysis': self.analyzer.detect_outliers(self.df[col])
            }

        return stats_result

    def _run_correlation_analysis(self) -> Dict[str, Any]:
        """상관계수 분석"""
        numeric_df = self.df.select_dtypes(include=[np.number])

        if len(numeric_df.columns) < 2:
            return {'message': '상관계수 분석을 위해 최소 2개 이상의 수치형 컬럼 필요'}

        correlation_matrix = self.analyzer.calculate_correlation(self.df)

        # 높은 상관계수 쌍 찾기
        high_corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i + 1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    high_corr_pairs.append({
                        'var1': correlation_matrix.columns[i],
                        'var2': correlation_matrix.columns[j],
                        'correlation': float(corr_value)
                    })

        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'high_correlation_pairs': high_corr_pairs
        }

    def _run_distribution_analysis(self) -> Dict[str, Any]:
        """분포 분석"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        distribution_info = {}
        for col in numeric_cols:
            data = self.df[col].dropna()

            distribution_info[col] = {
                'min': float(data.min()),
                'max': float(data.max()),
                'range': float(data.max() - data.min()),
                'mean': float(data.mean()),
                'median': float(data.median()),
                'mode': float(data.mode()[0]) if not data.mode().empty else None,
                'skewness': float(data.skew()),
                'kurtosis': float(data.kurtosis())
            }

        return distribution_info

    def _generate_recommendations(self) -> List[str]:
        """EDA 기반 추천사항 생성"""
        recommendations = []

        # 결측치 분석
        missing_percent = (self.df.isnull().sum() / len(self.df) * 100)
        if missing_percent.max() > 50:
            high_missing = missing_percent[missing_percent > 50].index.tolist()
            recommendations.append(f"높은 결측치를 가진 컬럼 제거 검토: {', '.join(high_missing)}")

        # 중복 행
        if self.df.duplicated().sum() > 0:
            recommendations.append(f"중복 행 {self.df.duplicated().sum()}개 발견 - 제거 검토")

        # 이상치
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            outlier_info = self.analyzer.detect_outliers(self.df[col])
            if outlier_info['outlier_percentage'] > 5:
                recommendations.append(f"{col}: 이상치 {outlier_info['outlier_percentage']:.1f}% 발견")

        # 데이터 불균형
        for col in self.df.select_dtypes(include=['object']).columns:
            if self.df[col].nunique() < 50:
                value_dist = self.df[col].value_counts()
                if len(value_dist) > 1:
                    max_freq = value_dist.iloc[0] / len(self.df)
                    if max_freq > 0.9:
                        recommendations.append(f"{col}: 심한 클래스 불균형 발견 ({max_freq*100:.1f}%)")

        if not recommendations:
            recommendations.append("데이터 품질이 양호합니다")

        return recommendations


# 사용 예제
if __name__ == "__main__":
    # 샘플 데이터셋 생성
    np.random.seed(42)
    sample_df = pd.DataFrame({
        'age': np.random.normal(35, 15, 100),
        'income': np.random.normal(50000, 20000, 100),
        'years_experience': np.random.normal(10, 5, 100),
        'department': np.random.choice(['Sales', 'Marketing', 'IT', 'HR'], 100),
        'satisfaction': np.random.randint(1, 6, 100)
    })

    # 일부 결측치 추가
    sample_df.loc[np.random.choice(sample_df.index, 5), 'age'] = np.nan

    # EDA 실행
    print("=== 자동 EDA 분석 ===\n")
    eda = EDAAutomation(sample_df)
    report = eda.run_complete_eda()

    # 결과 출력
    print("1. 데이터셋 정보:")
    print(json.dumps(report['data_profile']['dataset_info'], indent=2, ensure_ascii=False))

    print("\n2. 결측치 분석:")
    print(json.dumps(report['data_profile']['missing_data'], indent=2, ensure_ascii=False))

    print("\n3. 추천사항:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
