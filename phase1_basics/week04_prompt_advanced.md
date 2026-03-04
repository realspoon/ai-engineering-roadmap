# Week 4: Prompt Engineering 심화

## 🎯 학습 목표

1. 고급 프롬프팅 기법 (Self-consistency, ReAct)
2. 프롬프트 최적화 및 평가 방법
3. 프롬프트 템플릿화 및 버전 관리
4. A/B 테스트 수행

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Prompt Engineering for Generative AI](https://www.oreilly.com/library/view/prompt-engineering-for/9781098153427/) | James Phoenix | Chapter 6-10 |
| 📚 Book | [Prompt Engineering for LLMs](https://www.oreilly.com/library/view/prompt-engineering-for/9781098156145/) | John Berryman | Chapter 5-8 |

---

## 📖 핵심 개념

### 1. ReAct (Reasoning + Acting)
**ReAct(Reasoning + Acting)**는 AI 모델이 복잡한 문제를 해결할 때 **'추론(Reasoning)'**과 **'행동(Acting)'**을 번갈아 가며 수행하도록 유도하는 프롬프트 엔지니어링 기법입니다.

```
Thought: 사용자가 날씨를 묻고 있다. 현재 날씨 정보가 필요하다.
Action: weather_api("Seoul")
Observation: 서울 현재 기온 15도, 맑음
Thought: 날씨 정보를 얻었다. 사용자에게 알려줄 수 있다.
Answer: 서울의 현재 날씨는 맑고 기온은 15도입니다.
```
1. ReAct의 핵심 구성 요소
ReAct 프롬프트는 보통 **[Thought - Action - Observation]**의 반복 루프로 구성됩니다.

Thought (추론): 모델이 현재 상황을 분석하고, 다음 단계를 결정하기 위해 스스로 생각하는 과정입니다. (예: "이 질문에 답하려면 먼저 A를 검색해야겠다.")

Action (행동): 결정을 바탕으로 실제 동작을 수행합니다. 주로 외부 API 호출이나 데이터베이스 검색 등이 해당됩니다. (예: search[A에 대한 정보])

Observation (관찰): 행동의 결과로 얻은 정보를 확인합니다. (예: 검색 결과 내용)

이 과정을 거치며 모델은 자신의 오류를 수정하거나 부족한 정보를 보완하여 최종 답변에 도달합니다.

2. 왜 ReAct를 사용하나요?
기존의 기법들과 비교했을 때 다음과 같은 확실한 장점이 있습니다.

기법,특징,한계점
Standard Prompt,질문에 즉각 답함,복잡한 논리나 최신 정보 부족 시 환각(Hallucination) 발생
Chain of Thought (CoT),단계별 사고 과정을 출력,외부 세계와 단절되어 있어 잘못된 사실을 바탕으로 논리만 펼칠 수 있음
ReAct,사고 + 외부 도구 활용,CoT의 논리성과 실제 데이터의 정확성을 결합해 신뢰도가 높음

### 2. Self-Consistency

```python
def self_consistency(question: str, n_samples: int = 5) -> str:
    """여러 답변 생성 후 다수결로 선택"""
    answers = []
    for _ in range(n_samples):
        response = llm.invoke(question, temperature=0.7)
        answers.append(extract_answer(response))

    # 가장 많이 나온 답변 선택
    return Counter(answers).most_common(1)[0][0]
```

### 3. 프롬프트 최적화 기법

| 기법 | 설명 | 효과 |
|------|------|------|
| **구조화** | XML/JSON 태그 사용 | 명확한 구분 |
| **예시 순서** | 쉬운 것부터 어려운 순 | 학습 효과 향상 |
| **부정형 지시** | "하지 마세요" 보다 "~만 하세요" | 정확도 향상 |
| **출력 제한** | 글자수/형식 지정 | 일관성 확보 |

### 4. 프롬프트 A/B 테스트

```python
class PromptExperiment:
    def __init__(self, prompts: list[str], test_cases: list[dict]):
        self.prompts = prompts
        self.test_cases = test_cases

    def run(self) -> pd.DataFrame:
        results = []
        for prompt in self.prompts:
            for case in self.test_cases:
                response = llm.invoke(prompt.format(**case['input']))
                score = evaluate(response, case['expected'])
                results.append({
                    'prompt': prompt[:50],
                    'case': case['name'],
                    'score': score
                })
        return pd.DataFrame(results)
```

---

## 💻 실습 과제

### 과제 1: ReAct 패턴 구현

[샘플 코드 → week04_react_pattern.py](./samples/week04_react_pattern.py)

### 과제 2: 프롬프트 A/B 테스트 수행

- 동일 작업에 대해 3가지 프롬프트 작성
- 10개 테스트 케이스로 평가
- 결과 비교 및 분석

### 과제 3: 프롬프트 라이브러리 구축

- 5개 이상의 재사용 가능한 템플릿
- 버전 관리 (v1, v2, ...)
- 성능 기록 문서화

---

## ✅ 주간 체크포인트

```
□ ReAct 패턴의 동작 원리 설명 가능
□ Self-consistency 기법 구현 가능
□ 프롬프트 A/B 테스트 수행 가능
□ 프롬프트 최적화 5가지 기법 적용 가능
□ 재사용 가능한 프롬프트 라이브러리 구축
```

---

[← Week 3](./week03_prompt_basics.md) | [Week 5 →](./week05_langchain_intro.md)
