# Week 23: UI 구축 (Streamlit Interactive Interface)

## 학습 목표
- Streamlit을 활용한 인터랙티브 대시보드 구축
- 사용자 입력 처리 및 실시간 데이터 분석
- 시각화 대시보드 구현
- 다중 페이지 앱 아키텍처 설계

## O'Reilly 리소스
- "Streamlit Documentation" - 공식 문서
- "Building Data Applications with Python"
- "Web Application Development with Streamlit"
- O'Reilly Dashboard Design Best Practices

## 핵심 개념

### 1. Streamlit 기본 구조
```python
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="Data Analyst Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 캐싱으로 성능 최적화
@st.cache_data
def load_data(file_path):
    """데이터 캐싱"""
    return pd.read_csv(file_path)

# 앱 제목
st.title("📊 자동 데이터 분석 시스템")

# 사이드바 구성
st.sidebar.header("설정")
uploaded_file = st.sidebar.file_uploader(
    "CSV 파일 업로드",
    type=["csv", "xlsx"],
    accept_multiple_files=False
)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 기본 정보 표시
    st.subheader("데이터셋 개요")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("행 수", len(df))
    with col2:
        st.metric("열 수", len(df.columns))
    with col3:
        st.metric("결측값", df.isnull().sum().sum())

    # 데이터 미리보기
    st.subheader("데이터 미리보기")
    st.dataframe(df.head())
```

### 2. 인터랙티브 분석 대시보드
```python
class StreamlitAnalysisDashboard:
    def __init__(self):
        self.df = None
        self.analysis_results = {}

    def render_data_loading_section(self):
        """데이터 로딩 섹션"""
        st.subheader("1️⃣ 데이터 로딩")

        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_file = st.file_uploader(
                "데이터 파일 선택",
                type=["csv", "xlsx", "json"],
                key="data_loader"
            )

        with col2:
            if st.button("데이터 로드", key="load_btn"):
                if uploaded_file:
                    try:
                        if uploaded_file.name.endswith('.csv'):
                            self.df = pd.read_csv(uploaded_file)
                        elif uploaded_file.name.endswith('.xlsx'):
                            self.df = pd.read_excel(uploaded_file)
                        elif uploaded_file.name.endswith('.json'):
                            self.df = pd.read_json(uploaded_file)

                        st.success(f"데이터 로드 완료: {self.df.shape}")
                    except Exception as e:
                        st.error(f"오류: {e}")

    def render_eda_section(self):
        """탐색적 데이터 분석 섹션"""
        if self.df is not None:
            st.subheader("2️⃣ 탐색적 데이터 분석 (EDA)")

            with st.expander("기본 통계", expanded=True):
                st.dataframe(self.df.describe())

            with st.expander("데이터 타입 및 결측값"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**데이터 타입**")
                    st.dataframe(pd.DataFrame({
                        '컬럼': self.df.columns,
                        '타입': self.df.dtypes
                    }))

                with col2:
                    st.write("**결측값**")
                    missing = pd.DataFrame({
                        '컬럼': self.df.columns,
                        '결측값': self.df.isnull().sum(),
                        '비율(%)': (self.df.isnull().sum() / len(self.df) * 100).round(2)
                    })
                    st.dataframe(missing)

    def render_visualization_section(self):
        """시각화 섹션"""
        if self.df is not None:
            st.subheader("3️⃣ 시각화")

            viz_type = st.selectbox(
                "시각화 타입 선택",
                ["히스토그램", "산점도", "박스플롯", "상관관계 히트맵"]
            )

            numeric_cols = self.df.select_dtypes(include=[np.number]).columns

            if viz_type == "히스토그램":
                column = st.selectbox("컬럼 선택", numeric_cols, key="hist_col")
                bins = st.slider("빈 수", 5, 50, 20)

                fig, ax = plt.subplots(figsize=(10, 5))
                ax.hist(self.df[column], bins=bins, edgecolor='black')
                ax.set_title(f"{column} 분포도")
                st.pyplot(fig)

            elif viz_type == "산점도":
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X축", numeric_cols, key="scatter_x")
                with col2:
                    y_col = st.selectbox("Y축", numeric_cols, key="scatter_y")

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=self.df[x_col],
                    y=self.df[y_col],
                    mode='markers',
                    marker=dict(size=8)
                ))
                fig.update_layout(title=f"{x_col} vs {y_col}")
                st.plotly_chart(fig, use_container_width=True)

            elif viz_type == "상관관계 히트맵":
                import seaborn as sns

                fig, ax = plt.subplots(figsize=(10, 8))
                corr_matrix = self.df[numeric_cols].corr()
                sns.heatmap(corr_matrix, annot=True, fmt='.2f',
                           cmap='coolwarm', center=0, ax=ax)
                st.pyplot(fig)

    def render_analysis_section(self):
        """분석 섹션"""
        if self.df is not None:
            st.subheader("4️⃣ 자동 분석")

            if st.button("자동 분석 실행"):
                with st.spinner("분석 중..."):
                    # 통계 분석
                    numeric_cols = self.df.select_dtypes(include=[np.number]).columns
                    stats_summary = self.df[numeric_cols].describe().to_dict()

                    # 상관관계
                    corr_matrix = self.df[numeric_cols].corr()
                    high_corr_pairs = self._find_high_correlations(corr_matrix)

                    # 결과 표시
                    st.success("분석 완료!")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**높은 상관관계**")
                        st.dataframe(high_corr_pairs)

    def _find_high_correlations(self, corr_matrix, threshold=0.7):
        """높은 상관관계 찾기"""
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > threshold:
                    high_corr.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': round(corr_matrix.iloc[i, j], 3)
                    })

        return pd.DataFrame(high_corr) if high_corr else pd.DataFrame()

    def render(self):
        """전체 대시보드 렌더링"""
        self.render_data_loading_section()
        self.render_eda_section()
        self.render_visualization_section()
        self.render_analysis_section()
```

