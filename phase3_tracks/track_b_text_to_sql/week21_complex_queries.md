# Week 21: 고급 쿼리 (Multi-step, 쿼리 분해)

## 학습 목표
- 복잡한 쿼리를 단계별로 분해하고 처리
- Multi-step 질문을 여러 SQL 쿼리로 변환
- 중간 결과를 활용한 다단계 쿼리 구성
- 복잡한 비즈니스 로직을 SQL로 표현

## O'Reilly 리소스
- **"Advanced SQL Window Functions"** - Itzik Ben-Gan
- **"SQL Antipatterns"** - Bill Karwin
- **"A Guide to SQL Window Functions"** - Markus Winand

## 핵심 개념

### 1. 쿼리 분해 전략
```python
class QueryDecomposer:
    """복잡한 자연어 질문을 단계별 SQL로 분해"""

    def decompose(self, question: str) -> List[Dict]:
        """질문을 단계별 작업으로 분해"""
        steps = []

        # 예: "지난 6개월 동안 구매한 고객 중 5회 이상 주문한 고객의
        #     월별 평균 구매액과 총액을 구하세요"

        # Step 1: 지난 6개월 데이터 필터링
        steps.append({
            'order': 1,
            'description': 'Filter orders from last 6 months',
            'sql': """
                SELECT customer_id, order_date, amount
                FROM orders
                WHERE order_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            """,
            'output_alias': 'recent_orders'
        })

        # Step 2: 고객별 주문 수 계산
        steps.append({
            'order': 2,
            'description': 'Count orders per customer',
            'sql': """
                SELECT customer_id, COUNT(*) as order_count
                FROM recent_orders
                GROUP BY customer_id
                HAVING COUNT(*) >= 5
            """,
            'output_alias': 'frequent_customers'
        })

        # Step 3: 최종 분석
        steps.append({
            'order': 3,
            'description': 'Calculate monthly stats',
            'sql': """
                SELECT
                    fc.customer_id,
                    DATE_FORMAT(ro.order_date, '%Y-%m') as month,
                    COUNT(*) as order_count,
                    AVG(ro.amount) as avg_amount,
                    SUM(ro.amount) as total_amount
                FROM recent_orders ro
                INNER JOIN frequent_customers fc ON ro.customer_id = fc.customer_id
                GROUP BY fc.customer_id, month
            """,
            'output_alias': 'final_result'
        })

        return steps

    def execute_decomposed(self, steps: List[Dict],
                          connection) -> Dict[str, Any]:
        """분해된 단계별 쿼리 실행"""
        results = {}
        temp_tables = {}

        for step in steps:
            sql = step['sql']

            # 이전 결과를 현재 쿼리에 반영
            for alias, data in results.items():
                # CTE로 변환
                pass

            result = connection.execute(sql).fetchall()
            results[step['output_alias']] = result

            print(f"Step {step['order']}: {step['description']}")
            print(f"  Rows: {len(result)}")

        return results
```

### 2. Multi-step 쿼리 패턴
```python
class MultiStepQueryBuilder:
    """다단계 쿼리 구성"""

    @staticmethod
    def build_cte_chain(steps: List[Dict]) -> str:
        """CTE를 사용한 단계별 쿼리"""
        ctes = []

        for i, step in enumerate(steps):
            cte_name = step['output_alias'].upper()
            query = step['sql']

            if i == 0:
                # 첫 번째 CTE (기본 쿼리)
                ctes.append(f"{cte_name} AS (\n  {query}\n)")
            else:
                # 이후 CTE (이전 결과 참조)
                ctes.append(f",{cte_name} AS (\n  {query}\n)")

        # 최종 SELECT 문
        final_select = f"SELECT * FROM {steps[-1]['output_alias'].upper()}"

        return f"WITH {' '.join(ctes)}\n{final_select}"

    @staticmethod
    def build_temp_table_chain(steps: List[Dict], connection) -> List[str]:
        """임시 테이블을 사용한 단계별 쿼리"""
        sqls = []

        for i, step in enumerate(steps):
            temp_table = f"temp_{i}_{step['output_alias']}"
            query = f"CREATE TEMP TABLE {temp_table} AS\n{step['sql']}"
            sqls.append(query)

        return sqls

    @staticmethod
    def build_join_chain(steps: List[Dict]) -> str:
        """JOIN을 사용한 단계별 결과 통합"""
        # 단계별 서브쿼리를 생성하고 JOIN으로 통합
        subqueries = []

        for step in steps:
            subqueries.append(f"({step['sql']}) AS {step['output_alias']}")

        # 공통 키로 JOIN
        pass
```

