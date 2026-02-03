# Phase 2: 공통 심화 (월 3-4)

> **목표**: AI Agent의 핵심 개념 완전 이해, LangGraph 활용 능력 확보, 프로덕션 준비

## 📅 주차별 학습 내용

| 주차 | 주제 | 핵심 기술 | 실습 결과물 |
|------|------|----------|------------|
| [Week 9](./week09_agent_concepts.md) | Agent 개념 | ReAct, Plan-Execute | ReAct Agent |
| [Week 10](./week10_langgraph_intro.md) | LangGraph 입문 | StateGraph, Edge | 기본 그래프 |
| [Week 11](./week11_langgraph_advanced.md) | LangGraph 심화 | Multi-Agent, Checkpoint | Supervisor Agent |
| [Week 12](./week12_agent_tools.md) | Agent 도구 | Custom Tools, API 연동 | 업무 자동화 Agent |
| [Week 13](./week13_app_design.md) | 애플리케이션 설계 | 아키텍처, 비용 최적화 | 설계 문서 |
| [Week 14](./week14_evaluation.md) | 평가와 테스팅 | 메트릭, Guardrails | 테스트 파이프라인 |
| [Week 15](./week15_deployment.md) | 배포와 운영 | FastAPI, Docker | API 서버 |
| [Week 16](./week16_integration.md) | 통합 프로젝트 | 전체 통합 | RAG Assistant |

---

## 📚 핵심 O'Reilly 리소스

| 도서 | 저자 | 학습 범위 |
|------|------|----------|
| [Building Applications with AI Agents](https://www.oreilly.com/library/view/building-applications-with/9781098176495/) | Mariusz Skoneczko | Ch 1-8 |
| [Learning LangChain](https://www.oreilly.com/library/view/learning-langchain/9781098167271/) | Mayo Oshin | Ch 8-12 |
| [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) | Chip Huyen | Ch 5-10 |
| [LLMs in Production](https://www.oreilly.com/library/view/llms-in-production/9781633437203/) | Christopher Brousseau | Ch 1-8 |

---

## 💻 샘플 코드

```
samples/
├── week09_react_agent.py         # ReAct Agent 구현
├── week10_langgraph_basic.py     # LangGraph 기본
├── week11_multi_agent.py         # Multi-Agent 시스템
├── week12_custom_tools.py        # Custom Tool 생성
├── week13_architecture.py        # 아키텍처 템플릿
├── week14_testing.py             # LLM 테스팅
├── week15_fastapi.py             # FastAPI 서버
└── week16_rag_assistant/         # 통합 프로젝트
    ├── main.py
    ├── agent.py
    ├── tools.py
    └── config.py
```

---

## ✅ Phase 2 완료 체크리스트

- [ ] 다양한 Agent 유형 구현 가능 (ReAct, Plan-Execute)
- [ ] LangGraph로 복잡한 워크플로우 구축 가능
- [ ] Custom Tool 생성 및 연동 가능
- [ ] 프로덕션 레벨 아키텍처 설계 가능
- [ ] LLM 테스트 및 평가 파이프라인 구축
- [ ] FastAPI로 Agent 서버 배포 가능
- [ ] Phase 2 통합 프로젝트 완성

---

[← Phase 1](../phase1_basics/README.md) | [Phase 3 →](../phase3_tracks/README.md)
