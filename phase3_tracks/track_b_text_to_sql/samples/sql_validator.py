"""
SQL Validator Module
SQL 검증, 최적화, 보안 체크
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class SeverityLevel(Enum):
    """심각도 레벨"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ValidationIssue:
    """검증 이슈"""
    severity: SeverityLevel
    category: str
    message: str
    line: Optional[int] = None
    suggestion: Optional[str] = None


class SQLValidator:
    """SQL 검증기"""

    def __init__(self):
        self.issues = []
        self.sql = None

    def validate(self, sql: str) -> Dict[str, Any]:
        """SQL 검증"""
        self.sql = sql
        self.issues = []

        # 각 검증 실행
        self._check_syntax()
        self._check_performance()
        self._check_security()
        self._check_best_practices()

        # 결과 정리
        return {
            'sql': sql,
            'valid': len([i for i in self.issues if i.severity == SeverityLevel.ERROR]) == 0,
            'issues': self._serialize_issues(),
            'summary': self._generate_summary()
        }

    def _check_syntax(self) -> None:
        """구문 검증"""
        # 필수 키워드 확인
        sql_upper = self.sql.upper().strip()

        # SELECT, UPDATE, INSERT, DELETE 등 필수 키워드
        required_keywords = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP'
        ]

        has_keyword = any(kw in sql_upper for kw in required_keywords)
        if not has_keyword:
            self.issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="Syntax",
                message="유효한 SQL 키워드가 없습니다"
            ))

        # 괄호 짝 확인
        if self.sql.count('(') != self.sql.count(')'):
            self.issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="Syntax",
                message="괄호가 일치하지 않습니다"
            ))

        # 따옴표 짝 확인
        single_quotes = self.sql.count("'") % 2
        double_quotes = self.sql.count('"') % 2

        if single_quotes != 0:
            self.issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="Syntax",
                message="작은따옴표가 일치하지 않습니다"
            ))

        if double_quotes != 0:
            self.issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="Syntax",
                message="큰따옴표가 일치하지 않습니다"
            ))

        # SELECT ... FROM 확인
        if 'SELECT' in sql_upper and 'FROM' not in sql_upper:
            # COUNT(*) 같은 단순 집계 제외
            if 'COUNT' not in sql_upper:
                self.issues.append(ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    category="Syntax",
                    message="SELECT 쿼리에 FROM 절이 없습니다"
                ))

    def _check_performance(self) -> None:
        """성능 문제 검사"""
        sql_upper = self.sql.upper()

        # SELECT * 사용
        if re.search(r'SELECT\s+\*', sql_upper):
            self.issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="Performance",
                message="SELECT *는 성능이 나쁩니다. 필요한 컬럼만 선택하세요",
                suggestion="SELECT column1, column2, ... FROM table"
            ))

        # 서브쿼리 다중 사용
        subquery_count = len(re.findall(r'\(SELECT', sql_upper))
        if subquery_count > 2:
            self.issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="Performance",
                message=f"많은 서브쿼리({subquery_count}개) 사용. JOIN 사용을 권장합니다",
                suggestion="서브쿼리를 JOIN으로 변경해보세요"
            ))

        # 함수를 WHERE 절에 사용
        where_match = re.search(r'WHERE\s+(.+?)(?:GROUP|ORDER|LIMIT|$)', sql_upper)
        if where_match:
            where_clause = where_match.group(1)
            functions = ['LOWER', 'UPPER', 'SUBSTRING', 'CAST', 'CONVERT']
            if any(f in where_clause for f in functions):
                self.issues.append(ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    category="Performance",
                    message="WHERE 절에서 함수를 사용하면 인덱스를 사용할 수 없습니다"
                ))

        # LIKE %로 시작
        if re.search(r"LIKE\s+'%", sql_upper):
            self.issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="Performance",
                message="LIKE '%패턴'은 인덱스를 사용할 수 없습니다",
                suggestion="LIKE '패턴%' 형식을 권장합니다"
            ))

        # OR 조건 많음
        or_count = len(re.findall(r'\bOR\b', sql_upper))
        if or_count > 3:
            self.issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="Performance",
                message=f"많은 OR 조건({or_count}개)은 성능이 나쁠 수 있습니다. IN 사용 권장"
            ))

    def _check_security(self) -> None:
        """보안 검사"""
        sql_lower = self.sql.lower()

        # SQL Injection 패턴
        injection_patterns = [
            (r"'\s*OR\s*'1'\s*=\s*'1", "SQL Injection 패턴 감지"),
            (r'"\s*OR\s*"1"\s*=\s*"1', "SQL Injection 패턴 감지"),
            (r"'--", "SQL 주석 패턴 감지"),
            (r'/\*', "블록 주석 패턴 감지"),
        ]

        for pattern, message in injection_patterns:
            if re.search(pattern, self.sql):
                self.issues.append(ValidationIssue(
                    severity=SeverityLevel.CRITICAL,
                    category="Security",
                    message=message,
                    suggestion="매개변수화된 쿼리를 사용하세요"
                ))

        # DROP, TRUNCATE, DELETE without WHERE
        dangerous_ops = [
            (r'DROP\s+(?:TABLE|DATABASE|SCHEMA)', "DROP 문 사용"),
            (r'DELETE\s+FROM\s+\w+\s*(?:;|$)', "WHERE 없는 DELETE 문"),
            (r'TRUNCATE\s+TABLE', "TRUNCATE 문 사용")
        ]

        for pattern, message in dangerous_ops:
            if re.search(pattern, self.sql, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    severity=SeverityLevel.CRITICAL,
                    category="Security",
                    message=message,
                    suggestion="신중하게 실행하세요. 백업 확인 필수"
                ))

        # 공개 데이터 접근
        sensitive_tables = ['password', 'secret', 'token', 'key', 'credit_card', 'ssn']
        for table in sensitive_tables:
            if table in sql_lower:
                self.issues.append(ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    category="Security",
                    message=f"민감한 정보({table})에 접근합니다",
                    suggestion="접근 권한 확인 및 감시 로그 설정"
                ))

        # 사용자 입력 미검증
        if "'" in self.sql and not re.search(r'\?|\$\d|\:\w+', self.sql):
            self.issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="Security",
                message="매개변수화되지 않은 쿼리. SQL Injection 위험",
                suggestion="매개변수화된 쿼리 사용: WHERE id = ?"
            ))

    def _check_best_practices(self) -> None:
        """모범 사례 검사"""
        sql_upper = self.sql.upper()

        # 테이블 별칭 미사용 (JOIN 있을 때)
        if 'JOIN' in sql_upper and re.search(r'(\w+\.)+\w+', self.sql):
            # 별칭 없이 전체 테이블명 사용
            self.issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="BestPractice",
                message="JOIN 쿼리에서 별칭을 사용하면 가독성이 좋습니다",
                suggestion="FROM table1 t1 JOIN table2 t2 형식 사용"
            ))

        # 정렬 순서 명시 부족
        if 'ORDER BY' in sql_upper and 'ASC' not in sql_upper and 'DESC' not in sql_upper:
            self.issues.append(ValidationIssue(
                severity=SeverityLevel.INFO,
                category="BestPractice",
                message="ORDER BY에 정렬 순서(ASC/DESC)를 명시하세요",
                suggestion="ORDER BY column ASC 또는 ORDER BY column DESC"
            ))

        # NULL 처리
        if 'WHERE' in sql_upper and 'IS NULL' not in sql_upper and 'IS NOT NULL' not in sql_upper:
            if re.search(r'WHERE\s+\w+\s*=', sql_upper):
                self.issues.append(ValidationIssue(
                    severity=SeverityLevel.INFO,
                    category="BestPractice",
                    message="NULL 값 처리를 고려하세요",
                    suggestion="IS NULL 또는 COALESCE() 사용"
                ))

        # 대소문자 일관성
        keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'ORDER', 'GROUP', 'HAVING']
        uppercase_count = sum(self.sql.count(kw) for kw in keywords)
        lowercase_count = sum(self.sql.count(kw.lower()) for kw in keywords)

        if uppercase_count > 0 and lowercase_count > 0:
            self.issues.append(ValidationIssue(
                severity=SeverityLevel.INFO,
                category="BestPractice",
                message="SQL 키워드의 대소문자가 일관되지 않습니다",
                suggestion="대문자로 통일: SELECT, FROM, WHERE"
            ))

    def _serialize_issues(self) -> List[Dict[str, str]]:
        """이슈 직렬화"""
        return [
            {
                'severity': issue.severity.value,
                'category': issue.category,
                'message': issue.message,
                'suggestion': issue.suggestion
            }
            for issue in self.issues
        ]

    def _generate_summary(self) -> Dict[str, int]:
        """요약 생성"""
        severity_counts = {}
        for level in SeverityLevel:
            count = sum(1 for i in self.issues if i.severity == level)
            if count > 0:
                severity_counts[level.value] = count

        return severity_counts


