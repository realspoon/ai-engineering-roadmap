"""
Track A: Data Analyst Agent - 핵심 Agent 구현
=============================================
자연어 → 분석 계획 → 실행 → 시각화 → 인사이트

실행 전:
pip install langchain langchain-openai langgraph pandas matplotlib seaborn
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
from typing import TypedDict, Annotated, Literal
from operator import add
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ============================================
# 1. State 정의
# ============================================

class AnalysisState(TypedDict):
    """Data Analyst Agent 상태"""
    # 입력
    user_query: str
    data: pd.DataFrame | None

    # 분석 과정
    query_intent: dict | None
    analysis_plan: list | None
    analysis_code: str | None
    analysis_result: str | None

    # 출력
    visualization_code: str | None
    insights: str | None
    error: str | None


# ============================================
# 2. 노드 함수들
# ============================================

def understand_query(state: AnalysisState) -> dict:
    """사용자 질의 의도 분석"""

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""사용자의 데이터 분석 요청을 분석하세요.

사용자 질의: {state['user_query']}

데이터 컬럼: {list(state['data'].columns) if state['data'] is not None else '없음'}
데이터 샘플: {state['data'].head(3).to_string() if state['data'] is not None else '없음'}

다음 JSON 형식으로 분석 의도를 파악하세요:
{{
    "intent_type": "descriptive|comparative|trend|correlation|prediction",
    "target_columns": ["분석 대상 컬럼들"],
    "group_by": "그룹화 기준 컬럼 (있으면)",
    "time_column": "시간 컬럼 (있으면)",
    "filters": {{"컬럼": "조건"}},
    "aggregations": ["sum|mean|count|max|min"],
    "visualization_type": "bar|line|scatter|pie|heatmap|histogram"
}}

JSON만 출력:"""

    response = model.invoke([HumanMessage(content=prompt)])

    try:
        import json
        intent = json.loads(response.content)
    except:
        intent = {"intent_type": "descriptive", "error": "파싱 실패"}

    return {"query_intent": intent}


def create_analysis_plan(state: AnalysisState) -> dict:
    """분석 계획 수립"""

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""데이터 분석 계획을 수립하세요.

사용자 질의: {state['user_query']}
분석 의도: {state['query_intent']}
데이터 컬럼: {list(state['data'].columns) if state['data'] is not None else []}

다음 형식으로 단계별 분석 계획을 작성하세요:
[
    {{"step": 1, "action": "동작", "description": "설명", "code_hint": "pandas 코드 힌트"}},
    ...
]

JSON 배열만 출력:"""

    response = model.invoke([HumanMessage(content=prompt)])

    try:
        import json
        plan = json.loads(response.content)
    except:
        plan = [{"step": 1, "action": "기본 분석", "description": "기본 통계", "code_hint": "df.describe()"}]

    return {"analysis_plan": plan}


def generate_analysis_code(state: AnalysisState) -> dict:
    """분석 코드 생성"""

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""pandas를 사용한 데이터 분석 코드를 생성하세요.

사용자 질의: {state['user_query']}
분석 계획: {state['analysis_plan']}
데이터프레임 변수명: df
데이터 컬럼: {list(state['data'].columns) if state['data'] is not None else []}
데이터 타입: {state['data'].dtypes.to_dict() if state['data'] is not None else {{}}}

요구사항:
- 분석 결과를 'result' 변수에 저장
- 중간 과정은 주석으로 설명
- 에러 처리 포함

Python 코드만 출력 (```python 태그 없이):"""

    response = model.invoke([HumanMessage(content=prompt)])
    code = response.content.strip()

    # 코드 블록 태그 제거
    if code.startswith("```"):
        code = "\n".join(code.split("\n")[1:-1])

    return {"analysis_code": code}


def execute_analysis(state: AnalysisState) -> dict:
    """분석 코드 실행"""

    try:
        df = state['data']
        local_vars = {"df": df, "pd": pd}

        exec(state['analysis_code'], {"pd": pd, "np": __import__('numpy')}, local_vars)

        result = local_vars.get('result', "결과 없음")

        if isinstance(result, pd.DataFrame):
            result_str = result.to_string()
        elif isinstance(result, pd.Series):
            result_str = result.to_string()
        else:
            result_str = str(result)

        return {"analysis_result": result_str}

    except Exception as e:
        return {"error": f"분석 실행 오류: {str(e)}"}


def generate_visualization(state: AnalysisState) -> dict:
    """시각화 코드 생성"""

    if state.get('error'):
        return {"visualization_code": "# 에러로 인해 시각화 생략"}

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""matplotlib/seaborn을 사용한 시각화 코드를 생성하세요.

분석 결과: {state['analysis_result'][:1000]}
시각화 유형: {state['query_intent'].get('visualization_type', 'bar')}

요구사항:
- 한글 폰트 설정 포함
- 적절한 제목과 레이블
- figure 크기 (10, 6)
- plt.tight_layout() 호출
- plt.savefig('analysis_chart.png') 포함

