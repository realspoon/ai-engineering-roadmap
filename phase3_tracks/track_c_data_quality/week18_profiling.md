# Week 18: 데이터 프로파일링 및 검증

## 학습 목표
- Great Expectations 라이브러리 숙달
- 데이터 프로파일링 기법 학습
- 자동 검증 파이프라인 구축

## 1. 데이터 프로파일링이란?

### 1.1 정의
데이터의 통계적 특성, 패턴, 구조를 분석하는 프로세스

### 1.2 목표
- 데이터 이해도 향상
- 품질 문제 조기 발견
- 데이터 거버넌스 기초 마련

## 2. Great Expectations 소개

### 2.1 주요 특징
- Python 기반 오픈소스
- 데이터 검증 자동화
- 풍부한 Expectation 라이브러리
- 데이터 문서화 자동 생성

### 2.2 핵심 개념

```
Expectation: 데이터가 만족해야 할 조건
Example: expect_column_values_to_be_in_set()

Validation: 데이터가 Expectation을 만족하는지 확인
Result: 검증 결과 (Pass/Fail/Warning)

Suite: Expectation의 모음
Context: 프로젝트 설정 및 메타데이터
```

## 3. Great Expectations 실전 가이드

### 3.1 설치 및 초기 설정
```bash
pip install great-expectations

# GX 초기화
great_expectations init
```

### 3.2 기본 사용법
```python
import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest

# Context 초기화
context = gx.get_context()

# Datasource 연결
datasource = context.sources.add_pandas(
    name="my_datasource",
    dataframe=df
)

# Asset 추가
asset = datasource.add_dataframe_asset(name="my_asset")

# Batch 생성
batch = asset.build_batch_request()

# Validator 생성
validator = context.get_validator(
    batch_request=batch
)
```

### 3.3 Expectation 예제

#### 기본 Expectation
```python
# 1. 컬럼 존재 여부
validator.expect_column_to_exist(column="customer_id")

# 2. 값이 특정 범위에 있는지
validator.expect_column_values_to_be_between(
    column="age",
    min_value=0,
    max_value=150
)

# 3. NULL 값이 없는지
validator.expect_column_values_to_not_be_null(
    column="email"
)

# 4. 특정 패턴 매칭
validator.expect_column_values_to_match_regex(
    column="phone",
    regex=r"^\d{3}-\d{3}-\d{4}$"
)

# 5. 유일한 값만 존재
validator.expect_column_values_to_be_unique(
    column="user_id"
)
```

#### 복합 Expectation
```python
# 1. 여러 값 중 하나
validator.expect_column_values_to_be_in_set(
    column="status",
    value_set=["active", "inactive", "pending"]
)

# 2. 데이터 타입 확인
validator.expect_column_values_to_be_of_type(
    column="amount",
    type_="float"
)

# 3. 컬럼 간 관계
validator.expect_column_pair_values_to_be_in_set(
    column_A="country_code",
    column_B="city_code",
    value_pairs=[("US", "NYC"), ("US", "LA")]
)

# 4. 테이블 행 개수
validator.expect_table_row_count_to_be_between(
    min_value=1000,
    max_value=1000000
)
```

## 4. 자동 프로파일링

### 4.1 Automated Profiling
```python
# 자동 프로파일링 (모든 Expectation 자동 생성)
profiler = gx.rule_based_profiler.RuleBasedProfiler(
    name="my_profiler",
    config_version=1.0,
    rules=[
        {
            "domain_builder": {
                "class_name": "ColumnDomainBuilder"
            },
            "expectation_suite_builders": [
                {
                    "class_name": "DefaultExpectationSuiteBuilder"
                }
            ]
        }
    ]
)

expectation_suite = context.assistants.profile.run(
    profiler=profiler,
    batch_request=batch
)
```

