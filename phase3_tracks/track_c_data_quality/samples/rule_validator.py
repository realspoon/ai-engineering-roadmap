"""
Rule-Based Data Validator Module
규칙 기반 데이터 검증 (완전성, 유효성, 고유성, 범위 검증)

Features:
- 완전성 검증 (completeness)
- 유효성 검증 (validity)
- 고유성 검증 (uniqueness)
- 범위 검증 (range)
- 패턴 검증 (regex)
- 비즈니스 규칙 검증
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationRuleType(Enum):
    """검증 규칙 타입"""
    COMPLETENESS = "completeness"
    UNIQUENESS = "uniqueness"
    RANGE = "range"
    PATTERN = "pattern"
    VALIDITY = "validity"
    BUSINESS = "business"
    FOREIGN_KEY = "foreign_key"


@dataclass
class ValidationResult:
    """검증 결과"""
    rule_type: str
    column: str
    is_valid: bool
    error_count: int
    error_rate: float
    error_indices: List[int]
    message: str
    severity: str  # 'ERROR', 'WARNING', 'INFO'

    def to_dict(self) -> Dict:
        """Dictionary로 변환"""
        return {
            "rule_type": self.rule_type,
            "column": self.column,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "error_rate": self.error_rate,
            "error_indices": self.error_indices[:100],  # 처음 100개만
            "message": self.message,
            "severity": self.severity
        }


class ValidationRule:
    """검증 규칙 기본 클래스"""

    def __init__(self, column: str, rule_type: ValidationRuleType,
                 severity: str = "ERROR"):
        """
        초기화

        Args:
            column: 컬럼명
            rule_type: 규칙 타입
            severity: 심각도 (ERROR, WARNING, INFO)
        """
        self.column = column
        self.rule_type = rule_type
        self.severity = severity

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """검증 수행 (서브클래스에서 구현)"""
        raise NotImplementedError


class CompletenessRule(ValidationRule):
    """완전성 검증 규칙"""

    def __init__(self, column: str, null_threshold: float = 0.0):
        """
        초기화

        Args:
            column: 컬럼명
            null_threshold: 허용하는 결측치 비율 (0-1)
        """
        super().__init__(column, ValidationRuleType.COMPLETENESS)
        self.null_threshold = null_threshold

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """완전성 검증"""
        if self.column not in df.columns:
            return ValidationResult(
                rule_type=self.rule_type.value,
                column=self.column,
                is_valid=False,
                error_count=len(df),
                error_rate=1.0,
                error_indices=list(range(len(df))),
                message=f"Column '{self.column}' not found",
                severity="ERROR"
            )

        null_mask = df[self.column].isnull()
        error_count = null_mask.sum()
        error_rate = error_count / len(df)
        is_valid = error_rate <= self.null_threshold

        return ValidationResult(
            rule_type=self.rule_type.value,
            column=self.column,
            is_valid=is_valid,
            error_count=int(error_count),
            error_rate=float(error_rate),
            error_indices=np.where(null_mask)[0].tolist(),
            message=f"Null rate: {error_rate:.2%} (threshold: {self.null_threshold:.2%})",
            severity=self.severity if not is_valid else "INFO"
        )


class UniquenessRule(ValidationRule):
    """고유성 검증 규칙"""

    def __init__(self, column: str, allow_duplicates: bool = False):
        """
        초기화

        Args:
            column: 컬럼명
            allow_duplicates: 중복 허용 여부
        """
        super().__init__(column, ValidationRuleType.UNIQUENESS)
        self.allow_duplicates = allow_duplicates

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """고유성 검증"""
        if self.column not in df.columns:
            return ValidationResult(
                rule_type=self.rule_type.value,
                column=self.column,
                is_valid=False,
                error_count=len(df),
                error_rate=1.0,
                error_indices=list(range(len(df))),
                message=f"Column '{self.column}' not found",
                severity="ERROR"
            )

        # 결측치 제외하고 중복 검사
        valid_data = df[self.column].dropna()
        duplicate_mask = valid_data.duplicated(keep=False)
        error_indices = np.where(df[self.column].duplicated(keep=False))[0].tolist()
        error_count = len(error_indices)
        error_rate = error_count / len(df) if len(df) > 0 else 0
        is_valid = (error_count == 0) or self.allow_duplicates

        return ValidationResult(
            rule_type=self.rule_type.value,
            column=self.column,
            is_valid=is_valid,
            error_count=error_count,
            error_rate=float(error_rate),
            error_indices=error_indices,
            message=f"Duplicate count: {error_count}",
            severity=self.severity if not is_valid else "INFO"
        )


class RangeRule(ValidationRule):
    """범위 검증 규칙"""

    def __init__(self, column: str, min_value: Optional[float] = None,
                 max_value: Optional[float] = None):
        """
        초기화

        Args:
            column: 컬럼명
            min_value: 최소값
            max_value: 최대값
        """
        super().__init__(column, ValidationRuleType.RANGE)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """범위 검증"""
        if self.column not in df.columns:
            return ValidationResult(
                rule_type=self.rule_type.value,
                column=self.column,
                is_valid=False,
                error_count=len(df),
                error_rate=1.0,
                error_indices=list(range(len(df))),
                message=f"Column '{self.column}' not found",
                severity="ERROR"
            )

        try:
            data = pd.to_numeric(df[self.column], errors='coerce')
        except:
            return ValidationResult(
                rule_type=self.rule_type.value,
                column=self.column,
                is_valid=False,
                error_count=len(df),
                error_rate=1.0,
                error_indices=list(range(len(df))),
                message=f"Column '{self.column}' cannot be converted to numeric",
                severity="ERROR"
            )

        # 범위 검사
        invalid_mask = pd.Series([False] * len(df))

        if self.min_value is not None:
            invalid_mask |= (data < self.min_value) | data.isnull()
        if self.max_value is not None:
            invalid_mask |= (data > self.max_value) | data.isnull()

        error_indices = np.where(invalid_mask)[0].tolist()
        error_count = len(error_indices)
        error_rate = error_count / len(df) if len(df) > 0 else 0
        is_valid = error_count == 0

        range_str = f"[{self.min_value}, {self.max_value}]"
        return ValidationResult(
            rule_type=self.rule_type.value,
            column=self.column,
            is_valid=is_valid,
            error_count=error_count,
            error_rate=float(error_rate),
            error_indices=error_indices,
            message=f"Out of range {range_str}: {error_count} rows",
            severity=self.severity if not is_valid else "INFO"
        )


class PatternRule(ValidationRule):
    """패턴 검증 규칙 (정규표현식)"""

    def __init__(self, column: str, pattern: str):
        """
        초기화

        Args:
            column: 컬럼명
            pattern: 정규표현식 패턴
        """
        super().__init__(column, ValidationRuleType.PATTERN)
        self.pattern = pattern
        self.compiled_pattern = re.compile(pattern)

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """패턴 검증"""
        if self.column not in df.columns:
            return ValidationResult(
                rule_type=self.rule_type.value,
                column=self.column,
                is_valid=False,
                error_count=len(df),
                error_rate=1.0,
                error_indices=list(range(len(df))),
                message=f"Column '{self.column}' not found",
                severity="ERROR"
            )

        # 패턴 매칭
        invalid_mask = ~df[self.column].astype(str).str.match(self.pattern)
        error_indices = np.where(invalid_mask)[0].tolist()
        error_count = len(error_indices)
        error_rate = error_count / len(df) if len(df) > 0 else 0
        is_valid = error_count == 0

        return ValidationResult(
            rule_type=self.rule_type.value,
            column=self.column,
            is_valid=is_valid,
            error_count=error_count,
            error_rate=float(error_rate),
            error_indices=error_indices,
            message=f"Pattern mismatch for pattern '{self.pattern}': {error_count} rows",
            severity=self.severity if not is_valid else "INFO"
        )


class BusinessRule(ValidationRule):
    """비즈니스 규칙 검증"""

    def __init__(self, column: str, validator_func: Callable[[pd.Series], pd.Series]):
        """
        초기화

        Args:
            column: 컬럼명
            validator_func: 검증 함수 (Series -> bool Series)
        """
        super().__init__(column, ValidationRuleType.BUSINESS)
        self.validator_func = validator_func

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """비즈니스 규칙 검증"""
        if self.column not in df.columns:
            return ValidationResult(
                rule_type=self.rule_type.value,
                column=self.column,
                is_valid=False,
                error_count=len(df),
                error_rate=1.0,
                error_indices=list(range(len(df))),
                message=f"Column '{self.column}' not found",
                severity="ERROR"
            )

        try:
            is_valid_series = self.validator_func(df[self.column])
            invalid_mask = ~is_valid_series
            error_indices = np.where(invalid_mask)[0].tolist()
            error_count = len(error_indices)
            error_rate = error_count / len(df) if len(df) > 0 else 0
            is_valid = error_count == 0

            return ValidationResult(
                rule_type=self.rule_type.value,
                column=self.column,
                is_valid=is_valid,
                error_count=error_count,
                error_rate=float(error_rate),
                error_indices=error_indices,
                message=f"Business rule violation: {error_count} rows",
                severity=self.severity if not is_valid else "INFO"
            )
        except Exception as e:
            return ValidationResult(
                rule_type=self.rule_type.value,
                column=self.column,
                is_valid=False,
                error_count=0,
                error_rate=0.0,
                error_indices=[],
                message=f"Business rule validation error: {str(e)}",
                severity="ERROR"
            )


class RuleValidator:
    """규칙 기반 검증기"""

    def __init__(self):
        """초기화"""
        self.rules: List[ValidationRule] = []

    def add_rule(self, rule: ValidationRule) -> None:
        """규칙 추가"""
        self.rules.append(rule)
        logger.info(f"Rule added: {rule.rule_type.value} on {rule.column}")

    def validate(self, df: pd.DataFrame) -> Dict[str, List[ValidationResult]]:
        """모든 규칙으로 검증"""
        results = {}

        for rule in self.rules:
            try:
                result = rule.validate(df)
                if result.column not in results:
                    results[result.column] = []
                results[result.column].append(result)

                status = "PASS" if result.is_valid else "FAIL"
                logger.info(f"[{status}] {rule.rule_type.value} - {rule.column}")

            except Exception as e:
                logger.error(f"Error validating rule {rule.rule_type.value}: {str(e)}")

        return results

    def generate_report(self, df: pd.DataFrame) -> str:
        """검증 리포트 생성"""
        results = self.validate(df)

        report = f"""