class SQLOptimizer:
    """SQL 최적화"""

    @staticmethod
    def suggest_optimizations(sql: str) -> List[Dict[str, str]]:
        """최적화 제안"""
        suggestions = []
        sql_upper = sql.upper()

        # 1. SELECT * 최적화
        if 'SELECT *' in sql_upper:
            suggestions.append({
                'issue': 'SELECT *',
                'current': 'SELECT * FROM table',
                'suggested': 'SELECT id, name, email FROM table',
                'benefit': '네트워크 트래픽 감소, 인덱스 활용도 향상'
            })

        # 2. JOIN 순서 최적화
        if 'JOIN' in sql_upper:
            suggestions.append({
                'issue': 'JOIN 순서',
                'current': '큰 테이블부터 JOIN',
                'suggested': '작은 테이블부터 JOIN',
                'benefit': 'CPU 사용 최소화'
            })

        # 3. WHERE 조건 최적화
        if 'WHERE' in sql_upper:
            suggestions.append({
                'issue': 'WHERE 조건',
                'current': '함수 사용: WHERE YEAR(date) = 2024',
                'suggested': '직접 비교: WHERE date >= \'2024-01-01\'',
                'benefit': '인덱스 활용으로 성능 향상'
            })

        # 4. GROUP BY 최적화
        if 'GROUP BY' in sql_upper:
            suggestions.append({
                'issue': 'GROUP BY',
                'current': 'GROUP BY HAVING으로 필터링',
                'suggested': 'WHERE로 사전 필터링 후 GROUP BY',
                'benefit': 'GROUP 전 데이터량 감소'
            })

        return suggestions

    @staticmethod
    def estimate_execution_plan(sql: str) -> Dict[str, Any]:
        """실행 계획 추정"""
        plan = {
            'query': sql,
            'estimated_operations': [],
            'complexity': 'UNKNOWN'
        }

        sql_upper = sql.upper()

        # 복잡도 추정
        complexity_score = 0
        if 'JOIN' in sql_upper:
            complexity_score += 10 * (sql_upper.count('JOIN') + 1)
        if 'SUBQUERY' in sql_upper or '(SELECT' in sql_upper:
            complexity_score += 20
        if 'GROUP BY' in sql_upper:
            complexity_score += 10
        if 'ORDER BY' in sql_upper:
            complexity_score += 5

        if complexity_score < 20:
            plan['complexity'] = 'SIMPLE'
        elif complexity_score < 50:
            plan['complexity'] = 'MEDIUM'
        else:
            plan['complexity'] = 'COMPLEX'

        # 예상 작업
        if 'SELECT' in sql_upper:
            plan['estimated_operations'].append('Table Scan')
            if 'WHERE' in sql_upper:
                plan['estimated_operations'].append('Filter')
            if 'JOIN' in sql_upper:
                plan['estimated_operations'].append('Hash Join')
            if 'GROUP BY' in sql_upper:
                plan['estimated_operations'].append('Group Aggregate')
            if 'ORDER BY' in sql_upper:
                plan['estimated_operations'].append('Sort')

        return plan


