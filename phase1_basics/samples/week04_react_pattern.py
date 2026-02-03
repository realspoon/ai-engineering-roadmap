"""
Week 4: ReAct 패턴, Self-Consistency, 프롬프트 A/B 테스트
============================================================

이 모듈은 고급 프롬프트 엔지니어링 기법을 보여줍니다:
- ReAct (Reasoning + Acting) 패턴 구현
- Self-Consistency 샘플링
- 프롬프트 A/B 테스트
- 성능 메트릭 측정
"""

import json
import time
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class ReasoningType(Enum):
    """추론 유형 정의"""
    THOUGHT = "Thought"
    ACTION = "Action"
    OBSERVATION = "Observation"
    FINAL_ANSWER = "Final Answer"


@dataclass
class ReActStep:
    """ReAct 단계를 나타내는 데이터 클래스"""
    step_number: int
    type: ReasoningType
    content: str
    timestamp: float


@dataclass
class ReActTrace:
    """ReAct 추적 경로"""
    steps: List[ReActStep]
    final_answer: str
    total_steps: int
    execution_time: float


class ReActExecutor:
    """
    ReAct 패턴을 구현하는 클래스입니다.
    Reasoning + Acting을 반복하며 문제를 해결합니다.
    """

    def __init__(self, max_steps: int = 5, verbose: bool = True):
        """
        ReActExecutor 초기화

        Args:
            max_steps (int): 최대 실행 단계
            verbose (bool): 상세 출력 여부
        """
        self.max_steps = max_steps
        self.verbose = verbose
        self.steps: List[ReActStep] = []
        self.start_time = None

    def _log_step(self, step_type: ReasoningType, content: str) -> None:
        """
        단계 기록

        Args:
            step_type (ReasoningType): 단계 유형
            content (str): 단계 내용
        """
        step = ReActStep(
            step_number=len(self.steps) + 1,
            type=step_type,
            content=content,
            timestamp=time.time() - self.start_time,
        )
        self.steps.append(step)

        if self.verbose:
            print(f"\n[Step {step.step_number}] {step_type.value}:")
            print(f"  {content}")

    def execute_math_problem(self, problem: str) -> ReActTrace:
        """
        수학 문제를 ReAct 패턴으로 해결합니다.

        Args:
            problem (str): 해결할 수학 문제

        Returns:
            ReActTrace: 실행 추적 정보
        """
        self.start_time = time.time()
        self.steps = []

        print(f"\n{'='*60}")
        print(f"🔍 문제: {problem}")
        print(f"{'='*60}")

        # Step 1: 문제 분석
        self._log_step(
            ReasoningType.THOUGHT,
            f"문제 분석: '{problem}'을 단계별로 풀어야 합니다."
        )

        # Step 2: 계획 수립
        self._log_step(
            ReasoningType.ACTION,
            "1. 문제 유형 파악\n2. 필요한 연산 식별\n3. 단계별 계산"
        )

        # Step 3: 첫 번째 관찰
        self._log_step(
            ReasoningType.OBSERVATION,
            "문제는 덧셈 계산 문제로 파악됨"
        )

        # Step 4: 계산 실행
        self._log_step(
            ReasoningType.ACTION,
            "계산 수행: 2 + 3 = 5, 5 + 7 = 12"
        )

        # Step 5: 최종 답변
        final_answer = "12"
        self._log_step(
            ReasoningType.FINAL_ANSWER,
            f"최종 답: {final_answer}"
        )

        execution_time = time.time() - self.start_time

        return ReActTrace(
            steps=self.steps,
            final_answer=final_answer,
            total_steps=len(self.steps),
            execution_time=execution_time,
        )

    def execute_reasoning_task(self, task: str) -> ReActTrace:
        """
        추론 작업을 ReAct 패턴으로 실행합니다.

        Args:
            task (str): 실행할 작업

        Returns:
            ReActTrace: 실행 추적 정보
        """
        self.start_time = time.time()
        self.steps = []

        print(f"\n{'='*60}")
        print(f"🤔 작업: {task}")
        print(f"{'='*60}")

        # 작업 분해
        self._log_step(
            ReasoningType.THOUGHT,
            "이 작업을 해결하기 위해 어떤 정보가 필요한지 생각합니다."
        )

        # 정보 수집
        self._log_step(
            ReasoningType.ACTION,
            "관련 정보를 체계적으로 수집하고 정리합니다."
        )

        # 관찰
        self._log_step(
            ReasoningType.OBSERVATION,
            "수집된 정보를 분석하면 다음과 같은 패턴이 보입니다."
        )

        # 추가 분석
        self._log_step(
            ReasoningType.ACTION,
            "패턴을 바탕으로 논리적 결론을 도출합니다."
        )

        # 최종 답변
        final_answer = "작업 완료: 분석 결과를 기반으로 최적의 해결책을 제시합니다."
        self._log_step(
            ReasoningType.FINAL_ANSWER,
            final_answer
        )

        execution_time = time.time() - self.start_time

        return ReActTrace(
            steps=self.steps,
            final_answer=final_answer,
            total_steps=len(self.steps),
            execution_time=execution_time,
        )

    def get_trace_summary(self, trace: ReActTrace) -> Dict[str, Any]:
        """
        ReAct 추적의 요약정보를 생성합니다.

        Args:
            trace (ReActTrace): ReAct 추적 정보

        Returns:
            Dict: 요약 정보
        """
        return {
            "final_answer": trace.final_answer,
            "total_steps": trace.total_steps,
            "execution_time_seconds": round(trace.execution_time, 3),
            "steps_breakdown": {
                step.type.value: sum(1 for s in trace.steps if s.type == step.type)
                for step in trace.steps
            },
        }


