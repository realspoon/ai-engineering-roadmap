# Phase 1: 공통 기초 (월 1-2)

> **목표**: LLM과 AI Agent의 기본 개념 이해, 개발 환경 구축, RAG 파이프라인 구축

## 📅 주차별 학습 내용

| 주차 | 주제 | 핵심 기술 | 실습 결과물 |
|------|------|----------|------------|
| [Week 1](./week01_llm_fundamentals.md) | LLM 기초 | OpenAI/Claude API | 기본 챗봇 |
| [Week 2](./week02_python_environment.md) | Python 환경 | venv, pandas | 분석 환경 |
| [Week 3](./week03_prompt_basics.md) | Prompt 기초 | Zero/Few-shot, CoT | 프롬프트 라이브러리 |
| [Week 4](./week04_prompt_advanced.md) | Prompt 심화 | ReAct, Self-consistency | A/B 테스트 |
| [Week 5](./week05_langchain_intro.md) | LangChain 입문 | Chain, PromptTemplate | Sequential Chain |
| [Week 6](./week06_langchain_memory.md) | Memory & Tools | Memory, Custom Tool | Tool Agent |
| [Week 7](./week07_rag_basics.md) | RAG 기초 | Embedding, VectorDB | RAG Pipeline |
| [Week 8](./week08_rag_advanced.md) | RAG 심화 | Hybrid Search, 평가 | Q&A 챗봇 |

---

## 📚 핵심 O'Reilly 리소스

| 도서 | 저자 | 학습 범위 |
|------|------|----------|
| [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) | Chip Huyen | Ch 1-6 |
| [Learning LangChain](https://www.oreilly.com/library/view/learning-langchain/9781098167271/) | Mayo Oshin | Ch 1-7 |
| [Prompt Engineering for LLMs](https://www.oreilly.com/library/view/prompt-engineering-for/9781098156145/) | John Berryman | Ch 1-8 |
| [RAG-Driven Generative AI](https://www.oreilly.com/library/view/rag-driven-generative-ai/9781836200918/) | Denis Rothman | Ch 1-8 |

---

## 💻 샘플 코드

```
samples/
├── week01_chatbot_basic.py      # LLM API 기본 호출
├── week02_environment_setup.py  # 환경 설정 검증
├── week03_prompt_templates.py   # 프롬프트 템플릿
├── week04_react_pattern.py      # ReAct 패턴 구현
├── week05_langchain_chains.py   # LangChain 체인
├── week06_memory_tools.py       # 메모리와 도구
├── week07_rag_pipeline.py       # RAG 파이프라인
└── week08_rag_evaluation.py     # RAG 평가
```

---

## ✅ Phase 1 완료 체크리스트

- [ ] LLM API (OpenAI, Claude) 호출 가능
- [ ] 효과적인 프롬프트 작성 가능
- [ ] LangChain 기본 Chain 구축 가능
- [ ] RAG 파이프라인 독립 구축 가능
- [ ] 회사 문서 기반 Q&A 챗봇 완성

---

[← 메인으로](../README.md) | [Phase 2 →](../phase2_intermediate/README.md)