=== Data Validation Report ===
Generated: {datetime.now().isoformat()}
Total Rows: {len(df)}

"""

        total_errors = 0
        for col, col_results in results.items():
            report += f"\n{col}:\n"
            for result in col_results:
                status = "✓ PASS" if result.is_valid else "✗ FAIL"
                report += f"  [{status}] {result.rule_type}"
                report += f"\n       {result.message}\n"
                if not result.is_valid:
                    total_errors += result.error_count

        report += f"\nTotal Validation Errors: {total_errors}"
        return report

    def get_invalid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """검증에 실패한 행 조회"""
        results = self.validate(df)
        invalid_indices = set()

        for col_results in results.values():
            for result in col_results:
                if not result.is_valid:
                    invalid_indices.update(result.error_indices)

        return df.iloc[list(invalid_indices)].copy()


def main():
    """테스트"""
    # 샘플 데이터 생성
    np.random.seed(42)
    df = pd.DataFrame({
        'id': range(1, 101),
        'email': [f'user{i}@example.com' if i % 10 != 0 else None for i in range(100)],
        'age': np.random.normal(35, 10, 100).astype(int),
        'salary': np.random.normal(50000, 15000, 100),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    })

    # 검증기 생성
    validator = RuleValidator()

    # 규칙 추가
    validator.add_rule(CompletenessRule('email', null_threshold=0.05))
    validator.add_rule(UniquenessRule('id', allow_duplicates=False))
    validator.add_rule(RangeRule('age', min_value=0, max_value=120))
    validator.add_rule(RangeRule('salary', min_value=0, max_value=1000000))
    validator.add_rule(PatternRule('email', r'.*@example\.com'))
    validator.add_rule(BusinessRule('age', lambda x: x >= 18))

    # 검증 수행
    results = validator.validate(df)

    # 리포트 출력
    print(validator.generate_report(df))

    # 검증 실패한 행 출력
    print("\n=== Invalid Rows ===")
    print(validator.get_invalid_rows(df))


if __name__ == "__main__":
    main()