class SelfConsistencySampler:
    """
    Self-Consistency 샘플링을 구현하는 클래스입니다.
    여러 추론 경로를 샘플링하고 일관성 있는 답을 찾습니다.
    """

    def __init__(self, num_samples: int = 3):
        """
        SelfConsistencySampler 초기화

        Args:
            num_samples (int): 샘플 개수
        """
        self.num_samples = num_samples
        self.samples: List[Dict[str, Any]] = []

    def generate_reasoning_samples(self, problem: str) -> List[str]:
        """
        동일한 문제에 대한 여러 추론 경로를 생성합니다.

        Args:
            problem (str): 문제

        Returns:
            List[str]: 여러 추론 결과
        """
        print(f"\n{'='*60}")
        print(f"🎲 Self-Consistency 샘플링: {self.num_samples}개 샘플 생성")
        print(f"{'='*60}")

        results = []

        for i in range(self.num_samples):
            print(f"\n샘플 {i+1}/{self.num_samples}:")
            print("-" * 40)

            # 다양한 추론 경로 시뮬레이션
            if i == 0:
                reasoning = f"경로1: {problem}를 직접 계산\n결과: 42"
            elif i == 1:
                reasoning = f"경로2: {problem}를 다른 방식으로 접근\n결과: 42"
            else:
                reasoning = f"경로3: {problem}를 단계별로 검증\n결과: 42"

            print(reasoning)
            results.append(reasoning)
            self.samples.append({
                "sample_id": i + 1,
                "reasoning": reasoning,
                "answer": "42",
            })

        return results

    def extract_majority_answer(self) -> str:
        """
        샘플들로부터 다수결 답변을 추출합니다.

        Returns:
            str: 가장 많이 나온 답변
        """
        if not self.samples:
            return "No samples available"

        print(f"\n{'='*60}")
        print("🎯 다수결 답변 추출")
        print(f"{'='*60}")

        answer_counts = {}
        for sample in self.samples:
            answer = sample.get("answer", "unknown")
            answer_counts[answer] = answer_counts.get(answer, 0) + 1

        print("\n답변 분포:")
        for answer, count in answer_counts.items():
            percentage = (count / len(self.samples)) * 100
            print(f"  {answer}: {count}/{len(self.samples)} ({percentage:.1f}%)")

        majority_answer = max(answer_counts, key=answer_counts.get)
        print(f"\n✓ 다수결 답변: {majority_answer}")

        return majority_answer

    def get_consistency_score(self) -> float:
        """
        일관성 점수를 계산합니다 (0~1).

        Returns:
            float: 일관성 점수
        """
        if not self.samples:
            return 0.0

        # 모든 샘플의 답이 같은지 확인
        answers = [sample.get("answer") for sample in self.samples]
        unique_answers = len(set(answers))
        consistency = 1.0 - (unique_answers - 1) / max(len(answers) - 1, 1)

        return round(consistency, 3)


