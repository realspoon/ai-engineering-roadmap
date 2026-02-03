# Week 27-28: 핵심 기능 개발 (MVP 구현)

## 학습 목표
- MVP (Minimum Viable Product) 기능 개발
- 통합 테스트 수행
- 개발 환경에서의 end-to-end 검증

## 1. MVP 범위 정의

### 1.1 MVP 기능 (최소 기능 집합)
```
필수 기능:
  ✓ 단일 데이터 소스 연결 (PostgreSQL)
  ✓ 기본 품질 평가 (5가지 차원)
  ✓ 이상 탐지 (통계 기반)
  ✓ 기본 리포트 생성
  ✓ 대시보드 (Streamlit)
  ✓ 이메일 알림

선택 기능 (Stretch):
  - 다중 소스 지원
  - LLM 검증
  - 자동 수정
  - Slack 알림
```

### 1.2 MVP 아키텍처 (단순화)
```
┌────────────────────────────────────┐
│    Streamlit Dashboard              │
└────────────────────────────────────┘
            ↓
┌────────────────────────────────────┐
│    FastAPI Server                   │
│  - Data Ingestion                   │
│  - Quality Assessment               │
│  - Report Generation                │
└────────────────────────────────────┘
            ↓
┌────────────────────────────────────┐
│    PostgreSQL                        │
│  - Raw data storage                 │
│  - Metadata                          │
│  - Results                           │
└────────────────────────────────────┘
```

## 2. 개발 스프린트 계획

### 2.1 Week 27 - 기본 구조 및 데이터 수집
```
Day 1-2: 프로젝트 구조 생성
  - src/main.py (entry point)
  - src/api/main.py (FastAPI app)
  - src/config/ (설정)
  - src/models/ (데이터 모델)

Day 3-4: 데이터 수집 레이어
  - PostgreSQL 커넥터
  - 커넥션 풀 관리
  - 에러 핸들링

Day 5: 단위 테스트
  - 커넥터 테스트
  - 헬스 체크
```

### 2.2 Week 28 - 품질 평가 및 리포팅
```
Day 1-2: 품질 평가 엔진
  - 5가지 차원 구현
  - 점수 계산
  - 결과 저장

Day 3-4: 대시보드 개발
  - Streamlit UI
  - 실시간 업데이트
  - 그래프 시각화

Day 5: 통합 테스트 및 최적화
  - End-to-end 테스트
  - 성능 최적화
```

## 3. Week 27 상세 구현

### 3.1 프로젝트 초기 구조
```python
# src/main.py
import asyncio
from src.api.server import create_app
from src.config import Config

async def main():
    config = Config.from_env()
    app = create_app(config)

    # 애플리케이션 초기화
    await app.startup()

    # 서버 시작
    import uvicorn
    await uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000
    )

if __name__ == '__main__':
    asyncio.run(main())
```

### 3.2 데이터 모델 정의
```python
# src/models/data.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DataSource(BaseModel):
    """데이터 소스 정의"""
    id: str
    name: str
    source_type: str  # postgresql, mysql, api, file
    connection_string: str
    schema_def: Optional[Dict[str, Any]]
    refresh_interval: int = 3600  # 초 단위

class QualityResult(BaseModel):
    """품질 평가 결과"""
    source_id: str
    quality_score: float
    accuracy: float
    completeness: float
    consistency: float
    timeliness: float
    validity: float
    uniqueness: float
    issues_found: int
    anomalies_found: int
    timestamp: datetime
    report_url: Optional[str]
```

### 3.3 PostgreSQL 커넥터 구현
```python
# src/connectors/postgres.py
import asyncpg
from typing import List, Dict, Any
import logging

class PostgresConnector:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        """커넥션 풀 생성"""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=10,
                max_size=20,
                command_timeout=60
            )
            self.logger.info("PostgreSQL connection pool created")
        except Exception as e:
            self.logger.error(f"Failed to create connection pool: {e}")
            raise

    async def disconnect(self):
        """커넥션 풀 종료"""
        if self.pool:
            await self.pool.close()
            self.logger.info("PostgreSQL connection pool closed")

    async def fetch_data(self, query: str, limit: int = None) -> List[Dict]:
        """데이터 조회"""
        if not self.pool:
            raise RuntimeError("Not connected to database")

        async with self.pool.acquire() as connection:
            try:
                if limit:
                    query = f"{query} LIMIT {limit}"

                rows = await connection.fetch(query)
                return [dict(row) for row in rows]

            except Exception as e:
                self.logger.error(f"Query execution failed: {e}")
                raise

    async def get_schema(self, table_name: str) -> Dict[str, str]:
        """테이블 스키마 조회"""
        query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = $1
            ORDER BY ordinal_position
        """

        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, table_name)
            return {row['column_name']: row['data_type'] for row in rows}
```

