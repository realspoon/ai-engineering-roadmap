"""
Week 10: LangGraph 입문 - 기본 그래프 구현
==========================================
StateGraph, Node, Edge를 활용한 워크플로우 구축

실행 전: pip install langgraph langchain-openai
"""

import os
from typing import TypedDict, Annotated, Literal
from operator import add
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


# ============================================
# 1. 기본 State 정의
# ============================================

class BasicState(TypedDict):
    """기본 상태 스키마"""
    input: str
    output: str


class ConversationState(TypedDict):
    """대화 상태 스키마 (메시지 누적)"""
    messages: Annotated[list, add]  # add 연산자로 메시지 누적
    current_step: str


class AnalysisState(TypedDict):
    """분석 워크플로우 상태"""
    query: str
    analysis: str | None
    review_needed: bool
    final_output: str | None


# ============================================
# 2. 기본 그래프 (선형 워크플로우)
# ============================================

def create_basic_graph():
    """가장 단순한 선형 그래프: START → Process → END"""

    def process_input(state: BasicState) -> dict:
        """입력을 처리하는 노드"""
        result = f"Processed: {state['input'].upper()}"
        return {"output": result}

    # 그래프 생성
    graph = StateGraph(BasicState)

    # 노드 추가
    graph.add_node("process", process_input)

    # 엣지 연결
    graph.add_edge(START, "process")
    graph.add_edge("process", END)

    # 컴파일
    return graph.compile()


# ============================================
# 3. LLM 노드가 있는 그래프
# ============================================

def create_llm_graph():
    """LLM을 사용하는 분석 그래프"""

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    def analyze_node(state: AnalysisState) -> dict:
        """LLM으로 분석 수행"""
        prompt = f"""다음 질문을 분석하고 핵심 포인트를 정리하세요:

질문: {state['query']}

분석:"""

        response = model.invoke([HumanMessage(content=prompt)])

        # 분석 내용이 짧으면 리뷰 필요
        needs_review = len(response.content) < 100

        return {
            "analysis": response.content,
            "review_needed": needs_review
        }

    def review_node(state: AnalysisState) -> dict:
        """분석 결과 리뷰 및 보강"""
        prompt = f"""다음 분석을 더 상세하게 보강해주세요:

원래 질문: {state['query']}
기존 분석: {state['analysis']}

보강된 분석:"""

        response = model.invoke([HumanMessage(content=prompt)])

        return {"analysis": response.content}

    def finalize_node(state: AnalysisState) -> dict:
        """최종 출력 생성"""
        return {"final_output": state['analysis']}

    def route_after_analysis(state: AnalysisState) -> str:
        """분석 후 라우팅 결정"""
        if state['review_needed']:
            return "review"
        return "finalize"

    # 그래프 구성
    graph = StateGraph(AnalysisState)

    # 노드 추가
    graph.add_node("analyze", analyze_node)
    graph.add_node("review", review_node)
    graph.add_node("finalize", finalize_node)

    # 엣지 연결
    graph.add_edge(START, "analyze")

    # 조건부 엣지
    graph.add_conditional_edges(
        "analyze",
        route_after_analysis,
        {
            "review": "review",
            "finalize": "finalize"
        }
    )

    graph.add_edge("review", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()


# ============================================
# 4. 반복(Loop)이 있는 그래프
# ============================================

class IterativeState(TypedDict):
    """반복 워크플로우 상태"""
    task: str
    draft: str | None
    feedback: str | None
    iteration: int
    max_iterations: int
    is_approved: bool


def create_iterative_graph():
    """생성 → 검토 → 수정 반복 그래프"""

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    def generate_node(state: IterativeState) -> dict:
        """초안 생성"""
        if state['draft'] is None:
            # 첫 생성
            prompt = f"다음 주제에 대해 짧은 글을 작성하세요: {state['task']}"
        else:
            # 피드백 기반 수정
            prompt = f"""피드백을 반영하여 글을 수정하세요:

기존 글:
{state['draft']}

피드백:
{state['feedback']}

수정된 글:"""

        response = model.invoke([HumanMessage(content=prompt)])

        return {
            "draft": response.content,
            "iteration": state['iteration'] + 1
        }

    def review_node(state: IterativeState) -> dict:
        """검토 및 피드백 생성"""
        prompt = f"""다음 글을 검토하고 개선점을 제안하세요:

글:
{state['draft']}

검토 결과 (개선점이 없으면 "승인"이라고만 답하세요):"""

        response = model.invoke([HumanMessage(content=prompt)])
        feedback = response.content

        is_approved = "승인" in feedback or state['iteration'] >= state['max_iterations']

        return {
            "feedback": feedback,
            "is_approved": is_approved
        }

    def should_continue(state: IterativeState) -> str:
        """반복 여부 결정"""
        if state['is_approved']:
            return "end"
        return "generate"

    # 그래프 구성
    graph = StateGraph(IterativeState)

    graph.add_node("generate", generate_node)
    graph.add_node("review", review_node)

    graph.add_edge(START, "generate")
    graph.add_edge("generate", "review")

    graph.add_conditional_edges(
        "review",
        should_continue,
        {
            "generate": "generate",  # 다시 생성
            "end": END  # 종료
        }
    )

    return graph.compile()


# ============================================
# 5. Human-in-the-loop 그래프
# ============================================

class HumanInLoopState(TypedDict):
    """Human-in-the-loop 상태"""
    question: str
    ai_answer: str | None
    human_approved: bool | None
    final_answer: str | None


def create_human_in_loop_graph():
    """사람의 승인이 필요한 그래프"""

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    def generate_answer(state: HumanInLoopState) -> dict:
        """AI 답변 생성"""
        response = model.invoke([
            SystemMessage(content="간결하고 정확하게 답변하세요."),
            HumanMessage(content=state['question'])
        ])
        return {"ai_answer": response.content}

    def check_approval(state: HumanInLoopState) -> str:
        """승인 여부 확인"""
        if state['human_approved']:
            return "approve"
        return "reject"

    def approve_node(state: HumanInLoopState) -> dict:
        """승인된 답변 최종 확정"""
        return {"final_answer": state['ai_answer']}

    def reject_node(state: HumanInLoopState) -> dict:
        """거부 시 재생성 필요 표시"""
        return {"ai_answer": None}

    # 그래프 구성
    graph = StateGraph(HumanInLoopState)

    graph.add_node("generate", generate_answer)
    graph.add_node("approve", approve_node)
    graph.add_node("reject", reject_node)

    graph.add_edge(START, "generate")

    # 사람 검토 후 분기 (interrupt_before 사용)
    graph.add_conditional_edges(
        "generate",
        check_approval,
        {
            "approve": "approve",
            "reject": "reject"
        }
    )

    graph.add_edge("approve", END)
    graph.add_edge("reject", "generate")  # 재생성

    # 체크포인트로 컴파일 (Human-in-the-loop 필수)
    checkpointer = MemorySaver()
    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["generate"]  # generate 노드 전에 중단
    )


