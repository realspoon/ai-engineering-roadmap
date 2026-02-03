# Week 22: RAG 스키마 검색 (임베딩, Few-shot)

## 학습 목표
- RAG (Retrieval-Augmented Generation) 패턴 이해
- 벡터 임베딩을 통한 스키마 검색
- 유사 쿼리 예제 검색 및 활용
- Text-to-SQL에서의 RAG 구현

## O'Reilly 리소스
- **"Retrieval Augmented Generation (RAG)"** - Harrison Chase, et al.
- **"Vector Databases"** - Aniruddha Bhatnagar
- **"Building RAG Systems"** - Multiple Contributors

## 핵심 개념

### 1. RAG 아키텍처
```
사용자 질문
    ↓
┌───────────────────────────────────────────┐
│ Retrieval 단계                            │
├───────────────────────────────────────────┤
│ 1. 질문을 임베딩으로 변환                 │
│ 2. 벡터 DB에서 유사한 항목 검색          │
│    - 스키마 정보                          │
│    - 유사한 쿼리 예제                     │
│    - 도메인 지식                          │
│ 3. 검색 결과 랭킹 및 선택                 │
└────────┬────────────────────────────────┘
         │ Retrieved Context
         ↓
┌───────────────────────────────────────────┐
│ Generation 단계                           │
├───────────────────────────────────────────┤
│ 1. 질문 + 검색 결과를 프롬프트에 포함    │
│ 2. LLM으로 SQL 생성                       │
│ 3. SQL 검증 및 실행                       │
└────────┬────────────────────────────────┘
         ↓
      최종 결과
```

### 2. 벡터 임베딩 및 저장소
```python
import numpy as np
from typing import List, Tuple, Dict
import sqlite3

class EmbeddingStore:
    """벡터 임베딩 저장 및 검색"""

    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 db_path: str = "embeddings.db"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(embedding_model)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """임베딩 저장 DB 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id TEXT PRIMARY KEY,
                content_type TEXT,  -- 'schema', 'query_example', 'documentation'
                content TEXT,
                embedding BLOB,  -- numpy array를 pickle로 저장
                metadata TEXT,   -- JSON 형식
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_cache (
                query_id TEXT PRIMARY KEY,
                natural_language TEXT,
                generated_sql TEXT,
                success BOOLEAN,
                execution_time FLOAT,
                embedding BLOB
            )
        """)

        conn.commit()
        conn.close()

    def embed_text(self, text: str) -> np.ndarray:
        """텍스트를 임베딩으로 변환"""
        return self.model.encode(text)

    def store_embedding(self, content_id: str, content: str,
                       content_type: str, metadata: Dict = None):
        """임베딩 저장"""
        embedding = self.embed_text(content)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        import json
        import pickle

        cursor.execute("""
            INSERT OR REPLACE INTO embeddings
            (id, content_type, content, embedding, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            content_id,
            content_type,
            content,
            pickle.dumps(embedding),
            json.dumps(metadata or {})
        ))

        conn.commit()
        conn.close()

    def retrieve_similar(self, query: str, content_type: str = None,
                        top_k: int = 5) -> List[Dict]:
        """유사한 임베딩 검색"""
        query_embedding = self.embed_text(query)

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if content_type:
            cursor.execute("SELECT * FROM embeddings WHERE content_type = ?",
                          (content_type,))
        else:
            cursor.execute("SELECT * FROM embeddings")

        results = []
        import pickle

        for row in cursor.fetchall():
            stored_embedding = pickle.loads(row['embedding'])

            # 코사인 유사도 계산
            similarity = np.dot(query_embedding, stored_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
            )

            results.append({
                'id': row['id'],
                'content': row['content'],
                'type': row['content_type'],
                'similarity': similarity,
                'metadata': row['metadata']
            })

        conn.close()

        # 유사도 기준 정렬 및 상위 K개 반환
        return sorted(results, key=lambda x: x['similarity'],
                     reverse=True)[:top_k]
```

