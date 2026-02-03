# Week 18: 스키마 분석 (메타데이터, ERD 자동 생성)

## 학습 목표
- 데이터베이스 메타데이터 추출 및 분석
- 자동화된 ERD(Entity-Relationship Diagram) 생성
- 스키마 정보 수집 및 구조화
- 텍스트-SQL 모델을 위한 스키마 표현 학습

## O'Reilly 리소스
- **"Database Design and Relational Theory"** - Chris Date
- **"Seven Databases in Seven Weeks"** (2nd Edition) - Luc Perkins, et al.
- **"Designing Data-Intensive Applications"** - Martin Kleppmann (Chapter 2-3)

## 핵심 개념

### 1. 메타데이터 추출 (다양한 DB)
```sql
-- PostgreSQL: 테이블 정보 조회
SELECT
  t.table_name,
  c.column_name,
  c.data_type,
  c.is_nullable,
  tc.constraint_type
FROM information_schema.tables t
JOIN information_schema.columns c ON t.table_name = c.table_name
LEFT JOIN information_schema.table_constraints tc
  ON t.table_name = tc.table_name
WHERE t.table_schema = 'public'
ORDER BY t.table_name, c.ordinal_position;

-- MySQL: 테이블 정보 조회
SELECT
  TABLE_NAME,
  COLUMN_NAME,
  COLUMN_TYPE,
  IS_NULLABLE,
  COLUMN_KEY,
  COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- SQLite: 테이블 정보 조회
PRAGMA table_info(table_name);
SELECT name FROM sqlite_master WHERE type='table';

-- 모든 외래 키 정보
PRAGMA foreign_key_list(table_name);
```

### 2. 스키마 정보 구조화
```python
class SchemaMetadata:
    def __init__(self, db_type: str):
        self.db_type = db_type
        self.tables = {}
        self.relationships = []

    def add_table(self, table_name: str, columns: List[ColumnInfo]):
        """테이블 정보 추가"""
        self.tables[table_name] = {
            'name': table_name,
            'columns': columns,
            'primary_key': self._extract_pk(columns),
            'foreign_keys': self._extract_fk(columns)
        }

    def add_relationship(self, source_table: str, target_table: str,
                       source_col: str, target_col: str):
        """테이블 관계 추가"""
        self.relationships.append({
            'source': source_table,
            'target': target_table,
            'source_column': source_col,
            'target_column': target_col,
            'type': 'one_to_many'
        })

class ColumnInfo:
    def __init__(self, name: str, data_type: str, nullable: bool,
                 is_pk: bool = False, is_fk: bool = False):
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.is_pk = is_pk
        self.is_fk = is_fk
        self.description = ""
```

### 3. ERD 자동 생성
```python
import sqlite3
from typing import Dict, List, Tuple

class ERDGenerator:
    """SQL 스키마를 기반으로 ERD 생성"""

    def __init__(self, db_connection):
        self.conn = db_connection
        self.tables = {}
        self.relationships = []

    def extract_schema(self):
        """데이터베이스 스키마 추출"""
        cursor = self.conn.cursor()

        # 테이블 목록 조회
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'"
        )

        for (table_name,) in cursor.fetchall():
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            self.tables[table_name] = {
                'columns': [
                    {'name': col[1], 'type': col[2], 'notnull': col[3]}
                    for col in columns
                ]
            }

        # 외래 키 관계 추출
        for table_name in self.tables:
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            fks = cursor.fetchall()
            for fk in fks:
                self.relationships.append({
                    'from': table_name,
                    'to': fk[2],
                    'from_col': fk[3],
                    'to_col': fk[4]
                })

    def generate_mermaid_erd(self) -> str:
        """Mermaid 형식의 ERD 생성"""
        erd = "erDiagram\n"

        # 테이블과 컬럼 정의
        for table_name, info in self.tables.items():
            erd += f'  {table_name} {{\n'
            for col in info['columns']:
                erd += f'    {col["type"]} {col["name"]}\n'
            erd += '  }\n'

        # 관계 정의
        for rel in self.relationships:
            erd += f'  {rel["from"]} ||--o{{ {rel["to"]} : "{rel["from_col"]} -> {rel["to_col"]}"\n'

        return erd

    def generate_plantuml_erd(self) -> str:
        """PlantUML 형식의 ERD 생성"""
        erd = "@startuml\n"

        for table_name, info in self.tables.items():
            erd += f"entity {table_name} {{\n"
            for col in info['columns']:
                erd += f"  {col['name']} : {col['type']}\n"
            erd += "}\n"

        for rel in self.relationships:
            erd += f'{rel["from"]} }o--|| {rel["to"]}\n'

        erd += "@enduml"
        return erd
```

