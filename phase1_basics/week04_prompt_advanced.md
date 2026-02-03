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

```
Thought: 사용자가 날씨를 묻고 있다. 현재 날씨 정보가 필요하다.
Action: weather_api("Seoul")
Observation: 서울 현재 기온 15도, 맑음
Thought: 날씨 정보를 얻었다. 사용자에게 알려줄 수 있다.
Answer: 서울의 현재 날씨는 맑고 기온은 15도입니다.
```

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
