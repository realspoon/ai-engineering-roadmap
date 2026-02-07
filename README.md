# 🚀 Data AI Engineering 8개월 학습 로드맵

## 📋 프로그램 개요

| 항목 | 내용 |
|------|------|
| **대상** | AI 비경험자, 개발 실무 경험 보유자 (10여 명) |
| **기간** | 8개월 (32주) |
| **주당 학습시간** | 5-10시간 (파트타임) |
| **최종 목표** | 실무 적용 가능한 AI Agent 프로젝트 구축 |
---

## 🎯 3가지 트랙

| 트랙 | 설명 | 최종 결과물 |
|------|------|------------|
| **[Track A: Data Analyst Agent](./phase3_tracks/track_a_data_analyst/)** | 데이터 자동 분석 및 인사이트 생성 | 자연어 → 시각화 및 리포트 |
| **[Track B: Text-to-SQL Agent](./phase3_tracks/track_b_text_to_sql/)** | 자연어를 SQL로 변환 | 비개발자 DB 조회 시스템 |
| **[Track C: Data Quality Agent](./phase3_tracks/track_c_data_quality/)** | 데이터 품질 자동 검사 | 실시간 품질 모니터링 |

---

## 📅 Phase 별 학습 경로

```
┌─────────────────────────────────────────────────────────────────┐
│                    8개월 학습 로드맵 구조                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1 (월 1-2)          Phase 2 (월 3-4)                     │
│  ┌─────────────┐           ┌─────────────┐                      │
│  │  공통 기초   │  ──────▶  │  공통 심화   │                      │
│  │  Week 1-8   │           │  Week 9-16  │                      │
│  └─────────────┘           └──────┬──────┘                      │
│                                   │                             │
│                    ┌──────────────┼──────────────┐              │
│                    ▼              ▼              ▼              │
│  Phase 3 (월 5-6)                                               │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐                   │
│  │  Track A  │  │  Track B  │  │  Track C  │                   │
│  │ Week 17-24│  │ Week 17-24│  │ Week 17-24│                   │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘                   │
│        │              │              │                          │
│        └──────────────┼──────────────┘                          │
│                       ▼                                         │
│  Phase 4 (월 7-8)                                               │
│  ┌─────────────────────────────────────┐                       │
│  │      프로덕션 프로젝트 개발            │                       │
│  │           Week 25-32                │                       │
│  └─────────────────────────────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Phase 별 상세 링크

### [Phase 1: 공통 기초 (월 1-2)](./phase1_basics/)

| 주차 | 주제 | 파일 | 샘플 코드 |
|------|------|------|----------|
| Week 1 | LLM 기초와 생태계 | [week01_llm_fundamentals.md](./phase1_basics/week01_llm_fundamentals.md) | [chatbot_basic.py](./phase1_basics/samples/week01_chatbot_basic.py) |
| Week 2 | Python 환경 구축 | [week02_python_environment.md](./phase1_basics/week02_python_environment.md) | [environment_setup.py](./phase1_basics/samples/week02_environment_setup.py) |
| Week 3 | Prompt Engineering 기초 | [week03_prompt_basics.md](./phase1_basics/week03_prompt_basics.md) | [prompt_templates.py](./phase1_basics/samples/week03_prompt_templates.py) |
| Week 4 | Prompt Engineering 심화 | [week04_prompt_advanced.md](./phase1_basics/week04_prompt_advanced.md) | [react_pattern.py](./phase1_basics/samples/week04_react_pattern.py) |
| Week 5 | LangChain 시작하기 | [week05_langchain_intro.md](./phase1_basics/week05_langchain_intro.md) | [langchain_chains.py](./phase1_basics/samples/week05_langchain_chains.py) |
| Week 6 | LangChain Memory & Tools | [week06_langchain_memory.md](./phase1_basics/week06_langchain_memory.md) | [memory_tools.py](./phase1_basics/samples/week06_memory_tools.py) |
| Week 7 | RAG 기초 | [week07_rag_basics.md](./phase1_basics/week07_rag_basics.md) | [rag_pipeline.py](./phase1_basics/samples/week07_rag_pipeline.py) |
| Week 8 | RAG 심화 | [week08_rag_advanced.md](./phase1_basics/week08_rag_advanced.md) | [rag_evaluation.py](./phase1_basics/samples/week08_rag_evaluation.py) |

### [Phase 2: 공통 심화 (월 3-4)](./phase2_intermediate/)

| 주차 | 주제 | 파일 | 샘플 코드 |
|------|------|------|----------|
| Week 9 | Agent 개념과 설계 | [week09_agent_concepts.md](./phase2_intermediate/week09_agent_concepts.md) | [react_agent.py](./phase2_intermediate/samples/week09_react_agent.py) |
| Week 10 | LangGraph 입문 | [week10_langgraph_intro.md](./phase2_intermediate/week10_langgraph_intro.md) | [langgraph_basic.py](./phase2_intermediate/samples/week10_langgraph_basic.py) |
| Week 11 | LangGraph 심화 | [week11_langgraph_advanced.md](./phase2_intermediate/week11_langgraph_advanced.md) | [multi_agent.py](./phase2_intermediate/samples/week11_multi_agent.py) |
| Week 12 | Agent 도구 생태계 | [week12_agent_tools.md](./phase2_intermediate/week12_agent_tools.md) | [custom_tools.py](./phase2_intermediate/samples/week12_custom_tools.py) |
| Week 13 | LLM 애플리케이션 설계 | [week13_app_design.md](./phase2_intermediate/week13_app_design.md) | [architecture_template.py](./phase2_intermediate/samples/week13_architecture.py) |
| Week 14 | 평가와 테스팅 | [week14_evaluation.md](./phase2_intermediate/week14_evaluation.md) | [llm_testing.py](./phase2_intermediate/samples/week14_testing.py) |
| Week 15 | 배포와 운영 | [week15_deployment.md](./phase2_intermediate/week15_deployment.md) | [fastapi_server.py](./phase2_intermediate/samples/week15_fastapi.py) |
| Week 16 | 통합 프로젝트 | [week16_integration.md](./phase2_intermediate/week16_integration.md) | [rag_assistant/](./phase2_intermediate/samples/week16_rag_assistant/) |

### [Phase 3: 트랙별 특화 (월 5-6)](./phase3_tracks/)

#### [Track A: Data Analyst Agent](./phase3_tracks/track_a_data_analyst/)
| 주차 | 주제 | 파일 | 샘플 코드 |
|------|------|------|----------|
| Week 17-20 | 기초 구현 | [README.md](./phase3_tracks/track_a_data_analyst/README.md) | [samples/](./phase3_tracks/track_a_data_analyst/samples/) |
| Week 21-24 | 고도화 | 상동 | 상동 |

#### [Track B: Text-to-SQL Agent](./phase3_tracks/track_b_text_to_sql/)
| 주차 | 주제 | 파일 | 샘플 코드 |
|------|------|------|----------|
| Week 17-20 | 기초 구현 | [README.md](./phase3_tracks/track_b_text_to_sql/README.md) | [samples/](./phase3_tracks/track_b_text_to_sql/samples/) |
| Week 21-24 | 고도화 | 상동 | 상동 |

#### [Track C: Data Quality Agent](./phase3_tracks/track_c_data_quality/)
| 주차 | 주제 | 파일 | 샘플 코드 |
|------|------|------|----------|
| Week 17-20 | 기초 구현 | [README.md](./phase3_tracks/track_c_data_quality/README.md) | [samples/](./phase3_tracks/track_c_data_quality/samples/) |
| Week 21-24 | 고도화 | 상동 | 상동 |

### [Phase 4: 프로젝트 (월 7-8)](./phase4_project/)

| 주차 | 주제 | 파일 | 템플릿 |
|------|------|------|--------|
| Week 25-26 | 프로젝트 설계 | [week25_26_setup.md](./phase4_project/week25_26_setup.md) | [project_template/](./phase4_project/templates/) |
| Week 27-28 | 핵심 기능 개발 | [week27_28_development.md](./phase4_project/week27_28_development.md) | - |
| Week 29-30 | 최적화 | [week29_30_optimization.md](./phase4_project/week29_30_optimization.md) | - |
| Week 31-32 | 배포 및 발표 | [week31_32_launch.md](./phase4_project/week31_32_launch.md) | - |

---

## 📖 핵심 O'Reilly 리소스

### 필수 도서 (모든 트랙 공통)

| 우선순위 | 제목 | 저자 | 발행년도 |
|----------|------|------|----------|
| ⭐⭐⭐ | [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) | Chip Huyen | 2024.12 |
| ⭐⭐⭐ | [Learning LangChain](https://www.oreilly.com/library/view/learning-langchain/9781098167271/) | Mayo Oshin, Nuno Campos | 2025.02 |
| ⭐⭐⭐ | [Prompt Engineering for LLMs](https://www.oreilly.com/library/view/prompt-engineering-for/9781098156145/) | John Berryman, Albert Ziegler | 2024.12 |
| ⭐⭐ | [Building Applications with AI Agents](https://www.oreilly.com/library/view/building-applications-with/9781098176495/) | Mariusz Skoneczko | 2025.09 |
| ⭐⭐ | [RAG-Driven Generative AI](https://www.oreilly.com/library/view/rag-driven-generative-ai/9781836200918/) | Denis Rothman | 2024.09 |

---

## 🎓 FastCampus 부트캠프 강의

> 📌 **[전체 매핑 문서 보기](./FASTCAMPUS_MAPPING.md)**

### Phase별 핵심 강의

| Phase | 핵심 강의 | 비고 |
|-------|----------|------|
| **Phase 1** | ChatGPT/Claude 완벽가이드, 프롬프트 엔지니어링, LangChain, RAG 시스템 | 기초 필수 |
| **Phase 2** | AI 에이전트 완벽가이드, MCP 에이전트 개발, FastAPI | Agent 핵심 |
| **Phase 3-A** | Python 데이터 분석, 데이터 시각화, Streamlit | 분석 특화 |
| **Phase 3-B** | SQL 기초/심화, SQL 데이터 분석 | SQL 특화 |
| **Phase 3-C** | 데이터 엔지니어링, Python 데이터 분석 | 품질 특화 |
| **Phase 4** | FastAPI, Streamlit, AI 서비스 배포 | 프로덕션 |

🔗 강의 접속: https://fastcampusbootcamp.skillflo.io/enrollment

---

## 📊 주간 학습 시간 배분

**주당 8시간 기준**

| 활동 | 시간 | 비율 |
|------|------|------|
| 📚 이론 학습 (도서/영상) | 3시간 | 37.5% |
| 💻 실습 및 코딩 | 4시간 | 50% |
| 👥 팀 미팅/토론 | 1시간 | 12.5% |

---

## ✅ 월별 마일스톤

- [ ] **월 1**: LLM API 호출 및 Prompt Engineering 기초
- [ ] **월 2**: LangChain 기본 Chain 및 RAG 파이프라인
- [ ] **월 3**: AI Agent 구조 이해 및 LangGraph 활용
- [ ] **월 4**: 프로덕션 레벨 설계 및 배포 기초
- [ ] **월 5**: 트랙별 도메인 지식 및 Agent 프로토타입
- [ ] **월 6**: 트랙별 Agent v1.0 완성
- [ ] **월 7**: 프로덕션 프로젝트 핵심 기능 개발
- [ ] **월 8**: 최종 프로젝트 배포 및 발표

---

## 🔗 공식 문서

- [LangChain Documentation](https://python.langchain.com/docs/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)

---

## 목표 AI Agent 실제 동작 예시

---

## Data Analyst Agent 실제 동작 예시

### 시나리오: 사용자가 질문을 던짐

```
👤 사용자: "지난 3개월 매출 트렌드 분석하고 이상한 점 있으면 알려줘"
```

---

### Agent의 내부 동작 (자동으로 일어남)

```
🤖 Agent 내부 사고 과정:

