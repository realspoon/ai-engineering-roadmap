"""
Semantic Data Quality Checker Module
LLM 기반 의미적 품질 검증

Features:
- LLM을 이용한 의미적 검증
- 문맥 이해 기반 이상 탐지
- 자동 데이터 정제
- 품질 개선 제안
- 비즈니스 규칙 학습
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CheckType(Enum):
    """검증 타입"""
    SEMANTIC = "semantic"
    CONSISTENCY = "consistency"
    BUSINESS_LOGIC = "business_logic"
    CONTEXT = "context"


@dataclass
class SemanticCheckResult:
    """의미적 검증 결과"""
    check_type: str
    column: str
    is_valid: bool
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    confidence: float
    llm_feedback: str
    timestamp: str

    def to_dict(self) -> Dict:
        """Dictionary로 변환"""
        return {
            "check_type": self.check_type,
            "column": self.column,
            "is_valid": self.is_valid,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "confidence": self.confidence,
            "llm_feedback": self.llm_feedback,
            "timestamp": self.timestamp
        }


class LLMSemanticChecker:
    """LLM 기반 의미적 검증기 (Mock LLM)"""

    def __init__(self, mock_mode: bool = True):
        """
        초기화

        Args:
            mock_mode: Mock LLM 모드 (실제 API 대신 시뮬레이션)
        """
        self.mock_mode = mock_mode
        self.context_cache = {}
        self.pattern_library = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[str, Dict]:
        """패턴 라이브러리 초기화"""
        return {
            'email': {
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'description': 'Valid email format',
                'severity': 'HIGH'
            },
            'phone': {
                'pattern': r'^\+?1?\d{9,15}$',
                'description': 'Valid phone format',
                'severity': 'MEDIUM'
            },
            'url': {
                'pattern': r'^https?://[^\s]+$',
                'description': 'Valid URL format',
                'severity': 'MEDIUM'
            },
            'date': {
                'pattern': r'^\d{4}-\d{2}-\d{2}$',
                'description': 'Valid date format (YYYY-MM-DD)',
                'severity': 'HIGH'
            }
        }

    def analyze_text_quality(self, text: str) -> Dict[str, Any]:
        """텍스트 품질 분석"""
        issues = []
        suggestions = []

        # 길이 검사
        if len(text) == 0:
            issues.append({
                'type': 'empty',
                'severity': 'HIGH',
                'message': 'Text is empty'
            })

        # 특수문자 검사
        special_chars = sum(1 for c in text if not c.isalnum() and c != ' ')
        if special_chars / len(text) > 0.3:
            issues.append({
                'type': 'excessive_special_chars',
                'severity': 'MEDIUM',
                'message': f'Too many special characters ({special_chars}/{len(text)})'
            })

        # 숫자 검사
        digits = sum(1 for c in text if c.isdigit())
        if digits / len(text) > 0.5:
            issues.append({
                'type': 'too_many_digits',
                'severity': 'MEDIUM',
                'message': f'Too many digits ({digits}/{len(text)})'
            })
            suggestions.append('Check if this should be a numeric column instead')

        # 케이스 일관성 검사
        if text.isupper():
            suggestions.append('Consider converting to title case for better readability')
        elif text.islower() and len(text.split()) > 1:
            suggestions.append('Consider converting to title case')

        return {
            'issues': issues,
            'suggestions': suggestions,
            'quality_score': max(0, 1 - len(issues) * 0.2)
        }

    def check_semantic_consistency(self, df: pd.DataFrame, column: str,
                                  related_columns: Optional[List[str]] = None) -> SemanticCheckResult:
        """의미적 일관성 검증"""
        if column not in df.columns:
            return SemanticCheckResult(
                check_type=CheckType.CONSISTENCY.value,
                column=column,
                is_valid=False,
                issues=[{'type': 'column_not_found', 'message': f'Column {column} not found'}],
                suggestions=[],
                confidence=0.0,
                llm_feedback='Column not found in dataset',
                timestamp=datetime.now().isoformat()
            )

        issues = []
        suggestions = []

        # 1. 값의 일관성 검사
        value_counts = df[column].value_counts()
        if len(value_counts) == len(df):
            suggestions.append('All values are unique - verify if this is expected')

        # 2. 데이터 타입 일관성
        try:
            numeric_data = pd.to_numeric(df[column].dropna(), errors='coerce')
            non_numeric = df[column].dropna()[numeric_data.isna()].tolist()
            if non_numeric:
                issues.append({
                    'type': 'mixed_types',
                    'severity': 'MEDIUM',
                    'message': f'Found {len(non_numeric)} non-numeric values in numeric column'
                })
        except:
            pass

        # 3. 관련 컬럼 검사
        if related_columns:
            for rel_col in related_columns:
                if rel_col in df.columns:
                    if len(df[df[column].notna()]) != len(df[df[rel_col].notna()]):
                        issues.append({
                            'type': 'inconsistent_nulls',
                            'severity': 'MEDIUM',
                            'message': f'Null pattern differs from {rel_col}'
                        })

        is_valid = len(issues) == 0
        confidence = max(0.5, 1 - len(issues) * 0.2)

        return SemanticCheckResult(
            check_type=CheckType.CONSISTENCY.value,
            column=column,
            is_valid=is_valid,
            issues=issues,
            suggestions=suggestions,
            confidence=confidence,
            llm_feedback=f"Semantic consistency check completed with {len(issues)} issues found",
            timestamp=datetime.now().isoformat()
        )

    def check_business_logic(self, df: pd.DataFrame, column: str,
                           rules: Optional[Dict[str, Any]] = None) -> SemanticCheckResult:
        """비즈니스 로직 검증"""
        if column not in df.columns:
            return SemanticCheckResult(
                check_type=CheckType.BUSINESS_LOGIC.value,
                column=column,
                is_valid=False,
                issues=[{'type': 'column_not_found', 'message': f'Column {column} not found'}],
                suggestions=[],
                confidence=0.0,
                llm_feedback='Column not found in dataset',
                timestamp=datetime.now().isoformat()
            )

        issues = []
        suggestions = []

        if not rules:
            rules = self._get_default_business_rules(column)

        # 각 규칙 검증
        for rule_name, rule_config in rules.items():
            violations = self._check_rule(df, column, rule_config)
            if violations:
                issues.append({
                    'type': 'business_rule_violation',
                    'rule': rule_name,
                    'severity': rule_config.get('severity', 'MEDIUM'),
                    'violations': violations
                })

        is_valid = len(issues) == 0
        confidence = max(0.5, 1 - len(issues) * 0.25)

        if not is_valid:
            suggestions.append(f'Review and update data to comply with business rules')

        return SemanticCheckResult(
            check_type=CheckType.BUSINESS_LOGIC.value,
            column=column,
            is_valid=is_valid,
            issues=issues,
            suggestions=suggestions,
            confidence=confidence,
            llm_feedback=f"Business logic validation found {len(issues)} rule violations",
            timestamp=datetime.now().isoformat()
        )

    def _get_default_business_rules(self, column: str) -> Dict[str, Any]:
        """컬럼에 대한 기본 비즈니스 규칙"""
        rules = {}

        # 컬럼명 기반 규칙 추론
        col_lower = column.lower()

        if 'age' in col_lower:
            rules['age_range'] = {
                'description': 'Age should be between 0 and 150',
                'min': 0,
                'max': 150,
                'severity': 'HIGH'
            }

        elif 'salary' in col_lower or 'price' in col_lower or 'amount' in col_lower:
            rules['positive_value'] = {
                'description': 'Salary/Price should be positive',
                'min': 0,
                'severity': 'HIGH'
            }

        elif 'email' in col_lower:
            rules['email_format'] = {
                'description': 'Valid email format required',
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'severity': 'HIGH'
            }

        elif 'phone' in col_lower:
            rules['phone_format'] = {
                'description': 'Valid phone format required',
                'pattern': r'^\+?1?\d{9,15}$',
                'severity': 'MEDIUM'
            }

        return rules

    def _check_rule(self, df: pd.DataFrame, column: str,
                   rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """규칙 검증"""
        violations = []

        if 'min' in rule:
            invalid = df[(df[column] < rule['min']) & (df[column].notna())]
            if len(invalid) > 0:
                violations.append({
                    'count': len(invalid),
                    'message': f'{len(invalid)} values below minimum {rule["min"]}'
                })

        if 'max' in rule:
            invalid = df[(df[column] > rule['max']) & (df[column].notna())]
            if len(invalid) > 0:
                violations.append({
                    'count': len(invalid),
                    'message': f'{len(invalid)} values above maximum {rule["max"]}'
                })

        if 'pattern' in rule:
            import re
            pattern = rule['pattern']
            invalid = df[~df[column].astype(str).str.match(pattern)].index
            if len(invalid) > 0:
                violations.append({
                    'count': len(invalid),
                    'message': f'{len(invalid)} values do not match pattern'
                })

        return violations

    def check_contextual_anomalies(self, df: pd.DataFrame, column: str,
                                  context_window: int = 5) -> SemanticCheckResult:
        """문맥 기반 이상 탐지"""
        if column not in df.columns:
            return SemanticCheckResult(
                check_type=CheckType.CONTEXT.value,
                column=column,
                is_valid=False,
                issues=[{'type': 'column_not_found', 'message': f'Column {column} not found'}],
                suggestions=[],
                confidence=0.0,
                llm_feedback='Column not found in dataset',
                timestamp=datetime.now().isoformat()
            )

        issues = []
        suggestions = []

        # 시계열 데이터인 경우
        if pd.api.types.is_numeric_dtype(df[column]):
            try:
                data = df[column].dropna().values
                if len(data) > context_window:
                    # 이동 평균 기반 이상 탐지
                    moving_avg = pd.Series(data).rolling(window=context_window).mean()
                    deviation = np.abs(data - moving_avg.fillna(data.mean()))
                    threshold = deviation.std() * 2
                    anomalies = deviation > threshold

                    if anomalies.sum() > 0:
                        issues.append({
                            'type': 'contextual_anomaly',
                            'severity': 'MEDIUM',
                            'message': f'Found {anomalies.sum()} contextual anomalies'
                        })
                        suggestions.append('Check contextual anomalies - may indicate data entry errors')
            except Exception as e:
                logger.warning(f"Error in contextual analysis: {str(e)}")

        is_valid = len(issues) == 0
        confidence = 0.7 if is_valid else 0.5

        return SemanticCheckResult(
            check_type=CheckType.CONTEXT.value,
            column=column,
            is_valid=is_valid,
            issues=issues,
            suggestions=suggestions,
            confidence=confidence,
            llm_feedback=f"Contextual analysis completed",
            timestamp=datetime.now().isoformat()
        )

    def generate_report(self, results: List[SemanticCheckResult]) -> str:
        """검증 리포트 생성"""
        report = f"""