### 4. 스키마 문서화
```markdown
# 데이터베이스 스키마 문서

## 테이블 요약
- customers: 고객 정보 (id, name, email, created_at)
- orders: 주문 정보 (id, customer_id, order_date, total_amount)
- order_items: 주문 항목 (id, order_id, product_id, quantity, price)
- products: 상품 정보 (id, name, price, category_id)

## 관계도
```
customers (1) ----< (N) orders
orders (1) ----< (N) order_items
products (1) ----< (N) order_items
```

## 테이블 상세

### customers
| 컬럼 | 타입 | NULL | 설명 |
|------|------|------|------|
| id | INT | NO | 기본키 |
| name | VARCHAR(100) | NO | 고객명 |
| email | VARCHAR(100) | YES | 이메일 |
| country | VARCHAR(50) | YES | 국가 |
| created_at | TIMESTAMP | NO | 생성일시 |

### orders
| 컬럼 | 타입 | NULL | 설명 |
|------|------|------|------|
| id | INT | NO | 기본키 |
| customer_id | INT | NO | 외래키 (customers) |
| order_date | TIMESTAMP | NO | 주문일시 |
| total_amount | DECIMAL(10,2) | NO | 총액 |
```

## 실습 과제

### 과제 1: 스키마 메타데이터 추출
```python
import sqlite3

# 샘플 데이터베이스에 대한 메타데이터 추출 프로그램 작성
# 요구사항:
# 1. 모든 테이블명 추출
# 2. 각 테이블의 컬럼 정보 (이름, 타입, NULL 여부) 추출
# 3. 기본키 및 외래키 정보 추출
# 4. 결과를 JSON 형식으로 저장

def extract_schema_metadata(db_path: str) -> dict:
    conn = sqlite3.connect(db_path)
    # 구현하기
    pass

# 테스트
schema = extract_schema_metadata('sample.db')
print(schema)
```

### 과제 2: ERD 생성 도구 개발
```python
# 요구사항:
# 1. 데이터베이스에서 스키마 추출
# 2. Mermaid 형식의 ERD 생성
# 3. SQL로 테이블 관계 시각화
# 4. 마크다운 문서로 내보내기

class ERDBuilder:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.schema = {}
        self.relationships = []

    def build(self):
        """스키마 빌드"""
        pass

    def to_mermaid(self) -> str:
        """Mermaid ERD 생성"""
        pass

    def to_markdown(self) -> str:
        """마크다운 문서 생성"""
        pass

# 테스트 및 출력
builder = ERDBuilder('ecommerce.db')
builder.build()
print(builder.to_markdown())
```

### 과제 3: 스키마 검증
```python
# 요구사항:
# 1. 외래키 일관성 검사
# 2. 명명 규칙 검증 (테이블명, 컬럼명)
# 3. 데이터 타입 적절성 검증
# 4. NULL 제약조건 검증

def validate_schema(schema: dict) -> List[str]:
    """스키마 검증 및 경고 메시지 반환"""
    warnings = []

    # 명명 규칙 검사
    for table_name in schema['tables']:
        if not table_name.islower():
            warnings.append(f"Table '{table_name}' should be lowercase")

    return warnings
```

## 체크포인트

- [ ] PostgreSQL/MySQL/SQLite 메타데이터 조회 쿼리 작성 가능
- [ ] 스키마 정보를 Python 객체로 구조화 가능
- [ ] Mermaid 및 PlantUML 형식의 ERD 생성 가능
- [ ] 자동 ERD 생성 도구 개발 완료
- [ ] 스키마 검증 로직 구현 완료
- [ ] 3개 이상의 샘플 데이터베이스에서 ERD 자동 생성 성공

## 추가 학습 자료
- Database Metadata: https://en.wikipedia.org/wiki/Metadata
- Mermaid ERD Syntax: https://mermaid.js.org/syntax/entityRelationshipDiagram.html
- PlantUML Database Diagrams: https://plantuml.com/er-diagram
