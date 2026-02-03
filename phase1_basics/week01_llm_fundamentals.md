# Week 1: LLM 기초와 생태계 이해

## 🎯 학습 목표

1. LLM(Large Language Model)의 작동 원리 이해
2. 주요 LLM 모델들의 특징과 차이점 파악
3. OpenAI/Claude API 활용법 습득
4. AI Engineering의 전반적인 개념 습득

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) | Chip Huyen | Chapter 1-2 |
| 📚 Book | [Hands-On Large Language Models](https://www.oreilly.com/library/view/hands-on-large-language/9781098150952/) | Jay Alammar | Chapter 1-3 |
| 🎬 Video | [Fundamentals of Large Language Models](https://www.oreilly.com/live-events/fundamentals-of-large-language-models/0636920089792/) | Jonathan Fernandes | 전체 |

---

## 📖 핵심 개념

### 1. LLM이란?

Large Language Model은 대규모 텍스트 데이터로 학습된 딥러닝 모델로, 자연어를 이해하고 생성할 수 있습니다.

**핵심 특징:**
- **Transformer 아키텍처**: Attention 메커니즘 기반
- **사전 학습 (Pre-training)**: 대규모 텍스트로 일반적인 언어 패턴 학습
- **미세 조정 (Fine-tuning)**: 특정 태스크에 맞게 추가 학습

### 2. 주요 개념

| 개념 | 설명 | 예시 |
|------|------|------|
| **Token** | LLM이 처리하는 텍스트의 기본 단위 | "Hello" → ["Hel", "lo"] |
| **Context Window** | 한 번에 처리할 수 있는 최대 토큰 수 | GPT-4: 128K, Claude 3: 200K |
| **Temperature** | 출력의 무작위성 조절 (0~2) | 0: 결정적, 1+: 창의적 |
| **Top-p** | 확률 기반 샘플링 | 0.9: 상위 90% 토큰에서 선택 |

### 3. 주요 LLM 모델 비교

| 모델 | 제공사 | 특징 | 강점 |
|------|--------|------|------|
| GPT-4o | OpenAI | 멀티모달, 빠른 속도 | 범용성, 도구 사용 |
| Claude 3.5 | Anthropic | 긴 컨텍스트, 안전성 | 코딩, 분석, 긴 문서 |
| Gemini | Google | 멀티모달, 검색 통합 | Google 서비스 연동 |
| Llama 3 | Meta | 오픈소스, 커스터마이징 | 로컬 실행, 비용 절감 |

---

## 💻 실습 과제

### 과제 1: API 키 발급 및 환경 설정

```bash
# 1. 가상환경 생성
python -m venv llm_env
source llm_env/bin/activate  # Windows: llm_env\Scripts\activate

# 2. 필수 패키지 설치
pip install openai anthropic python-dotenv

# 3. .env 파일 생성
echo "OPENAI_API_KEY=your_key_here" > .env
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

### 과제 2: 기본 챗봇 구현

[샘플 코드 → week01_chatbot_basic.py](./samples/week01_chatbot_basic.py)

### 과제 3: 모델 비교 실험

동일한 프롬프트로 여러 모델의 응답을 비교해보세요:
- 응답 품질
- 응답 속도
- 토큰 사용량
- 비용

---

## ✅ 주간 체크포인트

```
□ LLM의 Token, Context Window 개념 설명 가능
□ GPT, Claude, Llama 등 주요 모델의 특징 비교 가능
□ API를 통한 LLM 호출 코드 작성 가능
□ Temperature, Top-p 파라미터의 효과 이해
```

---

## 🔗 추가 리소스

- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [Hugging Face LLM Course](https://huggingface.co/learn/nlp-course)

---

[← Phase 1 목록](./README.md) | [Week 2 →](./week02_python_environment.md)
