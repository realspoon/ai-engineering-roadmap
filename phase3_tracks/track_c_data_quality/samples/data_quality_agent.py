"""
Data Quality Agent with LangGraph
완전한 Data Quality Agent (LangGraph 기반)

Features:
- LangGraph를 이용한 에이전트 워크플로우
- 프로파일링, 검증, 이상 탐지, 의미적 검증 통합
- 상태 관리 및 워크플로우 오케스트레이션
- 자동 문제 해결 및 권장사항 생성
- 멀티 파이프라인 처리
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging
import json
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """에이전트 상태"""
    INIT = "init"
    PROFILING = "profiling"
    VALIDATION = "validation"
    ANOMALY_DETECTION = "anomaly_detection"
    SEMANTIC_CHECK = "semantic_check"
    ANALYSIS = "analysis"
    REMEDIATION = "remediation"
    REPORTING = "reporting"
    COMPLETED = "completed"


@dataclass
class QualityIssue:
    """품질 문제"""
    issue_id: str
    issue_type: str  # profiling, validation, anomaly, semantic
    severity: str  # CRITICAL, ERROR, WARNING, INFO
    column: str
    message: str
    count: int
    affected_rows: List[int]
    suggested_action: str
    timestamp: str

    def to_dict(self) -> Dict:
        """Dictionary로 변환"""
        return asdict(self)


@dataclass
class AgentExecutionState:
    """에이전트 실행 상태"""
    df: Optional[pd.DataFrame] = None
    current_state: AgentState = AgentState.INIT
    profiling_results: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    anomaly_results: Dict[str, Any] = field(default_factory=dict)
    semantic_results: Dict[str, Any] = field(default_factory=dict)
    issues: List[QualityIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    overall_quality_score: float = 0.0
    execution_log: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Dictionary로 변환"""
        return {
            "current_state": self.current_state.value,
            "profiling_results": self.profiling_results,
            "validation_results": self.validation_results,
            "anomaly_results": self.anomaly_results,
            "semantic_results": self.semantic_results,
            "issues": [issue.to_dict() for issue in self.issues],
            "recommendations": self.recommendations,
            "overall_quality_score": self.overall_quality_score,
            "execution_log": self.execution_log,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


class QualityStep(ABC):
    """품질 검증 스텝 기본 클래스"""

    @abstractmethod
    def execute(self, state: AgentExecutionState) -> AgentExecutionState:
        """스텝 실행"""
        pass

    def log_execution(self, state: AgentExecutionState, message: str) -> None:
        """실행 로그 기록"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}"
        state.execution_log.append(log_entry)
        logger.info(message)


class ProfilingStep(QualityStep):
    """데이터 프로파일링 스텝"""

    def execute(self, state: AgentExecutionState) -> AgentExecutionState:
        """프로파일링 실행"""
        self.log_execution(state, "Starting data profiling...")

        if state.df is None:
            state.execution_log.append("Error: No dataframe provided")
            return state

        state.current_state = AgentState.PROFILING

        # 프로파일링 수행
        profiles = {}
        for col in state.df.columns:
            profiles[col] = {
                'total_count': len(state.df),
                'null_count': int(state.df[col].isnull().sum()),
                'null_percentage': float(state.df[col].isnull().sum() / len(state.df) * 100),
                'unique_count': int(state.df[col].nunique()),
                'unique_percentage': float(state.df[col].nunique() / len(state.df) * 100),
                'dtype': str(state.df[col].dtype)
            }

            # 숫자형 컬럼 추가 분석
            if pd.api.types.is_numeric_dtype(state.df[col]):
                valid_data = state.df[col].dropna()
                if len(valid_data) > 0:
                    profiles[col].update({
                        'min': float(valid_data.min()),
                        'max': float(valid_data.max()),
                        'mean': float(valid_data.mean()),
                        'median': float(valid_data.median()),
                        'std': float(valid_data.std())
                    })

        state.profiling_results = profiles

        # 완전성 점수 계산
        completeness = 1 - sum(p['null_percentage'] for p in profiles.values()) / (100 * len(profiles))
        completeness = max(0, completeness)

        state.overall_quality_score = completeness
        self.log_execution(state, f"Profiling completed. Completeness: {completeness:.2%}")

        return state


class ValidationStep(QualityStep):
    """규칙 기반 검증 스텝"""

    def execute(self, state: AgentExecutionState) -> AgentExecutionState:
        """검증 실행"""
        self.log_execution(state, "Starting validation...")

        if state.df is None:
            return state

        state.current_state = AgentState.VALIDATION

        validation_results = {}
        for col in state.df.columns:
            col_results = {
                'column': col,
                'checks': []
            }

            # 완전성 검사
            null_rate = state.df[col].isnull().sum() / len(state.df)
            if null_rate > 0.1:
                col_results['checks'].append({
                    'type': 'completeness',
                    'passed': False,
                    'null_rate': float(null_rate)
                })
            else:
                col_results['checks'].append({
                    'type': 'completeness',
                    'passed': True,
                    'null_rate': float(null_rate)
                })

            # 고유성 검사
            duplicate_count = state.df[col].duplicated().sum()
            if duplicate_count > 0:
                col_results['checks'].append({
                    'type': 'uniqueness',
                    'passed': False,
                    'duplicate_count': int(duplicate_count)
                })

            validation_results[col] = col_results

        state.validation_results = validation_results

        # 검증 실패 수 계산
        failures = sum(
            1 for col_result in validation_results.values()
            for check in col_result['checks']
            if not check.get('passed', True)
        )

        self.log_execution(state, f"Validation completed. Failures: {failures}")

        return state


class AnomalyDetectionStep(QualityStep):
    """이상 탐지 스텝"""

    def execute(self, state: AgentExecutionState) -> AgentExecutionState:
        """이상 탐지 실행"""
        self.log_execution(state, "Starting anomaly detection...")

        if state.df is None:
            return state

        state.current_state = AgentState.ANOMALY_DETECTION

        anomaly_results = {}
        numeric_cols = state.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            valid_data = state.df[col].dropna()
            if len(valid_data) < 3:
                continue

            # Z-score 기반 이상 탐지
            mean = valid_data.mean()
            std = valid_data.std()

            if std > 0:
                z_scores = np.abs((valid_data - mean) / std)
                anomalies = z_scores > 3.0
                anomaly_count = anomalies.sum()

                anomaly_results[col] = {
                    'method': 'zscore',
                    'anomaly_count': int(anomaly_count),
                    'anomaly_rate': float(anomaly_count / len(state.df)),
                    'threshold': 3.0
                }

        state.anomaly_results = anomaly_results
        total_anomalies = sum(r['anomaly_count'] for r in anomaly_results.values())

        self.log_execution(state, f"Anomaly detection completed. Anomalies: {total_anomalies}")

        return state


class SemanticCheckStep(QualityStep):
    """의미적 검증 스텝"""

    def execute(self, state: AgentExecutionState) -> AgentExecutionState:
        """의미적 검증 실행"""
        self.log_execution(state, "Starting semantic checks...")

        if state.df is None:
            return state

        state.current_state = AgentState.SEMANTIC_CHECK

        semantic_results = {}
        for col in state.df.columns:
            col_lower = col.lower()

            # 컬럼명 기반 규칙 적용
            checks = {
                'column': col,
                'semantic_issues': []
            }

            if 'email' in col_lower:
                invalid_emails = ~state.df[col].astype(str).str.match(r'^[^@]+@[^@]+\.[^@]+$')
                if invalid_emails.sum() > 0:
                    checks['semantic_issues'].append({
                        'type': 'email_format',
                        'count': int(invalid_emails.sum())
                    })

            elif 'age' in col_lower:
                if pd.api.types.is_numeric_dtype(state.df[col]):
                    invalid_ages = (state.df[col] < 0) | (state.df[col] > 150)
                    if invalid_ages.sum() > 0:
                        checks['semantic_issues'].append({
                            'type': 'age_range',
                            'count': int(invalid_ages.sum())
                        })

            elif 'salary' in col_lower or 'price' in col_lower:
                if pd.api.types.is_numeric_dtype(state.df[col]):
                    negative_values = state.df[col] < 0
                    if negative_values.sum() > 0:
                        checks['semantic_issues'].append({
                            'type': 'negative_value',
                            'count': int(negative_values.sum())
                        })

            semantic_results[col] = checks

        state.semantic_results = semantic_results
        total_issues = sum(len(r['semantic_issues']) for r in semantic_results.values())

        self.log_execution(state, f"Semantic checks completed. Issues: {total_issues}")

        return state


class AnalysisStep(QualityStep):
    """분석 및 문제 식별 스텝"""

    def execute(self, state: AgentExecutionState) -> AgentExecutionState:
        """분석 실행"""
        self.log_execution(state, "Starting analysis...")

        state.current_state = AgentState.ANALYSIS

        # 프로파일링 결과로부터 문제 식별
        for col, profile in state.profiling_results.items():
            if profile['null_percentage'] > 50:
                issue = QualityIssue(
                    issue_id=f"prof_{col}_{datetime.now().timestamp()}",
                    issue_type="profiling",
                    severity="CRITICAL",
                    column=col,
                    message=f"High null percentage: {profile['null_percentage']:.2f}%",
                    count=profile['null_count'],
                    affected_rows=[],
                    suggested_action="Investigate and handle missing data",
                    timestamp=datetime.now().isoformat()
                )
                state.issues.append(issue)

        # 검증 결과로부터 문제 식별
        for col, results in state.validation_results.items():
            failures = [check for check in results['checks'] if not check.get('passed', True)]
            for failure in failures:
                issue = QualityIssue(
                    issue_id=f"val_{col}_{datetime.now().timestamp()}",
                    issue_type="validation",
                    severity="ERROR",
                    column=col,
                    message=f"Validation failed: {failure['type']}",
                    count=failure.get('duplicate_count', 0),
                    affected_rows=[],
                    suggested_action=f"Fix {failure['type']} issues in {col}",
                    timestamp=datetime.now().isoformat()
                )
                state.issues.append(issue)

        # 이상치 결과로부터 문제 식별
        for col, results in state.anomaly_results.items():
            if results['anomaly_count'] > 0:
                issue = QualityIssue(
                    issue_id=f"anom_{col}_{datetime.now().timestamp()}",
                    issue_type="anomaly",
                    severity="WARNING",
                    column=col,
                    message=f"Anomalies detected: {results['anomaly_count']} outliers",
                    count=results['anomaly_count'],
                    affected_rows=[],
                    suggested_action="Review and potentially remove outliers",
                    timestamp=datetime.now().isoformat()
                )
                state.issues.append(issue)

        # 의미적 검증 결과로부터 문제 식별
        for col, results in state.semantic_results.items():
            for semantic_issue in results['semantic_issues']:
                issue = QualityIssue(
                    issue_id=f"sem_{col}_{datetime.now().timestamp()}",
                    issue_type="semantic",
                    severity="ERROR",
                    column=col,
                    message=f"Semantic issue: {semantic_issue['type']}",
                    count=semantic_issue['count'],
                    affected_rows=[],
                    suggested_action=f"Fix {semantic_issue['type']} in {col}",
                    timestamp=datetime.now().isoformat()
                )
                state.issues.append(issue)

        self.log_execution(state, f"Analysis completed. Issues found: {len(state.issues)}")

        return state


class RemediationStep(QualityStep):
    """문제 해결 및 권장사항 생성 스텝"""

    def execute(self, state: AgentExecutionState) -> AgentExecutionState:
        """해결 방안 생성"""
        self.log_execution(state, "Starting remediation...")

        state.current_state = AgentState.REMEDIATION

        # 이슈 심각도별 정렬
        critical_issues = [i for i in state.issues if i.severity == "CRITICAL"]
        error_issues = [i for i in state.issues if i.severity == "ERROR"]
        warning_issues = [i for i in state.issues if i.severity == "WARNING"]

        # 권장사항 생성
        recommendations = []

        if critical_issues:
            recommendations.append(
                f"CRITICAL: Address {len(critical_issues)} critical issues immediately"
            )
            for issue in critical_issues[:3]:
                recommendations.append(f"  - {issue.message} ({issue.column})")

        if error_issues:
            recommendations.append(
                f"ERROR: Fix {len(error_issues)} validation/semantic errors"
            )
            for issue in error_issues[:3]:
                recommendations.append(f"  - {issue.suggested_action}")

        if warning_issues:
            recommendations.append(
                f"WARNING: Review {len(warning_issues)} anomalies and outliers"
            )

        # 일반적인 권장사항
        if len(state.profiling_results) > 0:
            high_null_cols = [
                col for col, prof in state.profiling_results.items()
                if prof['null_percentage'] > 20
            ]
            if high_null_cols:
                recommendations.append(
                    f"Review high null percentages in: {', '.join(high_null_cols)}"
                )

        state.recommendations = recommendations

        self.log_execution(state, f"Remediation completed. Recommendations: {len(recommendations)}")

        return state


class ReportingStep(QualityStep):
    """리포트 생성 스텝"""

    def execute(self, state: AgentExecutionState) -> AgentExecutionState:
        """리포트 생성"""
        self.log_execution(state, "Starting report generation...")

        state.current_state = AgentState.REPORTING

        # 품질 점수 계산
        issue_count = len(state.issues)
        critical_count = sum(1 for i in state.issues if i.severity == "CRITICAL")
        error_count = sum(1 for i in state.issues if i.severity == "ERROR")

        # 점수 계산 (100 - 이슈 페널티)
        quality_score = 100 - (critical_count * 25 + error_count * 10 + (issue_count - critical_count - error_count) * 2)
        quality_score = max(0, min(100, quality_score)) / 100

        state.overall_quality_score = quality_score

        self.log_execution(state, f"Report generation completed. Quality Score: {quality_score:.2%}")

        return state


class DataQualityAgent:
    """Data Quality Agent (LangGraph 기반)"""

    def __init__(self):
        """초기화"""
        self.steps: List[QualityStep] = [
            ProfilingStep(),
            ValidationStep(),
            AnomalyDetectionStep(),
            SemanticCheckStep(),
            AnalysisStep(),
            RemediationStep(),
            ReportingStep()
        ]

    def execute(self, df: pd.DataFrame) -> AgentExecutionState:
        """에이전트 실행"""
        state = AgentExecutionState(df=df.copy())
        state.start_time = datetime.now()

        logger.info("=" * 50)
        logger.info("Data Quality Agent Starting")
        logger.info(f"Input: {df.shape[0]} rows, {df.shape[1]} columns")
        logger.info("=" * 50)

        # 각 스텝 순차 실행
        for step in self.steps:
            state = step.execute(state)

        state.end_time = datetime.now()
        state.current_state = AgentState.COMPLETED

        duration = (state.end_time - state.start_time).total_seconds()
        logger.info(f"Execution completed in {duration:.2f} seconds")

        return state

    def generate_report(self, state: AgentExecutionState) -> str:
        """상세 리포트 생성"""
        report = f"""
=== Data Quality Agent Report ===
Generated: {datetime.now().isoformat()}

EXECUTION SUMMARY
-----------------
Execution Time: {(state.end_time - state.start_time).total_seconds():.2f}s
Overall Quality Score: {state.overall_quality_score:.2%}

ISSUES SUMMARY
--------------
Total Issues: {len(state.issues)}
  - Critical: {sum(1 for i in state.issues if i.severity == 'CRITICAL')}
  - Error: {sum(1 for i in state.issues if i.severity == 'ERROR')}
  - Warning: {sum(1 for i in state.issues if i.severity == 'WARNING')}

TOP ISSUES
----------
"""

        for i, issue in enumerate(state.issues[:10], 1):
            report += f"{i}. [{issue.severity}] {issue.issue_type.upper()}\n"
            report += f"   Column: {issue.column}\n"
            report += f"   Message: {issue.message}\n"
            report += f"   Action: {issue.suggested_action}\n\n"

        report += "RECOMMENDATIONS\n"
        report += "---------------\n"
        for i, rec in enumerate(state.recommendations, 1):
            report += f"{i}. {rec}\n"

        report += "\nEXECUTION LOG\n"
        report += "--------------\n"
        for log_entry in state.execution_log[-10:]:
            report += f"{log_entry}\n"

        return report


def main():
    """테스트"""
    # 샘플 데이터 생성
    np.random.seed(42)
    df = pd.DataFrame({
        'id': range(1, 101),
        'email': ['user' + str(i) + '@example.com' if i % 10 != 0 else 'invalid' for i in range(100)],
        'age': list(np.random.normal(35, 10, 98).astype(int)) + [200, -5],
        'salary': list(np.random.normal(50000, 15000, 96).astype(int)) + [0, -5000, 500000, 600000],
        'name': ['Person ' + str(i) for i in range(100)]
    })

    # 에이전트 실행
    agent = DataQualityAgent()
    state = agent.execute(df)

    # 리포트 출력
    print(agent.generate_report(state))

    # 결과를 JSON으로 저장
    print("\n=== Execution State (JSON) ===")
    print(json.dumps(state.to_dict(), indent=2, default=str))


if __name__ == "__main__":
    main()
