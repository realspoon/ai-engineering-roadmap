# Week 15: 배포와 운영

## 🎯 학습 목표

1. FastAPI를 사용한 API 개발
2. Docker를 이용한 컨테이너화
3. 클라우드 배포 전략
4. 모니터링 및 로깅 설정

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Building Web APIs with FastAPI](https://www.oreilly.com/library/view/building-web-apis/9781098135492/) | Sebastián Ramírez | Chapter 1-8 |
| 📚 Book | [Docker in Practice](https://www.oreilly.com/library/view/docker-in-practice/9781617294488/) | Ian Miell, Aidan Hobson Sayers | Chapter 1-5 |

---

## 📖 핵심 개념

### 1. FastAPI 기초

FastAPI는 **현대적이고 고성능인 파이썬 웹 프레임워크**입니다.

**특징:**
- 자동 API 문서 (Swagger UI)
- 비동기 (async/await) 기본 지원
- 유형 힌트를 통한 자동 검증
- 빠른 개발 속도

**기본 구조:**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(
    title="LLM Application API",
    description="LLM 기반 애플리케이션",
    version="1.0.0"
)

# 1. 요청 모델 정의
class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7

# 2. 응답 모델 정의
class GenerateResponse(BaseModel):
    result: str
    tokens_used: int
    latency_ms: float

# 3. API 엔드포인트 정의
@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    """LLM으로 텍스트 생성"""
    try:
        import time
        start = time.time()

        result = await llm.agenerate(request.prompt)
        tokens_used = estimate_tokens(result)

        latency = (time.time() - start) * 1000

        return GenerateResponse(
            result=result,
            tokens_used=tokens_used,
            latency_ms=latency
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {"status": "healthy"}

# 5. 실행
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Docker 컨테이너화

**Dockerfile 작성:**

```dockerfile
# 1단계: 베이스 이미지
FROM python:3.11-slim

# 2단계: 작업 디렉토리 설정
WORKDIR /app

# 3단계: 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4단계: Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5단계: 애플리케이션 코드 복사
COPY . .

# 6단계: 포트 노출
EXPOSE 8000

# 7단계: 헬스 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 8단계: 실행 명령어
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  # LLM API 서비스
  llm-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres

  # 캐시 서버
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # 데이터베이스
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=llm_app
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  redis_data:
  postgres_data:
```

### 3. 클라우드 배포

**AWS ECS 배포:**

```python
# AWS ECS Task Definition (JSON)
{
  "family": "llm-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "llm-api",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/llm-app:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/llm-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Kubernetes 배포:**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-app
  labels:
    app: llm-app

spec:
  replicas: 3  # 3개 Pod 실행

  selector:
    matchLabels:
      app: llm-app

  template:
    metadata:
      labels:
        app: llm-app

    spec:
      containers:
      - name: llm-api
        image: llm-app:latest
        ports:
        - containerPort: 8000

        # 자원 요청
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"

        # 환경 변수
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secrets
              key: openai-api-key

        # 헬스 체크
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: llm-app-service

spec:
  type: LoadBalancer
  selector:
    app: llm-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

### 4. 모니터링 및 로깅

**로깅 설정:**

```python
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON 형식의 구조화된 로그"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 파일 핸들러
file_handler = RotatingFileHandler(
    "app.log",
    maxBytes=10_000_000,  # 10MB
    backupCount=10
)
file_handler.setFormatter(JSONFormatter())

# 콘솔 핸들러
console_handler = logging.StreamHandler()
console_handler.setFormatter(JSONFormatter())

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 사용 예
logger.info("애플리케이션 시작", extra={"version": "1.0.0"})
```

**메트릭 수집:**

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# 메트릭 정의
request_count = Counter(
    'llm_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_latency = Histogram(
    'llm_request_latency_seconds',
    'Request latency',
    ['endpoint']
)

active_requests = Gauge(
    'llm_active_requests',
    'Active requests'
)

# 미들웨어로 메트릭 수집
from fastapi import Request

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    active_requests.inc()

    start = time.time()
    response = await call_next(request)
    latency = time.time() - start

    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    request_latency.labels(endpoint=request.url.path).observe(latency)

    active_requests.dec()

    return response

# Prometheus 엔드포인트
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

@app.get("/metrics")
async def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
```

---

## 💻 실습 과제

### 과제 1: FastAPI 애플리케이션 개발

```python
# 요구사항:
# 1. 최소 3개의 엔드포인트 구현
# 2. 요청/응답 모델 정의
# 3. 입력 검증 및 에러 처리
# 4. Swagger UI 자동 생성

# 엔드포인트:
# - POST /api/generate (텍스트 생성)
# - GET /api/history (생성 이력)
# - DELETE /api/cache (캐시 초기화)
# - GET /health (헬스 체크)
```

### 과제 2: Docker 컨테이너화

```dockerfile
# 요구사항:
# 1. Dockerfile 작성
# 2. 멀티스테이지 빌드 (선택)
# 3. 의존성 최소화
# 4. 보안 고려 (non-root 사용자)
# 5. 헬스 체크 포함

# 검증:
# docker build -t llm-app:1.0 .
# docker run -p 8000:8000 llm-app:1.0
```

### 과제 3: docker-compose 설정

```yaml
# 요구사항:
# 1. API 서비스
# 2. Redis (캐시)
# 3. PostgreSQL (데이터베이스)
# 4. 서비스 간 네트워크 연결
# 5. 볼륨 마운팅

# 테스트:
# docker-compose up
# curl http://localhost:8000/health
```

### 과제 4: 클라우드 배포 설정

```python
# 옵션 1: AWS ECS
# - ECR 저장소 생성
# - Task Definition 작성
# - ECS 클러스터 배포

# 옵션 2: Kubernetes
# - Deployment YAML 작성
# - Service 설정
# - Ingress 구성 (선택)

# 테스트 항목:
# - 롤링 업데이트
# - Pod 자동 복구
# - 리소스 제한 확인
```

### 과제 5: 모니터링 설정

```python
# 요구사항:
# 1. 구조화된 로깅 구현
# 2. Prometheus 메트릭 수집
# 3. Grafana 대시보드 설계
# 4. 알림 규칙 정의

# 수집할 메트릭:
# - 요청 수 및 성공률
# - 응답 시간 분포
# - 에러율 및 유형
# - 리소스 사용률 (CPU, 메모리)
# - 토큰 사용량
```

---

## 📝 주요 패턴

### 패턴 1: Basic FastAPI App

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/endpoint")
async def endpoint(request: Request) -> Response:
    return Response(...)
```

### 패턴 2: Middleware

```python
@app.middleware("http")
async def middleware(request: Request, call_next):
    # 요청 처리 전
    response = await call_next(request)
    # 응답 처리 후
    return response
```

### 패턴 3: 의존성 주입

```python
async def get_db():
    db = Database()
    try:
        yield db
    finally:
        await db.close()

@app.get("/api/data")
async def get_data(db: Database = Depends(get_db)):
    return await db.query()
```

### 패턴 4: 배경 작업

```python
from fastapi import BackgroundTasks

@app.post("/api/task")
async def create_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(long_running_task)
    return {"status": "processing"}
```

---

## ✅ 주간 체크포인트

```
□ FastAPI 기본 구조 이해 및 구현 가능
□ 비동기 처리 (async/await) 이해
□ Pydantic 모델로 요청/응답 정의 가능
□ Docker 기본 개념 이해 및 Dockerfile 작성 가능
□ docker-compose로 멀티 컨테이너 관리 가능
□ 클라우드 배포 (AWS/K8s) 기본 이해
□ 구조화된 로깅 구현 가능
□ Prometheus 메트릭 수집 가능
□ 헬스 체크 및 모니터링 엔드포인트 구현 가능
```

---

## 🔗 추가 리소스

- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [Docker Official Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Prometheus Monitoring](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

---

[← Week 14](./week14_evaluation.md) | [Week 16 →](./week16_integration.md)
