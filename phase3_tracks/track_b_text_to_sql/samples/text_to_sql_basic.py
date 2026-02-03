"""
Text-to-SQL Basic Module
자연어를 SQL로 변환하는 기본 구현
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum
import json


class QueryType(Enum):
    """쿼리 타입"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    AGGREGATE = "AGGREGATE"
    JOIN = "JOIN"


class SimpleTextToSQL:
    """간단한 Text-to-SQL 변환기"""

    def __init__(self):
        self.keywords = {
            'select': ['조회', '보여줘', '찾아'],
            'count': ['개수', '몇개', '갯수'],
            'sum': ['합계', '합', '총합'],
            'avg': ['평균'],
            'max': ['최대', '최고'],
            'min': ['최소', '최저'],
            'where': ['어디', '중', '조건'],
            'order': ['정렬', '순서'],
            'limit': ['상위', '개'],
            'group': ['그룹', '별로', '기준']
        }

    def parse_query(self, natural_text: str) -> Dict[str, str]:
        """자연어 쿼리 파싱"""
        # 한글 공백 제거
        text = natural_text.strip()

        # 기본 구조 추출
        parsed = {
            'action': None,
            'table': None,
            'columns': [],
            'conditions': [],
            'aggregations': [],
            'order_by': None,
            'limit': None,
            'group_by': None
        }

        # 액션 판단
        if any(kw in text for kw in self.keywords['select']):
            parsed['action'] = 'SELECT'
        elif '추가' in text or '저장' in text:
            parsed['action'] = 'INSERT'
        elif '수정' in text or '변경' in text:
            parsed['action'] = 'UPDATE'
        elif '삭제' in text:
            parsed['action'] = 'DELETE'

        return parsed

    def extract_table_name(self, text: str) -> str:
        """테이블명 추출"""
        # 정규식으로 테이블명 패턴 찾기
        # 예: "사용자 테이블에서", "employees 테이블"
        pattern = r'(\w+)\s*(?:테이블|from|의)'
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(1)
        return None

    def extract_columns(self, text: str) -> List[str]:
        """컬럼명 추출"""
        # 컬럼명 패턴: 단어들 (쉼표로 구분)
        # 예: "이름, 나이, 급여"
        columns = []

        # 영문 컬럼명
        word_pattern = r'(\w+)\s*(?:,|and|또는|와|그리고)'
        matches = re.findall(word_pattern, text, re.IGNORECASE)
        columns.extend(matches)

        return columns

    def extract_conditions(self, text: str) -> List[Dict[str, str]]:
        """WHERE 조건 추출"""
        conditions = []

        # 조건 패턴: "컬럼 = 값" 또는 "컬럼이 값"
        condition_pattern = r'(\w+)\s*(?:=|은|이|가|보다|초과|미만)\s*(["\']?)(.+?)\2(?:[,;]|그리고|그래서|$)'
        matches = re.findall(condition_pattern, text)

        for col, quote, value in matches:
            conditions.append({
                'column': col,
                'value': value.strip()
            })

        return conditions


