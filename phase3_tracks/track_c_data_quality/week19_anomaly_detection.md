# Week 19: 이상 탐지 (Anomaly Detection)

## 학습 목표
- 통계 기반 이상 탐지 이해
- 머신러닝 기반 이상 탐지 적용
- 시계열 데이터 이상 탐지

## 1. 이상 탐지의 필요성

### 1.1 정의
정상 범위를 벗어난 데이터 포인트를 자동으로 감지

### 1.2 데이터 품질 관점에서의 용도
- 오류 데이터 자동 감지
- 데이터 입력 오류 추적
- 시스템 장애 조기 발견

## 2. 통계 기반 이상 탐지

### 2.1 Z-Score 방법
```python
import numpy as np
from scipy import stats

def detect_anomaly_zscore(data, threshold=3):
    """
    Z-score를 사용한 이상 탐지

    z = (x - mean) / std
    |z| > threshold면 이상으로 판단
    """
    z_scores = np.abs(stats.zscore(data))
    anomalies = z_scores > threshold
    return anomalies, z_scores

# 사용 예
data = np.array([1, 2, 3, 4, 5, 100])  # 100은 이상치
anomalies, scores = detect_anomaly_zscore(data)
print(f"이상 데이터: {data[anomalies]}")
```

### 2.2 IQR (Interquartile Range) 방법
```python
def detect_anomaly_iqr(data):
    """
    IQR을 사용한 이상 탐지
    Q1 - 1.5*IQR ~ Q3 + 1.5*IQR 범위 벗어나면 이상
    """
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    anomalies = (data < lower_bound) | (data > upper_bound)
    return anomalies, lower_bound, upper_bound

# 사용 예
data = np.array([10, 12, 14, 16, 18, 100])
anomalies, lb, ub = detect_anomaly_iqr(data)
print(f"범위: [{lb}, {ub}], 이상: {data[anomalies]}")
```

### 2.3 Modified Z-Score
```python
def detect_anomaly_modified_zscore(data, threshold=3.5):
    """
    Median Absolute Deviation (MAD) 사용
    Z-score보다 outlier에 강건
    """
    median = np.median(data)
    mad = np.median(np.abs(data - median))
    modified_z = 0.6745 * (data - median) / mad if mad != 0 else 0

    anomalies = np.abs(modified_z) > threshold
    return anomalies, modified_z

# 사용 예
data = np.array([1, 2, 3, 4, 5, 1000])
anomalies, scores = detect_anomaly_modified_zscore(data)
print(f"이상 데이터: {data[anomalies]}")
```

## 3. 머신러닝 기반 이상 탐지

### 3.1 Isolation Forest
```python
from sklearn.ensemble import IsolationForest
import pandas as pd

def detect_anomaly_isolation_forest(data, contamination=0.1):
    """
    Isolation Forest를 사용한 이상 탐지
    - 고차원 데이터에 효과적
    - 계산 효율성 우수
    """
    # 데이터 준비
    X = data.reshape(-1, 1) if isinstance(data, np.ndarray) else data

    # 모델 학습
    model = IsolationForest(
        contamination=contamination,
        random_state=42
    )

    # 예측
    predictions = model.fit_predict(X)
    anomaly_scores = model.score_samples(X)

    return predictions == -1, anomaly_scores

# 사용 예
data = np.random.normal(100, 15, 1000)
data = np.append(data, [500, 600])  # 이상치 추가
anomalies, scores = detect_anomaly_isolation_forest(data)
print(f"이상 개수: {anomalies.sum()}")
```

### 3.2 Local Outlier Factor (LOF)
```python
from sklearn.neighbors import LocalOutlierFactor

def detect_anomaly_lof(data, n_neighbors=20):
    """
    LOF를 사용한 이상 탐지
    - 지역적 밀도 기반
    - 다양한 밀도의 데이터에 강건
    """
    X = data.reshape(-1, 1) if isinstance(data, np.ndarray) else data

    model = LocalOutlierFactor(n_neighbors=n_neighbors)
    predictions = model.fit_predict(X)
    scores = model.negative_outlier_factor_

    return predictions == -1, scores

# 사용 예
X = np.random.normal(0, 1, (100, 2))
X = np.vstack([X, [[5, 5], [6, 6]]])  # 이상치 추가
anomalies, scores = detect_anomaly_lof(X)
```

### 3.3 One-Class SVM
```python
from sklearn.svm import OneClassSVM

def detect_anomaly_ocsvm(data, nu=0.05):
    """
    One-Class SVM을 사용한 이상 탐지
    - 학습 데이터의 경계 학습
    - 고차원 데이터에 효과적
    """
    X = data.reshape(-1, 1) if isinstance(data, np.ndarray) else data

    model = OneClassSVM(kernel='rbf', gamma='auto', nu=nu)
    predictions = model.fit_predict(X)

    return predictions == -1, model.decision_function(X)

# 사용 예
X = np.random.normal(100, 10, 100)
anomalies, scores = detect_anomaly_ocsvm(X)
```

## 4. 시계열 이상 탐지

### 4.1 ARIMA 기반 이상 탐지
```python
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

def detect_anomaly_arima(time_series, order=(1, 1, 1), threshold=2):
    """
    ARIMA 모델을 사용한 시계열 이상 탐지
    - 예측값과 실제값의 잔차 분석
    """
    # 모델 학습
    model = ARIMA(time_series, order=order)
    fitted_model = model.fit()

    # 예측
    fitted_values = fitted_model.fittedvalues
    residuals = fitted_model.resid

    # 이상 탐지
    std = residuals.std()
    anomalies = np.abs(residuals) > threshold * std

    return anomalies, residuals, fitted_values

# 사용 예
ts = pd.Series([10, 11, 12, 13, 14, 15, 100, 16, 17])
anomalies, resid, fitted = detect_anomaly_arima(ts)
```

