"""
Week 14: LLM Testing, Evaluation Metrics, and Guardrails
LLM 테스팅, 평가 메트릭, 그리고 Guardrails 구현
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod


class MetricType(Enum):
    """평가 메트릭 타입"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    BLEU = "bleu"
    ROUGE = "rouge"
    LATENCY = "latency"
    COST = "cost"


class GuardrailType(Enum):
    """가드레일 타입"""
    CONTENT_FILTER = "content_filter"
    OUTPUT_FORMAT = "output_format"
    SAFETY_CHECK = "safety_check"
    RATE_LIMIT = "rate_limit"
    TOKEN_LIMIT = "token_limit"


@dataclass
class TestCase:
    """테스트 케이스"""
    id: str
    input: str
    expected_output: str
    category: str = "general"
    priority: str = "normal"  # critical, high, normal, low
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """테스트 결과"""
    test_case_id: str
    actual_output: str
    passed: bool
    score: float
    execution_time: float  # 밀리초
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class GuardrailConfig:
    """가드레일 설정"""
    type: GuardrailType
    enabled: bool = True
    severity: str = "warning"  # warning, error, critical
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardrailViolation:
    """가드레일 위반"""
    guardrail_type: GuardrailType
    severity: str
    message: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class Metric(ABC):
    """평가 메트릭의 기본 클래스"""

    def __init__(self, name: str):
        self.name = name
        self.values: List[float] = []

    @abstractmethod
    def calculate(self, prediction: str, reference: str) -> float:
        """메트릭 계산"""
        pass

    def add_value(self, value: float) -> None:
        """값 추가"""
        self.values.append(value)

    def get_average(self) -> float:
        """평균값 반환"""
        if not self.values:
            return 0.0
        return sum(self.values) / len(self.values)

    def get_stats(self) -> Dict[str, float]:
        """통계 정보"""
        if not self.values:
            return {"count": 0, "average": 0.0, "min": 0.0, "max": 0.0}

        return {
            "count": len(self.values),
            "average": self.get_average(),
            "min": min(self.values),
            "max": max(self.values),
            "sum": sum(self.values)
        }


class ExactMatchMetric(Metric):
    """정확히 일치하는지 확인하는 메트릭"""

    def __init__(self):
        super().__init__("exact_match")

    def calculate(self, prediction: str, reference: str) -> float:
        """정확히 일치하면 1.0, 아니면 0.0"""
        score = 1.0 if prediction.strip() == reference.strip() else 0.0
        self.add_value(score)
        return score


class SimilarityMetric(Metric):
    """유사도 메트릭 (간단한 구현)"""

    def __init__(self):
        super().__init__("similarity")

    def _jaccard_similarity(self, s1: str, s2: str) -> float:
        """Jaccard 유사도 계산"""
        set1 = set(s1.lower().split())
        set2 = set(s2.lower().split())

        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def calculate(self, prediction: str, reference: str) -> float:
        """유사도 계산"""
        score = self._jaccard_similarity(prediction, reference)
        self.add_value(score)
        return score


class LengthPenaltyMetric(Metric):
    """길이 차이에 따른 페널티"""

    def __init__(self, max_length: int = 500):
        super().__init__("length_penalty")
        self.max_length = max_length

    def calculate(self, prediction: str, reference: str) -> float:
        """길이 차이 페널티"""
        pred_len = len(prediction)
        ref_len = len(reference)

        diff = abs(pred_len - ref_len)
        penalty = 1.0 - (diff / self.max_length)
        score = max(0.0, penalty)

        self.add_value(score)
        return score


class Guardrail(ABC):
    """가드레일의 기본 클래스"""

    def __init__(self, config: GuardrailConfig):
        self.config = config
        self.violations: List[GuardrailViolation] = []

    @abstractmethod
    def check(self, content: str) -> Tuple[bool, Optional[str]]:
        """가드레일 검사"""
        pass

    def record_violation(self, message: str, content: str) -> None:
        """위반 기록"""
        violation = GuardrailViolation(
            guardrail_type=self.config.type,
            severity=self.config.severity,
            message=message,
            content=content
        )
        self.violations.append(violation)

    def get_violations(self) -> List[GuardrailViolation]:
        """위반 목록"""
        return self.violations


