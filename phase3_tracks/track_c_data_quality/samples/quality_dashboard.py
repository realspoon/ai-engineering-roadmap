"""
Streamlit Quality Monitoring Dashboard
Streamlit 기반 품질 모니터링 대시보드

Features:
- 실시간 품질 지표 시각화
- 시계열 모니터링
- 이상치 시각화
- 검증 규칙 상태 모니터링
- 데이터 프로필 비교
- 커스텀 필터 및 드릴다운
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Any

try:
    import streamlit as st
except ImportError:
    # Streamlit이 없어도 대시보드 클래스 정의 가능
    st = None

logger = logging.getLogger(__name__)


class QualityMetrics:
    """품질 지표"""

    def __init__(self):
        """초기화"""
        self.timestamps: List[datetime] = []
        self.overall_scores: List[float] = []
        self.completeness_scores: List[float] = []
        self.consistency_scores: List[float] = []
        self.validity_scores: List[float] = []
        self.uniqueness_scores: List[float] = []
        self.anomaly_counts: List[int] = []
        self.validation_errors: List[int] = []

    def add_measurement(self, timestamp: datetime, overall: float,
                       completeness: float, consistency: float,
                       validity: float, uniqueness: float,
                       anomalies: int = 0, errors: int = 0) -> None:
        """측정값 추가"""
        self.timestamps.append(timestamp)
        self.overall_scores.append(overall)
        self.completeness_scores.append(completeness)
        self.consistency_scores.append(consistency)
        self.validity_scores.append(validity)
        self.uniqueness_scores.append(uniqueness)
        self.anomaly_counts.append(anomalies)
        self.validation_errors.append(errors)

    def to_dataframe(self) -> pd.DataFrame:
        """DataFrame으로 변환"""
        return pd.DataFrame({
            'timestamp': self.timestamps,
            'overall_score': self.overall_scores,
            'completeness': self.completeness_scores,
            'consistency': self.consistency_scores,
            'validity': self.validity_scores,
            'uniqueness': self.uniqueness_scores,
            'anomalies': self.anomaly_counts,
            'errors': self.validation_errors
        })


class QualityDashboard:
    """품질 모니터링 대시보드"""

    def __init__(self):
        """초기화"""
        self.metrics = QualityMetrics()
        self.column_profiles: Dict[str, Dict[str, Any]] = {}
        self.validation_results: Dict[str, Dict[str, Any]] = {}
        self.anomaly_results: Dict[str, Dict[str, Any]] = {}

    def add_metrics(self, timestamp: datetime, overall: float,
                   completeness: float, consistency: float,
                   validity: float, uniqueness: float,
                   anomalies: int = 0, errors: int = 0) -> None:
        """지표 추가"""
        self.metrics.add_measurement(
            timestamp, overall, completeness, consistency,
            validity, uniqueness, anomalies, errors
        )

    def add_column_profile(self, column_name: str, profile: Dict[str, Any]) -> None:
        """컬럼 프로필 추가"""
        self.column_profiles[column_name] = profile

    def add_validation_results(self, column_name: str, results: Dict[str, Any]) -> None:
        """검증 결과 추가"""
        self.validation_results[column_name] = results

    def add_anomaly_results(self, column_name: str, results: Dict[str, Any]) -> None:
        """이상치 결과 추가"""
        self.anomaly_results[column_name] = results

    def plot_overall_trend(self) -> go.Figure:
        """전체 품질 점수 추이"""
        df = self.metrics.to_dataframe()

        if df.empty:
            return go.Figure()

        fig = go.Figure()

        # 전체 점수
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['overall_score'],
            name='Overall Score',
            mode='lines+markers',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        ))

        # 임계값
        fig.add_hline(y=0.75, line_dash="dash", line_color="orange", annotation_text="Target: 75%")

        fig.update_layout(
            title="Data Quality Score Trend",
            xaxis_title="Time",
            yaxis_title="Quality Score",
            hovermode='x unified',
            template='plotly_white',
            height=400
        )

        return fig

    def plot_dimension_scores(self) -> go.Figure:
        """차원별 점수 비교"""
        df = self.metrics.to_dataframe()

        if df.empty:
            return go.Figure()

        # 최근 10개 측정값
        df = df.tail(10)

        fig = go.Figure()

        dimensions = ['completeness', 'consistency', 'validity', 'uniqueness']
        for dim in dimensions:
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df[dim],
                name=dim.capitalize(),
                mode='lines+markers'
            ))

        fig.update_layout(
            title="Quality Dimensions Comparison",
            xaxis_title="Time",
            yaxis_title="Score",
            hovermode='x unified',
            template='plotly_white',
            height=400
        )

        return fig

    def plot_anomalies(self) -> go.Figure:
        """이상치 추이"""
        df = self.metrics.to_dataframe()

        if df.empty:
            return go.Figure()

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Anomaly Count", "Validation Errors"),
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )

        # 이상치
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['anomalies'],
                name='Anomalies',
                marker_color='rgba(255,0,0,0.5)'
            ),
            row=1, col=1
        )

        # 검증 오류
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['errors'],
                name='Validation Errors',
                marker_color='rgba(255,165,0,0.5)'
            ),
            row=2, col=1
        )

        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=2, col=1)

        fig.update_layout(
            title="Anomalies and Errors",
            height=500,
            template='plotly_white'
        )

        return fig

    def plot_column_quality(self) -> go.Figure:
        """컬럼별 품질 분포"""
        if not self.column_profiles:
            return go.Figure()

        columns = []
        null_rates = []
        unique_rates = []

        for col, profile in self.column_profiles.items():
            columns.append(col)
            null_rates.append(profile.get('null_percentage', 0))
            unique_rates.append(profile.get('unique_percentage', 0))

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Null Rate (%)',
            x=columns,
            y=null_rates,
            marker_color='rgba(255,0,0,0.6)'
        ))

        fig.add_trace(go.Bar(
            name='Unique Rate (%)',
            x=columns,
            y=unique_rates,
            marker_color='rgba(0,100,200,0.6)'
        ))

        fig.update_layout(
            title="Column Quality Metrics",
            xaxis_title="Column",
            yaxis_title="Percentage",
            barmode='group',
            height=400,
            template='plotly_white'
        )

        return fig

    def plot_validation_status(self) -> go.Figure:
        """검증 상태"""
        if not self.validation_results:
            return go.Figure()

        passed = 0
        failed = 0

        for col, results in self.validation_results.items():
            if results.get('is_valid', False):
                passed += 1
            else:
                failed += 1

        fig = go.Figure(data=[
            go.Pie(
                labels=['Passed', 'Failed'],
                values=[passed, failed],
                marker=dict(colors=['#2ecc71', '#e74c3c']),
                textposition='inside',
                textinfo='label+percent'
            )
        ])

        fig.update_layout(
            title="Validation Rules Status",
            height=400
        )

        return fig

    def plot_heatmap(self) -> go.Figure:
        """품질 지표 히트맵"""
        df = self.metrics.to_dataframe()

        if df.empty:
            return go.Figure()

        # 최근 20개 측정값
        df = df.tail(20)

        dimensions_data = df[['completeness', 'consistency', 'validity', 'uniqueness']].T

        fig = go.Figure(data=go.Heatmap(
            z=dimensions_data.values,
            x=range(len(df)),
            y=['Completeness', 'Consistency', 'Validity', 'Uniqueness'],
            colorscale='RdYlGn',
            zmid=0.75,
            text=np.round(dimensions_data.values, 2),
            texttemplate='%{text:.2f}',
            textfont={"size": 10}
        ))

        fig.update_layout(
            title="Quality Metrics Heatmap",
            xaxis_title="Time Index",
            yaxis_title="Dimension",
            height=400
        )

        return fig

    def create_summary_cards(self) -> Dict[str, float]:
        """요약 지표"""
        df = self.metrics.to_dataframe()

        if df.empty:
            return {
                "current_score": 0.0,
                "avg_score": 0.0,
                "min_score": 0.0,
                "total_anomalies": 0
            }

        return {
            "current_score": df['overall_score'].iloc[-1],
            "avg_score": df['overall_score'].mean(),
            "min_score": df['overall_score'].min(),
            "total_anomalies": int(df['anomalies'].sum())
        }

    def render_streamlit(self) -> None:
        """Streamlit 대시보드 렌더링"""
        if st is None:
            print("Streamlit is not installed. Install with: pip install streamlit")
            return

        # 페이지 설정
        st.set_page_config(
            page_title="Data Quality Dashboard",
            page_icon="📊",
            layout="wide"
        )

        # 제목
        st.title("📊 Data Quality Monitoring Dashboard")

        # 요약 지표
        cards = self.create_summary_cards()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Score", f"{cards['current_score']:.2%}", delta=None)
        with col2:
            st.metric("Average Score", f"{cards['avg_score']:.2%}")
        with col3:
            st.metric("Minimum Score", f"{cards['min_score']:.2%}")
        with col4:
            st.metric("Total Anomalies", int(cards['total_anomalies']))

        # 탭 구성
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Trend", "Dimensions", "Anomalies", "Columns", "Validation"
        ])

        with tab1:
            st.plotly_chart(self.plot_overall_trend(), use_container_width=True)

        with tab2:
            st.plotly_chart(self.plot_dimension_scores(), use_container_width=True)
            st.plotly_chart(self.plot_heatmap(), use_container_width=True)

        with tab3:
            st.plotly_chart(self.plot_anomalies(), use_container_width=True)

        with tab4:
            st.plotly_chart(self.plot_column_quality(), use_container_width=True)

        with tab5:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(self.plot_validation_status(), use_container_width=True)
            with col2:
                st.write("### Validation Details")
                for col, results in self.validation_results.items():
                    status = "✓" if results.get('is_valid', False) else "✗"
                    st.write(f"{status} {col}: {results.get('message', 'N/A')}")

        # 데이터 테이블
        with st.expander("View Raw Data"):
            st.dataframe(self.metrics.to_dataframe(), use_container_width=True)

    def export_report(self, filepath: str) -> None:
        """리포트 내보내기"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.create_summary_cards(),
            "metrics": self.metrics.to_dataframe().to_dict(),
            "column_profiles": self.column_profiles,
            "validation_results": self.validation_results,
            "anomaly_results": self.anomaly_results
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Report exported to {filepath}")


