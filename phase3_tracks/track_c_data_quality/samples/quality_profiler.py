"""
Data Quality Profiler Module
데이터 프로파일링 및 품질 점수 계산

Features:
- 데이터 분포 분석
- 결측치 분석
- 이상치 기본 통계
- 품질 점수 계산
- 프로필 리포트 생성
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataType(Enum):
    """데이터 타입 정의"""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    TEXT = "text"


@dataclass
class ColumnProfile:
    """컬럼 프로필 정보"""
    column_name: str
    data_type: str
    total_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_value: Optional[float] = None
    mode_value: Optional[Any] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None

    def to_dict(self) -> Dict:
        """Dictionary로 변환"""
        return asdict(self)


@dataclass
class DataQualityScore:
    """데이터 품질 점수"""
    overall_score: float
    completeness_score: float
    consistency_score: float
    validity_score: float
    uniqueness_score: float
    profiles: Dict[str, ColumnProfile]
    timestamp: str

    def to_dict(self) -> Dict:
        """Dictionary로 변환"""
        return {
            "overall_score": self.overall_score,
            "completeness_score": self.completeness_score,
            "consistency_score": self.consistency_score,
            "validity_score": self.validity_score,
            "uniqueness_score": self.uniqueness_score,
            "profiles": {k: v.to_dict() for k, v in self.profiles.items()},
            "timestamp": self.timestamp
        }


class QualityProfiler:
    """데이터 품질 프로파일러"""

    def __init__(self, null_threshold: float = 0.5,
                 duplicate_threshold: float = 0.3):
        """
        초기화

        Args:
            null_threshold: 결측치 임계값 (0-1)
            duplicate_threshold: 중복 임계값 (0-1)
        """
        self.null_threshold = null_threshold
        self.duplicate_threshold = duplicate_threshold
        self.profiles: Dict[str, ColumnProfile] = {}

    def detect_data_type(self, series: pd.Series) -> DataType:
        """데이터 타입 자동 감지"""
        # 결측치 제거
        valid_data = series.dropna()

        if len(valid_data) == 0:
            return DataType.TEXT

        # 숫자형 검사
        try:
            pd.to_numeric(valid_data)
            return DataType.NUMERIC
        except (ValueError, TypeError):
            pass

        # 날짜 검사
        try:
            pd.to_datetime(valid_data)
            return DataType.DATETIME
        except (ValueError, TypeError):
            pass

        # 범주형 검사 (고유값이 전체의 10% 미만)
        if valid_data.nunique() / len(valid_data) < 0.1:
            return DataType.CATEGORICAL

        return DataType.TEXT

    def profile_numeric_column(self, series: pd.Series) -> Dict[str, Any]:
        """숫자형 컬럼 프로파일링"""
        valid_data = pd.to_numeric(series.dropna())

        from scipy import stats

        return {
            "min_value": float(valid_data.min()),
            "max_value": float(valid_data.max()),
            "mean_value": float(valid_data.mean()),
            "median_value": float(valid_data.median()),
            "std_value": float(valid_data.std()),
            "skewness": float(stats.skew(valid_data)),
            "kurtosis": float(stats.kurtosis(valid_data))
        }

    def profile_categorical_column(self, series: pd.Series) -> Dict[str, Any]:
        """범주형 컬럼 프로파일링"""
        value_counts = series.dropna().value_counts()

        return {
            "mode_value": str(value_counts.index[0]) if len(value_counts) > 0 else None,
            "top_values": value_counts.head(5).to_dict()
        }

    def calculate_completeness(self, df: pd.DataFrame) -> float:
        """완전성 점수 계산 (0-1)"""
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        completeness = 1 - (null_cells / total_cells)
        return max(0, min(1, completeness))

    def calculate_uniqueness(self, df: pd.DataFrame) -> float:
        """고유성 점수 계산 (0-1)"""
        duplicate_rows = df.duplicated().sum()
        uniqueness = 1 - (duplicate_rows / len(df)) if len(df) > 0 else 1
        return max(0, min(1, uniqueness))

    def calculate_consistency(self, df: pd.DataFrame) -> float:
        """일관성 점수 계산 (0-1)"""
        consistency_scores = []

        for col in df.columns:
            null_ratio = df[col].isnull().sum() / len(df)
            consistency_scores.append(1 - null_ratio)

        return np.mean(consistency_scores) if consistency_scores else 1.0

    def calculate_validity(self, df: pd.DataFrame) -> float:
        """유효성 점수 계산 (0-1)"""
        validity_scores = []

        for col in df.columns:
            try:
                # 숫자 컬럼의 경우 범위 검사
                if pd.api.types.is_numeric_dtype(df[col]):
                    valid_range = (df[col].min() >= -1e10) and (df[col].max() <= 1e10)
                    validity_scores.append(1.0 if valid_range else 0.5)
                else:
                    validity_scores.append(1.0)
            except:
                validity_scores.append(0.5)

        return np.mean(validity_scores) if validity_scores else 1.0

    def profile_dataframe(self, df: pd.DataFrame) -> Dict[str, ColumnProfile]:
        """DataFrame 전체 프로파일링"""
        profiles = {}

        for col in df.columns:
            data_type = self.detect_data_type(df[col])
            null_count = df[col].isnull().sum()
            unique_count = df[col].nunique()

            profile = ColumnProfile(
                column_name=col,
                data_type=data_type.value,
                total_count=len(df),
                null_count=int(null_count),
                null_percentage=float(null_count / len(df) * 100),
                unique_count=int(unique_count),
                unique_percentage=float(unique_count / len(df) * 100)
            )

            # 데이터 타입별 추가 분석
            if data_type == DataType.NUMERIC:
                numeric_stats = self.profile_numeric_column(df[col])
                profile.min_value = numeric_stats["min_value"]
                profile.max_value = numeric_stats["max_value"]
                profile.mean_value = numeric_stats["mean_value"]
                profile.median_value = numeric_stats["median_value"]
                profile.std_value = numeric_stats["std_value"]
                profile.skewness = numeric_stats["skewness"]
                profile.kurtosis = numeric_stats["kurtosis"]

            elif data_type == DataType.CATEGORICAL:
                cat_stats = self.profile_categorical_column(df[col])
                profile.mode_value = cat_stats["mode_value"]

            profiles[col] = profile

        return profiles

    def calculate_quality_score(self, df: pd.DataFrame) -> DataQualityScore:
        """전체 품질 점수 계산"""
        # 프로파일링 수행
        profiles = self.profile_dataframe(df)

        # 개별 점수 계산
        completeness = self.calculate_completeness(df)
        consistency = self.calculate_consistency(df)
        validity = self.calculate_validity(df)
        uniqueness = self.calculate_uniqueness(df)

        # 전체 점수 (가중 평균)
        overall_score = (
            completeness * 0.3 +
            consistency * 0.25 +
            validity * 0.25 +
            uniqueness * 0.2
        )

        score = DataQualityScore(
            overall_score=round(overall_score, 4),
            completeness_score=round(completeness, 4),
            consistency_score=round(consistency, 4),
            validity_score=round(validity, 4),
            uniqueness_score=round(uniqueness, 4),
            profiles=profiles,
            timestamp=datetime.now().isoformat()
        )

        logger.info(f"Quality Score Calculated: {overall_score:.2%}")
        return score

    def generate_report(self, df: pd.DataFrame) -> str:
        """품질 리포트 생성"""
        score = self.calculate_quality_score(df)

        report = f"""
