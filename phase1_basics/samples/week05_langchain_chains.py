"""
Week 5: LangChain 시작하기 - Chain 구현
======================================
LCEL을 사용한 다양한 Chain 패턴 예제

실행 전: pip install langchain langchain-openai langchain-core
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from pydantic import BaseModel, Field

load_dotenv()


# ============================================
# 1. 기본 Chain (LCEL)
# ============================================

def basic_chain_example():
    """가장 기본적인 Chain: Prompt → Model → OutputParser"""

    # 컴포넌트 정의
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 {role} 전문가입니다. 간결하게 답변합니다."),
        ("human", "{question}")
    ])

    output_parser = StrOutputParser()

    # LCEL로 Chain 구성 (파이프 연산자 사용)
    chain = prompt | model | output_parser

    # 실행
    result = chain.invoke({
        "role": "Python 개발",
        "question": "리스트 컴프리헨션의 장점은?"
    })

    return result


# ============================================
# 2. 구조화된 출력 (Pydantic)
# ============================================

class DataAnalysisResult(BaseModel):
    """데이터 분석 결과 스키마"""
    summary: str = Field(description="분석 요약 (1-2문장)")
    key_insights: list[str] = Field(description="핵심 인사이트 3가지")
    data_quality_score: int = Field(description="데이터 품질 점수 (1-10)", ge=1, le=10)
    next_steps: list[str] = Field(description="다음 분석 단계 제안")


def structured_output_chain():
    """Pydantic을 사용한 구조화된 출력 Chain"""

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # JSON 출력 파서 (Pydantic 스키마 기반)
    parser = JsonOutputParser(pydantic_object=DataAnalysisResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 데이터 분석 전문가입니다.
주어진 데이터 설명을 분석하고 결과를 JSON 형식으로 출력하세요.

{format_instructions}"""),
        ("human", "데이터 설명: {data_description}")
    ])

    # 포맷 지시사항 주입
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())

    chain = prompt | model | parser

    result = chain.invoke({
        "data_description": "2023년 월별 매출 데이터. 1월 100만, 2월 120만, 3월 90만, 4월 150만원. 3월에 급감한 이유 불명."
    })

    return result


# ============================================
# 3. Sequential Chain (순차 실행)
# ============================================

def sequential_chain_example():
    """여러 단계를 순차적으로 실행하는 Chain"""

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    # Step 1: 주제 분석
    analyze_prompt = ChatPromptTemplate.from_template(
        "다음 텍스트의 주제와 핵심 키워드를 분석하세요:\n\n{text}\n\n분석:"
    )

    # Step 2: 요약 생성
    summarize_prompt = ChatPromptTemplate.from_template(
        "다음 분석을 바탕으로 원문을 3문장으로 요약하세요:\n\n분석: {analysis}\n\n요약:"
    )

    # Step 3: 제목 생성
    title_prompt = ChatPromptTemplate.from_template(
        "다음 요약에 적합한 제목을 5개 제안하세요:\n\n요약: {summary}\n\n제목들:"
    )

    # Chain 구성
    chain = (
        {"text": RunnablePassthrough()}
        | RunnableParallel(
            text=RunnablePassthrough(),
            analysis=analyze_prompt | model | StrOutputParser()
        )
        | RunnableParallel(
            analysis=lambda x: x["analysis"],
            summary=summarize_prompt | model | StrOutputParser()
        )
        | RunnableParallel(
            analysis=lambda x: x["analysis"],
            summary=lambda x: x["summary"],
            titles=title_prompt | model | StrOutputParser()
        )
    )

    result = chain.invoke(
        "인공지능은 21세기 가장 혁신적인 기술 중 하나입니다. 머신러닝과 딥러닝의 발전으로 AI는 이미지 인식, 자연어 처리 등 다양한 분야에서 활용되고 있습니다."
    )

    return result


# ============================================
# 4. 병렬 처리 Chain
# ============================================

def parallel_chain_example():
    """여러 작업을 동시에 병렬로 실행"""

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    # 각각 다른 분석을 수행하는 Chain
    sentiment_chain = (
        ChatPromptTemplate.from_template("텍스트의 감성(긍정/부정/중립)을 분석하세요: {text}")
        | model
        | StrOutputParser()
    )

    keyword_chain = (
        ChatPromptTemplate.from_template("텍스트에서 핵심 키워드 5개를 추출하세요: {text}")
        | model
        | StrOutputParser()
    )

    category_chain = (
        ChatPromptTemplate.from_template("텍스트의 카테고리를 분류하세요 (기술/비즈니스/일상/기타): {text}")
        | model
        | StrOutputParser()
    )

    # 병렬 실행
    parallel_chain = RunnableParallel(
        sentiment=sentiment_chain,
        keywords=keyword_chain,
        category=category_chain
    )

    result = parallel_chain.invoke({
        "text": "새로운 AI 스타트업이 1000억원의 투자를 유치했다. 이 회사는 자연어 처리 기술을 활용한 고객 서비스 자동화 솔루션을 개발하고 있다."
    })

    return result