1️⃣ [질문 분석]
   "매출 트렌드" → sales 테이블 필요
   "지난 3개월" → 날짜 필터 필요
   "이상한 점" → 이상치 탐지 필요
   
   → 계획: 데이터 조회 → 트렌드 분석 → 이상치 확인 → 리포트

2️⃣ [Tool 호출: SQL 실행]
   SELECT DATE_TRUNC('week', order_date) as week,
          SUM(amount) as total_sales
   FROM sales
   WHERE order_date >= CURRENT_DATE - INTERVAL '3 months'
   GROUP BY 1
   ORDER BY 1
   
   → 결과: 12주치 주간 매출 데이터 획득

3️⃣ [Tool 호출: Pandas 분석]
   - 주간 성장률 계산
   - 평균, 표준편차 계산
   - Z-score로 이상치 탐지
   
   → 발견: 6주차에 매출이 평균 대비 47% 급락

4️⃣ [자율 판단: 추가 분석 필요]
   "6주차 급락 원인을 파악해야겠다"
   
   → Tool 호출: 6주차 상세 데이터 조회

5️⃣ [Tool 호출: SQL 실행 - 상세 분석]
   SELECT product_category, SUM(amount)
   FROM sales
   WHERE week = 6주차
   GROUP BY 1
   
   → 발견: '전자제품' 카테고리만 90% 급락

