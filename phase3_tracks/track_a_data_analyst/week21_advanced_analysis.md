# Week 21: 고급 분석 (Advanced Analysis: Timeseries, Correlation, Forecasting)

## 학습 목표
- 시계열 데이터 분석 및 예측 자동화
- 상관관계 분석 및 인과관계 추론
- 머신러닝 기반 예측 모델 통합
- A/B 테스트 및 통계적 검정 자동화

## O'Reilly 리소스
- "Time Series Forecasting with ARIMA" - Rob J. Hyndman
- "An Introduction to Statistical Learning" - James, Witten, Hastie, Tibshirani
- "Causal Inference: The Mixtape" - Scott Cunningham
- "Practical Statistics for Data Scientists"

## 핵심 개념

### 1. 시계열 분석
```python
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA

class TimeSeriesAnalyzer:
    def __init__(self, series, freq='D'):
        self.series = series
        self.freq = freq
        self.results = {}

    def decompose_series(self):
        """시계열 분해"""
        decomposition = seasonal_decompose(
            self.series,
            model='additive',
            period=365 if self.freq == 'D' else 12
        )

        self.results['decomposition'] = {
            'trend': decomposition.trend.tolist(),
            'seasonal': decomposition.seasonal.tolist(),
            'residual': decomposition.resid.tolist()
        }

        return decomposition

    def stationarity_test(self):
        """정상성 검정 (ADF 검정)"""
        result = adfuller(self.series.dropna())

        self.results['stationarity'] = {
            'test_statistic': float(result[0]),
            'p_value': float(result[1]),
            'critical_values': {
                '1%': float(result[4]['1%']),
                '5%': float(result[4]['5%']),
                '10%': float(result[4]['10%'])
            },
            'is_stationary': result[1] < 0.05
        }

        return result

    def autocorrelation_analysis(self, lags=40):
        """자기상관 분석"""
        acf_values = acf(self.series.dropna(), nlags=lags)
        pacf_values = pacf(self.series.dropna(), nlags=lags)

        self.results['autocorrelation'] = {
            'acf': acf_values.tolist(),
            'pacf': pacf_values.tolist(),
            'optimal_lags': self._find_optimal_lags(acf_values, pacf_values)
        }

        return acf_values, pacf_values

    def _find_optimal_lags(self, acf, pacf):
        """최적 시차 찾기"""
        acf_sig = np.where(np.abs(acf[1:]) > 1.96/np.sqrt(len(acf)))[0]
        pacf_sig = np.where(np.abs(pacf[1:]) > 1.96/np.sqrt(len(pacf)))[0]

        return {
            'acf_lags': acf_sig.tolist(),
            'pacf_lags': pacf_sig.tolist()
        }

    def forecast_arima(self, order=(1,1,1), periods=30):
        """ARIMA 예측"""
        model = ARIMA(self.series, order=order)
        fitted = model.fit()

        forecast = fitted.get_forecast(steps=periods)
        forecast_df = forecast.conf_int()
        forecast_df['forecast'] = forecast.predicted_mean

        self.results['arima'] = {
            'model_summary': str(fitted.summary()),
            'forecast': forecast_df.to_dict(),
            'aic': float(fitted.aic),
            'bic': float(fitted.bic)
        }

        return forecast_df

    def auto_arima(self, max_p=5, max_d=2, max_q=5):
        """자동 ARIMA 파라미터 선택"""
        from pmdarima import auto_arima

        auto_model = auto_arima(
            self.series,
            max_p=max_p,
            max_d=max_d,
            max_q=max_q,
            seasonal=False,
            trace=True,
            error_action='ignore',
            suppress_warnings=True
        )

        self.results['auto_arima_order'] = auto_model.order

        return auto_model
```

### 2. 상관관계 및 인과관계 분석
```python
from scipy.stats import chi2_contingency, spearmanr, kendalltau
from sklearn.preprocessing import StandardScaler

class CorrelationAnalyzer:
    def __init__(self, df):
        self.df = df
        self.results = {}

    def correlation_matrix(self, method='pearson'):
        """상관관계 행렬"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        corr_matrix = self.df[numeric_cols].corr(method=method)

        self.results['correlation_matrix'] = corr_matrix.to_dict()

        return corr_matrix

    def partial_correlation(self, var1, var2, control_vars):
        """편상관관계 계산"""
        # var1과 control_vars의 잔차
        residuals1 = self._get_residuals(self.df[var1], self.df[control_vars])
        # var2와 control_vars의 잔차
        residuals2 = self._get_residuals(self.df[var2], self.df[control_vars])

        partial_corr = np.corrcoef(residuals1, residuals2)[0, 1]

        self.results['partial_correlation'] = {
            'var1': var1,
            'var2': var2,
            'control_variables': control_vars,
            'partial_correlation': float(partial_corr)
        }

        return partial_corr

    def _get_residuals(self, target, predictors):
        """선형 회귀 잔차 계산"""
        from sklearn.linear_model import LinearRegression

        model = LinearRegression()
        model.fit(predictors, target)
        return target - model.predict(predictors)

    def granger_causality_test(self, series1, series2, max_lag=4):
        """Granger 인과관계 검정"""
        from statsmodels.tsa.api import grangercausalitytests

        data = self.df[[series1, series2]].dropna()

        try:
            results = grangercausalitytests(data, max_lag, verbose=False)

            granger_results = {}
            for lag in range(1, max_lag + 1):
                p_value = results[lag][0]['ssr_ftest'][1]
                granger_results[lag] = {
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }

            self.results['granger_causality'] = {
                'series1': series1,
                'series2': series2,
                'results': granger_results
            }

            return results
        except Exception as e:
            print(f"Granger 검정 오류: {e}")
            return None

    def categorical_association(self, var1, var2):
        """범주형 변수 연관성 (카이제곱)"""
        contingency_table = pd.crosstab(self.df[var1], self.df[var2])
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)

        self.results['categorical_association'] = {
            'variables': [var1, var2],
            'chi2_statistic': float(chi2),
            'p_value': float(p_value),
            'degrees_of_freedom': int(dof),
            'significant': p_value < 0.05
        }

        return chi2, p_value
```