Python 코드만 출력:"""

    response = model.invoke([HumanMessage(content=prompt)])
    code = response.content.strip()

    if code.startswith("```"):
        code = "\n".join(code.split("\n")[1:-1])

    return {"visualization_code": code}


def generate_insights(state: AnalysisState) -> dict:
    """인사이트 생성"""

    if state.get('error'):
        return {"insights": f"분석 중 오류 발생: {state['error']}"}

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    prompt = f"""데이터 분석 결과를 바탕으로 비즈니스 인사이트를 도출하세요.

사용자 질의: {state['user_query']}
분석 결과:
{state['analysis_result'][:2000]}

다음 형식으로 인사이트를 작성하세요:

## 📊 분석 요약
(2-3문장으로 핵심 내용 요약)

## 🔍 주요 발견
1. (첫 번째 인사이트)
2. (두 번째 인사이트)
3. (세 번째 인사이트)

## 💡 권장 액션
- (실행 가능한 제안 1)
- (실행 가능한 제안 2)

## ❓ 추가 분석 제안
- (더 깊이 살펴볼 수 있는 분석)"""

    response = model.invoke([HumanMessage(content=prompt)])

    return {"insights": response.content}


def should_continue(state: AnalysisState) -> str:
    """에러 발생 시 분기"""
    if state.get('error'):
        return "error"
    return "continue"


# ============================================
# 3. Agent 그래프 구성
# ============================================

def create_data_analyst_agent():
    """Data Analyst Agent 생성"""

    graph = StateGraph(AnalysisState)

    # 노드 추가
    graph.add_node("understand", understand_query)
    graph.add_node("plan", create_analysis_plan)
    graph.add_node("code", generate_analysis_code)
    graph.add_node("execute", execute_analysis)
    graph.add_node("visualize", generate_visualization)
    graph.add_node("insights", generate_insights)

    # 엣지 연결
    graph.add_edge(START, "understand")
    graph.add_edge("understand", "plan")
    graph.add_edge("plan", "code")
    graph.add_edge("code", "execute")

    # 조건부 엣지 (에러 처리)
    graph.add_conditional_edges(
        "execute",
        should_continue,
        {
            "continue": "visualize",
            "error": "insights"  # 에러 시 인사이트로 바로 이동
        }
    )

    graph.add_edge("visualize", "insights")
    graph.add_edge("insights", END)

    return graph.compile()


# ============================================
# 4. 사용하기 쉬운 래퍼 클래스
# ============================================

class DataAnalystAgent:
    """Data Analyst Agent 래퍼 클래스"""

    def __init__(self):
        self.agent = create_data_analyst_agent()

    def analyze(self, query: str, data: pd.DataFrame) -> dict:
        """
        데이터 분석 수행

        Args:
            query: 자연어 분석 요청
            data: 분석할 DataFrame

        Returns:
            분석 결과 딕셔너리
        """
        initial_state = {
            "user_query": query,
            "data": data,
            "query_intent": None,
            "analysis_plan": None,
            "analysis_code": None,
            "analysis_result": None,
            "visualization_code": None,
            "insights": None,
            "error": None
        }

        result = self.agent.invoke(initial_state)

        return {
            "query_intent": result.get("query_intent"),
            "analysis_plan": result.get("analysis_plan"),
            "analysis_code": result.get("analysis_code"),
            "analysis_result": result.get("analysis_result"),
            "visualization_code": result.get("visualization_code"),
            "insights": result.get("insights"),
            "error": result.get("error")
        }


# ============================================
# 5. 샘플 데이터 및 테스트
# ============================================

def create_sample_data() -> pd.DataFrame:
    """테스트용 샘플 데이터 생성"""
    import numpy as np

    np.random.seed(42)

    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    categories = ['전자제품', '의류', '식품', '가전']

    data = {
        'date': np.random.choice(dates, 400),
        'category': np.random.choice(categories, 400),
        'sales': np.random.randint(10000, 100000, 400),
        'quantity': np.random.randint(1, 50, 400),
        'region': np.random.choice(['서울', '부산', '대구', '인천'], 400)
    }

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    return df


if __name__ == "__main__":
    # 샘플 데이터 생성
    print("=== 샘플 데이터 생성 ===")
    df = create_sample_data()
    print(df.head())
    print(f"\n데이터 크기: {df.shape}")
    print()

    # Agent 생성
    agent = DataAnalystAgent()

    # 테스트 쿼리들
    queries = [
        "카테고리별 총 매출을 비교해줘",
        "월별 매출 트렌드를 분석해줘",
        "지역별 판매량 분포를 보여줘"
    ]

    for query in queries[:1]:  # 첫 번째만 테스트
        print(f"\n{'='*60}")
        print(f"질의: {query}")
        print('='*60)

        result = agent.analyze(query, df)

        print("\n[분석 의도]")
        print(result['query_intent'])

        print("\n[분석 코드]")
        print(result['analysis_code'][:500] if result['analysis_code'] else "없음")

        print("\n[분석 결과]")
        print(result['analysis_result'][:500] if result['analysis_result'] else "없음")

        print("\n[인사이트]")
        print(result['insights'] if result['insights'] else "없음")

        if result['error']:
            print(f"\n[에러] {result['error']}")
