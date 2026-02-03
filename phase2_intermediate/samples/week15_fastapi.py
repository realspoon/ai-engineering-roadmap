"""
Week 15: FastAPI Agent Server and Docker Configuration
FastAPI를 사용한 에이전트 서버 구축 및 Docker 설정
"""

import json
import uuid
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import asyncio


# Pydantic 모델 대신 dataclass 사용 (의존성 최소화)
@dataclass
class Message:
    """메시지 모델"""
    id: str
    content: str
    role: str  # user, assistant, system
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentRequest:
    """에이전트 요청"""
    user_id: str
    query: str
    session_id: Optional[str] = None
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.session_id is None:
            self.session_id = str(uuid.uuid4())
        if self.parameters is None:
            self.parameters = {}


@dataclass
class AgentResponse:
    """에이전트 응답"""
    request_id: str
    session_id: str
    query: str
    response: str
    status: str
    execution_time: float
    metadata: Dict[str, Any] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HealthStatus:
    """헬스 체크 상태"""
    status: str
    version: str
    timestamp: str
    database: str = "connected"
    cache: str = "available"
    services: Dict[str, str] = None

    def __post_init__(self):
        if self.services is None:
            self.services = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Agent:
    """간단한 에이전트 구현"""

    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.conversations: Dict[str, List[Message]] = {}
        self.state: Dict[str, Any] = {}

    async def process(self, request: AgentRequest) -> str:
        """요청 처리"""
        session_id = request.session_id

        # 세션이 없으면 생성
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        # 사용자 메시지 추가
        user_message = Message(
            id=str(uuid.uuid4()),
            content=request.query,
            role="user"
        )
        self.conversations[session_id].append(user_message)

        # 간단한 에이전트 응답 생성 (실제로는 LLM 호출)
        await asyncio.sleep(0.1)  # 처리 시뮬레이션

        response_text = f"질문 '{request.query}'에 대한 응답입니다. (Session: {session_id[:8]}...)"

        # 어시스턴트 메시지 추가
        assistant_message = Message(
            id=str(uuid.uuid4()),
            content=response_text,
            role="assistant"
        )
        self.conversations[session_id].append(assistant_message)

        return response_text

    def get_conversation(self, session_id: str) -> List[Message]:
        """대화 히스토리 조회"""
        return self.conversations.get(session_id, [])

    def clear_conversation(self, session_id: str) -> bool:
        """대화 히스토리 삭제"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        return False


class FastAPIAgentServer:
    """FastAPI 에이전트 서버"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.app_name = "AI Agent API Server"
        self.version = "1.0.0"
        self.agent = Agent()
        self.request_count = 0
        self.start_time = datetime.now()

    def create_app(self):
        """FastAPI 앱 생성 (모의 구현)"""
        routes = {
            "health": "/health",
            "chat": "/api/v1/chat",
            "history": "/api/v1/history",
            "clear": "/api/v1/clear",
            "info": "/api/v1/info"
        }
        return {
            "app_name": self.app_name,
            "version": self.version,
            "routes": routes
        }

    async def health_check(self) -> HealthStatus:
        """헬스 체크"""
        uptime = (datetime.now() - self.start_time).total_seconds()

        return HealthStatus(
            status="healthy",
            version=self.version,
            timestamp=datetime.now().isoformat(),
            database="connected",
            cache="available",
            services={
                "agent": "running",
                "uptime_seconds": uptime,
                "requests_processed": self.request_count
            }
        )

    async def process_chat(self, request: AgentRequest) -> AgentResponse:
        """채팅 요청 처리"""
        import time

        self.request_count += 1
        request_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # 에이전트 처리
            response_text = await self.agent.process(request)
            execution_time = (time.time() - start_time) * 1000  # 밀리초

            return AgentResponse(
                request_id=request_id,
                session_id=request.session_id,
                query=request.query,
                response=response_text,
                status="success",
                execution_time=execution_time,
                metadata={
                    "user_id": request.user_id,
                    "agent_id": self.agent.agent_id,
                    "conversation_length": len(self.agent.get_conversation(request.session_id))
                }
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            return AgentResponse(
                request_id=request_id,
                session_id=request.session_id,
                query=request.query,
                response=str(e),
                status="error",
                execution_time=execution_time,
                metadata={"error": str(e)}
            )

    async def get_conversation_history(self, session_id: str) -> Dict[str, Any]:
        """대화 히스토리 조회"""
        messages = self.agent.get_conversation(session_id)

        return {
            "session_id": session_id,
            "message_count": len(messages),
            "messages": [msg.to_dict() for msg in messages]
        }

    async def clear_session(self, session_id: str) -> Dict[str, Any]:
        """세션 초기화"""
        success = self.agent.clear_conversation(session_id)

        return {
            "session_id": session_id,
            "cleared": success,
            "timestamp": datetime.now().isoformat()
        }

    def get_info(self) -> Dict[str, Any]:
        """서버 정보"""
        return {
            "app_name": self.app_name,
            "version": self.version,
            "host": self.host,
            "port": self.port,
            "agent_id": self.agent.agent_id,
            "requests_processed": self.request_count,
            "started_at": self.start_time.isoformat()
        }


class DockerConfig:
    """Docker 설정"""

    DOCKERFILE = """FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 애플리케이션 실행
CMD ["uvicorn", "week15_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    DOCKER_COMPOSE = """version: '3.8'

services:
  agent-api:
    build: .
    container_name: ai-agent-api
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - DB_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - agent-network

  postgres:
    image: postgres:15-alpine
    container_name: agent-db
    environment:
      POSTGRES_USER: agent_user
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: agent_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - agent-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: agent-cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - agent-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  agent-network:
    driver: bridge
"""

    REQUIREMENTS = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
aioredis==2.0.1
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic-settings==2.1.0
python-dotenv==1.0.0
requests==2.31.0
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
"""

    ENV_EXAMPLE = """# 환경 설정
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# 서버 설정
HOST=0.0.0.0
PORT=8000
WORKERS=4

# 데이터베이스
DB_HOST=localhost
DB_PORT=5432
DB_USER=agent_user
DB_PASSWORD=secure_password
DB_NAME=agent_db

# 캐시
REDIS_HOST=localhost
REDIS_PORT=6379

# API 설정
API_TITLE=AI Agent API
API_VERSION=1.0.0
API_DESCRIPTION=FastAPI로 구현된 AI 에이전트 서버

# 보안
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""

    @staticmethod
    def generate_files(output_dir: str = "./") -> Dict[str, str]:
        """Docker 관련 파일 생성"""
        files = {
            "Dockerfile": DockerConfig.DOCKERFILE,
            "docker-compose.yml": DockerConfig.DOCKER_COMPOSE,
            "requirements.txt": DockerConfig.REQUIREMENTS,
            ".env.example": DockerConfig.ENV_EXAMPLE
        }
        return files


async def demo_server():
    """서버 데모"""
    server = FastAPIAgentServer()

    print("="*60)
    print("FastAPI Agent Server 데모")
    print("="*60)

    # 앱 정보
    print("\n[서버 정보]")
    info = server.get_info()
    print(json.dumps(info, ensure_ascii=False, indent=2))

    # 헬스 체크
    print("\n[헬스 체크]")
    health = await server.health_check()
    print(json.dumps(health.to_dict(), ensure_ascii=False, indent=2))

    # 채팅 요청 처리
    print("\n[채팅 요청 처리]")
    request1 = AgentRequest(
        user_id="user_123",
        query="안녕하세요, 당신은 누구입니까?",
        parameters={"temperature": 0.7}
    )

    response1 = await server.process_chat(request1)
    print(f"요청: {response1.query}")
    print(f"응답: {response1.response}")
    print(f"상태: {response1.status}")
    print(f"실행 시간: {response1.execution_time:.2f}ms")

    # 같은 세션에서 두 번째 요청
    print("\n[같은 세션 내 두 번째 요청]")
    request2 = AgentRequest(
        user_id="user_123",
        query="앞서 말한 내용을 기억하나요?",
        session_id=response1.session_id
    )

    response2 = await server.process_chat(request2)
    print(f"요청: {response2.query}")
    print(f"응답: {response2.response}")

    # 대화 히스토리 조회
    print("\n[대화 히스토리]")
    history = await server.get_conversation_history(response1.session_id)
    print(f"세션 ID: {history['session_id']}")
    print(f"메시지 수: {history['message_count']}")
    for msg in history['messages']:
        print(f"  [{msg['role']}] {msg['content'][:50]}...")

    # Docker 파일 생성
    print("\n[Docker 파일]")
    docker_files = DockerConfig.generate_files()
    for filename, content in docker_files.items():
        print(f"\n{filename}:")
        print(content[:300] + "...")

    # 요청 통계
    print("\n[서버 통계]")
    print(f"처리된 요청: {server.request_count}")
    uptime = (datetime.now() - server.start_time).total_seconds()
    print(f"실행 시간: {uptime:.2f}초")


def main():
    """메인 함수"""
    asyncio.run(demo_server())


if __name__ == "__main__":
    main()
