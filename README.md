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

*최종 업데이트: 2026년 2월*