### 3.4 품질 평가 엔진 (단순 버전)
```python
# src/quality/assessor.py
import numpy as np
import pandas as pd
from typing import Dict, List, Any

class QualityAssessor:
    def __init__(self):
        self.weights = {
            'accuracy': 0.25,
            'completeness': 0.25,
            'consistency': 0.20,
            'timeliness': 0.15,
            'validity': 0.15
        }

    def assess(self, data: List[Dict]) -> Dict[str, Any]:
        """데이터 품질 평가"""
        df = pd.DataFrame(data)

        scores = {
            'accuracy': self._assess_accuracy(df),
            'completeness': self._assess_completeness(df),
            'consistency': self._assess_consistency(df),
            'timeliness': self._assess_timeliness(df),
            'validity': self._assess_validity(df)
        }

        # 가중 점수 계산
        overall_score = sum(
            scores[metric] * self.weights[metric]
            for metric in self.weights.keys()
        )

        return {
            'scores': scores,
            'overall_score': overall_score,
            'passed': overall_score >= 80
        }

    def _assess_accuracy(self, df: pd.DataFrame) -> float:
        """정확성 평가"""
        # 간단한 구현: 숫자형 컬럼의 범위 확인
        accuracy_score = 100
        for col in df.select_dtypes(include=[np.number]):
            outliers = len(df[
                (df[col] < df[col].quantile(0.01)) |
                (df[col] > df[col].quantile(0.99))
            ])
            if len(df) > 0:
                accuracy_score -= (outliers / len(df)) * 20
        return max(0, accuracy_score)

    def _assess_completeness(self, df: pd.DataFrame) -> float:
        """완전성 평가"""
        if len(df) == 0:
            return 0

        total_cells = len(df) * len(df.columns)
        null_cells = df.isnull().sum().sum()
        return 100 * (1 - null_cells / total_cells)

    def _assess_consistency(self, df: pd.DataFrame) -> float:
        """일관성 평가"""
        # 각 컬럼의 데이터 타입이 일관적인지 확인
        if len(df) == 0:
            return 100

        consistency = 100
        for col in df.columns:
            unique_types = df[col].apply(type).nunique()
            if unique_types > 1:
                consistency -= 10  # 각 혼합 타입당 10점 감소

        return max(0, consistency)

    def _assess_timeliness(self, df: pd.DataFrame) -> float:
        """적시성 평가"""
        # 간단한 구현: timestamp 컬럼 확인
        if 'timestamp' in df.columns or 'created_at' in df.columns:
            return 100
        return 50

    def _assess_validity(self, df: pd.DataFrame) -> float:
        """유효성 평가"""
        # 기본 유효성 검사
        validity = 100

        for col in df.select_dtypes(include=['object']):
            empty = (df[col] == '') | (df[col] == 'null')
            if empty.any():
                validity -= 10

        return max(0, validity)
```

## 4. Week 28 상세 구현

### 4.1 FastAPI 서버 구현
```python
# src/api/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.api.routes import router
from src.config import Config
from src.database import Database
import logging

def create_app(config: Config) -> FastAPI:
    app = FastAPI(
        title="Data Quality Agent",
        version="1.0.0",
        description="Comprehensive Data Quality Management System"
    )

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 의존성 주입
    @app.on_event("startup")
    async def startup():
        app.db = Database(config)
        await app.db.connect()
        logging.info("Application startup complete")

    @app.on_event("shutdown")
    async def shutdown():
        await app.db.disconnect()
        logging.info("Application shutdown complete")

    # 라우트 등록
    app.include_router(router, prefix="/api/v1")

    # 헬스 체크
    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app
```

### 4.2 API 라우트 구현
```python
# src/api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.models.data import DataSource, QualityResult
from src.services.quality import QualityService

router = APIRouter()
quality_service = QualityService()

@router.post("/assess")
async def assess_data(source: DataSource) -> QualityResult:
    """
    데이터 품질 평가 수행
    """
    try:
        result = await quality_service.assess(source)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{source_id}")
async def get_results(source_id: str) -> List[QualityResult]:
    """
    특정 소스의 평가 결과 조회
    """
    results = await quality_service.get_results(source_id)
    return results

@router.post("/schedule")
async def schedule_assessment(source: DataSource, interval: int):
    """
    정기적 평가 스케줄링
    """
    await quality_service.schedule(source, interval)
    return {"status": "scheduled"}
```

