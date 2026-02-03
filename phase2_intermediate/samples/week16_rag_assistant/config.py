"""
Week 16: RAG Assistant - Configuration Module
RAG 어시스턴트의 설정을 관리합니다
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class VectorDBType(Enum):
    """벡터 데이터베이스 타입"""
    FAISS = "faiss"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    CHROMADB = "chromadb"


class EmbeddingModel(Enum):
    """임베딩 모델"""
    OPENAI = "openai"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    COHERE = "cohere"
    LOCAL = "local"


class LLMModel(Enum):
    """LLM 모델"""
    OPENAI_GPT4 = "gpt-4"
    OPENAI_GPT35 = "gpt-3.5-turbo"
    ANTHROPIC_CLAUDE = "claude-3-sonnet"
    GOOGLE_PALM = "google-palm"
    LLAMA = "llama-2"


@dataclass
class VectorDBConfig:
    """벡터 데이터베이스 설정"""
    type: VectorDBType = VectorDBType.FAISS
    dimension: int = 384
    similarity_metric: str = "cosine"
    index_type: str = "flat"
    persist_dir: str = "./data/vector_db"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "dimension": self.dimension,
            "similarity_metric": self.similarity_metric,
            "index_type": self.index_type,
            "persist_dir": self.persist_dir
        }


@dataclass
class EmbeddingConfig:
    """임베딩 설정"""
    model: EmbeddingModel = EmbeddingModel.SENTENCE_TRANSFORMERS
    model_name: str = "all-MiniLM-L6-v2"
    device: str = "cpu"
    batch_size: int = 32
    normalize: bool = True
    cache_dir: str = "./data/embeddings"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model.value,
            "model_name": self.model_name,
            "device": self.device,
            "batch_size": self.batch_size,
            "normalize": self.normalize,
            "cache_dir": self.cache_dir
        }


@dataclass
class LLMConfig:
    """LLM 설정"""
    model: LLMModel = LLMModel.OPENAI_GPT35
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    api_key: str = ""
    api_base: str = ""
    timeout: int = 30

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model.value,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "timeout": self.timeout
        }


@dataclass
class RAGConfig:
    """RAG 설정"""
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 5
    similarity_threshold: float = 0.5
    rerank: bool = True
    max_context_length: int = 4096
    enable_cache: bool = True
    cache_ttl: int = 3600

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "top_k": self.top_k,
            "similarity_threshold": self.similarity_threshold,
            "rerank": self.rerank,
            "max_context_length": self.max_context_length,
            "enable_cache": self.enable_cache,
            "cache_ttl": self.cache_ttl
        }


@dataclass
class StreamlitConfig:
    """Streamlit 설정"""
    page_title: str = "RAG Assistant"
    page_icon: str = "🤖"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    theme_mode: str = "light"
    max_upload_size: int = 200  # MB
    session_state_ttl: int = 3600

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_title": self.page_title,
            "page_icon": self.page_icon,
            "layout": self.layout,
            "initial_sidebar_state": self.initial_sidebar_state,
            "theme_mode": self.theme_mode,
            "max_upload_size": self.max_upload_size,
            "session_state_ttl": self.session_state_ttl
        }


@dataclass
class LoggingConfig:
    """로깅 설정"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "./logs/rag_assistant.log"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    console_output: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "format": self.format,
            "log_file": self.log_file,
            "max_file_size": self.max_file_size,
            "backup_count": self.backup_count,
            "console_output": self.console_output
        }


