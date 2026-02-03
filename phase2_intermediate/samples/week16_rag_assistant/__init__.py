"""
Week 16: RAG (Retrieval-Augmented Generation) Assistant
RAG 패턴을 구현한 Streamlit 기반의 AI 어시스턴트

이 패키지는 다음 모듈들을 포함합니다:
- config: 설정 관리
- agent: RAG 에이전트 구현
- main: Streamlit 애플리케이션
"""

__version__ = "1.0.0"
__author__ = "AI Engineering Team"
__description__ = "Retrieval-Augmented Generation Assistant with Streamlit"

from . import config
from . import agent

__all__ = ["config", "agent"]