# ============================================
# 5. 조건부 분기 Chain
# ============================================

def conditional_chain_example():
    """입력에 따라 다른 Chain 실행"""

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    # 코드 관련 질문용 Chain
    code_chain = (
        ChatPromptTemplate.from_template(
            "당신은 시니어 개발자입니다. 코드 관련 질문에 답하세요:\n{question}"
        )
        | model
        | StrOutputParser()
    )

    # 데이터 관련 질문용 Chain
    data_chain = (
        ChatPromptTemplate.from_template(
            "당신은 데이터 분석가입니다. 데이터 관련 질문에 답하세요:\n{question}"
        )
        | model
        | StrOutputParser()
    )

    # 일반 질문용 Chain
    general_chain = (
        ChatPromptTemplate.from_template(
            "다음 질문에 친절하게 답하세요:\n{question}"
        )
        | model
        | StrOutputParser()
    )

    def route_question(input_dict):
        """질문 내용에 따라 적절한 Chain 선택"""
        question = input_dict["question"].lower()

        if any(word in question for word in ["코드", "프로그래밍", "python", "함수"]):
            return code_chain
        elif any(word in question for word in ["데이터", "분석", "sql", "통계"]):
            return data_chain
        else:
            return general_chain

    # 라우팅 Chain
    chain = RunnableLambda(route_question) | RunnableLambda(lambda chain: chain)

    # 실제로는 이렇게 사용:
    def smart_answer(question: str) -> str:
        q_lower = question.lower()
        if any(word in q_lower for word in ["코드", "프로그래밍", "python", "함수"]):
            return code_chain.invoke({"question": question})
        elif any(word in q_lower for word in ["데이터", "분석", "sql", "통계"]):
            return data_chain.invoke({"question": question})
        else:
            return general_chain.invoke({"question": question})

    return smart_answer


# ============================================
# 6. Chain with Fallback (에러 처리)
# ============================================

def chain_with_fallback():
    """메인 Chain 실패 시 대체 Chain 실행"""

    main_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    fallback_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    prompt = ChatPromptTemplate.from_template("질문: {question}")

    main_chain = prompt | main_model | StrOutputParser()
    fallback_chain = prompt | fallback_model | StrOutputParser()

    # with_fallbacks로 대체 Chain 설정
    robust_chain = main_chain.with_fallbacks([fallback_chain])

    return robust_chain


# ============================================
# 7. 실용적인 예제: 문서 요약 Pipeline
# ============================================

def document_summarization_pipeline():
    """실용적인 문서 요약 파이프라인"""

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    # 긴 문서를 청크로 나누는 함수
    def chunk_text(text: str, chunk_size: int = 2000) -> list[str]:
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0

        for word in words:
            if current_size + len(word) > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    # 개별 청크 요약 Chain
    chunk_summary_chain = (
        ChatPromptTemplate.from_template(
            "다음 텍스트를 3문장으로 요약하세요:\n\n{chunk}"
        )
        | model
        | StrOutputParser()
    )

    # 최종 요약 Chain
    final_summary_chain = (
        ChatPromptTemplate.from_template(
            "다음 요약들을 통합하여 전체 문서의 핵심을 5문장으로 정리하세요:\n\n{summaries}"
        )
        | model
        | StrOutputParser()
    )

    def summarize_document(document: str) -> str:
        # 1. 문서를 청크로 분할
        chunks = chunk_text(document)

        # 2. 각 청크 요약
        chunk_summaries = []
        for chunk in chunks:
            summary = chunk_summary_chain.invoke({"chunk": chunk})
            chunk_summaries.append(summary)

        # 3. 요약 통합
        combined = "\n\n".join(chunk_summaries)
        final_summary = final_summary_chain.invoke({"summaries": combined})

        return final_summary

    return summarize_document


# ============================================
# 실행 예제
# ============================================

if __name__ == "__main__":
    # 예제 1: 기본 Chain
    print("=== 기본 Chain ===")
    result = basic_chain_example()
    print(result)
    print()

    # 예제 2: 구조화된 출력
    print("=== 구조화된 출력 ===")
    result = structured_output_chain()
    print(f"Summary: {result['summary']}")
    print(f"Insights: {result['key_insights']}")
    print(f"Quality Score: {result['data_quality_score']}")
    print()

    # 예제 3: 병렬 처리
    print("=== 병렬 처리 Chain ===")
    result = parallel_chain_example()
    print(f"Sentiment: {result['sentiment']}")
    print(f"Keywords: {result['keywords']}")
    print(f"Category: {result['category']}")
    print()

    # 예제 4: 조건부 분기
    print("=== 조건부 분기 ===")
    smart_answer = conditional_chain_example()
    print("코드 질문:", smart_answer("Python에서 리스트를 정렬하는 방법은?")[:100], "...")
    print("데이터 질문:", smart_answer("데이터 분석에서 결측치를 처리하는 방법은?")[:100], "...")