6️⃣ [Tool 호출: 차트 생성]
   - 주간 매출 트렌드 라인 차트
   - 카테고리별 비교 바 차트

7️⃣ [리포트 생성]
```

---

### 사용자가 받는 결과

```
🤖 Agent 응답:

## 지난 3개월 매출 트렌드 분석 리포트

### 📈 전체 트렌드
- 총 매출: 4억 2,300만원
- 주간 평균: 3,525만원
- 전체적으로 완만한 상승 추세 (+2.3%/주)

### ⚠️ 이상 징후 발견
**6주차 (1월 둘째주)에 매출 47% 급락**

| 주차 | 매출 | 전주 대비 |
|------|------|-----------|
| 5주차 | 3,800만원 | +5% |
| 6주차 | 2,014만원 | ▼47% ⚠️ |
| 7주차 | 3,650만원 | +81% |

### 🔍 원인 분석
- **전자제품 카테고리**만 90% 급감
- 다른 카테고리는 정상 수준 유지
- 추정 원인: 해당 주 전자제품 프로모션 종료 또는 재고 이슈

### 📊 시각화
[주간 매출 트렌드 차트]
[카테고리별 매출 비교 차트]

### 💡 권장 조치
1. 6주차 전자제품 재고/프로모션 이력 확인
2. 향후 프로모션 종료 시 대체 이벤트 준비 검토
```

---

## 핵심 포인트: Agent vs 일반 챗봇

| 구분 | 일반 챗봇 (ChatGPT 등) | AI Agent |
|------|----------------------|----------|
| 데이터 접근 | ❌ 실제 DB 접근 불가 | ✅ 직접 SQL 실행 |
| 분석 수행 | ❌ "~해보세요" 조언만 | ✅ 실제 계산/분석 수행 |
| 자율 판단 | ❌ 시킨 것만 함 | ✅ "이상하네? 더 파보자" |
| 결과물 | 텍스트 답변 | 데이터 + 차트 + 리포트 |

---

## Text-to-SQL Agent 예시 (더 단순한 케이스)

```
👤 사용자: "지난달 가장 많이 팔린 제품 5개 알려줘"