class ContentFilterGuardrail(Guardrail):
    """콘텐츠 필터 가드레일"""

    def __init__(self):
        config = GuardrailConfig(
            type=GuardrailType.CONTENT_FILTER,
            description="해로운 콘텐츠를 필터링합니다"
        )
        super().__init__(config)

        self.harmful_keywords = [
            "violence", "hate", "illegal", "harmful",
            "폭력", "증오", "불법", "해로운"
        ]

    def check(self, content: str) -> Tuple[bool, Optional[str]]:
        """해로운 콘텐츠 확인"""
        content_lower = content.lower()

        for keyword in self.harmful_keywords:
            if keyword in content_lower:
                message = f"해로운 콘텐츠 감지: '{keyword}'"
                self.record_violation(message, content)
                return False, message

        return True, None


class OutputFormatGuardrail(Guardrail):
    """출력 형식 가드레일"""

    def __init__(self, expected_format: str = "json"):
        config = GuardrailConfig(
            type=GuardrailType.OUTPUT_FORMAT,
            description=f"출력 형식이 {expected_format}이어야 합니다"
        )
        super().__init__(config)
        self.expected_format = expected_format

    def check(self, content: str) -> Tuple[bool, Optional[str]]:
        """출력 형식 확인"""
        if self.expected_format == "json":
            try:
                json.loads(content)
                return True, None
            except json.JSONDecodeError as e:
                message = f"JSON 형식 오류: {str(e)}"
                self.record_violation(message, content)
                return False, message

        elif self.expected_format == "xml":
            if content.strip().startswith("<") and content.strip().endswith(">"):
                return True, None
            else:
                message = "XML 형식이 아닙니다"
                self.record_violation(message, content)
                return False, message

        return True, None


class SafetyCheckGuardrail(Guardrail):
    """안전성 검사 가드레일"""

    def __init__(self):
        config = GuardrailConfig(
            type=GuardrailType.SAFETY_CHECK,
            description="출력이 안전한지 확인합니다"
        )
        super().__init__(config)

    def check(self, content: str) -> Tuple[bool, Optional[str]]:
        """안전성 검사"""
        # 기본적인 안전성 검사
        unsafe_patterns = [
            r".*\$\{.*\}.*",  # 템플릿 인젝션
            r".*<script.*>.*",  # XSS
            r".*DROP\s+TABLE.*",  # SQL 인젝션
        ]

        for pattern in unsafe_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                message = f"안전하지 않은 패턴 감지: {pattern}"
                self.record_violation(message, content)
                return False, message

        return True, None


class TokenLimitGuardrail(Guardrail):
    """토큰 제한 가드레일"""

    def __init__(self, max_tokens: int = 2000):
        config = GuardrailConfig(
            type=GuardrailType.TOKEN_LIMIT,
            description=f"최대 토큰 수: {max_tokens}"
        )
        super().__init__(config)
        self.max_tokens = max_tokens

    def check(self, content: str) -> Tuple[bool, Optional[str]]:
        """토큰 수 확인"""
        # 간단한 토큰 카운트: 단어 + 문장 부호
        token_count = len(content.split())

        if token_count > self.max_tokens:
            message = f"토큰 초과: {token_count} > {self.max_tokens}"
            self.record_violation(message, content)
            return False, message

        return True, None


class TestSuite:
    """테스트 스위트"""

    def __init__(self, name: str):
        self.name = name
        self.test_cases: Dict[str, TestCase] = {}
        self.results: List[TestResult] = []
        self.metrics: Dict[str, Metric] = {}
        self.guardrails: List[Guardrail] = []

    def add_test_case(self, test_case: TestCase) -> None:
        """테스트 케이스 추가"""
        self.test_cases[test_case.id] = test_case

    def add_metric(self, metric: Metric) -> None:
        """메트릭 추가"""
        self.metrics[metric.name] = metric

    def add_guardrail(self, guardrail: Guardrail) -> None:
        """가드레일 추가"""
        self.guardrails.append(guardrail)

    def run_guardrails(self, content: str) -> Tuple[bool, List[GuardrailViolation]]:
        """모든 가드레일 실행"""
        violations = []
        passed = True

        for guardrail in self.guardrails:
            if not guardrail.config.enabled:
                continue

            success, message = guardrail.check(content)

            if not success:
                passed = False
                violations.extend(guardrail.violations[-1:])

        return passed, violations

    def run_test(self, test_case_id: str, actual_output: str,
                execution_time: float) -> TestResult:
        """테스트 실행"""
        test_case = self.test_cases.get(test_case_id)
        if not test_case:
            raise ValueError(f"테스트 케이스를 찾을 수 없습니다: {test_case_id}")

        # 가드레일 검사
        guardrails_passed, violations = self.run_guardrails(actual_output)

        if not guardrails_passed:
            return TestResult(
                test_case_id=test_case_id,
                actual_output=actual_output,
                passed=False,
                score=0.0,
                execution_time=execution_time,
                error="가드레일 위반",
                metrics={}
            )

        # 메트릭 계산
        metrics = {}
        total_score = 0.0

        for metric_name, metric in self.metrics.items():
            score = metric.calculate(actual_output, test_case.expected_output)
            metrics[metric_name] = score
            total_score += score

        average_score = total_score / len(self.metrics) if self.metrics else 0.0

        # 결과 저장
        result = TestResult(
            test_case_id=test_case_id,
            actual_output=actual_output,
            passed=average_score >= 0.7,
            score=average_score,
            execution_time=execution_time,
            metrics=metrics
        )

        self.results.append(result)
        return result

    def get_summary(self) -> Dict[str, Any]:
        """테스트 요약"""
        if not self.results:
            return {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0.0}

        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        avg_score = sum(r.score for r in self.results) / total if total > 0 else 0.0
        avg_time = sum(r.execution_time for r in self.results) / total if total > 0 else 0.0

        return {
            "name": self.name,
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "average_score": avg_score,
            "average_execution_time_ms": avg_time,
            "metric_stats": {
                name: metric.get_stats()
                for name, metric in self.metrics.items()
            }
        }