@dataclass
class PromptVariant:
    """프롬프트 변형"""
    name: str
    template: str
    description: str


@dataclass
class TestResult:
    """테스트 결과"""
    variant_name: str
    prompt_hash: str
    response: str
    latency_ms: float
    quality_score: float
    timestamp: float


class PromptABTester:
    """
    프롬프트 A/B 테스트를 수행하는 클래스입니다.
    """

    def __init__(self):
        """PromptABTester 초기화"""
        self.variants: List[PromptVariant] = []
        self.results: List[TestResult] = []

    def add_variant(self, name: str, template: str, description: str) -> None:
        """
        테스트할 프롬프트 변형을 추가합니다.

        Args:
            name (str): 변형 이름
            template (str): 프롬프트 템플릿
            description (str): 변형 설명
        """
        variant = PromptVariant(
            name=name,
            template=template,
            description=description,
        )
        self.variants.append(variant)
        print(f"✓ 변형 추가: {name}")

    def create_test_variants(self) -> None:
        """표준 테스트 변형들을 생성합니다."""
        print(f"\n{'='*60}")
        print("📝 프롬프트 A/B 테스트 변형 생성")
        print(f"{'='*60}\n")

        # Variant A: 직접적이고 명확한 프롬프트
        self.add_variant(
            name="Variant A: Direct Instruction",
            template="다음 문제를 해결하시오: {question}",
            description="직접적이고 명확한 지시문",
        )

        # Variant B: 상세한 단계별 프롬프트
        self.add_variant(
            name="Variant B: Step-by-Step",
            template="""다음 문제를 단계별로 해결하시오:

문제: {question}

다음 단계를 따르시오:
1. 문제 이해
2. 정보 수집
3. 계획 수립
4. 실행
5. 검증""",
            description="단계별 상세 지시문",
        )

        # Variant C: 예제 기반 프롬프트
        self.add_variant(
            name="Variant C: Few-Shot Example",
            template="""다음과 유사한 문제를 해결한 예시가 있습니다:

예시: Q: 2+2=? A: 4 (각 숫자를 더함)

이제 당신의 문제입니다:
Q: {question}
A:""",
            description="예제를 포함한 Few-shot 프롬프트",
        )

        # Variant D: 역할 지정 프롬프트
        self.add_variant(
            name="Variant D: Role-Based",
            template="""당신은 전문 문제 해결사입니다. 당신의 역할은 복잡한 문제를 체계적으로 분석하고 해결하는 것입니다.

문제: {question}

전문가로서의 통찰력을 적용하여 해결책을 제시하시오.""",
            description="역할 기반 지시문",
        )

    def simulate_model_response(self, prompt: str) -> Tuple[str, float]:
        """
        모델 응답을 시뮬레이션합니다.

        Args:
            prompt (str): 프롬프트

        Returns:
            Tuple[str, float]: (응답, 지연시간_ms)
        """
        # 실제 API 호출을 대신하여 시뮬레이션
        time.sleep(0.1)  # API 지연 시뮬레이션

        response = f"응답: 이 프롬프트에 대한 모델의 응답입니다. 프롬프트 길이: {len(prompt)} 문자"
        latency_ms = 150 + (len(prompt) / 10)  # 길이에 따른 지연 시간

        return response, latency_ms

    def calculate_quality_score(self, prompt: str, response: str) -> float:
        """
        응답의 품질 점수를 계산합니다 (0~1).

        Args:
            prompt (str): 프롬프트
            response (str): 응답

        Returns:
            float: 품질 점수
        """
        # 간단한 품질 메트릭
        score = 0.0

        # 길이 기반 점수 (적절한 길이 100~500 문자)
        response_length = len(response)
        if 100 <= response_length <= 500:
            score += 0.3
        elif response_length > 0:
            score += 0.15

        # 프롬프트 복잡도 점수
        prompt_words = len(prompt.split())
        if prompt_words > 20:
            score += 0.3  # 상세한 지시문이 더 나음
        else:
            score += 0.15

        # 응답 관련성 점수
        if any(word in response for word in ["문제", "해결", "단계"]):
            score += 0.4
        else:
            score += 0.2

        return round(min(score, 1.0), 3)

    def run_ab_test(self, question: str, iterations: int = 1) -> None:
        """
        A/B 테스트를 실행합니다.

        Args:
            question (str): 테스트할 질문
            iterations (int): 반복 횟수
        """
        print(f"\n{'='*60}")
        print(f"🧪 A/B 테스트 실행")
        print(f"{'='*60}")
        print(f"질문: {question}")
        print(f"반복: {iterations}회\n")

        for variant in self.variants:
            print(f"\n테스트 중: {variant.name}")
            print("-" * 40)

            variant_latencies = []
            variant_scores = []

            for iteration in range(iterations):
                # 프롬프트 생성
                prompt = variant.template.format(question=question)

                # 응답 생성
                start_time = time.time()
                response, latency = self.simulate_model_response(prompt)
                latency_ms = latency

                # 품질 점수
                quality_score = self.calculate_quality_score(prompt, response)

                # 결과 저장
                result = TestResult(
                    variant_name=variant.name,
                    prompt_hash=hashlib.md5(prompt.encode()).hexdigest()[:8],
                    response=response,
                    latency_ms=latency_ms,
                    quality_score=quality_score,
                    timestamp=time.time(),
                )
                self.results.append(result)

                variant_latencies.append(latency_ms)
                variant_scores.append(quality_score)

            # 통계
            avg_latency = sum(variant_latencies) / len(variant_latencies)
            avg_score = sum(variant_scores) / len(variant_scores)

            print(f"  평균 지연: {avg_latency:.1f}ms")
            print(f"  평균 품질: {avg_score:.3f}")

    def generate_report(self) -> Dict[str, Any]:
        """
        테스트 결과 보고서를 생성합니다.

        Returns:
            Dict: 보고서 데이터
        """
        print(f"\n{'='*60}")
        print("📊 A/B 테스트 결과 보고서")
        print(f"{'='*60}\n")

        variant_stats = {}

        for variant in self.variants:
            variant_results = [r for r in self.results if r.variant_name == variant.name]

            if not variant_results:
                continue

            latencies = [r.latency_ms for r in variant_results]
            scores = [r.quality_score for r in variant_results]

            stats = {
                "description": variant.description,
                "test_count": len(variant_results),
                "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
                "avg_quality_score": round(sum(scores) / len(scores), 3),
                "min_latency_ms": round(min(latencies), 2),
                "max_latency_ms": round(max(latencies), 2),
            }

            variant_stats[variant.name] = stats

            print(f"{variant.name}")
            print("-" * 40)
            print(f"  테스트 횟수: {stats['test_count']}")
            print(f"  평균 지연: {stats['avg_latency_ms']}ms")
            print(f"  평균 품질: {stats['avg_quality_score']}")

        # 최적 변형 선택
        if variant_stats:
            best_variant = max(
                variant_stats.items(),
                key=lambda x: x[1]["avg_quality_score"],
            )
            print(f"\n🏆 권장 변형: {best_variant[0]}")
            print(f"   품질 점수: {best_variant[1]['avg_quality_score']}")

        return {
            "total_tests": len(self.results),
            "variants": variant_stats,
            "best_variant": best_variant[0] if variant_stats else None,
        }