### 4.2 Prophet를 사용한 이상 탐지
```python
from prophet import Prophet
import pandas as pd

def detect_anomaly_prophet(df, interval_width=0.95):
    """
    Facebook Prophet를 사용한 시계열 이상 탐지
    - 계절성 처리
    - 휴일 영향 고려
    """
    # 데이터 준비
    df_prophet = df.copy()
    df_prophet.columns = ['ds', 'y']
    df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])

    # 모델 학습
    model = Prophet(
        interval_width=interval_width,
        yearly_seasonality=True,
        weekly_seasonality=True
    )
    model.fit(df_prophet)

    # 예측
    forecast = model.predict(df_prophet[['ds']])

    # 이상 탐지
    df_prophet = df_prophet.merge(
        forecast[['ds', 'yhat', 'yhat_upper', 'yhat_lower']],
        on='ds'
    )

    anomalies = (df_prophet['y'] > df_prophet['yhat_upper']) | \
                (df_prophet['y'] < df_prophet['yhat_lower'])

    return anomalies, df_prophet

# 사용 예
dates = pd.date_range('2024-01-01', periods=100)
values = np.sin(np.arange(100) * 2 * np.pi / 30) + np.random.normal(0, 0.1, 100)
values[50] = 5  # 이상치 추가
df = pd.DataFrame({'ds': dates, 'y': values})
anomalies, result = detect_anomaly_prophet(df)
```

### 4.3 Seasonal Decomposition 기반
```python
from statsmodels.tsa.seasonal import seasonal_decompose

def detect_anomaly_seasonal(time_series, period=12):
    """
    계절성 분해를 사용한 이상 탐지
    """
    # 분해
    decomposition = seasonal_decompose(
        time_series,
        model='additive',
        period=period
    )

    # 잔차 분석
    residuals = decomposition.resid
    std = residuals.std()
    threshold = 2 * std  # 2-sigma rule

    anomalies = np.abs(residuals) > threshold

    return anomalies, decomposition, residuals

# 사용 예
ts = pd.Series(np.random.normal(100, 10, 120))
anomalies, decomp, resid = detect_anomaly_seasonal(ts)
```

## 5. 실전 구현: DQ Agent의 이상 탐지 모듈

### 5.1 통합 이상 탐지 엔진
```python
class AnomalyDetectionEngine:
    def __init__(self, methods=['zscore', 'isolation_forest']):
        self.methods = methods

    def detect(self, data, column):
        """
        다중 방법으로 이상 탐지
        """
        results = {}

        if 'zscore' in self.methods:
            results['zscore'] = self._detect_zscore(data[column])

        if 'isolation_forest' in self.methods:
            results['isolation_forest'] = self._detect_isolation_forest(data[column])

        if 'lof' in self.methods:
            results['lof'] = self._detect_lof(data[column])

        # 앙상블: 2개 이상에서 이상으로 판단
        ensemble = self._ensemble_results(results)

        return {
            'results': results,
            'ensemble': ensemble,
            'anomaly_count': ensemble.sum()
        }

    def _detect_zscore(self, data):
        return np.abs(stats.zscore(data)) > 3

    def _detect_isolation_forest(self, data):
        model = IsolationForest(contamination=0.1)
        return model.fit_predict(data.values.reshape(-1, 1)) == -1

    def _detect_lof(self, data):
        model = LocalOutlierFactor()
        return model.fit_predict(data.values.reshape(-1, 1)) == -1

    def _ensemble_results(self, results):
        ensemble = np.zeros(len(list(results.values())[0]), dtype=bool)
        for anomalies in results.values():
            ensemble += anomalies
        return ensemble >= 2
```

## 6. 실습 프로젝트

### 6.1 프로젝트: 실시간 트랜잭션 이상 탐지
```
1. 트랜잭션 데이터 생성 (정상 + 이상치)
2. 5가지 이상 탐지 알고리즘 구현
3. 알고리즘별 성능 비교
4. 최적 파라미터 찾기
5. 앙상블 이상 탐지 구현
6. 시각화 및 리포트
```

### 6.2 평가 메트릭
```python
from sklearn.metrics import confusion_matrix, precision_score, recall_score

def evaluate_anomaly_detection(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = 2 * (precision * recall) / (precision + recall)

    return {
        'confusion_matrix': cm,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }
```

## 7. 평가 기준

- [ ] 5가지 이상 탐지 방법 구현
- [ ] 통계 기반 방법 이해도
- [ ] ML 기반 방법 적용
- [ ] 시계열 이상 탐지
- [ ] 앙상블 방법 구현
- [ ] 프로젝트 완료

## 8. 주요 고려사항

| 항목 | 설명 |
|------|------|
| 데이터 특성 | 정규분포 vs 비정규분포 |
| 차원 | 1차원 vs 고차원 |
| 시간 | 정적 vs 동적 이상 |
| 성능 | 속도 vs 정확도 트레이드오프 |

## 9. 참고 자료

- Scikit-learn 이상 탐지 모듈
- "Outlier Detection for Temporal Data" - 논문
- Prophet 시계열 예측
- Statsmodels ARIMA 가이드