def main():
    """메인 함수"""

    print("="*60)
    print("LLM 테스팅, 평가 메트릭, Guardrails")
    print("="*60)

    # 테스트 스위트 생성
    test_suite = TestSuite("AI Agent Testing")

    # 테스트 케이스 추가
    test_cases = [
        TestCase(
            id="test_001",
            input="1 + 1의 답은?",
            expected_output="1 + 1 = 2",
            category="math"
        ),
        TestCase(
            id="test_002",
            input="Python의 장점은?",
            expected_output="Python은 간단한 문법, 풍부한 라이브러리를 제공합니다",
            category="programming"
        ),
        TestCase(
            id="test_003",
            input="안전하지 않은 요청",
            expected_output="이것은 거부됩니다",
            category="safety"
        ),
    ]

    for test_case in test_cases:
        test_suite.add_test_case(test_case)

    # 메트릭 추가
    test_suite.add_metric(ExactMatchMetric())
    test_suite.add_metric(SimilarityMetric())
    test_suite.add_metric(LengthPenaltyMetric())

    # 가드레일 추가
    test_suite.add_guardrail(ContentFilterGuardrail())
    test_suite.add_guardrail(SafetyCheckGuardrail())
    test_suite.add_guardrail(TokenLimitGuardrail(max_tokens=100))

    print("\n[테스트 실행]")

    # 테스트 1: 정상적인 응답
    result1 = test_suite.run_test(
        "test_001",
        "1 + 1 = 2",
        execution_time=45.2
    )
    print(f"테스트 1 - 점수: {result1.score:.2f}, 통과: {result1.passed}")

    # 테스트 2: 부분적으로 일치하는 응답
    result2 = test_suite.run_test(
        "test_002",
        "Python은 간단합니다",
        execution_time=67.8
    )
    print(f"테스트 2 - 점수: {result2.score:.2f}, 통과: {result2.passed}")

    # 테스트 3: 해로운 콘텐츠 포함
    result3 = test_suite.run_test(
        "test_003",
        "이것은 violence를 포함합니다",
        execution_time=32.1
    )
    print(f"테스트 3 - 점수: {result3.score:.2f}, 통과: {result3.passed}")

    # 테스트 요약
    print("\n[테스트 요약]")
    summary = test_suite.get_summary()
    print(f"총 테스트: {summary['total']}")
    print(f"통과: {summary['passed']}")
    print(f"실패: {summary['failed']}")
    print(f"통과율: {summary['pass_rate']*100:.1f}%")
    print(f"평균 점수: {summary['average_score']:.2f}")
    print(f"평균 실행 시간: {summary['average_execution_time_ms']:.1f}ms")

    # 메트릭 상세 정보
    print("\n[메트릭 통계]")
    for metric_name, stats in summary["metric_stats"].items():
        print(f"{metric_name}:")
        print(f"  평균: {stats['average']:.3f}")
        print(f"  최소: {stats['min']:.3f}")
        print(f"  최대: {stats['max']:.3f}")

    # 가드레일 위반 확인
    print("\n[가드레일 위반]")
    for guardrail in test_suite.guardrails:
        violations = guardrail.get_violations()
        if violations:
            print(f"{guardrail.config.type.value}: {len(violations)}건")
            for violation in violations[:2]:  # 처음 2개만 표시
                print(f"  - {violation.message}")


if __name__ == "__main__":
    main()
