"""
Anomaly Detection Module
통계 및 ML 기반 이상 탐지 (Z-score, IQR, Isolation Forest, Local Outlier Factor)

Features:
- Z-score 기반 이상치 탐지
- IQR (Interquartile Range) 기반 탐지
- Isolation Forest 기반 탐지
- Local Outlier Factor (LOF) 기반 탐지
- 시계열 이상 탐지
- 이상치 시각화
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
try:
    from scipy import stats
except ImportError:
    stats = None

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    IsolationForest = None
    LocalOutlierFactor = None
    StandardScaler = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyMethod(Enum):
    """이상 탐지 방법"""
    ZSCORE = "zscore"
    IQR = "iqr"
    ISOLATION_FOREST = "isolation_forest"
    LOF = "local_outlier_factor"
    STATISTICAL = "statistical"


@dataclass
class AnomalyResult:
    """이상 탐지 결과"""
    column: str
    method: str
    total_count: int
    anomaly_count: int
    anomaly_rate: float
    anomaly_indices: List[int]
    anomaly_values: List[float]
    anomaly_scores: List[float]
    threshold: float
    message: str

    def to_dict(self) -> Dict:
        """Dictionary로 변환"""
        return {
            "column": self.column,
            "method": self.method,
            "total_count": self.total_count,
            "anomaly_count": self.anomaly_count,
            "anomaly_rate": self.anomaly_rate,
            "anomaly_indices": self.anomaly_indices[:100],
            "anomaly_values": [float(v) for v in self.anomaly_values[:100]],
            "anomaly_scores": [float(s) for s in self.anomaly_scores[:100]],
            "threshold": self.threshold,
            "message": self.message
        }


class AnomalyDetector:
    """이상 탐지기"""

    def __init__(self, contamination: float = 0.05):
        """
        초기화

        Args:
            contamination: 예상되는 이상치 비율 (0-1)
        """
        self.contamination = contamination
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None

    def zscore_detection(self, series: pd.Series, threshold: float = 3.0) -> AnomalyResult:
        """Z-score 기반 이상 탐지"""
        # 결측치 제외
        valid_data = series.dropna()
        indices = valid_data.index

        # Z-score 계산
        if stats is not None:
            z_scores = np.abs(stats.zscore(valid_data))
        else:
            # Scipy 없을 때 수동 계산
            mean = valid_data.mean()
            std = valid_data.std()
            z_scores = np.abs((valid_data - mean) / (std + 1e-10))

        anomaly_mask = z_scores > threshold

        anomaly_indices = np.where(anomaly_mask)[0].tolist()
        anomaly_values = valid_data[anomaly_mask].values.tolist()
        anomaly_scores = z_scores[anomaly_mask].tolist()

        # 원본 인덱스로 변환
        true_anomaly_indices = [indices[i] for i in anomaly_indices]

        return AnomalyResult(
            column=series.name,
            method=AnomalyMethod.ZSCORE.value,
            total_count=len(series),
            anomaly_count=len(true_anomaly_indices),
            anomaly_rate=len(true_anomaly_indices) / len(series),
            anomaly_indices=true_anomaly_indices,
            anomaly_values=anomaly_values,
            anomaly_scores=anomaly_scores,
            threshold=threshold,
            message=f"Detected {len(true_anomaly_indices)} anomalies using Z-score"
        )

    def iqr_detection(self, series: pd.Series, k: float = 1.5) -> AnomalyResult:
        """IQR (Interquartile Range) 기반 이상 탐지"""
        # 결측치 제외
        valid_data = series.dropna()
        indices = valid_data.index

        # IQR 계산
        Q1 = valid_data.quantile(0.25)
        Q3 = valid_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - k * IQR
        upper_bound = Q3 + k * IQR

        anomaly_mask = (valid_data < lower_bound) | (valid_data > upper_bound)
        anomaly_indices = np.where(anomaly_mask)[0].tolist()
        anomaly_values = valid_data[anomaly_mask].values.tolist()

        # 이상 점수 계산 (0-1)
        distances = np.minimum(
            np.maximum(0, lower_bound - valid_data),
            np.maximum(0, valid_data - upper_bound)
        )
        anomaly_scores = (distances / (IQR + 1e-10))[anomaly_mask].tolist()

        # 원본 인덱스로 변환
        true_anomaly_indices = [indices[i] for i in anomaly_indices]

        return AnomalyResult(
            column=series.name,
            method=AnomalyMethod.IQR.value,
            total_count=len(series),
            anomaly_count=len(true_anomaly_indices),
            anomaly_rate=len(true_anomaly_indices) / len(series),
            anomaly_indices=true_anomaly_indices,
            anomaly_values=anomaly_values,
            anomaly_scores=anomaly_scores,
            threshold=upper_bound,
            message=f"Detected {len(true_anomaly_indices)} anomalies using IQR (bounds: [{lower_bound:.2f}, {upper_bound:.2f}])"
        )

    def isolation_forest_detection(self, df: pd.DataFrame,
                                  numeric_cols: Optional[List[str]] = None) -> Dict[str, AnomalyResult]:
        """Isolation Forest 기반 다변량 이상 탐지"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. Skipping Isolation Forest detection.")
            return {}

        if numeric_cols is None:
            # 숫자형 컬럼 자동 선택
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            logger.warning("No numeric columns found for Isolation Forest")
            return {}

        # 데이터 준비
        data = df[numeric_cols].copy()
        data_filled = data.fillna(data.mean())

        # 모델 학습
        iso_forest = IsolationForest(contamination=self.contamination, random_state=42)
        anomaly_pred = iso_forest.fit_predict(data_filled)
        anomaly_scores = -iso_forest.score_samples(data_filled)

        results = {}
        anomaly_indices = np.where(anomaly_pred == -1)[0].tolist()

        for col in numeric_cols:
            col_anomalies = [idx for idx in anomaly_indices if not pd.isna(df[col].iloc[idx])]
            col_scores = [anomaly_scores[idx] for idx in col_anomalies]
            col_values = [df[col].iloc[idx] for idx in col_anomalies]

            results[col] = AnomalyResult(
                column=col,
                method=AnomalyMethod.ISOLATION_FOREST.value,
                total_count=len(df),
                anomaly_count=len(col_anomalies),
                anomaly_rate=len(col_anomalies) / len(df),
                anomaly_indices=col_anomalies,
                anomaly_values=col_values,
                anomaly_scores=col_scores,
                threshold=0.5,
                message=f"Isolation Forest detected {len(anomaly_indices)} total anomalies"
            )

        return results

    def lof_detection(self, df: pd.DataFrame, n_neighbors: int = 20,
                     numeric_cols: Optional[List[str]] = None) -> Dict[str, AnomalyResult]:
        """LOF (Local Outlier Factor) 기반 다변량 이상 탐지"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. Skipping LOF detection.")
            return {}

        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            logger.warning("No numeric columns found for LOF")
            return {}

        # 데이터 준비
        data = df[numeric_cols].copy()
        data_filled = data.fillna(data.mean())

        # 모델 학습
        lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=self.contamination)
        anomaly_pred = lof.fit_predict(data_filled)
        lof_scores = -lof.negative_outlier_factor_

        results = {}
        anomaly_indices = np.where(anomaly_pred == -1)[0].tolist()

        for col in numeric_cols:
            col_anomalies = [idx for idx in anomaly_indices if not pd.isna(df[col].iloc[idx])]
            col_scores = [lof_scores[idx] for idx in col_anomalies]
            col_values = [df[col].iloc[idx] for idx in col_anomalies]

            results[col] = AnomalyResult(
                column=col,
                method=AnomalyMethod.LOF.value,
                total_count=len(df),
                anomaly_count=len(col_anomalies),
                anomaly_rate=len(col_anomalies) / len(df),
                anomaly_indices=col_anomalies,
                anomaly_values=col_values,
                anomaly_scores=col_scores,
                threshold=1.0,
                message=f"LOF detected {len(anomaly_indices)} total anomalies"
            )

        return results

    def statistical_detection(self, series: pd.Series,
                            alpha: float = 0.05) -> AnomalyResult:
        """통계적 이상 탐지 (Grubbs' test)"""
        valid_data = series.dropna().values
        indices = series.dropna().index

        anomaly_indices = []
        anomaly_values = []
        anomaly_scores = []

        data = valid_data.copy()

        while len(data) > 2:
            # Grubbs 통계량 계산
            mean = np.mean(data)
            std = np.std(data)

            if std == 0:
                break

            z_scores = np.abs((data - mean) / std)
            max_idx = np.argmax(z_scores)
            max_z = z_scores[max_idx]

            # 간단한 임계값 (3-sigma 사용)
            threshold = 3.0

            if max_z > threshold:
                anomaly_values.append(data[max_idx])
                anomaly_scores.append(float(max_z))
                anomaly_indices.append(np.where(series.values == data[max_idx])[0][0] if len(np.where(series.values == data[max_idx])[0]) > 0 else 0)
                data = np.delete(data, max_idx)
            else:
                break

        return AnomalyResult(
            column=series.name,
            method=AnomalyMethod.STATISTICAL.value,
            total_count=len(series),
            anomaly_count=len(anomaly_indices),
            anomaly_rate=len(anomaly_indices) / len(series),
            anomaly_indices=anomaly_indices,
            anomaly_values=anomaly_values,
            anomaly_scores=anomaly_scores,
            threshold=alpha,
            message=f"Statistical test detected {len(anomaly_indices)} anomalies"
        )

    def detect_ensemble(self, df: pd.DataFrame,
                       numeric_cols: Optional[List[str]] = None) -> Dict[str, AnomalyResult]:
        """앙상블 이상 탐지 (모든 방법 결합)"""
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        ensemble_results = {}

        # 각 컬럼에 대해 다양한 방법 적용
        for col in numeric_cols:
            if df[col].dropna().shape[0] < 3:
                continue

            anomaly_count = {}
            all_anomaly_indices = []

            # Z-score
            try:
                result = self.zscore_detection(df[col], threshold=3.0)
                anomaly_count['zscore'] = result.anomaly_count
                all_anomaly_indices.extend(result.anomaly_indices)
            except:
                pass

            # IQR
            try:
                result = self.iqr_detection(df[col], k=1.5)
                anomaly_count['iqr'] = result.anomaly_count
                all_anomaly_indices.extend(result.anomaly_indices)
            except:
                pass

            # 다중 방법에서 감지된 이상치
            from collections import Counter
            anomaly_freq = Counter(all_anomaly_indices)
            consensus_anomalies = [idx for idx, freq in anomaly_freq.items() if freq >= 2]

            if consensus_anomalies:
                anomaly_values = [df[col].iloc[idx] for idx in consensus_anomalies]
                ensemble_results[col] = AnomalyResult(
                    column=col,
                    method="ensemble",
                    total_count=len(df),
                    anomaly_count=len(consensus_anomalies),
                    anomaly_rate=len(consensus_anomalies) / len(df),
                    anomaly_indices=consensus_anomalies,
                    anomaly_values=anomaly_values,
                    anomaly_scores=[1.0] * len(consensus_anomalies),
                    threshold=0.5,
                    message=f"Ensemble detected {len(consensus_anomalies)} anomalies (consensus: 2+ methods)"
                )

        return ensemble_results

    def generate_report(self, results: Dict[str, AnomalyResult]) -> str:
        """이상 탐지 리포트 생성"""
        report = f"""
=== Anomaly Detection Report ===
Generated: {datetime.now().isoformat()}

"""

        total_anomalies = 0
        for col, result in results.items():
            report += f"\n{col}:"
            report += f"\n  Method: {result.method}"
            report += f"\n  Anomalies: {result.anomaly_count}/{result.total_count} ({result.anomaly_rate:.2%})"
            report += f"\n  Threshold: {result.threshold}"
            report += f"\n  {result.message}\n"
            total_anomalies += result.anomaly_count

        report += f"\nTotal Anomalies Found: {total_anomalies}"
        return report


def main():
    """테스트"""
    # 샘플 데이터 생성 (정상 + 이상치)
    np.random.seed(42)
    normal_data = np.random.normal(50, 10, 95)
    anomaly_data = np.array([100, 120, -50, 110, 105])
    data = np.concatenate([normal_data, anomaly_data])
    np.random.shuffle(data)

    df = pd.DataFrame({
        'value': data,
        'age': np.concatenate([np.random.normal(35, 10, 95), [100, 2, 120, -10, 150]]),
        'salary': np.concatenate([np.random.normal(50000, 15000, 95), [500000, 10000, 600000, -100000, 1000000]])
    })

    # 이상 탐지
    detector = AnomalyDetector(contamination=0.05)

    # 단일 컬럼 이상 탐지
    print("=== Z-score Detection ===")
    result = detector.zscore_detection(df['value'], threshold=2.5)
    print(f"Anomalies: {result.anomaly_count}")
    print(f"Indices: {result.anomaly_indices[:10]}")

    print("\n=== IQR Detection ===")
    result = detector.iqr_detection(df['value'], k=1.5)
    print(f"Anomalies: {result.anomaly_count}")

    print("\n=== Isolation Forest ===")
    results = detector.isolation_forest_detection(df)
    for col, result in results.items():
        print(f"{col}: {result.anomaly_count} anomalies")

    print("\n=== LOF Detection ===")
    results = detector.lof_detection(df, n_neighbors=5)
    for col, result in results.items():
        print(f"{col}: {result.anomaly_count} anomalies")

    print("\n=== Ensemble Detection ===")
    results = detector.detect_ensemble(df)
    print(detector.generate_report(results))


if __name__ == "__main__":
    main()
