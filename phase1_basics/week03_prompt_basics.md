# Week 3: Prompt Engineering 기초

## 🎯 학습 목표

1. 효과적인 프롬프트 작성 원칙 습득
2. Zero-shot, Few-shot 프롬프팅 이해
3. Chain-of-Thought (CoT) 기법 실습
4. 프롬프트 템플릿 설계

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Prompt Engineering for Generative AI](https://www.oreilly.com/library/view/prompt-engineering-for/9781098153427/) | James Phoenix | Chapter 1-5 |
| 📚 Book | [Prompt Engineering for LLMs](https://www.oreilly.com/library/view/prompt-engineering-for/9781098156145/) | John Berryman | Chapter 1-4 |

---

## 📖 핵심 개념

### 1. 프롬프트의 구성 요소

```
┌─────────────────────────────────────────┐
│              PROMPT 구조                 │
├─────────────────────────────────────────┤
│  1. Role (역할)                          │
│     → "당신은 데이터 분석 전문가입니다"     │
├─────────────────────────────────────────┤
│  2. Context (배경)                       │
│     → 작업에 필요한 배경 정보              │
├─────────────────────────────────────────┤
│  3. Task (작업)                          │
│     → 구체적으로 수행할 작업               │
├─────────────────────────────────────────┤
│  4. Format (형식)                        │
│     → 원하는 출력 형식                    │
├─────────────────────────────────────────┤
│  5. Examples (예시)                      │
│     → Few-shot 학습을 위한 예제           │
└─────────────────────────────────────────┘
```

### 2. 프롬프팅 기법 비교

| 기법 | 설명 | 사용 시점 |
|------|------|----------|
| **Zero-shot** | 예시 없이 직접 질문 | 단순 작업, 일반 지식 |
| **Few-shot** | 몇 가지 예시 제공 | 특정 패턴/형식 필요 |
| **Chain-of-Thought** | 단계별 사고 과정 유도 | 복잡한 추론 문제 |
| **Self-consistency** | 여러 답변 생성 후 선택 | 정확도가 중요한 경우 |

### 3. Zero-shot vs Few-shot

**Zero-shot 예시:**
```
다음 리뷰의 감성을 분석해주세요: "이 제품 정말 좋아요!"
→ 긍정
```

**Few-shot 예시:**
```
리뷰 감성 분석 예시:
- "정말 만족합니다" → 긍정
- "별로예요" → 부정
- "그냥 그래요" → 중립

다음 리뷰를 분석해주세요: "가격 대비 괜찮네요"
→ 중립
```

### 4. Chain-of-Thought (CoT)

복잡한 문제를 단계별로 해결하도록 유도:

```
Q: 사과 5개가 있습니다. 2개를 먹고, 3개를 더 샀습니다. 몇 개가 남았나요?

A: 단계별로 생각해보겠습니다:
1. 처음 사과 개수: 5개
2. 먹은 후: 5 - 2 = 3개
3. 더 산 후: 3 + 3 = 6개
따라서 6개가 남았습니다.
```

---

## 💻 실습 과제

### 과제 1: 프롬프트 5원칙 적용

각 원칙에 맞는 프롬프트를 작성해보세요:

1. **명확성**: 모호하지 않은 지시
2. **구체성**: 상세한 요구사항
3. **구조화**: 논리적 구성
4. **예시 제공**: Few-shot 활용
5. **제약 조건**: 출력 형식 지정

### 과제 2: Few-shot 분류 실습

[샘플 코드 → week03_prompt_templates.py](./samples/week03_prompt_templates.py)

### 과제 3: CoT로 복잡한 문제 해결

다음 문제를 CoT 프롬프팅으로 해결:
- 수학 문제
- 논리 퍼즐
- 데이터 분석 계획 수립

---

## 📝 프롬프트 템플릿 라이브러리

### 데이터 분석용 템플릿

```python
DATA_ANALYSIS_TEMPLATE = """
당신은 시니어 데이터 분석가입니다.

### 데이터 설명
{data_description}

### 분석 목표
{analysis_goal}

### 요청 사항
다음 형식으로 분석 결과를 제공해주세요:
1. 핵심 인사이트 (3가지)
2. 데이터 품질 이슈
3. 추가 분석 제안

### 제약 사항
- 전문 용어는 쉽게 설명
- 숫자는 반드시 포함
- 시각화 제안 포함
"""
```

### 코드 리뷰용 템플릿

```python
CODE_REVIEW_TEMPLATE = """
당신은 10년 경력의 소프트웨어 엔지니어입니다.

### 코드
```{language}
{code}
```

### 리뷰 관점
1. 코드 품질
2. 성능
3. 보안
4. 가독성

### 출력 형식
각 관점에 대해:
- 점수 (1-10)
- 개선 제안
- 수정된 코드 (필요시)
"""
```

---

## ✅ 주간 체크포인트

```
□ Zero-shot vs Few-shot 차이 설명 가능
□ 효과적인 시스템 프롬프트 작성 가능
□ CoT 프롬프팅의 장단점 이해
□ 프롬프트 템플릿 라이브러리 5개 이상 작성
□ 동일 작업에 대해 3가지 다른 프롬프트 비교 실험
```

---

## 🔗 추가 리소스

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [Learn Prompting](https://learnprompting.org/)

---

[← Week 2](./week02_python_environment.md) | [Week 4 →](./week04_prompt_advanced.md)
