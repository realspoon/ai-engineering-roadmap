# Week 20: LLM 기반 품질 검사 (의미적 검증)

## 학습 목표
- LLM을 활용한 의미적 데이터 검증
- 컨텍스트 기반 품질 평가
- 자동 데이터 정규화 및 수정

## 1. LLM 기반 검증의 필요성

### 1.1 규칙 기반 검증의 한계
```
규칙 기반:
✓ 빠르고 명확
✗ 복잡한 논리 표현 어려움
✗ 문맥 이해 불가
✗ 비정형 데이터 처리 불가

LLM 기반:
✓ 의미적 이해 가능
✓ 복잡한 논리 처리
✓ 문맥 반영
✓ 비정형 데이터 처리
✗ 느리고 비용 발생
✗ 비결정적 결과
```

### 1.2 활용 사례
- 고객 리뷰 감정 분석
- 제품 설명 정확성 검증
- 주소 정규화
- 이름/회사명 오류 수정
- 범주 분류 정확성 확인

## 2. LLM을 활용한 데이터 검증 아키텍처

```
┌─────────────────────────────────────────┐
│     Raw Data                            │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  1. Rule-Based Validation              │
│  (빠른 검증)                            │
└────────────────┬────────────────────────┘
                 ↓
         ┌──────┴──────┐
         ↓             ↓
     Pass         Fail/Uncertain
         ↓             ↓
    Output      ┌───────────────────┐
                │ 2. LLM Validation │
                │ (의미적 검증)      │
                └────────┬──────────┘
                         ↓
                    ┌─────┴──────┐
                    ↓            ↓
                  Valid       Invalid
                    ↓            ↓
                  Output     Fix/Reject
```

## 3. OpenAI API를 활용한 LLM 검증

### 3.1 기본 검증 프롬프트
```python
import openai

class LLMValidator:
    def __init__(self, api_key):
        openai.api_key = api_key

    def validate_email(self, email):
        """이메일 주소 검증"""
        prompt = f"""
        다음 이메일 주소가 유효한가? 유효하면 'VALID',
        아니면 수정된 형태를 제안하세요.

        이메일: {email}

        응답 형식:
        STATUS: VALID/INVALID
        REASON: (이유)
        SUGGESTION: (수정 제안)
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return response.choices[0].message.content

    def validate_address(self, address):
        """주소 검증 및 정규화"""
        prompt = f"""
        다음 주소를 검증하고 정규화하세요.

        주소: {address}

        응답 형식:
        VALID: YES/NO
        NORMALIZED: (정규화된 주소)
        ISSUES: (발견된 문제들)
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return response.choices[0].message.content
```

### 3.2 범주 분류 검증
```python
class CategoryValidator:
    def __init__(self, api_key, valid_categories):
        openai.api_key = api_key
        self.valid_categories = valid_categories

    def validate_and_correct(self, item, assigned_category):
        """
        아이템이 올바른 범주로 분류되었는지 검증
        """
        prompt = f"""
        제품: {item}
        할당된 범주: {assigned_category}
        유효한 범주: {', '.join(self.valid_categories)}

        할당된 범주가 올바른지 판단하세요.
        잘못되었다면 올바른 범주를 제안하세요.

        응답 형식:
        CORRECT: YES/NO
        CONFIDENCE: 0-100
        SUGGESTED_CATEGORY: (제안 범주)
        REASON: (이유)
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return response.choices[0].message.content
```

## 4. 구조화된 출력 (Function Calling)

### 4.1 Function Definition
```python
def create_validation_function():
    """LLM 검증을 위한 함수 정의"""
    return {
        "name": "validate_data",
        "description": "데이터 유효성 검증",
        "parameters": {
            "type": "object",
            "properties": {
                "is_valid": {
                    "type": "boolean",
                    "description": "데이터 유효성"
                },
                "confidence": {
                    "type": "number",
                    "description": "신뢰도 (0-1)"
                },
                "issues": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "발견된 문제"
                },
                "suggestions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "개선 제안"
                },
                "corrected_value": {
                    "type": "string",
                    "description": "수정된 값"
                }
            },
            "required": ["is_valid", "confidence"]
        }
    }
```

### 4.2 구조화된 검증
```python
class StructuredValidator:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.validation_function = create_validation_function()

    def validate(self, data_item, context=None):
        """구조화된 형식으로 검증"""
        prompt = f"""
        다음 데이터를 검증하세요:

        데이터: {data_item}
        {f"컨텍스트: {context}" if context else ""}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            functions=[self.validation_function],
            function_call={"name": "validate_data"}
        )

        # 함수 호출 결과 파싱
        function_args = json.loads(
            response.choices[0].message.function_call.arguments
        )

        return function_args
```

## 5. 배치 검증 (비용 최적화)