🤖 Agent 내부:
1️⃣ 질문 분석 → products, orders 테이블 JOIN 필요
2️⃣ 스키마 확인 → product_id로 연결 가능
3️⃣ SQL 생성:
    SELECT p.name, SUM(o.quantity) as total_sold
    FROM orders o
    JOIN products p ON o.product_id = p.id
    WHERE o.order_date >= '2024-01-01'
    GROUP BY p.name
    ORDER BY total_sold DESC
    LIMIT 5
4️⃣ SQL 실행
5️⃣ 결과 해석

🤖 Agent 응답:
지난달 판매량 Top 5 제품입니다:

| 순위 | 제품명 | 판매 수량 |
|------|--------|-----------|
| 1 | 무선 이어폰 Pro | 1,247개 |
| 2 | 스마트워치 S3 | 892개 |
| 3 | 보조배터리 20000 | 756개 |
| 4 | USB-C 케이블 | 623개 |
| 5 | 블루투스 스피커 | 589개 |
```

---

## Data Quality Agent 예시

```
👤 사용자: "users 테이블 품질 체크해줘"

🤖 Agent 내부:
1️⃣ 테이블 프로파일링 실행
2️⃣ 규칙 검사 (null, 중복, 형식)
3️⃣ 이상 탐지 (ML 모델)
4️⃣ 이슈 분류 및 원인 추론

🤖 Agent 응답:
## users 테이블 품질 리포트

### 품질 점수: 78/100 🟡

### 발견된 이슈

| 심각도 | 컬럼 | 이슈 | 영향 |
|--------|------|------|------|
| 🔴 HIGH | email | 12% null | 1,247건 |
| 🔴 HIGH | phone | 잘못된 형식 | 89건 |
| 🟡 MEDIUM | created_at | 미래 날짜 | 23건 |
| 🟢 LOW | name | 중복 의심 | 156건 |

### 수정 제안
1. email null → 기본값 설정 또는 필수 입력으로 변경
2. phone 형식 → 정규식 검증 추가 권장
   ```sql
   -- 잘못된 형식 확인
   SELECT * FROM users 
   WHERE phone NOT SIMILAR TO '[0-9]{3}-[0-9]{4}-[0-9]{4}'
   ```

[실행하시겠습니까? Y/N]
```

---

## 정리: Agent가 "스스로 일한다"의 의미

```
일반 프로그램:
  입력 → [정해진 로직] → 출력

AI Agent:
  질문 → [LLM이 판단] → Tool 선택 → 실행 → [결과 보고 판단] → 
       → 추가 분석 필요? → Tool 선택 → ... → 최종 응답
```

**Agent의 핵심은 "판단"과 "도구 사용"의 조합**입니다:
- LLM이 상황을 판단하고
- 적절한 Tool(SQL, Pandas, 차트 등)을 선택하고
- 결과를 보고 다음 행동을 결정합니다

---

*최종 업데이트: 2026년 2월*