=== Semantic Data Quality Report ===
Generated: {datetime.now().isoformat()}

Total Checks: {len(results)}
Passed: {sum(1 for r in results if r.is_valid)}
Failed: {sum(1 for r in results if not r.is_valid)}

"""

        for result in results:
            status = "✓ PASS" if result.is_valid else "✗ FAIL"
            report += f"\n{result.column} [{result.check_type}]:"
            report += f"\n  Status: {status}"
            report += f"\n  Confidence: {result.confidence:.2%}"

            if result.issues:
                report += f"\n  Issues: {len(result.issues)}"
                for issue in result.issues[:3]:
                    report += f"\n    - {issue.get('message', issue.get('type'))}"

            if result.suggestions:
                report += f"\n  Suggestions:"
                for suggestion in result.suggestions[:2]:
                    report += f"\n    - {suggestion}"

        return report


def main():
    """테스트"""
    # 샘플 데이터
    np.random.seed(42)
    df = pd.DataFrame({
        'email': ['user1@example.com', 'invalid_email', 'user3@test.org', None, 'user5@company.com'],
        'age': [25, 35, 200, 28, 32],
        'salary': [50000, 60000, 75000, -5000, 55000],
        'phone': ['1234567890', '12345', '9876543210', '111', None],
        'name': ['John Doe', 'JANE SMITH', 'bob johnson', 'alice WONDER', 'charlie brown']
    })

    # 의미적 검증 수행
    checker = LLMSemanticChecker(mock_mode=True)

    results = []
    for col in ['email', 'age', 'salary']:
        # 일관성 검사
        result = checker.check_semantic_consistency(df, col)
        results.append(result)

        # 비즈니스 로직 검사
        result = checker.check_business_logic(df, col)
        results.append(result)

        # 문맥 기반 검사
        result = checker.check_contextual_anomalies(df, col)
        results.append(result)

    # 리포트 생성
    print(checker.generate_report(results))

    # 상세 결과
    print("\n=== Detailed Results ===")
    for result in results[:3]:
        print(f"\n{result.column} ({result.check_type}):")
        print(f"  Valid: {result.is_valid}")
        print(f"  Issues: {result.issues}")


if __name__ == "__main__":
    main()
