"""
Week 13: Production Architecture Template and Configuration Management
프로덕션 레벨의 에이전트 아키텍처와 설정 관리 시스템
"""

import json
import os
import yaml
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
import logging


class Environment(Enum):
    """실행 환경"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """로그 레벨"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class DatabaseConfig:
    """데이터베이스 설정"""
    host: str
    port: int
    user: str
    password: str
    database: str
    pool_size: int = 10
    timeout: int = 30

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def get_connection_string(self) -> str:
        """연결 문자열 생성"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class CacheConfig:
    """캐시 설정"""
    enabled: bool = True
    backend: str = "redis"  # redis, memcached, in-memory
    host: str = "localhost"
    port: int = 6379
    ttl: int = 3600  # 초 단위
    max_connections: int = 50

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LoggingConfig:
    """로깅 설정"""
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/agent.log"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    console_output: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['level'] = self.level.value
        return data


@dataclass
class APIConfig:
    """API 서버 설정"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 30
    max_request_size: int = 1048576  # 1MB
    rate_limit: int = 100  # 분당 요청 수

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentConfig:
    """에이전트 설정"""
    max_iterations: int = 10
    timeout: int = 300  # 초 단위
    retry_count: int = 3
    retry_delay: int = 5  # 초 단위
    enable_memory: bool = True
    memory_size: int = 1000  # 최근 1000개 메시지 저장

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Config:
    """전체 설정"""
    environment: Environment
    app_name: str
    version: str
    debug: bool
    database: DatabaseConfig
    cache: CacheConfig
    logging: LoggingConfig
    api: APIConfig
    agent: AgentConfig
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "environment": self.environment.value,
            "app_name": self.app_name,
            "version": self.version,
            "debug": self.debug,
            "database": self.database.to_dict(),
            "cache": self.cache.to_dict(),
            "logging": self.logging.to_dict(),
            "api": self.api.to_dict(),
            "agent": self.agent.to_dict(),
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        """JSON 형식으로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2, default=str)

    def to_yaml(self) -> str:
        """YAML 형식으로 변환"""
        return yaml.dump(self.to_dict(), allow_unicode=True, default_flow_style=False)


class ConfigManager:
    """설정 관리자"""

    def __init__(self):
        self.config: Optional[Config] = None
        self.env_vars: Dict[str, str] = {}
        self._load_env_vars()

    def _load_env_vars(self) -> None:
        """환경 변수 로드"""
        self.env_vars = dict(os.environ)

    def load_from_file(self, filepath: str) -> Config:
        """파일에서 설정 로드"""
        if filepath.endswith('.json'):
            return self._load_from_json(filepath)
        elif filepath.endswith('.yaml') or filepath.endswith('.yml'):
            return self._load_from_yaml(filepath)
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {filepath}")

    def _load_from_json(self, filepath: str) -> Config:
        """JSON 파일에서 로드"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        config = self._create_config_from_dict(data)
        self.config = config
        return config

    def _load_from_yaml(self, filepath: str) -> Config:
        """YAML 파일에서 로드"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        config = self._create_config_from_dict(data)
        self.config = config
        return config

    def _create_config_from_dict(self, data: Dict[str, Any]) -> Config:
        """딕셔너리에서 Config 객체 생성"""
        db_config = DatabaseConfig(**data.get("database", {}))
        cache_config = CacheConfig(**data.get("cache", {}))

        log_config_data = data.get("logging", {})
        if isinstance(log_config_data.get("level"), str):
            log_config_data["level"] = LogLevel[log_config_data["level"]]
        logging_config = LoggingConfig(**log_config_data)

        api_config = APIConfig(**data.get("api", {}))
        agent_config = AgentConfig(**data.get("agent", {}))

        return Config(
            environment=Environment[data.get("environment", "DEVELOPMENT").upper()],
            app_name=data.get("app_name", "AI Agent"),
            version=data.get("version", "1.0.0"),
            debug=data.get("debug", False),
            database=db_config,
            cache=cache_config,
            logging=logging_config,
            api=api_config,
            agent=agent_config,
            metadata=data.get("metadata", {})
        )

    def create_default_config(self, environment: Environment = Environment.DEVELOPMENT) -> Config:
        """기본 설정 생성"""
        return Config(
            environment=environment,
            app_name="AI Agent System",
            version="1.0.0",
            debug=environment == Environment.DEVELOPMENT,
            database=DatabaseConfig(
                host="localhost",
                port=5432,
                user="agent_user",
                password="secure_password",
                database="agent_db"
            ),
            cache=CacheConfig(
                enabled=True,
                backend="redis",
                host="localhost",
                port=6379
            ),
            logging=LoggingConfig(
                level=LogLevel.DEBUG if environment == Environment.DEVELOPMENT else LogLevel.INFO,
                console_output=True
            ),
            api=APIConfig(
                host="0.0.0.0",
                port=8000,
                workers=4
            ),
            agent=AgentConfig(
                max_iterations=10,
                timeout=300
            ),
            metadata={
                "created_at": datetime.now().isoformat(),
                "environment": environment.value
            }
        )

    def save_config(self, config: Config, filepath: str, format: str = "json") -> None:
        """설정 저장"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        if format.lower() == "json":
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(config.to_json())
        elif format.lower() == "yaml":
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(config.to_yaml())
        else:
            raise ValueError(f"지원하지 않는 형식: {format}")

    def get_config(self) -> Optional[Config]:
        """현재 설정 반환"""
        return self.config

    def update_config(self, updates: Dict[str, Any]) -> Config:
        """설정 업데이트"""
        if not self.config:
            self.config = self.create_default_config()

        config_dict = self.config.to_dict()
        config_dict.update(updates)

        self.config = self._create_config_from_dict(config_dict)
        return self.config


