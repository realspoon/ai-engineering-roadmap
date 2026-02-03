"""
Streamlit Interactive Data Analysis App
대화형 데이터 분석 UI 애플리케이션

실행: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
import json


# 페이지 설정
st.set_page_config(
    page_title="Data Analysis Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


class DataAnalysisApp:
    """데이터 분석 애플리케이션"""

    def __init__(self):
        self.df = None
        self.df_name = None

    def load_data(self):
        """데이터 로드"""
        st.sidebar.header("데이터 로드")

        # 샘플 데이터 또는 파일 업로드
        option = st.sidebar.radio(
            "데이터 선택:",
            ["샘플 데이터", "파일 업로드"]
        )

        if option == "샘플 데이터":
            if st.sidebar.button("샘플 데이터 로드"):
                self.df = self._create_sample_data()
                self.df_name = "Sample Data"
                st.sidebar.success("샘플 데이터 로드 완료!")

        else:
            uploaded_file = st.sidebar.file_uploader(
                "CSV/Excel 파일 선택",
                type=["csv", "xlsx"]
            )
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        self.df = pd.read_csv(uploaded_file)
                    else:
                        self.df = pd.read_excel(uploaded_file)
                    self.df_name = uploaded_file.name
                    st.sidebar.success(f"파일 로드 완료: {uploaded_file.name}")
                except Exception as e:
                    st.sidebar.error(f"파일 로드 실패: {str(e)}")

    def _create_sample_data(self) -> pd.DataFrame:
        """샘플 데이터셋 생성"""
        np.random.seed(42)
        data = {
            'ID': range(1, 201),
            'Age': np.random.normal(35, 12, 200),
            'Salary': np.random.normal(55000, 20000, 200),
            'Experience': np.random.normal(10, 5, 200),
            'Department': np.random.choice(
                ['Sales', 'Marketing', 'IT', 'HR', 'Finance'],
                200
            ),
            'Performance': np.random.choice(['A', 'B', 'C'], 200, p=[0.5, 0.3, 0.2]),
            'Satisfaction': np.random.randint(1, 6, 200)
        }
        return pd.DataFrame(data)

    def show_overview(self):
        """데이터 개요"""
        if self.df is None:
            st.warning("먼저 데이터를 로드하세요.")
            return

        st.header("📋 데이터 개요")

        # 기본 통계
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", len(self.df))
        with col2:
            st.metric("Total Columns", len(self.df.columns))
        with col3:
            st.metric("Memory Usage", f"{self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        with col4:
            st.metric("Missing Values", self.df.isnull().sum().sum())

        # 데이터 샘플
        st.subheader("Data Sample")
        st.dataframe(self.df.head(10), use_container_width=True)

        # 데이터 타입
        st.subheader("Data Types")
        dtype_df = pd.DataFrame({
            'Column': self.df.columns,
            'Type': self.df.dtypes.values,
            'Non-Null Count': self.df.count().values,
            'Null Count': self.df.isnull().sum().values
        })
        st.dataframe(dtype_df, use_container_width=True)

    def show_descriptive_statistics(self):
        """기술통계"""
        if self.df is None:
            st.warning("먼저 데이터를 로드하세요.")
            return

        st.header("📊 기술통계")

        # 수치형 컬럼만
        numeric_df = self.df.select_dtypes(include=[np.number])

        if len(numeric_df.columns) == 0:
            st.warning("수치형 컬럼이 없습니다.")
            return

        # 기술통계 테이블
        st.subheader("Descriptive Statistics")
        st.dataframe(
            numeric_df.describe().T,
            use_container_width=True
        )

        # 선택된 컬럼의 상세 통계
        selected_col = st.selectbox(
            "상세 통계 컬럼 선택",
            numeric_df.columns
        )

        if selected_col:
            col1, col2, col3, col4 = st.columns(4)
            data = numeric_df[selected_col]

            with col1:
                st.metric("Mean", f"{data.mean():.2f}")
            with col2:
                st.metric("Median", f"{data.median():.2f}")
            with col3:
                st.metric("Std Dev", f"{data.std():.2f}")
            with col4:
                st.metric("Range", f"{data.max() - data.min():.2f}")

            # 분포도
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=data,
                nbinsx=30,
                name=selected_col
            ))
            fig.update_layout(
                title=f"{selected_col} Distribution",
                xaxis_title=selected_col,
                yaxis_title="Frequency",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

    def show_missing_data_analysis(self):
        """결측치 분석"""
        if self.df is None:
            st.warning("먼저 데이터를 로드하세요.")
            return

        st.header("🔍 결측치 분석")

        missing_data = self.df.isnull().sum()
        missing_percent = (missing_data / len(self.df)) * 100

        missing_df = pd.DataFrame({
            'Column': missing_data.index,
            'Missing Count': missing_data.values,
            'Missing Percentage': missing_percent.values
        }).sort_values('Missing Count', ascending=False)

        missing_df = missing_df[missing_df['Missing Count'] > 0]

        if len(missing_df) == 0:
            st.success("결측치가 없습니다!")
            return

        st.subheader("Missing Data Summary")
        st.dataframe(missing_df, use_container_width=True)

        # 결측치 시각화
        fig = px.bar(
            missing_df,
            x='Column',
            y='Missing Percentage',
            title="Missing Data by Column",
            labels={'Missing Percentage': '결측 비율 (%)'}
        )
        st.plotly_chart(fig, use_container_width=True)

    def show_correlation_analysis(self):
        """상관계수 분석"""
        if self.df is None:
            st.warning("먼저 데이터를 로드하세요.")
            return

        st.header("🔗 상관계수 분석")

        numeric_df = self.df.select_dtypes(include=[np.number])

        if len(numeric_df.columns) < 2:
            st.warning("상관계수 분석을 위해 최소 2개 이상의 수치형 컬럼이 필요합니다.")
            return

        # 상관계수 행렬
        corr_matrix = numeric_df.corr()

        # 히트맵
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10}
        ))
        fig.update_layout(
            title="Correlation Matrix",
            height=600,
            width=700
        )
        st.plotly_chart(fig, use_container_width=True)

        # 높은 상관계수 쌍
        st.subheader("High Correlations (|r| > 0.7)")
        high_corr_pairs = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > 0.7:
                    high_corr_pairs.append({
                        'Variable 1': corr_matrix.columns[i],
                        'Variable 2': corr_matrix.columns[j],
                        'Correlation': corr_matrix.iloc[i, j]
                    })

        if high_corr_pairs:
            high_corr_df = pd.DataFrame(high_corr_pairs)
            st.dataframe(high_corr_df, use_container_width=True)
        else:
            st.info("높은 상관관계를 가진 변수 쌍이 없습니다.")

    def show_visualization(self):
        """시각화"""
        if self.df is None:
            st.warning("먼저 데이터를 로드하세요.")
            return

        st.header("📈 데이터 시각화")

        # 차트 타입 선택
        chart_type = st.selectbox(
            "차트 타입 선택",
            ["Scatter Plot", "Line Chart", "Bar Chart", "Histogram", "Box Plot"]
        )

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()

        if chart_type == "Scatter Plot":
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("X축 선택", numeric_cols)
            with col2:
                y_col = st.selectbox("Y축 선택", numeric_cols)

            if x_col and y_col:
                fig = px.scatter(
                    self.df,
                    x=x_col,
                    y=y_col,
                    title=f"{x_col} vs {y_col}",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Line Chart":
            col = st.selectbox("컬럼 선택", numeric_cols)
            if col:
                fig = px.line(
                    y=self.df[col],
                    title=f"{col} Trend",
                    height=500,
                    labels={'y': col, 'index': 'Index'}
                )
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Bar Chart":
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("X축 (범주) 선택", categorical_cols if categorical_cols else numeric_cols)
            with col2:
                y_col = st.selectbox("Y축 (수치) 선택", numeric_cols)

            if x_col and y_col:
                fig = px.bar(
                    self.df,
                    x=x_col,
                    y=y_col,
                    title=f"{x_col} by {y_col}",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Histogram":
            col = st.selectbox("컬럼 선택", numeric_cols)
            if col:
                fig = px.histogram(
                    self.df,
                    x=col,
                    nbins=30,
                    title=f"{col} Distribution",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Box Plot":
            col = st.selectbox("컬럼 선택", numeric_cols)
            if col:
                fig = px.box(
                    self.df,
                    y=col,
                    title=f"{col} Box Plot",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)

    def show_insights(self):
        """자동 인사이트"""
        if self.df is None:
            st.warning("먼저 데이터를 로드하세요.")
            return

        st.header("💡 자동 인사이트")

        insights = []

        # 결측치 인사이트
        missing_total = self.df.isnull().sum().sum()
        if missing_total > 0:
            insights.append(f"⚠️ 결측치 {missing_total}개 발견")

        # 중복행 인사이트
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            insights.append(f"⚠️ 중복행 {duplicates}개 발견 ({duplicates/len(self.df)*100:.1f}%)")

        # 수치형 컬럼 분석
        numeric_df = self.df.select_dtypes(include=[np.number])
        for col in numeric_df.columns[:3]:
            data = numeric_df[col]
            skewness = data.skew()
            if abs(skewness) > 1:
                direction = "우측" if skewness > 0 else "좌측"
                insights.append(f"📊 {col}: {direction} 왜곡 분포")

        # 범주형 컬럼 분석
        categorical_df = self.df.select_dtypes(include=['object'])
        for col in categorical_df.columns[:2]:
            value_counts = self.df[col].value_counts()
            if len(value_counts) > 0:
                top_pct = (value_counts.iloc[0] / len(self.df)) * 100
                if top_pct > 50:
                    insights.append(
                        f"🎯 {col}: '{value_counts.index[0]}'가 {top_pct:.1f}%로 편중"
                    )

        if insights:
            for insight in insights:
                st.info(insight)
        else:
            st.success("특이사항이 없습니다!")

    def run(self):
        """애플리케이션 실행"""
        st.title("📊 Data Analysis Agent")
        st.write("다양한 데이터 분석 기능을 제공합니다.")

        # 데이터 로드
        self.load_data()

        if self.df is not None:
            # 탭 생성
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "Overview",
                "Statistics",
                "Missing Data",
                "Correlation",
                "Visualization",
                "Insights"
            ])

            with tab1:
                self.show_overview()

            with tab2:
                self.show_descriptive_statistics()

            with tab3:
                self.show_missing_data_analysis()

            with tab4:
                self.show_correlation_analysis()

            with tab5:
                self.show_visualization()

            with tab6:
                self.show_insights()


# 메인 실행
if __name__ == "__main__":
    app = DataAnalysisApp()
    app.run()