### 3. 스키마 기반 RAG
```python
class SchemaRAG:
    """스키마 정보를 활용한 RAG"""

    def __init__(self, embedding_store: EmbeddingStore):
        self.store = embedding_store

    def index_schema(self, tables: List[Dict]):
        """스키마 정보를 임베딩으로 인덱싱"""
        for table in tables:
            table_name = table['name']
            table_desc = table.get('description', '')

            # 테이블 단위 임베딩
            table_text = f"Table: {table_name}. {table_desc}"
            self.store.store_embedding(
                f"table_{table_name}",
                table_text,
                'schema_table',
                {'table_name': table_name, 'type': 'table'}
            )

            # 컬럼 단위 임베딩
            for col in table['columns']:
                col_text = f"Column {col['name']} in table {table_name}. " \
                          f"Type: {col['type']}. {col.get('description', '')}"
                self.store.store_embedding(
                    f"column_{table_name}_{col['name']}",
                    col_text,
                    'schema_column',
                    {
                        'table_name': table_name,
                        'column_name': col['name'],
                        'type': col['type']
                    }
                )

    def retrieve_relevant_schema(self, question: str,
                                top_k: int = 5) -> Dict:
        """질문과 관련된 스키마 정보 검색"""
        # 테이블 검색
        table_results = self.store.retrieve_similar(
            question, content_type='schema_table', top_k=top_k
        )

        # 컬럼 검색
        column_results = self.store.retrieve_similar(
            question, content_type='schema_column', top_k=top_k
        )

        return {
            'tables': table_results,
            'columns': column_results,
            'relevant_schema': self._build_schema_context(
                table_results, column_results
            )
        }

    def _build_schema_context(self, tables: List[Dict],
                             columns: List[Dict]) -> str:
        """검색된 스키마 정보를 텍스트로 포맷팅"""
        context = "Relevant Schema Information:\n\n"

        # 테이블 정보
        for table in tables:
            context += f"Table: {table['content']}\n"

        # 컬럼 정보
        context += "\nRelevant Columns:\n"
        for col in columns:
            context += f"  - {col['content']}\n"

        return context
```

### 4. Few-shot 임베딩 및 검색
```python
class FewShotExampleStore:
    """Few-shot 예제 저장 및 검색"""

    def __init__(self, embedding_store: EmbeddingStore):
        self.store = embedding_store

    def add_example(self, natural_language: str, sql: str,
                   category: str = "general", difficulty: str = "medium"):
        """쿼리 예제 추가"""
        example_id = f"example_{hash(natural_language) % 10000000}"

        # 자연어를 임베딩으로 변환
        self.store.store_embedding(
            example_id,
            f"{natural_language} => {sql}",
            'query_example',
            {
                'question': natural_language,
                'sql': sql,
                'category': category,
                'difficulty': difficulty
            }
        )

    def retrieve_similar_examples(self, question: str,
                                 category: str = None,
                                 difficulty: str = None,
                                 top_k: int = 5) -> List[Dict]:
        """유사한 쿼리 예제 검색"""
        # 유사도 기반 검색
        results = self.store.retrieve_similar(
            question, content_type='query_example', top_k=top_k * 2
        )

        # 카테고리/난이도 필터링
        filtered = []
        for result in results:
            metadata = eval(result['metadata']) if isinstance(result['metadata'], str) else result['metadata']

            if category and metadata.get('category') != category:
                continue
            if difficulty and metadata.get('difficulty') != difficulty:
                continue

            # 메타데이터에서 SQL 추출
            result['sql'] = metadata.get('sql', '')
            result['question'] = metadata.get('question', '')
            filtered.append(result)

        return filtered[:top_k]

    def build_fewshot_prompt(self, question: str, num_examples: int = 3) -> str:
        """Few-shot 프롬프트 구성"""
        examples = self.retrieve_similar_examples(question, top_k=num_examples)

        prompt = "You are a SQL expert. Answer these examples first:\n\n"

        for i, example in enumerate(examples, 1):
            prompt += f"Example {i}:\n"
            prompt += f"Q: {example['question']}\n"
            prompt += f"A: {example['sql']}\n\n"

        prompt += f"Now answer this question:\nQ: {question}\nA:"

        return prompt
```

