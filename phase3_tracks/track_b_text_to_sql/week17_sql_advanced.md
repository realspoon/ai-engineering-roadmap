# Week 17: SQL 고급 (Window Functions, CTE, 최적화)

## 학습 목표
- Window Functions을 통한 고급 데이터 분석
- Common Table Expressions (CTE)를 활용한 복잡한 쿼리 구성
- 쿼리 최적화 및 성능 튜닝 기초
- 쿼리 실행 계획 분석 및 인덱싱 전략

## O'Reilly 리소스
- **"SQL Performance Explained"** - Markus Winand
- **"SQL Cookbook"** (2nd Edition) - Anthony Molinaro
- **"Learning SQL"** (3rd Edition) - Alan Beaulieu

## 핵심 개념

### 1. Window Functions
```sql
-- ROW_NUMBER 예제
SELECT
  department,
  employee_name,
  salary,
  ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank
FROM employees;

-- RANK vs DENSE_RANK
SELECT
  product_id,
  month,
  sales,
  RANK() OVER (PARTITION BY product_id ORDER BY sales DESC) as rank,
  DENSE_RANK() OVER (PARTITION BY product_id ORDER BY sales DESC) as dense_rank
FROM monthly_sales;

-- Running Total
SELECT
  order_date,
  amount,
  SUM(amount) OVER (ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as running_total
FROM orders;

-- LAG/LEAD
SELECT
  date,
  sales,
  LAG(sales, 1) OVER (ORDER BY date) as prev_sales,
  LEAD(sales, 1) OVER (ORDER BY date) as next_sales,
  sales - LAG(sales, 1) OVER (ORDER BY date) as sales_change
FROM daily_sales;
```

### 2. Common Table Expressions (CTE)
```sql
-- 단순 CTE
WITH sales_cte AS (
  SELECT
    customer_id,
    SUM(amount) as total_sales
  FROM orders
  GROUP BY customer_id
)
SELECT
  customer_id,
  total_sales,
  total_sales * 0.1 as discount_amount
FROM sales_cte
WHERE total_sales > 10000;

-- 재귀적 CTE
WITH RECURSIVE dates AS (
  SELECT DATE('2024-01-01') as date
  UNION ALL
  SELECT DATE_ADD(date, INTERVAL 1 DAY)
  FROM dates
  WHERE date < DATE('2024-01-31')
)
SELECT * FROM dates;

-- 다중 CTE
WITH dept_sales AS (
  SELECT department, SUM(salary) as total_salary
  FROM employees
  GROUP BY department
),
top_depts AS (
  SELECT department
  FROM dept_sales
  WHERE total_salary > 100000
)
SELECT e.*
FROM employees e
WHERE e.department IN (SELECT department FROM top_depts);
```

### 3. 쿼리 최적화 원칙
- **Index 활용**: WHERE, JOIN, ORDER BY 절에서 선택적 컬럼 인덱싱
- **JOIN 최적화**: 더 작은 테이블을 먼저 처리
- **Filter Early**: 조인 전에 데이터 필터링
- **Avoid Subqueries**: JOIN이나 CTE로 대체

```sql
-- 최적화 전: 서브쿼리 사용
SELECT *
FROM products
WHERE product_id IN (
  SELECT product_id
  FROM orders
  WHERE order_date >= '2024-01-01'
);

-- 최적화 후: JOIN 사용
SELECT DISTINCT p.*
FROM products p
INNER JOIN orders o ON p.product_id = o.product_id
WHERE o.order_date >= '2024-01-01';
```

### 4. 쿼리 실행 계획
- EXPLAIN PLAN 또는 EXPLAIN ANALYZE 사용
- Sequential Scan vs Index Scan 이해
- Join 방식 분석 (Nested Loop, Hash Join, Merge Join)

## 실습 과제

### 과제 1: Window Functions 실습
```sql
-- 1. 부서별 직원의 급여 순위
CREATE OR REPLACE VIEW employee_rankings AS
SELECT
  department,
  employee_name,
  salary,
  ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rank_in_dept
FROM employees;

-- 2. 월별 누적 매출 계산
CREATE OR REPLACE VIEW monthly_cumulative_sales AS
SELECT
  DATE_TRUNC('month', order_date) as month,
  SUM(amount) as monthly_total,
  SUM(SUM(amount)) OVER (ORDER BY DATE_TRUNC('month', order_date)) as cumulative_total
FROM orders
GROUP BY DATE_TRUNC('month', order_date);

-- 3. 직원 급여 비교: 자신 vs 부서 평균
SELECT
  employee_id,
  employee_name,
  salary,
  AVG(salary) OVER (PARTITION BY department) as dept_avg_salary,
  salary - AVG(salary) OVER (PARTITION BY department) as salary_diff
FROM employees;
```

### 과제 2: CTE 활용
```sql
-- 1. Top 10 고객별 주문 통계
WITH customer_stats AS (
  SELECT
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) as order_count,
    SUM(o.amount) as total_spent,
    AVG(o.amount) as avg_order_value
  FROM customers c
  LEFT JOIN orders o ON c.customer_id = o.customer_id
  GROUP BY c.customer_id, c.customer_name
)
SELECT *
FROM customer_stats
ORDER BY total_spent DESC
LIMIT 10;

-- 2. 계층적 카테고리 분석
WITH category_hierarchy AS (
  SELECT
    category_id,
    category_name,
    parent_category_id,
    0 as level
  FROM categories
  WHERE parent_category_id IS NULL

  UNION ALL

  SELECT
    c.category_id,
    c.category_name,
    c.parent_category_id,
    ch.level + 1
  FROM categories c
  INNER JOIN category_hierarchy ch ON c.parent_category_id = ch.category_id
)
SELECT * FROM category_hierarchy;
```

### 과제 3: 쿼리 최적화
```sql
-- 주어진 느린 쿼리를 최적화하세요:
-- 원본 (비효율적):
SELECT o.order_id, o.customer_id, c.customer_name
FROM orders o
WHERE o.customer_id IN (
  SELECT customer_id
  FROM customers
  WHERE country = 'USA'
);

-- 최적화된 버전을 작성하세요.
```

## 체크포인트

- [ ] Window Functions (ROW_NUMBER, RANK, SUM OVER) 마스터
- [ ] LAG/LEAD 함수 이해 및 활용
- [ ] 단순 및 재귀적 CTE 작성 가능
- [ ] EXPLAIN PLAN 읽고 해석 가능
- [ ] Index 활용한 쿼리 최적화 경험
- [ ] 5개 이상의 Window Function 실습 완료
- [ ] 3개 이상의 복잡한 CTE 작성 완료

## 추가 학습 자료
- PostgreSQL Window Functions: https://www.postgresql.org/docs/current/functions-window.html
- SQLite CTE Tutorial: https://www.sqlite.org/lang_with.html
- Query Optimization Best Practices: https://use-the-index-luke.com/