=== Data Quality Report ===
Generated: {score.timestamp}

Overall Quality Score: {score.overall_score:.2%}

Dimension Scores:
- Completeness: {score.completeness_score:.2%}
- Consistency: {score.consistency_score:.2%}
- Validity: {score.validity_score:.2%}
- Uniqueness: {score.uniqueness_score:.2%}

Column Profiles:
"""

        for col, profile in score.profiles.items():
            report += f"\n{col}:"
            report += f"\n  Type: {profile.data_type}"
            report += f"\n  Null Rate: {profile.null_percentage:.2f}%"
            report += f"\n  Unique: {profile.unique_count} ({profile.unique_percentage:.2f}%)"

            if profile.data_type == "numeric":
                report += f"\n  Range: [{profile.min_value:.2f}, {profile.max_value:.2f}]"
                report += f"\n  Mean: {profile.mean_value:.2f}, Std: {profile.std_value:.2f}"

        return report

    def export_profile(self, df: pd.DataFrame, filepath: str) -> None:
        """프로필을 JSON으로 내보내기"""
        score = self.calculate_quality_score(df)

        with open(filepath, 'w') as f:
            json.dump(score.to_dict(), f, indent=2)

        logger.info(f"Profile exported to {filepath}")


def main():
    """테스트"""
    # 샘플 데이터 생성
    np.random.seed(42)
    df = pd.DataFrame({
        'id': range(1, 101),
        'age': np.random.normal(35, 10, 100).astype(int),
        'salary': np.random.normal(50000, 15000, 100).astype(int),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'email': [f'user{i}@example.com' if np.random.random() > 0.1 else None for i in range(100)]
    })

    # 품질 점수 계산
    profiler = QualityProfiler()
    score = profiler.calculate_quality_score(df)

    # 리포트 출력
    print(profiler.generate_report(df))

    # 점수를 JSON으로 출력
    print("\nQuality Score JSON:")
    print(json.dumps(score.to_dict(), indent=2, default=str))


if __name__ == "__main__":
    main()