### 4.2 프로파일 분석
```python
# 데이터 통계 추출
stats = validator.get_expectation_suite()

# 컬럼별 통계
for column in df.columns:
    unique_count = df[column].nunique()
    null_count = df[column].isna().sum()
    print(f"{column}: {unique_count} unique, {null_count} nulls")
```

## 5. Checkpoint 구성

### 5.1 Checkpoint 정의
```python
# Checkpoint 생성
checkpoint = context.add_or_update_checkpoint(
    name="my_checkpoint",
    config_version=1.0,
    template_name=None,
    validations=[
        {
            "batch_request": batch.to_json_dict(),
            "expectation_suite_name": "my_suite"
        }
    ]
)
```

### 5.2 Checkpoint 실행
```python
# Checkpoint 실행
checkpoint_result = checkpoint.run()

# 결과 확인
if checkpoint_result.success:
    print("모든 검증 통과!")
else:
    print(f"검증 실패: {checkpoint_result.statistics}")
```

## 6. 데이터 문서 생성

### 6.1 자동 문서화
```python
# HTML 문서 생성
context.build_data_docs()

# 브라우저에서 보기
import webbrowser
webbrowser.open(context.root_directory)
```

## 7. 파이프라인 통합

### 7.1 전체 검증 파이프라인
```python
class DataValidationPipeline:
    def __init__(self, context):
        self.context = context

    def validate_data(self, data, suite_name):
        # 1. Datasource 연결
        datasource = self.context.sources.add_pandas(
            name="pipeline_ds",
            dataframe=data
        )

        # 2. Validator 생성
        asset = datasource.add_dataframe_asset(
            name="pipeline_asset"
        )
        batch = asset.build_batch_request()
        validator = self.context.get_validator(batch)

        # 3. Expectation 설정
        self._set_expectations(validator)

        # 4. 검증 실행
        result = validator.validate()

        return result

    def _set_expectations(self, validator):
        # 커스텀 Expectation 설정
        pass

    def generate_report(self, result):
        # 검증 결과 리포트 생성
        pass
```

## 8. 실습 프로젝트

### 8.1 프로젝트: E-Commerce 데이터 검증
```
1. Great Expectations 프로젝트 초기화
2. 3개 테이블(customers, orders, products) 연결
3. 각 테이블별 15개 이상의 Expectation 작성
4. 자동 프로파일링 실행
5. Checkpoint 구성 및 실행
6. 데이터 문서 생성
7. 검증 결과 분석 및 리포트
```

### 8.2 검증 규칙 예제
```python
# Customers 테이블
validator.expect_table_row_count_to_be_between(1000, 100000)
validator.expect_column_to_exist("customer_id")
validator.expect_column_values_to_be_unique("customer_id")
validator.expect_column_values_to_not_be_null("email")
validator.expect_column_values_to_match_regex(
    "email", r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
)

# Orders 테이블
validator.expect_column_values_to_be_between(
    "order_amount", 0, 1000000
)
validator.expect_column_values_to_be_in_set(
    "status", ["pending", "confirmed", "shipped", "delivered"]
)
```

## 9. 평가 기준

- [ ] Great Expectations 설치 및 기본 사용
- [ ] 20개 이상 Expectation 코드 작성
- [ ] 자동 프로파일링 실행
- [ ] Checkpoint 구성 및 실행
- [ ] 데이터 문서 생성
- [ ] 프로젝트 완료 및 리포트

## 10. 주요 실수 방지

| 주의사항 | 해결방법 |
|---------|---------|
| Expectation 과다 설정 | 비즈니스 규칙에 맞는 것만 선택 |
| 성능 저하 | 대용량 데이터는 샘플링 고려 |
| 유지보수 어려움 | 버전 관리 및 문서화 필수 |
| 거짓 긍정 | 임계값 정기적 검토 |

## 11. 참고 자료

- Great Expectations 공식 문서
- "Data Validation" - 우디 생 (Windy Sung)
- Apache Griffin 아키텍처