@dataclass
class Config:
    """전체 설정"""
    environment: str = "development"
    debug: bool = True
    data_dir: str = "./data"
    documents_dir: str = "./data/documents"

    vector_db: VectorDBConfig = field(default_factory=VectorDBConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    streamlit: StreamlitConfig = field(default_factory=StreamlitConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def __post_init__(self):
        """설정 초기화"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.documents_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.logging.log_file), exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환"""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "data_dir": self.data_dir,
            "documents_dir": self.documents_dir,
            "vector_db": self.vector_db.to_dict(),
            "embedding": self.embedding.to_dict(),
            "llm": self.llm.to_dict(),
            "rag": self.rag.to_dict(),
            "streamlit": self.streamlit.to_dict(),
            "logging": self.logging.to_dict()
        }

    @classmethod
    def from_env(cls) -> "Config":
        """환경 변수에서 설정 로드"""
        config = cls()

        # 환경 설정
        config.environment = os.getenv("ENVIRONMENT", "development")
        config.debug = os.getenv("DEBUG", "True").lower() == "true"

        # LLM 설정
        api_key = os.getenv("LLM_API_KEY", "")
        if api_key:
            config.llm.api_key = api_key

        # 벡터 DB 설정
        config.vector_db.type = VectorDBType[os.getenv("VECTOR_DB_TYPE", "FAISS")]

        # 임베딩 설정
        config.embedding.device = os.getenv("EMBEDDING_DEVICE", "cpu")

        return config

    @classmethod
    def create_development(cls) -> "Config":
        """개발 환경 설정 생성"""
        config = cls(environment="development", debug=True)
        config.embedding.model = EmbeddingModel.SENTENCE_TRANSFORMERS
        config.embedding.device = "cpu"
        return config

    @classmethod
    def create_production(cls) -> "Config":
        """프로덕션 환경 설정 생성"""
        config = cls(environment="production", debug=False)
        config.embedding.device = "cuda"
        config.rag.enable_cache = True
        config.logging.level = "WARNING"
        return config


class ConfigManager:
    """설정 관리자"""

    _instance: Config = None

    @classmethod
    def get_config(cls) -> Config:
        """설정 싱글톤 인스턴스 반환"""
        if cls._instance is None:
            cls._instance = Config.from_env()
        return cls._instance

    @classmethod
    def set_config(cls, config: Config) -> None:
        """설정 설정"""
        cls._instance = config

    @classmethod
    def reset(cls) -> None:
        """설정 리셋"""
        cls._instance = None


def get_config() -> Config:
    """현재 설정 반환"""
    return ConfigManager.get_config()


def main():
    """테스트 함수"""
    import json

    print("="*60)
    print("RAG Assistant Configuration")
    print("="*60)

    # 개발 환경 설정
    print("\n[Development Environment]")
    dev_config = Config.create_development()
    print(f"Environment: {dev_config.environment}")
    print(f"Debug: {dev_config.debug}")
    print(f"Embedding Device: {dev_config.embedding.device}")

    # 프로덕션 환경 설정
    print("\n[Production Environment]")
    prod_config = Config.create_production()
    print(f"Environment: {prod_config.environment}")
    print(f"Debug: {prod_config.debug}")
    print(f"Embedding Device: {prod_config.embedding.device}")
    print(f"Cache Enabled: {prod_config.rag.enable_cache}")

    # 전체 설정 표시
    print("\n[Configuration Details]")
    config = get_config()
    config_dict = config.to_dict()
    print(json.dumps(config_dict, ensure_ascii=False, indent=2)[:500] + "...")

    # 설정 요소별 상세 정보
    print("\n[Vector DB Configuration]")
    print(f"Type: {config.vector_db.type.value}")
    print(f"Dimension: {config.vector_db.dimension}")
    print(f"Similarity Metric: {config.vector_db.similarity_metric}")

    print("\n[Embedding Configuration]")
    print(f"Model: {config.embedding.model.value}")
    print(f"Model Name: {config.embedding.model_name}")

    print("\n[RAG Configuration]")
    print(f"Chunk Size: {config.rag.chunk_size}")
    print(f"Top K: {config.rag.top_k}")
    print(f"Similarity Threshold: {config.rag.similarity_threshold}")

    print("\n[Logging Configuration]")
    print(f"Log Level: {config.logging.level}")
    print(f"Log File: {config.logging.log_file}")


if __name__ == "__main__":
    main()
