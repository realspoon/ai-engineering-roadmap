# Week 29-30: 최적화 (성능, 비용, 보안)

## 학습 목표
- 시스템 성능 최적화
- 비용 효율화
- 보안 강화

## 1. 성능 최적화 (Performance Optimization)

### 1.1 데이터베이스 최적화
```python
# 1. 인덱스 생성
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_transaction_date ON transactions(transaction_date);
CREATE INDEX idx_log_timestamp ON logs(timestamp) WHERE status = 'ERROR';

# 2. 쿼리 최적화
# Before: N+1 Query Problem
for user in users:
    posts = db.query("SELECT * FROM posts WHERE user_id = ?", user.id)

# After: Join
posts = db.query("""
    SELECT u.*, p.* FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
""")

# 3. 배치 처리
# Before
for row in data:
    db.insert("INSERT INTO table VALUES (?)", row)

# After
db.execute_many(
    "INSERT INTO table VALUES (?, ?, ?)",
    data
)

# 4. 연결 풀링 최적화
pool_size = 20  # 동시 연결 수
overflow_size = 10  # 추가 연결 허용
pool_recycle = 3600  # 매 시간 연결 재활용
```

### 1.2 애플리케이션 레벨 최적화
```python
# 1. 캐싱 전략
from functools import lru_cache
import redis

class CacheManager:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379)

    def get_quality_score(self, source_id: str):
        # Redis에서 조회
        cached = self.redis.get(f"quality_score:{source_id}")
        if cached:
            return float(cached)

        # 캐시 미스 - 계산 후 저장
        score = self._calculate_score(source_id)
        self.redis.setex(
            f"quality_score:{source_id}",
            300,  # 5분 TTL
            score
        )
        return score

    def _calculate_score(self, source_id: str) -> float:
        # 실제 계산 로직
        pass

# 2. 배치 처리 및 백그라운드 작업
from celery import Celery

app = Celery('dq_agent')

@app.task(bind=True, max_retries=3)
def assess_data_quality(self, source_id: str):
    try:
        # 시간이 오래 걸리는 작업
        result = perform_assessment(source_id)
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

# 3. 라이브러리 성능 최적화
import numpy as np

def assess_data_vectorized(data):
    """벡터화된 연산으로 성능 향상"""
    # Before: 반복문
    nulls = 0
    for row in data:
        if row['value'] is None:
            nulls += 1

    # After: NumPy 벡터화
    arr = np.array(data)
    nulls = np.isnan(arr).sum()  # 훨씬 빠름
    return nulls

# 4. 메모리 최적화
import pandas as pd

def process_large_data(filename: str):
    """청크 처리로 메모리 효율화"""
    # Before: 전체 파일 로드 (메모리 부족)
    df = pd.read_csv(filename)

    # After: 청크 단위 처리
    chunks = []
    for chunk in pd.read_csv(filename, chunksize=10000):
        result = process_chunk(chunk)
        chunks.append(result)

    final_result = pd.concat(chunks)
    return final_result
```

### 1.3 API 응답 최적화
```python
# 1. Pagination
from fastapi import Query
from pydantic import BaseModel

class PaginationParams(BaseModel):
    skip: int = Query(0, ge=0)
    limit: int = Query(100, le=1000)

@app.get("/results")
async def get_results(params: PaginationParams):
    offset = params.skip
    limit = params.limit

    results = db.query(
        f"SELECT * FROM results OFFSET {offset} LIMIT {limit}"
    )
    return results

# 2. 선택적 필드 반환
@app.get("/results/{source_id}")
async def get_result_detail(
    source_id: str,
    fields: str = Query("id,score,timestamp")
):
    selected_fields = fields.split(",")
    query = f"SELECT {','.join(selected_fields)} FROM results"
    return db.query(query)

# 3. 응답 압축
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)

# 4. CDN 활용 (정적 자산)
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

### 1.4 성능 모니터링
```python
# 1. 성능 메트릭 수집
from prometheus_client import Counter, Histogram, Gauge
import time

request_count = Counter(
    'requests_total',
    'Total requests',
    ['method', 'endpoint']
)

request_duration = Histogram(
    'request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'active_connections',
    'Active database connections'
)

# 2. 미들웨어로 메트릭 수집
@app.middleware("http")
async def track_metrics(request, call_next):
    start_time = time.time()

    request_count.labels(
        method=request.method,
        endpoint=request.url.path
    ).inc()

    response = await call_next(request)

    duration = time.time() - start_time
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response

# 3. 성능 기준 설정
PERFORMANCE_TARGETS = {
    'data_ingestion': 1.0,  # 1초 (1000 records)
    'quality_assessment': 0.5,  # 500ms
    'api_response': 0.2,  # 200ms
    'dashboard_load': 2.0  # 2초
}
```

## 2. 비용 최적화 (Cost Optimization)

### 2.1 인프라 비용 절감
```python
# 1. 자동 스케일링 설정
# Kubernetes HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dq-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dq-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

# 2. 리소스 요청/제한 설정 (pod 당 비용 절감)
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi

# 3. Spot Instances 활용
nodeSelector:
  cloud.google.com/gke-nodepool: spot-pool
  karpenter.sh/capacity-type: spot
```

### 2.2 데이터 저장소 비용 절감
```python
# 1. 데이터 보관 정책 (TTL)
class RetentionPolicy:
    RAW_DATA_RETENTION = 7  # days
    PROCESSED_DATA_RETENTION = 30  # days
    METRICS_RETENTION = 90  # days
    LOGS_RETENTION = 14  # days

# 2. 압축 및 아카이빙
import gzip
import boto3