class SQLFormatter:
    """SQL 포맷팅"""

    @staticmethod
    def format_sql(sql: str, indent: int = 2) -> str:
        """SQL 포맷팅"""
        # 키워드별 개행
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER JOIN',
            'LEFT JOIN', 'RIGHT JOIN', 'GROUP BY', 'HAVING',
            'ORDER BY', 'LIMIT', 'OFFSET'
        ]

        formatted = sql
        indent_str = ' ' * indent

        for keyword in keywords:
            pattern = f'\\b{keyword}\\b'
            formatted = re.sub(
                pattern,
                f'\n{keyword}',
                formatted,
                flags=re.IGNORECASE
            )

        # 들여쓰기 추가
        lines = formatted.split('\n')
        indented_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped:
                if i == 0 or stripped[0:3].upper() in ['SEL', 'FRO', 'WHE', 'JOI', 'GRO', 'HAV', 'ORD', 'LIM']:
                    indented_lines.append(stripped)
                else:
                    indented_lines.append(indent_str + stripped)

        return '\n'.join(indented_lines)


# 사용 예제
if __name__ == "__main__":
    print("=== SQL 검증 및 최적화 ===\n")

    test_sqls = [
        "SELECT * FROM users WHERE id = 1",
        "DELETE FROM orders WHERE user_id = 123",
        "SELECT * FROM users u JOIN orders o ON u.id = o.user_id WHERE u.id = 1 OR u.id = 2 OR u.id = 3",
        "SELECT * FROM users WHERE '1'='1'",
    ]

    validator = SQLValidator()

    for sql in test_sqls:
        print(f"SQL: {sql}")
        result = validator.validate(sql)

        print(f"유효: {result['valid']}")
        print(f"이슈: {len(result['issues'])}개")

        for issue in result['issues']:
            print(f"  - [{issue['severity']}] {issue['message']}")
            if issue['suggestion']:
                print(f"    제안: {issue['suggestion']}")

        print()