def demo_dashboard():
    """데모 대시보드"""
    dashboard = QualityDashboard()

    # 샘플 데이터 생성
    base_time = datetime.now()
    for i in range(20):
        timestamp = base_time - timedelta(hours=20-i)
        overall = 0.70 + np.random.normal(0.05, 0.03)
        overall = max(0.5, min(0.95, overall))

        dashboard.add_metrics(
            timestamp=timestamp,
            overall=overall,
            completeness=overall + np.random.normal(0, 0.02),
            consistency=overall + np.random.normal(0, 0.02),
            validity=overall + np.random.normal(0, 0.02),
            uniqueness=overall + np.random.normal(0, 0.02),
            anomalies=int(np.random.poisson(2)),
            errors=int(np.random.poisson(1))
        )

    # 컬럼 프로필 추가
    for col in ['id', 'email', 'age', 'salary']:
        dashboard.add_column_profile(col, {
            'null_percentage': np.random.uniform(0, 5),
            'unique_percentage': np.random.uniform(90, 100)
        })

    # 검증 결과 추가
    for col in ['email', 'age']:
        dashboard.add_validation_results(col, {
            'is_valid': np.random.random() > 0.2,
            'message': f"Validation rule for {col}"
        })

    return dashboard


def main():
    """테스트"""
    dashboard = demo_dashboard()

    # 그래프 생성 및 저장 (HTML로)
    print("Generating charts...")

    charts = {
        "overall_trend.html": dashboard.plot_overall_trend(),
        "dimension_scores.html": dashboard.plot_dimension_scores(),
        "anomalies.html": dashboard.plot_anomalies(),
        "column_quality.html": dashboard.plot_column_quality(),
        "validation_status.html": dashboard.plot_validation_status(),
        "heatmap.html": dashboard.plot_heatmap()
    }

    for filename, fig in charts.items():
        # fig.write_html(filename)  # 실제 환경에서 저장
        print(f"  - {filename}")

    # 요약 지표 출력
    print("\n=== Summary Metrics ===")
    cards = dashboard.create_summary_cards()
    for key, value in cards.items():
        print(f"  {key}: {value}")

    # Streamlit 대시보드 렌더링 (있는 경우)
    if st is not None:
        dashboard.render_streamlit()


if __name__ == "__main__":
    main()