### 5. RAG 통합 Text-to-SQL Agent
```python
class RAGTextToSQLAgent:
    """RAG를 활용한 Text-to-SQL Agent"""

    def __init__(self, db_path: str, embedding_store: EmbeddingStore):
        self.db = sqlite3.connect(db_path)
        self.embedding_store = embedding_store
        self.schema_rag = SchemaRAG(embedding_store)
        self.fewshot_store = FewShotExampleStore(embedding_store)

    def process_question(self, question: str) -> Dict:
        """RAG를 활용한 질문 처리"""
        # 1. 관련 스키마 검색
        schema_context = self.schema_rag.retrieve_relevant_schema(question)

        # 2. 유사 쿼리 예제 검색
        fewshot_examples = self.fewshot_store.retrieve_similar_examples(
            question, top_k=3
        )

        # 3. 프롬프트 구성
        prompt = self._build_rag_prompt(question, schema_context, fewshot_examples)

        # 4. SQL 생성 (LLM 호출)
        generated_sql = self._call_llm(prompt)

        # 5. 검증 및 실행
        result = self._validate_and_execute(generated_sql)

        # 6. 쿼리 캐시에 저장 (미래 학습용)
        self._cache_query(question, generated_sql, result['success'])

        return {
            'question': question,
            'sql': generated_sql,
            'result': result,
            'context': {
                'retrieved_schema': schema_context['relevant_schema'],
                'fewshot_examples': [e['question'] for e in fewshot_examples]
            }
        }

    def _build_rag_prompt(self, question: str, schema_context: Dict,
                         fewshot_examples: List[Dict]) -> str:
        """RAG 컨텍스트를 포함한 프롬프트 구성"""
        prompt = "You are a SQL expert.\n\n"

        # 스키마 정보
        prompt += schema_context['relevant_schema'] + "\n"

        # Few-shot 예제
        prompt += "Examples:\n"
        for i, example in enumerate(fewshot_examples, 1):
            prompt += f"{i}. Q: {example['question']}\n"
            prompt += f"   A: {example['sql']}\n\n"

        # 사용자 질문
        prompt += f"Question: {question}\n"
        prompt += "SQL Query:"

        return prompt

    def _call_llm(self, prompt: str) -> str:
        """LLM 호출 (구현 필요)"""
        # OpenAI, Claude 등의 API 호출
        pass

    def _validate_and_execute(self, sql: str) -> Dict:
        """SQL 검증 및 실행"""
        try:
            cursor = self.db.execute(sql)
            result = cursor.fetchall()
            return {
                'success': True,
                'data': result,
                'row_count': len(result)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _cache_query(self, question: str, sql: str, success: bool):
        """성공한 쿼리를 캐시에 저장"""
        import time
        if success:
            # 성공한 쿼리는 향후 유사 질문의 Few-shot 예제로 활용
            self.fewshot_store.add_example(question, sql)
```

## 실습 과제

### 과제 1: 임베딩 저장소 구축
```python
# 요구사항:
# 1. EmbeddingStore 완전 구현
# 2. 샘플 스키마 임베딩 저장
# 3. 유사도 기반 검색 테스트
# 4. 성능 측정

tables = [
    {
        'name': 'customers',
        'description': 'Customer information',
        'columns': [
            {'name': 'id', 'type': 'INT', 'description': 'Customer ID'},
            {'name': 'name', 'type': 'VARCHAR', 'description': 'Customer name'},
            {'name': 'email', 'type': 'VARCHAR', 'description': 'Customer email'}
        ]
    },
    # ... 추가 테이블들
]

store = EmbeddingStore()
for table in tables:
    for col in table['columns']:
        store.store_embedding(
            f"{table['name']}.{col['name']}",
            f"{col['description']}",
            'schema_column'
        )

# 검색 테스트
results = store.retrieve_similar("Find customer email addresses", top_k=5)
for result in results:
    print(f"{result['content']} (similarity: {result['similarity']:.2f})")
```