### 3. 복잡한 비즈니스 로직 쿼리 예제
```sql
-- 예제 1: RFM 분석 (Recency, Frequency, Monetary)
WITH customer_metrics AS (
  SELECT
    customer_id,
    MAX(order_date) as last_order_date,
    COUNT(*) as order_frequency,
    SUM(amount) as total_spending,
    DATEDIFF(NOW(), MAX(order_date)) as days_since_last_order
  FROM orders
  WHERE order_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
  GROUP BY customer_id
),
rfm_scores AS (
  SELECT
    customer_id,
    CASE
      WHEN days_since_last_order <= 30 THEN 5
      WHEN days_since_last_order <= 90 THEN 4
      WHEN days_since_last_order <= 180 THEN 3
      WHEN days_since_last_order <= 365 THEN 2
      ELSE 1
    END as recency_score,
    CASE
      WHEN order_frequency >= 10 THEN 5
      WHEN order_frequency >= 7 THEN 4
      WHEN order_frequency >= 4 THEN 3
      WHEN order_frequency >= 2 THEN 2
      ELSE 1
    END as frequency_score,
    CASE
      WHEN total_spending >= 10000 THEN 5
      WHEN total_spending >= 5000 THEN 4
      WHEN total_spending >= 2000 THEN 3
      WHEN total_spending >= 500 THEN 2
      ELSE 1
    END as monetary_score
  FROM customer_metrics
)
SELECT
  customer_id,
  recency_score,
  frequency_score,
  monetary_score,
  recency_score + frequency_score + monetary_score as total_score,
  CASE
    WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'VIP'
    WHEN recency_score >= 3 AND frequency_score >= 3 THEN 'High Value'
    WHEN recency_score >= 2 THEN 'Active'
    ELSE 'Inactive'
  END as customer_segment
FROM rfm_scores
ORDER BY total_score DESC;

-- 예제 2: 시계열 분석 (월별 변화율)
WITH monthly_sales AS (
  SELECT
    DATE_TRUNC('month', order_date) as month,
    SUM(amount) as monthly_revenue
  FROM orders
  GROUP BY DATE_TRUNC('month', order_date)
),
sales_with_lag AS (
  SELECT
    month,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY month) as prev_month_revenue,
    LAG(monthly_revenue, 12) OVER (ORDER BY month) as prev_year_revenue
  FROM monthly_sales
)
SELECT
  month,
  monthly_revenue,
  ROUND(((monthly_revenue - prev_month_revenue) / prev_month_revenue * 100), 2) as mom_growth,
  ROUND(((monthly_revenue - prev_year_revenue) / prev_year_revenue * 100), 2) as yoy_growth
FROM sales_with_lag
WHERE prev_month_revenue IS NOT NULL;

-- 예제 3: 누적 및 비율 분석
WITH product_sales AS (
  SELECT
    p.category,
    p.product_name,
    SUM(oi.quantity * oi.price) as total_sales
  FROM order_items oi
  JOIN products p ON oi.product_id = p.id
  GROUP BY p.category, p.product_name
),
category_totals AS (
  SELECT
    category,
    SUM(total_sales) as category_total
  FROM product_sales
  GROUP BY category
),
ranked_products AS (
  SELECT
    ps.category,
    ps.product_name,
    ps.total_sales,
    ct.category_total,
    ROUND((ps.total_sales / ct.category_total * 100), 2) as pct_of_category,
    ROW_NUMBER() OVER (PARTITION BY ps.category ORDER BY ps.total_sales DESC) as rank_in_category,
    SUM(ps.total_sales) OVER (PARTITION BY ps.category ORDER BY ps.total_sales DESC) as cumulative_sales
  FROM product_sales ps
  JOIN category_totals ct ON ps.category = ct.category
)
SELECT * FROM ranked_products
WHERE rank_in_category <= 10
ORDER BY category, rank_in_category;
```

### 4. 자연어에서 Multi-step 추출
```python
class MultiStepExtractor:
    """자연어 질문에서 Multi-step 추출"""

    def extract_steps(self, question: str) -> List[str]:
        """자연어를 처리 단계로 분해"""
        import re

        # 주요 키워드 식별
        keywords = {
            'filter': ['where', 'from', 'between', 'during', 'in'],
            'aggregate': ['sum', 'count', 'average', 'total', 'average'],
            'group': ['by', 'per', 'each'],
            'rank': ['top', 'bottom', 'highest', 'lowest', 'rank'],
            'compare': ['vs', 'compared to', 'change', 'growth', 'difference']
        }

        steps = []

        # 문장 분할
        sentences = re.split(r'[.;]', question)

        for sentence in sentences:
            sentence = sentence.strip().lower()
            if not sentence:
                continue

            # 각 문장이 어떤 작업인지 분류
            step_type = None
            for op_type, keywords_list in keywords.items():
                if any(kw in sentence for kw in keywords_list):
                    step_type = op_type
                    break

            if step_type:
                steps.append({
                    'type': step_type,
                    'description': sentence,
                    'original': sentence
                })

        return steps

    def convert_to_sql_steps(self, steps: List[Dict],
                            schema: Dict) -> List[Dict]:
        """처리 단계를 SQL로 변환"""
        sql_steps = []

        for i, step in enumerate(steps):
            if step['type'] == 'filter':
                sql = self._generate_filter_sql(step, schema)
            elif step['type'] == 'aggregate':
                sql = self._generate_aggregate_sql(step, schema)
            elif step['type'] == 'group':
                sql = self._generate_group_sql(step, schema)
            elif step['type'] == 'rank':
                sql = self._generate_rank_sql(step, schema)
            elif step['type'] == 'compare':
                sql = self._generate_compare_sql(step, schema)

            sql_steps.append({
                'order': i + 1,
                'type': step['type'],
                'description': step['description'],
                'sql': sql
            })

        return sql_steps

    def _generate_filter_sql(self, step: Dict, schema: Dict) -> str:
        # 필터 SQL 생성 로직
        pass

    def _generate_aggregate_sql(self, step: Dict, schema: Dict) -> str:
        # 집계 SQL 생성 로직
        pass

    # ... 추가 메서드들
```