class LoggerFactory:
    """로거 생성 팩토리"""

    _loggers: Dict[str, logging.Logger] = {}

    @staticmethod
    def get_logger(name: str, config: LoggingConfig) -> logging.Logger:
        """로거 생성 또는 반환"""
        if name in LoggerFactory._loggers:
            return LoggerFactory._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(config.level.value)

        # 파일 핸들러
        os.makedirs(os.path.dirname(config.file_path), exist_ok=True)
        file_handler = logging.FileHandler(config.file_path)
        file_handler.setLevel(config.level.value)

        # 포매터
        formatter = logging.Formatter(config.format)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        # 콘솔 핸들러
        if config.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(config.level.value)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        LoggerFactory._loggers[name] = logger
        return logger


class ArchitectureTemplate:
    """프로덕션 아키텍처 템플릿"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = LoggerFactory.get_logger(
            self.__class__.__name__,
            config.logging
        )
        self.services: Dict[str, Any] = {}

    def initialize(self) -> None:
        """아키텍처 초기화"""
        self.logger.info(f"아키텍처 초기화 시작 (환경: {self.config.environment.value})")

        # 데이터베이스 초기화
        self._init_database()

        # 캐시 초기화
        self._init_cache()

        # 에이전트 초기화
        self._init_agents()

        self.logger.info("아키텍처 초기화 완료")

    def _init_database(self) -> None:
        """데이터베이스 초기화"""
        self.logger.info(f"데이터베이스 연결: {self.config.database.host}:{self.config.database.port}")
        self.services["database"] = {
            "connection_string": self.config.database.get_connection_string(),
            "pool_size": self.config.database.pool_size
        }

    def _init_cache(self) -> None:
        """캐시 초기화"""
        if self.config.cache.enabled:
            self.logger.info(f"캐시 활성화: {self.config.cache.backend}")
            self.services["cache"] = {
                "backend": self.config.cache.backend,
                "host": self.config.cache.host,
                "port": self.config.cache.port,
                "ttl": self.config.cache.ttl
            }
        else:
            self.logger.info("캐시 비활성화")

    def _init_agents(self) -> None:
        """에이전트 초기화"""
        self.logger.info(f"에이전트 설정: {self.config.agent.to_dict()}")
        self.services["agent"] = self.config.agent.to_dict()

    def get_status(self) -> Dict[str, Any]:
        """시스템 상태"""
        return {
            "environment": self.config.environment.value,
            "app_name": self.config.app_name,
            "version": self.config.version,
            "debug": self.config.debug,
            "services": list(self.services.keys()),
            "initialized_at": datetime.now().isoformat()
        }

    def shutdown(self) -> None:
        """시스템 종료"""
        self.logger.info("시스템 종료 중...")
        self.services.clear()
        self.logger.info("시스템 종료 완료")


def main():
    """메인 함수"""

    print("="*60)
    print("프로덕션 아키텍처 및 설정 관리")
    print("="*60)

    # ConfigManager 생성
    config_manager = ConfigManager()

    # 기본 설정 생성
    print("\n[개발 환경 설정]")
    dev_config = config_manager.create_default_config(Environment.DEVELOPMENT)
    print(f"환경: {dev_config.environment.value}")
    print(f"앱 이름: {dev_config.app_name}")
    print(f"디버그: {dev_config.debug}")

    # 프로덕션 환경 설정 생성
    print("\n[프로덕션 환경 설정]")
    prod_config = config_manager.create_default_config(Environment.PRODUCTION)
    prod_config.database.host = "prod-db.example.com"
    prod_config.api.workers = 8
    prod_config.logging.level = LogLevel.WARNING
    print(f"환경: {prod_config.environment.value}")
    print(f"DB 호스트: {prod_config.database.host}")
    print(f"API 워커: {prod_config.api.workers}")

    # 설정 저장
    print("\n[설정 저장]")
    config_manager.save_config(dev_config, "config_dev.json", format="json")
    print("✓ config_dev.json 저장 완료")

    config_manager.save_config(prod_config, "config_prod.yaml", format="yaml")
    print("✓ config_prod.yaml 저장 완료")

    # 설정 표시
    print("\n[개발 환경 설정 (JSON)]")
    print(dev_config.to_json()[:200] + "...")

    # 아키텍처 초기화
    print("\n[프로덕션 아키텍처 초기화]")
    architecture = ArchitectureTemplate(prod_config)
    architecture.initialize()

    # 시스템 상태
    status = architecture.get_status()
    print("\n시스템 상태:")
    print(json.dumps(status, ensure_ascii=False, indent=2))

    # 설정 업데이트
    print("\n[설정 업데이트]")
    updated_config = config_manager.update_config({
        "api": {
            "host": "0.0.0.0",
            "port": 9000,
            "workers": 16,
            "timeout": 60,
            "max_request_size": 1048576,
            "rate_limit": 200
        }
    })
    print(f"API 포트 업데이트: {updated_config.api.port}")
    print(f"API 워커 수 업데이트: {updated_config.api.workers}")

    # 정리
    architecture.shutdown()


if __name__ == "__main__":
    main()