### 3. 다중 페이지 앱 구조
```python
# app.py - 메인 앱
import streamlit as st

# 페이지 설정
page = st.sidebar.radio(
    "페이지 선택",
    ["📊 개요", "🔍 EDA", "📈 분석", "📑 리포트"]
)

if page == "📊 개요":
    from pages import overview
    overview.run()

elif page == "🔍 EDA":
    from pages import eda
    eda.run()

elif page == "📈 분석":
    from pages import analysis
    analysis.run()

elif page == "📑 리포트":
    from pages import report
    report.run()

# pages/overview.py
import streamlit as st

def run():
    st.title("📊 데이터 분석 시스템 개요")
    st.write("이 앱은 자동 데이터 분석을 수행합니다.")
    # 개요 콘텐츠

# pages/eda.py
import streamlit as st

def run():
    st.title("🔍 탐색적 데이터 분석")
    # EDA 콘텐츠

# pages/analysis.py
import streamlit as st

def run():
    st.title("📈 고급 분석")
    # 분석 콘텐츠

# pages/report.py
import streamlit as st

def run():
    st.title("📑 자동 리포트")
    # 리포트 콘텐츠
```

### 4. 실시간 업데이트 및 세션 관리
```python
# 세션 상태 관리
def initialize_session():
    """세션 상태 초기화"""
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    if 'selected_columns' not in st.session_state:
        st.session_state.selected_columns = []

initialize_session()

# 상태 업데이트
def update_dataframe(df):
    """데이터프레임 업데이트"""
    st.session_state.df = df
    st.rerun()

# 캐싱된 분석 함수
@st.cache_data(ttl=3600)
def run_analysis(data_hash):
    """분석 실행 (캐싱됨)"""
    df = st.session_state.df
    return {
        'stats': df.describe().to_dict(),
        'correlations': df.corr().to_dict()
    }

# 다운로드 기능
def download_results(results_dict, filename="results.json"):
    """결과 다운로드"""
    import json

    json_str = json.dumps(results_dict, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 결과 다운로드",
        data=json_str,
        file_name=filename,
        mime="application/json"
    )
```

## 실습 과제

### Task 1: 기본 대시보드
```python
# 최소 5개 섹션 포함:
# 1. 데이터 로딩
# 2. EDA
# 3. 시각화
# 4. 분석
# 5. 리포트 다운로드
```

### Task 2: 고급 기능
- 다중 파일 업로드
- 실시간 필터링
- 커스텀 분석 옵션
- 결과 캐싱

### Task 3: 다중 페이지 앱
```bash
# 디렉토리 구조
streamlit_app/
├── app.py
├── pages/
│   ├── overview.py
│   ├── eda.py
│   ├── analysis.py
│   └── report.py
└── config.py
```

## 실행 방법
```bash
streamlit run app.py
```

## 주간 체크포인트

- [ ] Streamlit 기본 앱 구축
- [ ] 데이터 로딩 기능
- [ ] EDA 섹션 구현
- [ ] 시각화 대시보드
- [ ] 분석 자동화 통합
- [ ] 세션 상태 관리
- [ ] 다중 페이지 구조
- [ ] 결과 다운로드 기능

## 학습 성과 기준
- [ ] 5개 이상의 기능 페이지 구축
- [ ] 사용성 평가 > 4/5
- [ ] 로딩 시간 < 3초