### 과제 2: 스키마 RAG 구현
```python
# 요구사항:
# 1. SchemaRAG 완전 구현
# 2. 20개 이상의 질문으로 스키마 검색 테스트
# 3. 검색 정확도 평가
# 4. 검색 결과를 SQL 생성에 활용

schema_rag = SchemaRAG(embedding_store)
schema_rag.index_schema(tables)

questions = [
    "고객 이름을 찾아주세요",
    "주문 날짜가 언제인가요?",
    "상품 가격은 얼마인가요?",
    # ... 17개 더
]

for q in questions:
    results = schema_rag.retrieve_relevant_schema(q)
    print(f"Question: {q}")
    print(f"Relevant Tables: {[r['content'] for r in results['tables']]}")
    print()
```

### 과제 3: Few-shot 예제 저장소 구축
```python
# 요구사항:
# 1. FewShotExampleStore 구현
# 2. 30개 이상의 쿼리 예제 추가
# 3. 카테고리별로 체계화
# 4. 유사 쿼리 검색 테스트

fewshot_store = FewShotExampleStore(embedding_store)

# 다양한 카테고리의 예제 추가
examples = [
    {
        'question': 'List all customers',
        'sql': 'SELECT * FROM customers;',
        'category': 'basic_select',
        'difficulty': 'easy'
    },
    {
        'question': 'Count orders per customer',
        'sql': 'SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id;',
        'category': 'aggregation',
        'difficulty': 'medium'
    },
    # ... 28개 더 추가
]

for example in examples:
    fewshot_store.add_example(
        example['question'],
        example['sql'],
        example['category'],
        example['difficulty']
    )

# 유사 예제 검색
test_question = "How many orders has each customer made?"
similar = fewshot_store.retrieve_similar_examples(test_question, top_k=3)
print(f"Similar examples for: {test_question}")
for ex in similar:
    print(f"  Q: {ex['question']}")
    print(f"  A: {ex['sql']}")
```

### 과제 4: RAG Agent 통합 및 평가
```python
# 요구사항:
# 1. RAGTextToSQLAgent 완전 구현
# 2. 20개 이상의 질문으로 테스트
# 3. RAG 없는 Agent와 비교
# 4. 성능 개선 정량화

agent = RAGTextToSQLAgent('ecommerce.db', embedding_store)

test_questions = [
    "What are the top 5 customers by spending?",
    "Show monthly sales trends for the last year",
    "Which products are in the electronics category?",
    # ... 17개 더
]

results = []
for question in test_questions:
    result = agent.process_question(question)
    results.append({
        'question': question,
        'success': result['result']['success'],
        'examples_used': len(result['context']['fewshot_examples'])
    })

# 성공률 계산
success_count = sum(1 for r in results if r['success'])
print(f"Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
```

## 체크포인트

- [ ] EmbeddingStore 완전 구현 및 테스트
- [ ] 벡터 임베딩 저장 및 검색 동작 확인
- [ ] SchemaRAG 구현 및 스키마 인덱싱 완료
- [ ] 질문 기반 스키마 검색 정확도 80% 이상
- [ ] FewShotExampleStore 구현 완료
- [ ] 30개 이상의 예제 저장 및 검색 가능
- [ ] RAGTextToSQLAgent 통합 구현 완료
- [ ] RAG 도입으로 SQL 생성 정확도 20% 이상 향상

## 추가 학습 자료
- RAG Survey: https://arxiv.org/abs/2312.10997
- Sentence Transformers: https://www.sbert.net/
- Vector Database Guide: https://www.pinecone.io/learn/vector-database/
- LangChain RAG: https://python.langchain.com/docs/use_cases/question_answering/
