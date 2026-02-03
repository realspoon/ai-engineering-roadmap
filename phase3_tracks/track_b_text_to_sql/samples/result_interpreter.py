"""
Result Interpreter Module
SQL 쿼리 결과를 자연어로 해석 및 설명
"""

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import json
from enum import Enum
import statistics


class ResultType(Enum):
    """결과 타입"""
    SINGLE_VALUE = "single_value"
    AGGREGATION = "aggregation"
    LIST = "list"
    TABLE = "table"
    COMPARISON = "comparison"
    DISTRIBUTION = "distribution"


@dataclass
class QueryResult:
    """쿼리 결과"""
    query: str
    rows: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time: float = 0.0


class ResultAnalyzer:
    """결과 분석"""

    def __init__(self, result: QueryResult):
        self.result = result
        self.analysis = {}

    def analyze(self) -> Dict[str, Any]:
        """결과 분석"""
        analysis = {
            'result_type': self._determine_result_type(),
            'row_count': self.result.row_count,
            'columns': self.result.columns,
            'statistics': self._calculate_statistics(),
            'insights': self._extract_insights()
        }

        return analysis

    def _determine_result_type(self) -> str:
        """결과 타입 판단"""
        if self.result.row_count == 0:
            return ResultType.LIST.value

        if self.result.row_count == 1 and len(self.result.columns) == 1:
            return ResultType.SINGLE_VALUE.value

        if len(self.result.columns) == 1:
            return ResultType.LIST.value

        if self._is_aggregation_result():
            return ResultType.AGGREGATION.value

        return ResultType.TABLE.value

    def _is_aggregation_result(self) -> bool:
        """집계 결과 판단"""
        agg_keywords = ['count', 'sum', 'avg', 'min', 'max']
        query_lower = self.result.query.lower()

        return any(kw in query_lower for kw in agg_keywords)

    def _calculate_statistics(self) -> Dict[str, Any]:
        """통계 계산"""
        stats = {}

        if self.result.row_count == 0:
            return stats

        # 수치형 컬럼 통계
        for col in self.result.columns:
            try:
                values = [
                    float(row[col]) for row in self.result.rows
                    if row[col] is not None and str(row[col]).replace('.', '', 1).isdigit()
                ]

                if values:
                    stats[col] = {
                        'min': min(values),
                        'max': max(values),
                        'avg': statistics.mean(values),
                        'median': statistics.median(values),
                        'total': sum(values),
                        'count': len(values)
                    }
            except (ValueError, TypeError):
                pass

        return stats

    def _extract_insights(self) -> List[str]:
        """인사이트 추출"""
        insights = []

        if self.result.row_count == 0:
            insights.append("결과가 없습니다")
            return insights

        # 행 수 인사이트
        if self.result.row_count == 1:
            insights.append("정확히 1개 행이 반환되었습니다")
        elif self.result.row_count < 10:
            insights.append(f"적은 수({self.result.row_count}개)의 결과가 반환되었습니다")
        elif self.result.row_count > 1000:
            insights.append(f"많은 수({self.result.row_count}개)의 결과가 반환되었습니다")

        # 컬럼별 인사이트
        for col, stats in self.analysis.get('statistics', {}).items():
            if stats['count'] > 0:
                # NULL 값 비율
                null_count = self.result.row_count - stats['count']
                if null_count > 0:
                    null_pct = (null_count / self.result.row_count) * 100
                    insights.append(f"{col}: {null_pct:.1f}%의 NULL 값")

                # 범위
                if stats['max'] - stats['min'] > 0:
                    insights.append(
                        f"{col}: {stats['min']} ~ {stats['max']} 범위"
                    )

        return insights