class DataArchiver:
    def __init__(self):
        self.s3 = boto3.client('s3')

    def archive_old_data(self, days_threshold: int = 30):
        """오래된 데이터 압축 및 아카이빙"""
        for record in get_old_records(days_threshold):
            # 압축
            compressed = gzip.compress(
                json.dumps(record).encode()
            )

            # S3에 아카이빙
            self.s3.put_object(
                Bucket='dq-archive',
                Key=f"archive/{record['id']}.gz",
                Body=compressed
            )

            # 원본 데이터 삭제
            delete_record(record['id'])

# 3. 인덱싱 전략 (스토리지 효율화)
# 자주 사용하는 컬럼에만 인덱스 생성
CREATE INDEX idx_source_id ON results(source_id);
# 복합 인덱스
CREATE INDEX idx_source_timestamp ON results(source_id, timestamp);
```

### 2.3 API 호출 비용 절감
```python
# 1. LLM API 호출 최소화
class SmartLLMValidator:
    def __init__(self):
        self.cache = {}
        self.batch_queue = []

    def validate(self, field: str, value: str):
        """캐시와 배치 활용"""
        # 1. 캐시 확인
        cache_key = f"{field}:{value}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 2. 배치 큐에 추가
        self.batch_queue.append({
            'field': field,
            'value': value,
            'cache_key': cache_key
        })

        # 3. 배치 크기 도달시 한번에 처리
        if len(self.batch_queue) >= 100:
            self.process_batch()

    def process_batch(self):
        """배치 처리로 비용 절감"""
        # 한 번의 API 호출로 100개 항목 처리
        batch_data = self.batch_queue.copy()
        results = call_llm_batch_api(batch_data)

        # 결과 캐싱
        for item, result in zip(batch_data, results):
            self.cache[item['cache_key']] = result

        self.batch_queue.clear()
```

## 3. 보안 강화 (Security Hardening)

### 3.1 인증 및 권한 관리
```python
# 1. JWT 기반 인증
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str
    role: str  # admin, user, viewer

class Settings(BaseModel):
    authjwt_secret_key: str = "secret-key-change-me"

@app.post("/login")
def login(user: User, Authorize: AuthJWT = Depends()):
    # 사용자 검증
    if not verify_password(user.username, user.password):
        raise HTTPException(status_code=401)

    # JWT 토큰 생성
    access_token = Authorize.create_access_token(
        subject=user.username,
        expires_time=3600  # 1시간
    )

    return {"access_token": access_token}

# 2. 역할 기반 접근 제어 (RBAC)
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

def require_role(required_role: Role):
    async def check_role(Authorize: AuthJWT = Depends()):
        Authorize.jwt_required()
        user_role = Authorize.get_jwt_subject()

        if user_role != required_role:
            raise HTTPException(status_code=403)

        return user_role

    return Depends(check_role)

@app.post("/admin/settings")
async def update_settings(
    settings: Settings,
    role: str = require_role(Role.ADMIN)
):
    # 관리자만 접근 가능
    update_system_settings(settings)
```

### 3.2 데이터 보안
```python
# 1. 민감한 데이터 암호화
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())

    def encrypt(self, data: str) -> str:
        """데이터 암호화"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """데이터 복호화"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# 2. 데이터베이스 암호화
# PostgreSQL transparent encryption
ALTER TABLE sensitive_data
    SET (
        fillfactor=70
    );

# 3. 연결 암호화 (TLS/SSL)
connection_string = (
    "postgresql+psycopg2://user:pass@localhost/db"
    "?sslmode=require&sslcert=/path/to/cert"
)

# 4. 감사 로그
class AuditLog:
    def log(self, action: str, user_id: str, details: dict):
        """감사 로그 기록"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user_id': user_id,
            'details': details,
            'ip_address': get_client_ip(),
            'user_agent': get_user_agent()
        }

        db.insert('audit_logs', log_entry)
```

### 3.3 네트워크 보안
```python
# 1. CORS 설정
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://example.com",
        "https://app.example.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600
)

# 2. HTTPS 강제
from fastapi.middleware import trustedhost

app.add_middleware(
    trustedhost.TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)

# 3. 보안 헤더 설정
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    return response

# 4. Rate Limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/results")
@limiter.limit("100/minute")
async def get_results(request: Request):
    pass
```

## 4. 보안 감사 체크리스트

### 4.1 애플리케이션 보안
- [ ] OWASP Top 10 취약점 검토
- [ ] 의존성 보안 스캔
- [ ] 코드 정적 분석
- [ ] 침투 테스트

### 4.2 인프라 보안
- [ ] 네트워크 정책 검토
- [ ] IAM 권한 최소화
- [ ] 암호화 설정 확인
- [ ] 방화벽 규칙 검토

### 4.3 데이터 보안
- [ ] 데이터 분류
- [ ] 암호화 적용
- [ ] 접근 제어
- [ ] 감사 로그

## 5. 성능 벤치마크

### 5.1 최적화 전후 비교
```
작업                 최적화 전    최적화 후    개선율
────────────────────────────────────────────────
데이터 수집         2.5s        0.8s        68%
품질 평가           1.2s        0.3s        75%
API 응답            800ms       150ms       81%
대시보드 로드       5s          1.5s        70%
메모리 사용         512MB       256MB       50%
```

## 6. 체크리스트

### 6.1 Week 29 완료 조건
- [ ] 성능 목표 달성
- [ ] 성능 모니터링 구현
- [ ] 주요 최적화 완료

### 6.2 Week 30 완료 조건
- [ ] 보안 감사 완료
- [ ] 보안 개선 사항 적용
- [ ] 비용 최적화 계획 수립

## 7. 참고 자료

- PostgreSQL 성능 튜닝 가이드
- OWASP Top 10
- Kubernetes 성능 최적화
- AWS Well-Architected Framework