def example_react_pattern():
    """ReAct 패턴 예제"""
    print("\n" + "=" * 70)
    print("예제 1: ReAct (Reasoning + Acting) 패턴")
    print("=" * 70)

    executor = ReActExecutor(verbose=True)

    # 수학 문제 해결
    trace1 = executor.execute_math_problem("2 + 3 + 7은?")
    summary1 = executor.get_trace_summary(trace1)

    print("\n📈 추적 요약:")
    print(json.dumps(summary1, indent=2, ensure_ascii=False))

    # 추론 작업 실행
    trace2 = executor.execute_reasoning_task("효율적인 학습 방법 찾기")
    summary2 = executor.get_trace_summary(trace2)

    print("\n📈 추적 요약:")
    print(json.dumps(summary2, indent=2, ensure_ascii=False))


def example_self_consistency():
    """Self-Consistency 패턴 예제"""
    print("\n" + "=" * 70)
    print("예제 2: Self-Consistency 샘플링")
    print("=" * 70)

    sampler = SelfConsistencySampler(num_samples=3)
    results = sampler.generate_reasoning_samples("8 * 5 + 2는?")
    majority = sampler.extract_majority_answer()
    consistency = sampler.get_consistency_score()

    print(f"\n📊 일관성 점수: {consistency}")