class NaturalLanguageInterpreter:
    """자연언어 해석"""

    def __init__(self, query: str, result: QueryResult, analyzer: ResultAnalyzer):
        self.query = query
        self.result = result
        self.analyzer = analyzer

    def generate_explanation(self) -> str:
        """설명 생성"""
        explanation = self._generate_summary()

        if self.result.row_count > 0:
            explanation += "\n\n" + self._generate_details()

        return explanation

    def _generate_summary(self) -> str:
        """요약 생성"""
        analysis = self.analyzer.analysis

        if self.result.row_count == 0:
            return "쿼리 결과가 없습니다. 조건을 확인하세요."

        # 결과 타입별 요약
        result_type = analysis['result_type']

        if result_type == ResultType.SINGLE_VALUE.value:
            value = self.result.rows[0][self.result.columns[0]]
            return f"결과: {value}"

        elif result_type == ResultType.AGGREGATION.value:
            return self._generate_aggregation_summary()

        elif result_type == ResultType.LIST.value:
            col = self.result.columns[0]
            values = [row[col] for row in self.result.rows]
            return f"{col}: {', '.join(str(v) for v in values[:5])}"

        else:
            return f"{self.result.row_count}개 행이 반환되었습니다."

    def _generate_aggregation_summary(self) -> str:
        """집계 결과 요약"""
        col = self.result.columns[0]
        stats = self.analyzer.analysis['statistics'].get(col, {})

        if 'total' in stats:
            return f"합계: {stats['total']:.0f}"
        elif 'count' in stats:
            return f"개수: {stats['count']}"

        value = self.result.rows[0][col]
        return f"결과: {value}"

    def _generate_details(self) -> str:
        """상세 정보 생성"""
        details = []

        details.append(f"반환 행 수: {self.result.row_count}개")

        # 통계 정보
        for col, stats in self.analyzer.analysis.get('statistics', {}).items():
            detail_str = f"{col}: "

            if 'total' in stats:
                detail_str += f"합계={stats['total']:.0f}, "

            if 'avg' in stats:
                detail_str += f"평균={stats['avg']:.2f}, "

            if 'min' in stats and 'max' in stats:
                detail_str += f"범위=[{stats['min']}, {stats['max']}]"

            details.append(detail_str)

        # 인사이트
        for insight in self.analyzer.analysis.get('insights', []):
            details.append(f"• {insight}")

        return '\n'.join(details)

    def generate_visualization_suggestion(self) -> Dict[str, str]:
        """시각화 제안"""
        result_type = self.analyzer.analysis['result_type']

        suggestions = {
            ResultType.SINGLE_VALUE.value: {
                'chart_type': 'metric',
                'description': '단일 값 표시'
            },
            ResultType.AGGREGATION.value: {
                'chart_type': 'card',
                'description': '집계 결과 표시'
            },
            ResultType.LIST.value: {
                'chart_type': 'bar',
                'description': '값 목록을 막대 차트로 표시'
            },
            ResultType.TABLE.value: {
                'chart_type': 'table',
                'description': '테이블 형태로 표시'
            },
            ResultType.COMPARISON.value: {
                'chart_type': 'bar',
                'description': '비교 차트 표시'
            },
            ResultType.DISTRIBUTION.value: {
                'chart_type': 'histogram',
                'description': '분포 히스토그램'
            }
        }

        return suggestions.get(result_type, {
            'chart_type': 'table',
            'description': '데이터를 테이블로 표시'
        })


class ResultFormatter:
    """결과 포맷팅"""

    @staticmethod
    def format_as_text(result: QueryResult) -> str:
        """텍스트로 포맷"""
        if result.row_count == 0:
            return "결과 없음"

        # 테이블 형식
        lines = []

        # 헤더
        header = " | ".join(result.columns)
        lines.append(header)
        lines.append("-" * len(header))

        # 데이터
        for row in result.rows[:10]:  # 처음 10개만
            values = [str(row.get(col, 'NULL')) for col in result.columns]
            lines.append(" | ".join(values))

        if result.row_count > 10:
            lines.append(f"... 외 {result.row_count - 10}개 행")

        return '\n'.join(lines)

    @staticmethod
    def format_as_json(result: QueryResult) -> str:
        """JSON으로 포맷"""
        return json.dumps({
            'row_count': result.row_count,
            'columns': result.columns,
            'data': result.rows
        }, indent=2, ensure_ascii=False)

    @staticmethod
    def format_as_markdown(result: QueryResult) -> str:
        """Markdown으로 포맷"""
        if result.row_count == 0:
            return "결과 없음"

        lines = []

        # 테이블 헤더
        lines.append("| " + " | ".join(result.columns) + " |")
        lines.append("|" + "|".join(["---"] * len(result.columns)) + "|")

        # 테이블 데이터
        for row in result.rows[:10]:
            values = [str(row.get(col, 'NULL')) for col in result.columns]
            lines.append("| " + " | ".join(values) + " |")

        if result.row_count > 10:
            lines.append(f"\n*... 외 {result.row_count - 10}개 행*")

        return '\n'.join(lines)

    @staticmethod
    def format_as_html(result: QueryResult) -> str:
        """HTML로 포맷"""
        html = ["<table>"]

        # 헤더
        html.append("<thead><tr>")
        for col in result.columns:
            html.append(f"<th>{col}</th>")
        html.append("</tr></thead>")

        # 바디
        html.append("<tbody>")
        for row in result.rows:
            html.append("<tr>")
            for col in result.columns:
                value = row.get(col, 'NULL')
                html.append(f"<td>{value}</td>")
            html.append("</tr>")
        html.append("</tbody>")

        html.append("</table>")

        return '\n'.join(html)


