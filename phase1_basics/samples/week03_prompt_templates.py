"""
Week 3: Prompt Engineering 기초 - 프롬프트 템플릿
================================================
Zero-shot, Few-shot, Chain-of-Thought 프롬프팅 예제

실행 전: pip install openai python-dotenv
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


# ============================================
# 1. Zero-shot 프롬프팅
# ============================================

def zero_shot_classification(text: str) -> str:
    """
    Zero-shot: 예시 없이 직접 분류
    """
    prompt = f"""다음 텍스트의 감성을 분석하세요.

텍스트: "{text}"

감성 (긍정/부정/중립 중 하나만):"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# ============================================
# 2. Few-shot 프롬프팅
# ============================================

def few_shot_classification(text: str) -> str:
    """
    Few-shot: 예시를 제공하여 패턴 학습 유도
    """
    prompt = f"""다음은 고객 리뷰 감성 분석 예시입니다:

예시 1:
리뷰: "배송이 빠르고 제품 품질이 좋아요!"
감성: 긍정

예시 2:
리뷰: "포장이 망가져서 왔고 환불도 어렵네요"
감성: 부정

예시 3:
리뷰: "가격은 적당한데 특별한 건 없어요"
감성: 중립

이제 다음 리뷰를 분석하세요:
리뷰: "{text}"
감성:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# ============================================
# 3. Chain-of-Thought (CoT) 프롬프팅
# ============================================

def chain_of_thought(problem: str) -> str:
    """
    CoT: 단계별 사고 과정을 유도하여 복잡한 문제 해결
    """
    prompt = f"""다음 문제를 단계별로 생각하며 풀어주세요.

문제: {problem}

단계별 풀이:
1단계:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content


def zero_shot_cot(problem: str) -> str:
    """
    Zero-shot CoT: "단계별로 생각해보세요" 프롬프트 추가
    """
    prompt = f"""{problem}

단계별로 차근차근 생각해보세요."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content


# ============================================
# 4. 구조화된 프롬프트 템플릿
# ============================================

class PromptTemplate:
    """재사용 가능한 프롬프트 템플릿 클래스"""

    def __init__(self, template: str):
        self.template = template

    def format(self, **kwargs) -> str:
        """템플릿에 변수 삽입"""
        return self.template.format(**kwargs)


# 데이터 분석 템플릿
DATA_ANALYSIS_TEMPLATE = PromptTemplate("""
당신은 10년 경력의 시니어 데이터 분석가입니다.

## 역할
주어진 데이터를 분석하고 비즈니스 인사이트를 도출합니다.

## 데이터 설명
{data_description}

## 분석 목표
{analysis_goal}

## 출력 형식
다음 형식으로 분석 결과를 제공해주세요:

### 1. 핵심 인사이트 (3가지)
- 인사이트 1: [설명]
- 인사이트 2: [설명]
- 인사이트 3: [설명]

### 2. 데이터 품질 이슈
- [발견된 이슈들]

### 3. 추천 액션
- [비즈니스 제안]

### 4. 추가 분석 제안
- [다음 단계 분석]
""")


# 코드 생성 템플릿
CODE_GENERATION_TEMPLATE = PromptTemplate("""
당신은 Python 전문 개발자입니다.

## 작업
{task_description}

## 요구사항
- Python 3.10+ 문법 사용
- Type hints 포함
- Docstring 포함
- 에러 처리 포함

## 사용 가능한 라이브러리
{libraries}

## 출력
```python
# 코드를 여기에 작성
```
""")


# SQL 생성 템플릿
SQL_GENERATION_TEMPLATE = PromptTemplate("""
당신은 SQL 전문가입니다.

## 테이블 스키마
{schema}

## 자연어 질문
{question}

## 요구사항
- 표준 SQL 문법 사용
- 주석으로 설명 추가
- 최적화된 쿼리 작성

## SQL 쿼리:
```sql
""")


# ============================================
# 5. 프롬프트 체이닝
# ============================================

def analyze_and_visualize(data_description: str) -> dict:
    """
    프롬프트 체이닝: 분석 → 시각화 코드 생성
    """
    # Step 1: 데이터 분석
    analysis_prompt = DATA_ANALYSIS_TEMPLATE.format(
        data_description=data_description,
        analysis_goal="주요 패턴과 이상치를 발견하세요"
    )

    analysis_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": analysis_prompt}],
        temperature=0.3
    )
    analysis = analysis_response.choices[0].message.content

    # Step 2: 분석 결과 기반 시각화 코드 생성
    viz_prompt = CODE_GENERATION_TEMPLATE.format(
        task_description=f"""
다음 분석 결과를 시각화하는 코드를 작성하세요:

{analysis}

적절한 차트 유형을 선택하여 인사이트를 시각적으로 표현하세요.
        """,
        libraries="pandas, matplotlib, seaborn"
    )

    viz_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": viz_prompt}],
        temperature=0.3
    )
    viz_code = viz_response.choices[0].message.content

    return {
        "analysis": analysis,
        "visualization_code": viz_code
    }


# ============================================
# 6. 역할 기반 프롬프팅
# ============================================

def role_based_prompt(question: str, role: str) -> str:
    """
    역할에 따라 다른 관점의 답변 생성
    """
    roles = {
        "data_scientist": "당신은 머신러닝에 정통한 데이터 사이언티스트입니다. 통계와 모델링 관점에서 답변합니다.",
        "business_analyst": "당신은 비즈니스 분석가입니다. ROI와 비즈니스 가치 관점에서 답변합니다.",
        "engineer": "당신은 데이터 엔지니어입니다. 확장성과 시스템 아키텍처 관점에서 답변합니다."
    }

    system_prompt = roles.get(role, roles["data_scientist"])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


# ============================================
# 실행 예제
# ============================================

if __name__ == "__main__":
    # 예제 1: Zero-shot vs Few-shot 비교
    test_text = "가격이 좀 비싸지만 품질은 확실히 좋네요"

    print("=== Zero-shot vs Few-shot 비교 ===")
    print(f"텍스트: {test_text}")
    print(f"Zero-shot 결과: {zero_shot_classification(test_text)}")
    print(f"Few-shot 결과: {few_shot_classification(test_text)}")
    print()

    # 예제 2: Chain-of-Thought
    print("=== Chain-of-Thought ===")
    problem = """
    회사에 직원이 100명 있습니다.
    1분기에 20%가 퇴사하고,
    2분기에 새로 15명을 채용했습니다.
    3분기 시작 시점의 직원 수는?
    """
    print(f"문제: {problem}")
    print(f"CoT 답변:\n{chain_of_thought(problem)}")
    print()

    # 예제 3: 템플릿 활용
    print("=== 데이터 분석 템플릿 ===")
    prompt = DATA_ANALYSIS_TEMPLATE.format(
        data_description="월별 매출 데이터 (2023년 1월~12월), 컬럼: 날짜, 매출액, 지역, 제품카테고리",
        analysis_goal="매출 트렌드와 성장 기회 발견"
    )
    print(prompt[:500] + "...")
    print()

    # 예제 4: 역할 기반 답변 비교
    print("=== 역할 기반 프롬프팅 ===")
    question = "데이터 웨어하우스 도입을 고려하고 있습니다. 어떤 점을 고려해야 할까요?"

    for role in ["data_scientist", "business_analyst", "engineer"]:
        print(f"\n[{role}의 관점]")
        response = role_based_prompt(question, role)
        print(response[:300] + "...")