def example_prompt_ab_test():
    """프롬프트 A/B 테스트 예제"""
    print("\n" + "=" * 70)
    print("예제 3: 프롬프트 A/B 테스트")
    print("=" * 70)

    tester = PromptABTester()
    tester.create_test_variants()

    question = "효율적인 시간 관리 방법은?"
    tester.run_ab_test(question, iterations=2)

    report = tester.generate_report()

    print("\n📋 최종 보고서:")
    print(json.dumps(report, indent=2, ensure_ascii=False))


def example_combined_approach():
    """통합 접근 방식 예제"""
    print("\n" + "=" * 70)
    print("예제 4: ReAct + Self-Consistency + A/B 테스트 통합")
    print("=" * 70)

    print("\n1️⃣ ReAct로 추론 경로 생성")
    executor = ReActExecutor(verbose=False)
    trace = executor.execute_math_problem("복잡한 문제 해결")

    print("\n2️⃣ Self-Consistency로 여러 경로 샘플링")
    sampler = SelfConsistencySampler(num_samples=3)
    samples = sampler.generate_reasoning_samples("동일 문제")
    majority = sampler.extract_majority_answer()

    print("\n3️⃣ 최선의 프롬프트 스타일 A/B 테스트")
    tester = PromptABTester()
    tester.create_test_variants()
    tester.run_ab_test("테스트 질문")
    report = tester.generate_report()

    print("\n✅ 통합 접근 완료")
    print(f"  - ReAct 단계: {len(trace.steps)}")
    print(f"  - Self-Consistency 샘플: {len(sampler.samples)}")
    print(f"  - A/B 테스트 변형: {len(tester.variants)}")


if __name__ == "__main__":
    """메인 실행 영역"""

    print("\n" + "#" * 70)
    print("# Week 4: ReAct 패턴, Self-Consistency, 프롬프트 A/B 테스트")
    print("#" * 70)

    # 예제 1: ReAct 패턴
    example_react_pattern()

    # 예제 2: Self-Consistency
    example_self_consistency()

    # 예제 3: 프롬프트 A/B 테스트
    example_prompt_ab_test()

    # 예제 4: 통합 접근
    example_combined_approach()

    print("\n" + "#" * 70)
    print("# 모든 예제 완료")
    print("#" * 70)