class ResultInterpreterPipeline:
    """결과 해석 파이프라인"""

    def __init__(self, query: str, result: QueryResult):
        self.query = query
        self.result = result
        self.analyzer = ResultAnalyzer(result)
        self.interpreter = NaturalLanguageInterpreter(
            query, result, self.analyzer
        )

    def process(self) -> Dict[str, Any]:
        """전체 처리"""
        analysis = self.analyzer.analyze()

        return {
            'query': self.query,
            'analysis': analysis,
            'explanation': self.interpreter.generate_explanation(),
            'visualization_suggestion': self.interpreter.generate_visualization_suggestion(),
            'formatted': {
                'text': ResultFormatter.format_as_text(self.result),
                'markdown': ResultFormatter.format_as_markdown(self.result),
                'json': ResultFormatter.format_as_json(self.result)
            }
        }


class ConversationalResultInterpreter:
    """대화형 결과 해석"""

    def __init__(self):
        self.last_result = None
        self.conversation = []

    def interpret_result(self, query: str, result: QueryResult) -> str:
        """결과 해석 및 대답 생성"""
        self.last_result = result

        pipeline = ResultInterpreterPipeline(query, result)
        processed = pipeline.process()

        explanation = processed['explanation']

        # 대화 기록
        self.conversation.append({
            'query': query,
            'explanation': explanation
        })

        return explanation

    def ask_followup_question(self, question: str) -> str:
        """후속 질문 처리"""
        if not self.last_result:
            return "먼저 데이터를 조회하세요"

        question_lower = question.lower()

        # 질문 타입 판단
        if any(kw in question_lower for kw in ['다시', '다르게', '또다른']):
            return "다른 쿼리를 실행해주세요"

        elif any(kw in question_lower for kw in ['상세', '자세히', '더']):
            return self._generate_detailed_explanation()

        elif any(kw in question_lower for kw in ['시각화', '차트', '그래프']):
            return "이 데이터는 막대 차트로 시각화하면 좋을 것 같습니다"

        elif any(kw in question_lower for kw in ['비교', '다른']):
            return "비교를 위해 추가 조회가 필요합니다"

        return "알겠습니다. 추가 질문이 있으신가요?"

    def _generate_detailed_explanation(self) -> str:
        """상세 설명 생성"""
        if not self.last_result:
            return ""

        analyzer = ResultAnalyzer(self.last_result)
        analysis = analyzer.analyze()

        details = [
            f"총 {self.last_result.row_count}개 행이 반환되었습니다.",
            f"컬럼: {', '.join(self.last_result.columns)}"
        ]

        for col, stats in analysis['statistics'].items():
            if 'count' in stats:
                details.append(f"\n{col} 통계:")
                if 'min' in stats:
                    details.append(f"  최소값: {stats['min']}")
                if 'max' in stats:
                    details.append(f"  최대값: {stats['max']}")
                if 'avg' in stats:
                    details.append(f"  평균: {stats['avg']:.2f}")

        return '\n'.join(details)


# 사용 예제
if __name__ == "__main__":
    print("=== 결과 해석 및 자연어 생성 ===\n")

    # 샘플 결과
    sample_result = QueryResult(
        query="SELECT department, AVG(salary) FROM employees GROUP BY department",
        rows=[
            {'department': 'Sales', 'AVG(salary)': 55000},
            {'department': 'IT', 'AVG(salary)': 75000},
            {'department': 'HR', 'AVG(salary)': 50000}
        ],
        columns=['department', 'AVG(salary)'],
        row_count=3
    )

    # 파이프라인 처리
    pipeline = ResultInterpreterPipeline(
        sample_result.query,
        sample_result
    )
    result = pipeline.process()

    print("=" * 50)
    print("쿼리 해석 결과")
    print("=" * 50)

    print(f"\n원본 쿼리:\n{sample_result.query}\n")

    print(f"설명:\n{result['explanation']}\n")

    print(f"시각화 제안:")
    print(f"  타입: {result['visualization_suggestion']['chart_type']}")
    print(f"  설명: {result['visualization_suggestion']['description']}\n")

    print("포맷된 결과 (텍스트):")
    print(result['formatted']['text'])

    print("\n\nMarkdown 형식:")
    print(result['formatted']['markdown'])

    # 대화형 해석
    print("\n" + "=" * 50)
    print("대화형 해석")
    print("=" * 50)

    conversational = ConversationalResultInterpreter()
    explanation = conversational.interpret_result(
        sample_result.query,
        sample_result
    )
    print(f"\n해석: {explanation}")

    followup = conversational.ask_followup_question("더 자세히 알려줄래?")
    print(f"후속 답변: {followup}")