### 5.1 배치 검증 구현
```python
class BatchLLMValidator:
    def __init__(self, api_key, batch_size=10):
        openai.api_key = api_key
        self.batch_size = batch_size

    def validate_batch(self, items, validation_type='email'):
        """여러 아이템을 한 번에 검증 (비용 절감)"""

        if validation_type == 'email':
            prompt = self._create_email_batch_prompt(items)
        elif validation_type == 'category':
            prompt = self._create_category_batch_prompt(items)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        results = self._parse_batch_response(
            response.choices[0].message.content,
            items
        )

        return results

    def _create_email_batch_prompt(self, emails):
        """배치 이메일 검증 프롬프트"""
        email_list = "\n".join([f"{i}. {e}" for i, e in enumerate(emails)])

        return f"""
        다음 이메일들을 검증하세요.
        각 항목마다 VALID/INVALID와 이유를 제시하세요.

        {email_list}

        응답 형식:
        1. STATUS: REASON
        2. STATUS: REASON
        ...
        """

    def _parse_batch_response(self, response_text, items):
        """배치 응답 파싱"""
        results = []
        lines = response_text.strip().split('\n')

        for i, line in enumerate(lines):
            if i < len(items):
                # 응답 파싱 로직
                parts = line.split(': ', 1)
                status = 'VALID' in parts[0]
                reason = parts[1] if len(parts) > 1 else ''

                results.append({
                    'item': items[i],
                    'valid': status,
                    'reason': reason
                })

        return results
```

## 6. Few-Shot Prompting

### 6.1 예제 기반 검증
```python
class FewShotValidator:
    def __init__(self, api_key):
        openai.api_key = api_key

    def validate_with_examples(self, data_item, examples):
        """
        몇 가지 예제를 제시하고 검증
        """
        example_text = self._format_examples(examples)

        prompt = f"""
        다음은 올바른 데이터 형식의 예제입니다:

        {example_text}

        이제 다음 데이터를 평가하세요:
        {data_item}

        유효한가? 필요하면 수정하세요.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return response.choices[0].message.content

    def _format_examples(self, examples):
        """예제 포매팅"""
        formatted = []
        for example in examples:
            formatted.append(f"- {example['input']} → {example['output']}")
        return "\n".join(formatted)
```

## 7. 신뢰도 기반 필터링

### 7.1 신뢰도 점수 계산
```python
class ConfidenceBasedValidator:
    def __init__(self, api_key, confidence_threshold=0.8):
        openai.api_key = api_key
        self.threshold = confidence_threshold

    def validate_with_confidence(self, items, validation_context):
        """신뢰도 점수와 함께 검증"""
        results = {
            'high_confidence': [],
            'low_confidence': [],
            'requires_manual_review': []
        }

        for item in items:
            validation = self.validate_item(item, validation_context)

            if validation['confidence'] >= self.threshold:
                results['high_confidence'].append(validation)
            elif validation['confidence'] >= 0.5:
                results['low_confidence'].append(validation)
            else:
                results['requires_manual_review'].append(validation)

        return results

    def validate_item(self, item, context):
        """개별 아이템 검증"""
        # LLM 호출 및 신뢰도 추출
        pass
```

## 8. 실전 사례: 고객 데이터 검증

### 8.1 통합 검증 파이프라인
```python
class CustomerDataValidator:
    def __init__(self, api_key):
        self.llm = LLMValidator(api_key)
        self.rule_validator = RuleBasedValidator()
        self.confidence_validator = ConfidenceBasedValidator(api_key)

    def validate_customer_record(self, customer):
        """고객 레코드 전체 검증"""
        results = {
            'email': self._validate_email(customer['email']),
            'phone': self._validate_phone(customer['phone']),
            'address': self._validate_address(customer['address']),
            'name': self._validate_name(customer['name']),
            'overall_quality': None
        }

        # 전체 품질 점수 계산
        score = self._calculate_quality_score(results)
        results['overall_quality'] = score

        return results

    def _validate_email(self, email):
        """이메일 검증"""
        # 1단계: 규칙 기반 검증
        if not self.rule_validator.validate_email_format(email):
            return {'valid': False, 'method': 'rule', 'reason': '형식 오류'}

        # 2단계: LLM 검증 (필요시)
        llm_result = self.llm.validate_email(email)
        return {'valid': True, 'method': 'llm', 'details': llm_result}

    def _calculate_quality_score(self, results):
        """품질 점수 계산"""
        valid_fields = sum(1 for v in results.values() if isinstance(v, dict) and v.get('valid'))
        total_fields = len([k for k in results.keys() if k != 'overall_quality'])
        return (valid_fields / total_fields) * 100 if total_fields > 0 else 0
```

## 9. 실습 프로젝트

### 9.1 프로젝트: E-Commerce 제품 검증
```
1. LLM 기반 제품 설명 검증
2. 범주 분류 정확성 확인
3. 가격 데이터 검증
4. 배치 검증 구현
5. 신뢰도 기반 필터링
6. 검증 결과 분석 및 리포트
```

## 10. 평가 기준

- [ ] LLM 기반 검증 기본 이해
- [ ] OpenAI API 활용
- [ ] 구조화된 출력 구현
- [ ] 배치 검증 최적화
- [ ] 신뢰도 기반 필터링
- [ ] 프로젝트 완료

## 11. 비용 및 성능 고려사항

| 항목 | 고려사항 |
|------|---------|
| 비용 | 배치 처리로 API 호출 최소화 |
| 속도 | 규칙 기반과 LLM 기반 조합 |
| 정확도 | Few-shot examples 제공 |
| 스케일 | 캐싱 및 재검증 방지 |

## 12. 참고 자료

- OpenAI API 문서
- "Prompt Engineering" - deeplearning.ai
- LangChain 라이브러리
- Guidance 구조화된 프롬프팅