class ContextualTextToSQL:
    """컨텍스트를 고려한 Text-to-SQL"""

    def __init__(self, schema: Dict[str, Dict[str, Any]]):
        """
        스키마 초기화
        schema = {
            'table_name': {
                'columns': ['col1', 'col2', ...],
                'types': {'col1': 'int', 'col2': 'string', ...}
            }
        }
        """
        self.schema = schema
        self.converter = SimpleTextToSQL()

    def convert(self, natural_text: str, table_name: str = None) -> str:
        """자연어를 SQL로 변환"""
        # 테이블명 추출 (명시적이거나 파싱)
        if not table_name:
            table_name = self.converter.extract_table_name(natural_text)

        if not table_name or table_name not in self.schema:
            raise ValueError(f"테이블을 찾을 수 없습니다: {table_name}")

        # 액션 판단
        action = self._determine_action(natural_text)

        if action == QueryType.SELECT:
            return self._generate_select(natural_text, table_name)
        elif action == QueryType.AGGREGATE:
            return self._generate_aggregate(natural_text, table_name)
        elif action == QueryType.INSERT:
            return self._generate_insert(natural_text, table_name)
        elif action == QueryType.UPDATE:
            return self._generate_update(natural_text, table_name)
        elif action == QueryType.DELETE:
            return self._generate_delete(natural_text, table_name)

        return f"SELECT * FROM {table_name}"

    def _determine_action(self, text: str) -> QueryType:
        """액션 판단"""
        if any(kw in text for kw in ['개수', '몇개', '합계', '합', '평균', '최대', '최소']):
            return QueryType.AGGREGATE
        elif any(kw in text for kw in ['추가', '저장', '입력']):
            return QueryType.INSERT
        elif any(kw in text for kw in ['수정', '변경', '업데이트']):
            return QueryType.UPDATE
        elif any(kw in text for kw in ['삭제', '제거']):
            return QueryType.DELETE
        else:
            return QueryType.SELECT

    def _generate_select(self, natural_text: str, table_name: str) -> str:
        """SELECT 쿼리 생성"""
        columns = self.converter.extract_columns(natural_text)
        conditions = self.converter.extract_conditions(natural_text)

        # 컬럼명 검증
        valid_columns = self.schema[table_name]['columns']
        selected_columns = [c for c in columns if c in valid_columns]

        if not selected_columns:
            selected_columns = ['*']

        # 기본 SELECT
        sql = f"SELECT {', '.join(selected_columns)} FROM {table_name}"

        # WHERE 조건 추가
        if conditions:
            where_clauses = []
            for cond in conditions:
                col = cond['column']
                val = cond['value']

                # 문자열/숫자 판단
                if val.isdigit():
                    where_clauses.append(f"{col} = {val}")
                else:
                    where_clauses.append(f"{col} = '{val}'")

            sql += " WHERE " + " AND ".join(where_clauses)

        # ORDER BY 추가
        if '정렬' in natural_text:
            if '내림' in natural_text or '큰' in natural_text:
                sql += " ORDER BY " + selected_columns[0] + " DESC"
            else:
                sql += " ORDER BY " + selected_columns[0] + " ASC"

        # LIMIT 추가
        limit_match = re.search(r'(?:상위|상단|처음)\s*(\d+)', natural_text)
        if limit_match:
            sql += f" LIMIT {limit_match.group(1)}"

        return sql

    def _generate_aggregate(self, natural_text: str, table_name: str) -> str:
        """집계 쿼리 생성"""
        columns = self.converter.extract_columns(natural_text)
        valid_columns = self.schema[table_name]['columns']

        # 집계 함수 판단
        agg_func = None
        if '개수' in natural_text or '몇개' in natural_text:
            agg_func = 'COUNT'
        elif '합계' in natural_text or '합' in natural_text:
            agg_func = 'SUM'
        elif '평균' in natural_text:
            agg_func = 'AVG'
        elif '최대' in natural_text or '최고' in natural_text:
            agg_func = 'MAX'
        elif '최소' in natural_text or '최저' in natural_text:
            agg_func = 'MIN'

        if not agg_func:
            agg_func = 'COUNT'

        # 컬럼 선택
        target_col = next((c for c in columns if c in valid_columns), '*')

        # GROUP BY 확인
        if '별로' in natural_text or '그룹' in natural_text:
            group_col = next((c for c in columns if c != target_col and c in valid_columns), columns[0] if columns else None)
            if group_col:
                return f"SELECT {group_col}, {agg_func}({target_col}) FROM {table_name} GROUP BY {group_col}"

        return f"SELECT {agg_func}({target_col}) FROM {table_name}"

    def _generate_insert(self, natural_text: str, table_name: str) -> str:
        """INSERT 쿼리 생성"""
        # 간단한 INSERT 생성
        return f"INSERT INTO {table_name} VALUES (...)"

    def _generate_update(self, natural_text: str, table_name: str) -> str:
        """UPDATE 쿼리 생성"""
        # 간단한 UPDATE 생성
        return f"UPDATE {table_name} SET ... WHERE ..."

    def _generate_delete(self, natural_text: str, table_name: str) -> str:
        """DELETE 쿼리 생성"""
        # 간단한 DELETE 생성
        return f"DELETE FROM {table_name} WHERE ..."


