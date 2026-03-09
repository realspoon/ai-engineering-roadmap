# Week 2: Python 환경 구축 및 공유 (uv) + Dify 설정

## 🎯 학습 목표

1. uv로 재현 가능한 Python 환경 구축
2. `uv.lock`을 활용한 팀 환경 공유
3. Dify 로컬 환경 구축 (Docker)
4. API 키 및 환경변수 관리

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Python for Data Analysis, 3rd Ed](https://www.oreilly.com/library/view/python-for-data/9781098104023/) | Wes McKinney | Chapter 1-2 |
| 📚 Book | [Fluent Python, 2nd Ed](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) | Luciano Ramalho | Chapter 1-2 |

---

## 📖 핵심 개념

### 왜 uv인가?

기존 방식(`venv` + `pip`)의 문제점:
- `pip install` 결과가 실행 시점마다 달라질 수 있음
- `requirements.txt`는 의존성 트리를 완전히 잠그지 못함
- Python 버전 자체를 팀 전체가 맞추기 어려움

`uv`가 해결하는 것:
- **`uv.lock`**: 패키지 버전과 해시를 완전히 잠금 → 누가 언제 설치해도 동일한 환경
- **`.python-version`**: 프로젝트에 사용할 Python 버전을 파일로 고정
- **`uv sync`**: 명령 하나로 잠금 파일 기준의 환경 완전 재현

---

### 1. uv 설치

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 설치 확인
uv --version
```

### 2. 프로젝트 생성 및 Python 버전 고정

```bash
uv init my_ai_project
cd my_ai_project

# Python 버전을 파일로 고정 (.python-version 생성)
uv python pin 3.12
```

`.python-version` 파일이 git에 포함되어 팀원 모두가 동일한 Python 버전을 사용합니다.

### 3. 패키지 추가 및 잠금

```bash
# 패키지 추가 → pyproject.toml 업데이트 + uv.lock 자동 갱신
uv add langchain langchain-openai anthropic openai python-dotenv

# 개발 전용 패키지
uv add --dev jupyter pytest
```

`uv.lock`은 모든 의존성의 정확한 버전과 해시를 기록합니다. **반드시 git에 커밋**해야 합니다.

### 4. 환경 공유 및 재현 (핵심)

프로젝트를 받은 팀원이 해야 할 일:

```bash
git clone <repo-url>
cd my_ai_project

# uv.lock 기준으로 완전히 동일한 환경 구성 (명령 하나로 끝)
uv sync
```

`uv sync`는 다음을 자동으로 처리합니다:
- `.python-version`에 지정된 Python 설치
- `.venv` 가상환경 생성
- `uv.lock`에 명시된 패키지를 정확한 버전으로 설치

### 5. 가상환경 활성화 없이 실행

```bash
# 가상환경 활성화 없이 바로 실행
uv run python src/main.py
uv run jupyter lab
uv run pytest
```

### 6. 프로젝트 구조

```
my_ai_project/
├── .env                 # API 키 (git 제외 — .gitignore에 추가)
├── .gitignore
├── .python-version      # Python 버전 고정 (git 포함)
├── pyproject.toml       # 프로젝트 메타데이터 및 의존성 선언
├── uv.lock              # 의존성 완전 잠금 파일 (git 포함)
├── src/
│   ├── __init__.py
│   └── main.py
├── notebooks/
│   └── exploration.ipynb
└── tests/
    └── test_main.py
```

**git에 꼭 포함해야 할 파일**: `.python-version`, `pyproject.toml`, `uv.lock`
**git에서 제외할 파일**: `.env`, `.venv/`

### 7. pyproject.toml 예시

```toml
[project]
name = "my-ai-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "langchain>=0.2.0",
    "langchain-openai>=0.1.0",
    "anthropic>=0.20.0",
    "openai>=1.0.0",
    "python-dotenv>=1.0.0",
]

[tool.uv]
dev-dependencies = [
    "jupyter>=1.0.0",
    "pytest>=8.0.0",
]
```

---

## 🚀 Dify 환경 구축

### Dify란?

Dify는 LLM 기반 앱을 빠르게 개발·배포할 수 있는 오픈소스 플랫폼입니다. RAG 파이프라인, Agent, 워크플로우를 GUI로 구성하고 API로 바로 호출할 수 있습니다.

### 1. Docker로 로컬 설치

```bash
# 사전 요구사항: Docker Desktop 설치
# https://docs.docker.com/get-docker/

git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env

docker compose up -d

# 실행 확인
docker compose ps
```

### 2. 초기 설정

브라우저에서 `http://localhost/install` 접속 후 관리자 계정 생성

### 3. LLM 연결

대시보드 → **Settings → Model Provider**에서 API 키 등록

| Provider | 설정값 |
|----------|--------|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic (Claude) | `ANTHROPIC_API_KEY` |
| Ollama (로컬) | `http://host.docker.internal:11434` |

### 4. Python에서 Dify API 호출

Dify 앱을 생성하고 발급된 API 키로 호출합니다.

```python
# src/dify_client.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_BASE_URL = "http://localhost/v1"

def chat(message: str, conversation_id: str = "") -> str:
    response = requests.post(
        f"{DIFY_BASE_URL}/chat-messages",
        headers={"Authorization": f"Bearer {DIFY_API_KEY}"},
        json={
            "inputs": {},
            "query": message,
            "response_mode": "blocking",
            "conversation_id": conversation_id,
            "user": "user-001",
        },
    )
    return response.json()["answer"]

if __name__ == "__main__":
    print(chat("안녕하세요!"))
```

```bash
# uv로 바로 실행
uv run python src/dify_client.py
```

---

## 💻 실습 과제

### 과제 1: uv 프로젝트 생성 및 환경 공유 실습

```bash
# 1. 프로젝트 생성
uv init ai_week2
cd ai_week2
uv python pin 3.12
uv add langchain anthropic openai python-dotenv
uv add --dev jupyter

# 2. git 저장소 초기화 및 커밋
git init
echo ".venv/\n.env" >> .gitignore
git add .python-version pyproject.toml uv.lock .gitignore
git commit -m "init: uv 프로젝트 환경 설정"

# 3. 다른 경로에서 복원 테스트 (환경 재현 확인)
cd /tmp && git clone <repo> test_clone && cd test_clone
uv sync   # 이것만으로 완전히 동일한 환경 구성 완료
```

### 과제 2: Dify 앱 생성 및 API 호출

1. Docker로 Dify 실행
2. 대시보드에서 API 키 등록 및 챗봇 앱 생성
3. `.env`에 `DIFY_API_KEY` 추가
4. `uv run python src/dify_client.py`로 호출 확인

---

## ✅ 주간 체크포인트

```
□ uv 설치 및 Python 버전 고정 가능 (.python-version)
□ uv add로 패키지 추가 시 uv.lock이 갱신됨을 확인
□ git clone 후 uv sync 한 번으로 환경 재현 가능
□ uv run으로 가상환경 활성화 없이 스크립트 실행 가능
□ Docker로 Dify 로컬 환경 실행 가능
□ Dify에서 LLM 연결 및 앱 생성 후 API 호출 성공
□ .env 파일로 API 키 관리, git에서 제외 확인
```

---

[← Week 1](./week01_llm_fundamentals.md) | [Week 3 →](./week03_prompt_basics.md)
