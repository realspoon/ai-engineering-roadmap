# Week 19: Text-to-SQL 기초 (프롬프트 엔지니어링)

## 학습 목표
- 자연어를 SQL로 변환하는 기본 원리 이해
- 효과적인 프롬프트 엔지니어링 기법 학습
- LLM을 활용한 SQL 생성의 도전과제 파악
- Few-shot 예제를 통한 모델 성능 향상

## O'Reilly 리소스
- **"Prompt Engineering for Generative AI"** - James Phoenix, Mike Taylor
- **"Building LLM Applications"** - Sharon Zhou, et al.
- **"Designing Machine Learning Systems"** (Chapter 5-6) - Chip Huyen

## 핵심 개념

### 1. Text-to-SQL 기본 원리
```
사용자 자연어 입력
    ↓
LLM (프롬프트 + 스키마 정보)
    ↓
SQL 쿼리 생성
    ↓
SQL 검증 및 실행
    ↓
결과 반환
```

### 2. 프롬프트 구조
```python
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

# 기본 프롬프트 템플릿
BASIC_PROMPT = """
Given the following database schema:

{schema}

Write a SQL query to answer this question: {question}

SQL Query:
"""

prompt_template = PromptTemplate(
    input_variables=["schema", "question"],
    template=BASIC_PROMPT
)

llm = OpenAI(temperature=0)
result = llm.predict(
    schema="CREATE TABLE users (id INT, name VARCHAR(100), email VARCHAR(100));",
    question="Find all users with gmail accounts"
)
print(result)
```

### 3. 효과적인 프롬프트 엔지니어링
```python
# 방법 1: 스키마 정보 강화
ENHANCED_PROMPT = """
You are a SQL expert. Given the following database:

Table: customers
- id (INT, Primary Key): Unique customer identifier
- name (VARCHAR): Customer full name
- email (VARCHAR): Customer email address
- country (VARCHAR): Customer country
- created_at (TIMESTAMP): Account creation date

Table: orders
- id (INT, Primary Key): Unique order identifier
- customer_id (INT, Foreign Key): Reference to customers.id
- order_date (TIMESTAMP): Order date
- total_amount (DECIMAL): Total order amount
- status (VARCHAR): Order status (pending, completed, cancelled)

Write a SQL query to: {question}

Requirements:
1. Only use columns that exist in the schema
2. Use proper JOIN syntax
3. Include aliases for clarity
4. Write valid SQL syntax

SQL Query:
"""

# 방법 2: Few-shot 예제 포함
FEWSHOT_PROMPT = """
You are a SQL expert. Given the following schema, answer the question.

Schema:
{schema}

Examples:
Q: How many customers are from USA?
A: SELECT COUNT(*) FROM customers WHERE country = 'USA';

Q: List top 5 customers by total spending
A: SELECT c.name, SUM(o.total_amount) as total_spent
   FROM customers c
   JOIN orders o ON c.id = o.customer_id
   GROUP BY c.id, c.name
   ORDER BY total_spent DESC
   LIMIT 5;

Q: {question}
A:
"""

# 방법 3: 단계별 사고 (Chain of Thought)
COTHOUGHT_PROMPT = """
You are a SQL expert. Answer the following question step by step.

Schema: {schema}

Question: {question}

Step 1: Identify which tables are needed
Step 2: Determine the JOIN conditions
Step 3: Write the SELECT clause
Step 4: Write the WHERE clause
Step 5: Write the final SQL query

Final SQL Query:
"""
```

### 4. 일반적인 패턴 및 템플릿
```python
class SQLPatternLibrary:
    """SQL 생성 패턴 라이브러리"""

    PATTERNS = {
        'simple_select': """
            SELECT {columns}
            FROM {table}
            WHERE {conditions}
        """,

        'single_join': """
            SELECT {columns}
            FROM {table1}
            JOIN {table2} ON {join_condition}
            WHERE {conditions}
        """,

        'aggregation': """
            SELECT {group_by_cols},
                   {aggregation}
            FROM {table}
            WHERE {conditions}
            GROUP BY {group_by_cols}
            HAVING {having_condition}
        """,

        'subquery': """
            SELECT {columns}
            FROM {table}
            WHERE {column} IN (
                SELECT {subquery_col}
                FROM {subquery_table}
                WHERE {subquery_condition}
            )
        """,

        'window_function': """
            SELECT {columns},
                   {window_function} OVER (
                       PARTITION BY {partition_col}
                       ORDER BY {order_col}
                   ) as {alias}
            FROM {table}
        """
    }

    @staticmethod
    def get_pattern(pattern_type: str) -> str:
        return SQLPatternLibrary.PATTERNS.get(pattern_type, "")
```