### 4.3 Streamlit 대시보드
```python
# src/dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

st.set_page_config(
    page_title="Data Quality Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Data Quality Agent Dashboard")

# API 기본 URL
API_URL = st.secrets.get("API_URL", "http://localhost:8000/api/v1")

# 사이드바
with st.sidebar:
    st.header("Configuration")
    selected_source = st.selectbox(
        "Select Data Source",
        ["source_1", "source_2", "source_3"]
    )
    refresh_interval = st.slider(
        "Refresh Interval (seconds)",
        min_value=5,
        max_value=300,
        value=30,
        step=5
    )

# 메인 콘텐츠
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Overall Quality Score",
        value="92.5%",
        delta="+2.1%"
    )

with col2:
    st.metric(
        label="Issues Found",
        value="12",
        delta="-3"
    )

with col3:
    st.metric(
        label="Data Records",
        value="50,235",
        delta="+1,245"
    )

with col4:
    st.metric(
        label="Last Updated",
        value=datetime.now().strftime("%H:%M:%S"),
        delta="2 mins ago"
    )

# 차트
st.header("Quality Metrics")
col1, col2 = st.columns(2)

with col1:
    # 품질 차원별 점수
    dimensions = ["Accuracy", "Completeness", "Consistency", "Timeliness", "Validity"]
    scores = [95, 88, 92, 85, 90]

    fig = go.Figure(data=go.Scatterpolar(
        r=scores,
        theta=dimensions,
        fill='toself'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    # 시간별 품질 점수
    times = pd.date_range(end=datetime.now(), periods=24, freq='H')
    quality_scores = [85 + i*0.5 for i in range(24)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=quality_scores,
        mode='lines+markers',
        name='Quality Score'
    ))

    fig.update_layout(
        title="Quality Score Trend (24H)",
        xaxis_title="Time",
        yaxis_title="Score (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

# 이슈 테이블
st.header("Detected Issues")
issues_data = {
    "Timestamp": ["2024-01-15 10:30", "2024-01-15 10:15", "2024-01-15 10:00"],
    "Type": ["NULL_VALUE", "INVALID_FORMAT", "DUPLICATE"],
    "Field": ["email", "phone", "user_id"],
    "Severity": ["WARNING", "INFO", "WARNING"],
    "Records Affected": [5, 2, 8]
}

issues_df = pd.DataFrame(issues_data)
st.dataframe(issues_df, use_container_width=True)
```

## 5. 통합 테스트

### 5.1 End-to-End 테스트
```python
# tests/integration/test_e2e.py
import pytest
import asyncio
from src.api.server import create_app
from src.config import Config
from src.models.data import DataSource

@pytest.fixture
async def app():
    config = Config.from_env()
    return create_app(config)

@pytest.mark.asyncio
async def test_full_pipeline(app):
    """End-to-end 파이프라인 테스트"""
    # 1. 데이터 소스 생성
    source = DataSource(
        id="test_source",
        name="Test Source",
        source_type="postgresql",
        connection_string="postgresql://user:pass@localhost/testdb",
        schema_def={
            "id": "integer",
            "email": "text",
            "age": "integer"
        }
    )

    # 2. 품질 평가 수행
    client = app.test_client()

    response = await client.post(
        "/api/v1/assess",
        json=source.dict()
    )

    assert response.status_code == 200
    result = response.json()

    # 3. 결과 검증
    assert "overall_score" in result
    assert 0 <= result["overall_score"] <= 100

    # 4. 결과 조회
    response = await client.get(
        f"/api/v1/results/{source.id}"
    )

    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
```

## 6. 성능 검증

### 6.1 성능 테스트
```python
# tests/performance/test_performance.py
import time
import pytest

def test_data_ingestion_performance():
    """데이터 수집 성능 테스트"""
    # 1000 행 처리 시간 측정
    from src.connectors.postgres import PostgresConnector

    connector = PostgresConnector("postgresql://localhost/testdb")

    start = time.time()
    data = connector.fetch_data(
        "SELECT * FROM large_table",
        limit=1000
    )
    elapsed = time.time() - start

    assert elapsed < 1.0  # 1초 이내
    assert len(data) == 1000

def test_quality_assessment_performance():
    """품질 평가 성능 테스트"""
    from src.quality.assessor import QualityAssessor
    import pandas as pd

    assessor = QualityAssessor()
    df = pd.DataFrame({
        'id': range(10000),
        'value': range(10000),
        'timestamp': pd.date_range('2024-01-01', periods=10000)
    })

    start = time.time()
    result = assessor.assess(df.to_dict('records'))
    elapsed = time.time() - start

    assert elapsed < 0.5  # 500ms 이내
    assert result['overall_score'] > 0
```

## 7. 배포 준비

### 7.1 Docker 이미지 빌드
```bash
docker build -t dq-agent:1.0.0 .
docker run -p 8000:8000 dq-agent:1.0.0
```

### 7.2 로컬 테스트
```bash
# 데이터베이스 시작
docker-compose up -d

# 애플리케이션 시작
python -m uvicorn src.api.server:app --reload

# 대시보드 시작
streamlit run src/dashboard/app.py

# 테스트 실행
pytest tests/ -v --cov=src
```

## 8. 체크리스트

### 8.1 Week 27 완료 조건
- [ ] 프로젝트 구조 생성
- [ ] PostgreSQL 커넥터 구현
- [ ] 커넥터 테스트 통과

### 8.2 Week 28 완료 조건
- [ ] 품질 평가 엔진 완성
- [ ] FastAPI 서버 동작
- [ ] Streamlit 대시보드 동작
- [ ] End-to-end 테스트 통과
- [ ] 성능 기준 달성

## 9. 주요 학습 포인트

- FastAPI 비동기 프로그래밍
- Pandas 데이터 처리
- Streamlit 대시보드 개발
- 통합 테스트 작성
- Docker 컨테이너화

## 10. 참고 자료

- FastAPI 공식 문서
- Streamlit 갤러리
- Pandas 데이터 처리 가이드
- PostgreSQL 드라이버 (asyncpg)