# ============================================
# 6. 병렬 처리 그래프
# ============================================

class ParallelState(TypedDict):
    """병렬 처리 상태"""
    text: str
    sentiment: str | None
    keywords: list | None
    summary: str | None
    combined_result: dict | None


def create_parallel_graph():
    """여러 분석을 병렬로 수행하는 그래프"""

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def sentiment_node(state: ParallelState) -> dict:
        """감성 분석"""
        response = model.invoke([
            HumanMessage(content=f"다음 텍스트의 감성(긍정/부정/중립)을 한 단어로: {state['text']}")
        ])
        return {"sentiment": response.content.strip()}

    def keywords_node(state: ParallelState) -> dict:
        """키워드 추출"""
        response = model.invoke([
            HumanMessage(content=f"다음 텍스트의 핵심 키워드 3개를 쉼표로 구분: {state['text']}")
        ])
        keywords = [k.strip() for k in response.content.split(",")]
        return {"keywords": keywords}

    def summary_node(state: ParallelState) -> dict:
        """요약"""
        response = model.invoke([
            HumanMessage(content=f"다음 텍스트를 한 문장으로 요약: {state['text']}")
        ])
        return {"summary": response.content.strip()}

    def combine_node(state: ParallelState) -> dict:
        """결과 통합"""
        return {
            "combined_result": {
                "sentiment": state['sentiment'],
                "keywords": state['keywords'],
                "summary": state['summary']
            }
        }

    # 그래프 구성
    graph = StateGraph(ParallelState)

    # 병렬 노드 추가
    graph.add_node("sentiment", sentiment_node)
    graph.add_node("keywords", keywords_node)
    graph.add_node("summary", summary_node)
    graph.add_node("combine", combine_node)

    # START에서 3개 노드로 분기 (병렬 실행)
    graph.add_edge(START, "sentiment")
    graph.add_edge(START, "keywords")
    graph.add_edge(START, "summary")

    # 3개 노드 모두 combine으로 연결
    graph.add_edge("sentiment", "combine")
    graph.add_edge("keywords", "combine")
    graph.add_edge("summary", "combine")

    graph.add_edge("combine", END)

    return graph.compile()


# ============================================
# 실행 예제
# ============================================

if __name__ == "__main__":
    # 예제 1: 기본 그래프
    print("=== 기본 그래프 ===")
    basic_app = create_basic_graph()
    result = basic_app.invoke({"input": "hello world", "output": ""})
    print(f"결과: {result['output']}")
    print()

    # 예제 2: LLM 분석 그래프
    print("=== LLM 분석 그래프 ===")
    llm_app = create_llm_graph()
    result = llm_app.invoke({
        "query": "AI Agent의 장점은 무엇인가요?",
        "analysis": None,
        "review_needed": False,
        "final_output": None
    })
    print(f"최종 분석:\n{result['final_output'][:300]}...")
    print()

    # 예제 3: 반복 그래프
    print("=== 반복 그래프 ===")
    iterative_app = create_iterative_graph()
    result = iterative_app.invoke({
        "task": "인공지능의 미래",
        "draft": None,
        "feedback": None,
        "iteration": 0,
        "max_iterations": 2,
        "is_approved": False
    })
    print(f"최종 초안 (반복 {result['iteration']}회):\n{result['draft'][:300]}...")
    print()

    # 예제 4: 병렬 처리 그래프
    print("=== 병렬 처리 그래프 ===")
    parallel_app = create_parallel_graph()
    result = parallel_app.invoke({
        "text": "AI 기술이 급격히 발전하면서 다양한 산업에서 혁신이 일어나고 있다. 특히 자연어 처리 분야의 발전이 두드러진다.",
        "sentiment": None,
        "keywords": None,
        "summary": None,
        "combined_result": None
    })
    print(f"통합 결과: {result['combined_result']}")
