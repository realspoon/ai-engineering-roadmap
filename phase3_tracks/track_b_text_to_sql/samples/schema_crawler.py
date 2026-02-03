"""
Schema Crawler Module
데이터베이스 스키마 자동 분석 및 메타데이터 추출
"""

import sqlite3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
from abc import ABC, abstractmethod


@dataclass
class Column:
    """컬럼 정보"""
    name: str
    type: str
    nullable: bool
    primary_key: bool
    foreign_key: Optional[str] = None
    default_value: Optional[str] = None


@dataclass
class Table:
    """테이블 정보"""
    name: str
    columns: List[Column]
    primary_keys: List[str]
    foreign_keys: Dict[str, str]
    row_count: int = 0


@dataclass
class Index:
    """인덱스 정보"""
    name: str
    table_name: str
    columns: List[str]
    is_unique: bool


class SchemaCrawlerBase(ABC):
    """스키마 크롤러 기본 클래스"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None

    @abstractmethod
    def connect(self) -> None:
        """데이터베이스 연결"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """데이터베이스 연결 종료"""
        pass

    @abstractmethod
    def get_tables(self) -> List[str]:
        """테이블 목록 조회"""
        pass

    @abstractmethod
    def get_table_schema(self, table_name: str) -> Table:
        """테이블 스키마 조회"""
        pass

    @abstractmethod
    def get_all_schemas(self) -> Dict[str, Table]:
        """모든 스키마 조회"""
        pass


class SQLiteSchemaCrawler(SchemaCrawlerBase):
    """SQLite 스키마 크롤러"""

    def connect(self) -> None:
        """SQLite 데이터베이스 연결"""
        try:
            self.connection = sqlite3.connect(self.connection_string)
            self.cursor = self.connection.cursor()
        except Exception as e:
            raise ConnectionError(f"SQLite 연결 실패: {str(e)}")

    def disconnect(self) -> None:
        """연결 종료"""
        if self.connection:
            self.connection.close()

    def get_tables(self) -> List[str]:
        """테이블 목록"""
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def get_table_schema(self, table_name: str) -> Table:
        """테이블 스키마"""
        try:
            # 컬럼 정보 조회
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = self.cursor.fetchall()

            columns = []
            primary_keys = []

            for col_info in columns_info:
                cid, name, col_type, notnull, default_value, pk = col_info

                column = Column(
                    name=name,
                    type=col_type,
                    nullable=not bool(notnull),
                    primary_key=bool(pk),
                    default_value=default_value
                )

                if pk:
                    primary_keys.append(name)

                columns.append(column)

            # 외래키 정보 조회
            self.cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys_info = self.cursor.fetchall()

            foreign_keys = {}
            for fk_info in foreign_keys_info:
                id, seq, table, from_col, to_col, on_delete, on_update, match = fk_info
                foreign_keys[from_col] = f"{table}.{to_col}"

            # 행 수 조회
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = self.cursor.fetchone()[0]

            return Table(
                name=table_name,
                columns=columns,
                primary_keys=primary_keys,
                foreign_keys=foreign_keys,
                row_count=row_count
            )

        except Exception as e:
            raise ValueError(f"스키마 조회 실패 ({table_name}): {str(e)}")

    def get_all_schemas(self) -> Dict[str, Table]:
        """모든 테이블 스키마"""
        tables = self.get_tables()
        schemas = {}

        for table_name in tables:
            try:
                schemas[table_name] = self.get_table_schema(table_name)
            except Exception as e:
                print(f"경고: {table_name} 스키마 조회 실패 - {str(e)}")

        return schemas

    def get_indexes(self, table_name: str) -> List[Index]:
        """테이블의 인덱스 조회"""
        self.cursor.execute(f"PRAGMA index_list({table_name})")
        indexes_info = self.cursor.fetchall()

        indexes = []

        for idx_info in indexes_info:
            seq, name, unique, origin, partial = idx_info

            # 인덱스 컬럼 조회
            self.cursor.execute(f"PRAGMA index_info({name})")
            cols_info = self.cursor.fetchall()
            columns = [col_info[2] for col_info in cols_info]

            index = Index(
                name=name,
                table_name=table_name,
                columns=columns,
                is_unique=bool(unique)
            )

            indexes.append(index)

        return indexes


class MySQLSchemaCrawler(SchemaCrawlerBase):
    """MySQL 스키마 크롤러 (샘플)"""

    def connect(self) -> None:
        """MySQL 연결"""
        try:
            import pymysql
            self.connection = pymysql.connect(
                **self._parse_connection_string()
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            raise ConnectionError(f"MySQL 연결 실패: {str(e)}")

    def disconnect(self) -> None:
        """연결 종료"""
        if self.connection:
            self.connection.close()

    def _parse_connection_string(self) -> Dict[str, str]:
        """연결 문자열 파싱"""
        # 형식: mysql://user:password@host:port/database
        import re
        pattern = r'mysql://(?P<user>\w+):(?P<password>\w+)@(?P<host>[^:]+):(?P<port>\d+)/(?P<database>\w+)'
        match = re.match(pattern, self.connection_string)

        if not match:
            raise ValueError("올바르지 않은 연결 문자열 형식")

        return match.groupdict()

    def get_tables(self) -> List[str]:
        """테이블 목록"""
        self.cursor.execute("SHOW TABLES")
        return [row[0] for row in self.cursor.fetchall()]

    def get_table_schema(self, table_name: str) -> Table:
        """테이블 스키마"""
        try:
            self.cursor.execute(f"DESCRIBE {table_name}")
            columns_info = self.cursor.fetchall()

            columns = []
            primary_keys = []

            for col_info in columns_info:
                name, col_type, nullable, key, default_value, extra = col_info

                column = Column(
                    name=name,
                    type=col_type,
                    nullable=nullable.upper() == 'YES',
                    primary_key=key.upper() == 'PRI',
                    default_value=default_value
                )

                if key.upper() == 'PRI':
                    primary_keys.append(name)

                columns.append(column)

            # 외래키 정보
            self.cursor.execute(f"""
                SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_NAME = '{table_name}' AND REFERENCED_TABLE_NAME IS NOT NULL
            """)

            foreign_keys = {}
            for fk_info in self.cursor.fetchall():
                from_col, ref_table, ref_col = fk_info
                foreign_keys[from_col] = f"{ref_table}.{ref_col}"

            # 행 수
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = self.cursor.fetchone()[0]

            return Table(
                name=table_name,
                columns=columns,
                primary_keys=primary_keys,
                foreign_keys=foreign_keys,
                row_count=row_count
            )

        except Exception as e:
            raise ValueError(f"스키마 조회 실패: {str(e)}")

    def get_all_schemas(self) -> Dict[str, Table]:
        """모든 테이블 스키마"""
        tables = self.get_tables()
        schemas = {}

        for table_name in tables:
            try:
                schemas[table_name] = self.get_table_schema(table_name)
            except Exception as e:
                print(f"경고: {table_name} 스키마 조회 실패")

        return schemas


class SchemaAnalyzer:
    """스키마 분석"""

    def __init__(self, schemas: Dict[str, Table]):
        self.schemas = schemas

    def get_relationship_graph(self) -> Dict[str, List[str]]:
        """테이블 관계도"""
        graph = {}

        for table_name, table in self.schemas.items():
            related_tables = set()

            # 외래키 관계
            for fk_table in table.foreign_keys.values():
                ref_table = fk_table.split('.')[0]
                related_tables.add(ref_table)

            graph[table_name] = list(related_tables)

        return graph

    def find_orphan_tables(self) -> List[str]:
        """고아 테이블 (관계 없는 테이블)"""
        graph = self.get_relationship_graph()
        orphan_tables = []

        for table_name, related_tables in graph.items():
            # 다른 테이블에서 참조되는지 확인
            is_referenced = False

            for other_table, fks in graph.items():
                if table_name in fks:
                    is_referenced = True
                    break

            # 다른 테이블을 참조하지도, 참조되지도 않음
            if not related_tables and not is_referenced:
                orphan_tables.append(table_name)

        return orphan_tables

    def get_table_statistics(self) -> Dict[str, Any]:
        """테이블 통계"""
        stats = {
            'total_tables': len(self.schemas),
            'total_columns': sum(len(table.columns) for table in self.schemas.values()),
            'total_rows': sum(table.row_count for table in self.schemas.values()),
            'tables_with_fk': 0,
            'tables_by_size': []
        }

        # 외래키 있는 테이블
        stats['tables_with_fk'] = sum(
            1 for table in self.schemas.values() if table.foreign_keys
        )

        # 크기별 테이블
        tables_by_size = [
            {
                'name': table.name,
                'row_count': table.row_count,
                'column_count': len(table.columns)
            }
            for table in self.schemas.values()
        ]

        stats['tables_by_size'] = sorted(
            tables_by_size,
            key=lambda x: x['row_count'],
            reverse=True
        )

        return stats

    def get_column_stats(self) -> Dict[str, Any]:
        """컬럼 통계"""
        stats = {
            'total_columns': 0,
            'columns_by_type': {},
            'nullable_columns': 0,
            'pk_columns': 0
        }

        for table in self.schemas.values():
            for column in table.columns:
                stats['total_columns'] += 1

                # 타입별 통계
                col_type = column.type.upper()
                stats['columns_by_type'][col_type] = stats['columns_by_type'].get(col_type, 0) + 1

                # NULL 허용 컬럼
                if column.nullable:
                    stats['nullable_columns'] += 1

                # 주키 컬럼
                if column.primary_key:
                    stats['pk_columns'] += 1

        return stats


class SchemaCrawlerFactory:
    """스키마 크롤러 팩토리"""

    _crawlers = {
        'sqlite': SQLiteSchemaCrawler,
        'mysql': MySQLSchemaCrawler,
    }

    @classmethod
    def create_crawler(cls, connection_string: str) -> SchemaCrawlerBase:
        """연결 문자열로 크롤러 생성"""
        db_type = connection_string.split('://')[0].lower()

        if db_type not in cls._crawlers:
            raise ValueError(f"지원하지 않는 DB 타입: {db_type}")

        return cls._crawlers[db_type](connection_string)


class SchemaManager:
    """스키마 관리"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.crawler = SchemaCrawlerFactory.create_crawler(connection_string)
        self.schemas = {}
        self.analyzer = None

    def analyze_schema(self) -> Dict[str, Any]:
        """스키마 분석"""
        try:
            self.crawler.connect()
            self.schemas = self.crawler.get_all_schemas()
            self.analyzer = SchemaAnalyzer(self.schemas)

            analysis = {
                'schemas': self._serialize_schemas(),
                'statistics': self.analyzer.get_table_statistics(),
                'column_stats': self.analyzer.get_column_stats(),
                'relationships': self.analyzer.get_relationship_graph(),
                'orphan_tables': self.analyzer.find_orphan_tables()
            }

            return analysis

        finally:
            self.crawler.disconnect()

    def _serialize_schemas(self) -> Dict[str, Dict[str, Any]]:
        """스키마를 JSON 직렬화 가능한 형태로"""
        result = {}

        for table_name, table in self.schemas.items():
            result[table_name] = {
                'name': table.name,
                'columns': [
                    {
                        'name': col.name,
                        'type': col.type,
                        'nullable': col.nullable,
                        'primary_key': col.primary_key,
                        'default_value': col.default_value
                    }
                    for col in table.columns
                ],
                'primary_keys': table.primary_keys,
                'foreign_keys': table.foreign_keys,
                'row_count': table.row_count
            }

        return result

    def export_schema(self, output_path: str) -> None:
        """스키마를 JSON으로 내보내기"""
        analysis = self.analyze_schema()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

    def get_table_description(self, table_name: str) -> str:
        """테이블 설명 생성"""
        if table_name not in self.schemas:
            raise ValueError(f"테이블을 찾을 수 없습니다: {table_name}")

        table = self.schemas[table_name]

        description = f"""
Table: {table.name}
Rows: {table.row_count}
Columns: {len(table.columns)}

Columns:
"""

        for column in table.columns:
            pk_marker = " [PK]" if column.primary_key else ""
            nullable_marker = "" if column.nullable else " [NOT NULL]"
            description += f"  - {column.name}: {column.type}{pk_marker}{nullable_marker}\n"

        if table.foreign_keys:
            description += "\nForeign Keys:\n"
            for from_col, to_table_col in table.foreign_keys.items():
                description += f"  - {from_col} -> {to_table_col}\n"

        return description


# 사용 예제
if __name__ == "__main__":
    # SQLite 샘플 데이터베이스 생성
    import sqlite3

    db_path = '/tmp/sample.db'

    # 데이터베이스 생성
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            salary REAL,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT
        )
    ''')

    conn.commit()
    conn.close()

    # 스키마 분석
    print("=== 스키마 크롤링 및 분석 ===\n")

    manager = SchemaManager(f'sqlite:///{db_path}')
    analysis = manager.analyze_schema()

    print("1. 테이블 통계:")
    print(json.dumps(analysis['statistics'], indent=2, ensure_ascii=False))

    print("\n2. 컬럼 통계:")
    print(json.dumps(analysis['column_stats'], indent=2, ensure_ascii=False))

    print("\n3. 테이블 관계:")
    print(json.dumps(analysis['relationships'], indent=2, ensure_ascii=False))

    print("\n4. 테이블 설명:")
    print(manager.get_table_description('employees'))