class NaturalLanguageParser:
    """자연언어 파서"""

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """텍스트 토큰화"""
        # 간단한 토큰화
        tokens = re.findall(r'\b\w+\b|[=<>!]+', text, re.IGNORECASE)
        return tokens

    @staticmethod
    def identify_entities(text: str) -> Dict[str, List[str]]:
        """엔티티 식별"""
        entities = {
            'tables': [],
            'columns': [],
            'values': [],
            'operators': [],
            'functions': []
        }

        # 함수 식별
        functions = ['count', 'sum', 'avg', 'max', 'min', 'group']
        for func in functions:
            if func in text.lower():
                entities['functions'].append(func)

        # 연산자 식별
        operators = ['=', '>', '<', '>=', '<=', '!=', 'and', 'or']
        for op in operators:
            if op in text.lower():
                entities['operators'].append(op)

        return entities


class TextToSQLPipeline:
    """Text-to-SQL 파이프라인"""

    def __init__(self, schema: Dict[str, Dict[str, Any]]):
        self.schema = schema
        self.converter = ContextualTextToSQL(schema)
        self.parser = NaturalLanguageParser()

    def process(self, natural_text: str) -> Dict[str, str]:
        """전체 파이프라인 처리"""
        # 1. 텍스트 정규화
        normalized_text = self._normalize_text(natural_text)

        # 2. 엔티티 식별
        entities = self.parser.identify_entities(normalized_text)

        # 3. SQL 생성
        try:
            sql = self.converter.convert(normalized_text)
        except Exception as e:
            sql = f"-- 변환 실패: {str(e)}"

        # 4. 결과 반환
        return {
            'input': natural_text,
            'normalized': normalized_text,
            'entities': entities,
            'sql': sql,
            'confidence': self._estimate_confidence(normalized_text, sql)
        }

    def _normalize_text(self, text: str) -> str:
        """텍스트 정규화"""
        # 여러 공백 정규화
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _estimate_confidence(self, text: str, sql: str) -> float:
        """변환 신뢰도 추정"""
        # 간단한 휴리스틱
        if '--' in sql or '...' in sql:
            return 0.3

        tokens = len(text.split())
        if tokens < 3:
            return 0.5

        return min(1.0, 0.7 + (len(sql) / 100))


# 사용 예제
if __name__ == "__main__":
    # 스키마 정의
    schema = {
        'employees': {
            'columns': ['id', 'name', 'salary', 'department_id', 'hire_date'],
            'types': {
                'id': 'int',
                'name': 'string',
                'salary': 'float',
                'department_id': 'int',
                'hire_date': 'date'
            }
        },
        'departments': {
            'columns': ['id', 'name', 'location'],
            'types': {'id': 'int', 'name': 'string', 'location': 'string'}
        }
    }

    # Text-to-SQL 변환
    print("=== Text-to-SQL 기본 변환 ===\n")

    pipeline = TextToSQLPipeline(schema)

    test_queries = [
        "직원 테이블에서 모든 이름과 급여를 조회해",
        "employees 테이블의 급여 합계를 구해",
        "부서별 직원 개수를 조회해",
        "급여가 50000보다 큰 직원을 찾아"
    ]

    for query in test_queries:
        result = pipeline.process(query)
        print(f"입력: {result['input']}")
        print(f"SQL: {result['sql']}")
        print(f"신뢰도: {result['confidence']:.2%}")
        print()