### 3. 머신러닝 기반 예측
```python
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

class PredictiveModeler:
    def __init__(self, df, target_column):
        self.df = df
        self.target = target_column
        self.models = {}
        self.results = {}

    def prepare_features(self):
        """특성 준비"""
        X = self.df.drop(columns=[self.target])
        X = X.select_dtypes(include=[np.number])
        y = self.df[self.target]

        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_models(self):
        """여러 모델 학습"""
        X_train, X_test, y_train, y_test = self.prepare_features()

        models = {
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }

        for name, model in models.items():
            # 모델 학습
            model.fit(X_train, y_train)

            # 예측
            y_pred = model.predict(X_test)

            # 평가
            self.results[name] = {
                'mse': float(mean_squared_error(y_test, y_pred)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
                'mae': float(mean_absolute_error(y_test, y_pred)),
                'r2': float(r2_score(y_test, y_pred)),
                'cross_val_score': float(cross_val_score(model, X_train, y_train, cv=5).mean())
            }

            self.models[name] = model

        return self.results

    def feature_importance(self):
        """특성 중요도"""
        importances = {}

        for name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                importances[name] = model.feature_importances_.tolist()

        self.results['feature_importance'] = importances

        return importances
```

### 4. A/B 테스트 자동화
```python
from scipy.stats import ttest_ind, mannwhitneyu, chi2_contingency

class ABTestAnalyzer:
    def __init__(self, control_data, treatment_data):
        self.control = control_data
        self.treatment = treatment_data
        self.results = {}

    def ttest_analysis(self, alpha=0.05):
        """T-test 분석"""
        t_stat, p_value = ttest_ind(self.control, self.treatment)

        effect_size = (self.treatment.mean() - self.control.mean()) / np.sqrt(
            (self.control.std()**2 + self.treatment.std()**2) / 2
        )

        self.results['ttest'] = {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'effect_size': float(effect_size),
            'significant': p_value < alpha,
            'control_mean': float(self.control.mean()),
            'treatment_mean': float(self.treatment.mean()),
            'lift': float((self.treatment.mean() - self.control.mean()) / self.control.mean() * 100)
        }

        return t_stat, p_value

    def mann_whitney_test(self, alpha=0.05):
        """Mann-Whitney U 검정 (비모수)"""
        u_stat, p_value = mannwhitneyu(self.control, self.treatment)

        self.results['mann_whitney'] = {
            'u_statistic': float(u_stat),
            'p_value': float(p_value),
            'significant': p_value < alpha
        }

        return u_stat, p_value

    def sample_size_calculation(self, effect_size=0.5, alpha=0.05, power=0.8):
        """필요 표본 크기 계산"""
        from scipy.stats import norm

        z_alpha = norm.ppf(1 - alpha / 2)
        z_beta = norm.ppf(power)

        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2

        self.results['sample_size'] = {
            'required_sample_size': int(np.ceil(n)),
            'effect_size': effect_size,
            'alpha': alpha,
            'power': power
        }

        return int(np.ceil(n))
```

## 실습 과제

### Task 1: 완전한 시계열 분석 파이프라인
```python
# 예시 사용
ts_analyzer = TimeSeriesAnalyzer(df['sales_data'])
ts_analyzer.decompose_series()
ts_analyzer.stationarity_test()
ts_analyzer.autocorrelation_analysis()
forecast_df = ts_analyzer.forecast_arima()
```

### Task 2: 상관관계 및 인과관계 분석
- 다변량 상관관계 분석
- Granger 인과관계 검정
- 범주형 변수 연관성 검정

### Task 3: 예측 모델 비교
- 여러 머신러닝 모델 학습
- 성능 지표 비교
- 특성 중요도 분석

## 주간 체크포인트

- [ ] 시계열 분해 구현
- [ ] 정상성 검정 자동화
- [ ] 자기상관 분석
- [ ] ARIMA 예측 모델
- [ ] 상관관계 행렬 계산
- [ ] Granger 인과관계 검정
- [ ] 머신러닝 기반 예측
- [ ] A/B 테스트 분석

## 학습 성과 기준
- [ ] 시계열 예측 정확도(RMSE) 개선 > 20%
- [ ] 인과관계 추론 신뢰도 > 85%
- [ ] A/B 테스트 결론 신뢰도 > 95%