## 실습 과제

### 과제 1: 쿼리 분해기 구현
```python
# 요구사항:
# 1. QueryDecomposer 완전 구현
# 2. 5개의 복잡한 질문 분해
# 3. 각 단계별 SQL 생성 및 검증
# 4. 최종 결과 비교

complex_questions = [
    "지난 분기 매출이 전년 대비 10% 이상 증가한 제품별 판매량을 보여주세요",
    "2024년 구매한 고객 중 5회 이상 주문한 고객의 월별 평균 구매액을 계산하세요",
    "각 카테고리별로 가장 많이 팔린 상품과 그 판매액의 비율을 구하세요",
    "최근 3개월 활동이 없었던 VIP 고객 목록을 추출하세요",
    "상품별 판매 추세 변화를 월별로 분석하세요"
]

decomposer = QueryDecomposer()
for question in complex_questions:
    steps = decomposer.decompose(question)
    for step in steps:
        print(f"Step {step['order']}: {step['description']}")
        print(f"SQL: {step['sql']}\n")
```

### 과제 2: Multi-step 쿼리 구성
```python
# 요구사항:
# 1. 세 가지 방식의 Multi-step 쿼리 구성
#    - CTE 체인
#    - 임시 테이블 체인
#    - JOIN 기반
# 2. 동일한 결과 확인
# 3. 성능 비교

steps = [
    {
        'order': 1,
        'description': 'Base orders',
        'sql': 'SELECT * FROM orders WHERE order_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)',
        'output_alias': 'recent_orders'
    },
    {
        'order': 2,
        'description': 'Customer aggregation',
        'sql': 'SELECT customer_id, COUNT(*) as order_count FROM recent_orders GROUP BY customer_id',
        'output_alias': 'customer_stats'
    },
    {
        'order': 3,
        'description': 'Final result',
        'sql': 'SELECT c.name, cs.order_count FROM customers c JOIN customer_stats cs ON c.id = cs.customer_id',
        'output_alias': 'final_result'
    }
]

builder = MultiStepQueryBuilder()
cte_query = builder.build_cte_chain(steps)
print("CTE Query:")
print(cte_query)
```

### 과제 3: RFM 분석 쿼리 작성
```python
# 요구사항:
# 1. 고객 RFM 점수 계산
# 2. 고객 세그먼트 분류
# 3. 세그먼트별 통계 생성
# 4. 결과 시각화

# RFM 분석 쿼리 작성
# - Recency: 마지막 구매로부터의 일수
# - Frequency: 구매 횟수
# - Monetary: 총 구매액

# 예상 결과:
# customer_id | recency_score | frequency_score | monetary_score | segment
# 1           | 5             | 5               | 5              | VIP
# 2           | 4             | 3               | 3              | High Value
```

### 과제 4: 자동 Multi-step 생성
```python
# 요구사항:
# 1. MultiStepExtractor 완전 구현
# 2. 10개의 자연어 질문 처리
# 3. 자동으로 SQL 단계 생성
# 4. 최종 SQL 작성 및 실행

extractor = MultiStepExtractor()

questions = [
    "2024년 매출이 전년 대비 증가한 상품의 판매량",
    "분기별로 고객 수와 평균 구매액의 변화",
    "카테고리별 가장 인기있는 상품 Top 5",
    # ... 7개 더
]

for q in questions:
    steps = extractor.extract_steps(q)
    sql_steps = extractor.convert_to_sql_steps(steps, schema)
    print(f"Question: {q}")
    for sql_step in sql_steps:
        print(f"  {sql_step['order']}. {sql_step['type']}: {sql_step['sql']}")
```

## 체크포인트

- [ ] QueryDecomposer 완전 구현 및 테스트
- [ ] 3가지 Multi-step 쿼리 구성 방식 이해
- [ ] CTE 기반 복잡한 쿼리 작성 가능
- [ ] RFM 분석, 시계열 분석, 누적 분석 쿼리 작성
- [ ] MultiStepExtractor 구현 완료
- [ ] 10개 이상의 복잡한 질문 처리 및 SQL 생성
- [ ] 다단계 쿼리 최적화 기법 이해

## 추가 학습 자료
- Complex SQL Patterns: https://use-the-index-luke.com/sql/join
- Window Functions Advanced: https://www.postgresql.org/docs/current/functions-window.html
- Query Optimization: https://sqlperformance.com/