### 5. 프롬프트 최적화 기법
```python
class PromptOptimizer:
    """프롬프트 최적화 기법"""

    @staticmethod
    def add_context(base_prompt: str, schema_info: str,
                    task_instruction: str) -> str:
        """컨텍스트 추가"""
        return f"""{task_instruction}

Database Schema:
{schema_info}

{base_prompt}"""

    @staticmethod
    def add_constraints(base_prompt: str) -> str:
        """제약조건 추가"""
        constraints = """
        Constraints:
        - Only use columns that exist in the provided schema
        - Use proper JOIN syntax for multiple tables
        - Avoid SELECT *; specify exact columns
        - Include meaningful aliases
        - Ensure syntactically valid SQL
        """
        return base_prompt + constraints

    @staticmethod
    def add_examples(base_prompt: str, examples: List[Tuple[str, str]]) -> str:
        """예제 추가"""
        examples_text = "\nExamples:\n"
        for question, sql in examples:
            examples_text += f"\nQ: {question}\nA: {sql}\n"
        return base_prompt + examples_text

    @staticmethod
    def format_schema(tables: List[Dict]) -> str:
        """스키마 포맷팅"""
        formatted = ""
        for table in tables:
            formatted += f"\nTable: {table['name']}\n"
            formatted += "Columns:\n"
            for col in table['columns']:
                formatted += f"  - {col['name']} ({col['type']})"
                if col.get('description'):
                    formatted += f": {col['description']}"
                formatted += "\n"
        return formatted
```

## 실습 과제

### 과제 1: 기본 프롬프트 작성
```python
# 요구사항:
# 1. 스키마 정보가 포함된 프롬프트 작성
# 2. 5개의 다양한 자연어 질문에 대해 프롬프트 생성
# 3. 생성된 프롬프트로 LLM 호출

questions = [
    "What is the average order value?",
    "Find customers who haven't placed any orders",
    "List products ordered in the last month",
    "Which customer spent the most?",
    "Show the top 10 best-selling products"
]

schema = """
CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    order_date TIMESTAMP,
    total_amount DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE order_items (
    id INT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);
"""

for question in questions:
    # 프롬프트 생성 및 테스트
    pass
```

### 과제 2: Few-shot 프롬프트 구축
```python
# 요구사항:
# 1. 도메인 별 예제 수집 (3가지 카테고리)
#    - 단순 SELECT
#    - JOIN을 포함한 쿼리
#    - 집계 함수 포함
# 2. Few-shot 프롬프트 작성
# 3. 성능 평가 (프롬프트 없음 vs Few-shot)

examples = {
    'simple_select': [
        {
            'question': 'List all customers',
            'sql': 'SELECT * FROM customers;'
        },
        # 더 추가하기
    ],
    'joins': [
        {
            'question': 'Show customer names and their order dates',
            'sql': 'SELECT c.name, o.order_date FROM customers c JOIN orders o ON c.id = o.customer_id;'
        },
        # 더 추가하기
    ],
    'aggregation': [
        {
            'question': 'How many orders per customer?',
            'sql': 'SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id;'
        },
        # 더 추가하기
    ]
}

def build_fewshot_prompt(examples: dict, question: str) -> str:
    # 구현하기
    pass
```

### 과제 3: 프롬프트 엔지니어링 실험
```python
# 요구사항:
# 1. 다양한 프롬프트 스타일 구현:
#    - 기본 (스키마만)
#    - 상세 (컨텍스트 추가)
#    - Few-shot (예제 포함)
#    - Chain of Thought (단계별)
# 2. 동일한 질문으로 비교
# 3. 결과 분석 및 평가

prompt_styles = {
    'basic': BASIC_PROMPT,
    'enhanced': ENHANCED_PROMPT,
    'fewshot': FEWSHOT_PROMPT,
    'cot': COTHOUGHT_PROMPT
}

test_questions = [
    "Get customers from USA with more than 5 orders",
    "Find the top 3 most expensive products",
    "Calculate monthly revenue trend"
]

results = {}
for style_name, prompt_template in prompt_styles.items():
    results[style_name] = {}
    for question in test_questions:
        # LLM 호출 및 결과 저장
        pass

# 비교 분석 및 결과 출력
```

## 체크포인트

- [ ] Text-to-SQL의 기본 아키텍처 이해
- [ ] 스키마 정보를 프롬프트에 포함시키는 방법 습득
- [ ] 5가지 이상의 프롬프트 템플릿 작성 완료
- [ ] Few-shot 프롬프트 구축 및 테스트 완료
- [ ] Chain of Thought 프롬프트 실습 완료
- [ ] 3가지 이상의 프롬프트 스타일 비교 분석 완료
- [ ] 프롬프트 최적화의 영향 이해

## 추가 학습 자료
- LangChain SQL Chain: https://python.langchain.com/docs/use_cases/sql/
- OpenAI Prompt Engineering: https://platform.openai.com/docs/guides/prompt-engineering
- Few-Shot Prompting: https://github.com/dair-ai/Prompt-Engineering-Guide
