"""
Week 2: 환경 설정 및 검증
==========================

이 모듈은 AI 엔지니어링 프로젝트의 환경을 설정하고 검증하는 방법을 보여줍니다.
- 패키지 설치 확인
- 필수 라이브러리 검증
- 프로젝트 디렉토리 구조 생성
- 환경 변수 설정 및 검증
- API 키 관리
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import importlib
from datetime import datetime


class EnvironmentValidator:
    """
    환경 설정 및 검증을 담당하는 클래스입니다.
    """

    def __init__(self):
        """EnvironmentValidator 초기화"""
        self.validation_results = {}
        self.warnings = []
        self.errors = []

    def check_python_version(self) -> Tuple[bool, str]:
        """
        Python 버전 확인 (3.8 이상 필요)

        Returns:
            Tuple[bool, str]: (성공 여부, 메시지)
        """
        version = sys.version_info
        minimum_version = (3, 8)

        if version >= minimum_version:
            message = f"✓ Python 버전 확인: {version.major}.{version.minor}.{version.micro}"
            return True, message
        else:
            message = f"✗ Python 버전 부족: {version.major}.{version.minor}.{version.micro} (3.8 이상 필요)"
            return False, message

    def check_package_installed(self, package_name: str) -> Tuple[bool, str]:
        """
        특정 패키지가 설치되었는지 확인합니다.

        Args:
            package_name (str): 확인할 패키지 이름

        Returns:
            Tuple[bool, str]: (설치 여부, 메시지)
        """
        try:
            # 패키지 명과 import 명이 다를 수 있으므로 처리
            import_name = package_name.replace("-", "_")
            importlib.import_module(import_name)
            return True, f"✓ {package_name} 설치됨"
        except ImportError:
            return False, f"✗ {package_name} 미설치"

    def check_required_packages(self) -> Dict[str, bool]:
        """
        필수 패키지 목록 확인

        Returns:
            Dict[str, bool]: 패키지별 설치 상태
        """
        required_packages = [
            "python-dotenv",
            "requests",
            "langchain",
            "openai",
            "pydantic",
            "pandas",
            "numpy",
        ]

        results = {}
        print("\n📦 필수 패키지 확인:")
        print("-" * 50)

        for package in required_packages:
            is_installed, message = self.check_package_installed(package)
            results[package] = is_installed
            print(message)
            if not is_installed:
                self.errors.append(f"필수 패키지 미설치: {package}")

        return results

    def check_environment_variables(self) -> Dict[str, bool]:
        """
        필수 환경 변수 확인

        Returns:
            Dict[str, bool]: 환경 변수별 설정 상태
        """
        required_vars = [
            "OPENAI_API_KEY",
            "LANGCHAIN_API_KEY",
        ]

        optional_vars = [
            "PINECONE_API_KEY",
            "WEAVIATE_URL",
        ]

        results = {"required": {}, "optional": {}}

        print("\n🔐 필수 환경 변수 확인:")
        print("-" * 50)

        for var in required_vars:
            if os.getenv(var):
                print(f"✓ {var} 설정됨")
                results["required"][var] = True
            else:
                print(f"✗ {var} 미설정")
                results["required"][var] = False
                self.warnings.append(f"필수 환경 변수 미설정: {var}")

        print("\n📝 선택사항 환경 변수 확인:")
        print("-" * 50)

        for var in optional_vars:
            if os.getenv(var):
                print(f"✓ {var} 설정됨")
                results["optional"][var] = True
            else:
                print(f"○ {var} 미설정 (선택사항)")
                results["optional"][var] = False

        return results

    def create_project_structure(self, base_path: str) -> bool:
        """
        프로젝트 디렉토리 구조 생성

        Args:
            base_path (str): 프로젝트 기본 경로

        Returns:
            bool: 성공 여부
        """
        directories = [
            "src",
            "src/agents",
            "src/tools",
            "src/prompts",
            "src/utils",
            "data",
            "data/raw",
            "data/processed",
            "models",
            "notebooks",
            "tests",
            "logs",
            "config",
        ]

        print("\n📁 프로젝트 디렉토리 구조 생성:")
        print("-" * 50)

        base_path = Path(base_path)

        try:
            for directory in directories:
                dir_path = base_path / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✓ {directory}/ 생성")

            # .gitignore 파일 생성
            gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Data and Models
data/raw/
data/processed/
models/*.pkl
models/*.h5
"""
            gitignore_path = base_path / ".gitignore"
            with open(gitignore_path, "w") as f:
                f.write(gitignore_content)
            print("✓ .gitignore 생성")

            # config.json 생성
            config_template = {
                "project": "AI_Engineering",
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "environment": "development",
                "log_level": "INFO",
            }
            config_path = base_path / "config" / "config.json"
            with open(config_path, "w") as f:
                json.dump(config_template, f, indent=2)
            print("✓ config/config.json 생성")

            # __init__.py 파일 생성
            init_files = [
                "src/__init__.py",
                "src/agents/__init__.py",
                "src/tools/__init__.py",
                "src/prompts/__init__.py",
                "src/utils/__init__.py",
            ]

            for init_file in init_files:
                init_path = base_path / init_file
                init_path.touch()

            print("✓ __init__.py 파일들 생성")

            return True

        except Exception as e:
            self.errors.append(f"디렉토리 생성 실패: {str(e)}")
            return False

    def check_git_installed(self) -> Tuple[bool, str]:
        """
        Git 설치 여부 확인

        Returns:
            Tuple[bool, str]: (설치 여부, 메시지)
        """
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, f"✓ Git 설치됨: {version}"
            else:
                return False, "✗ Git 설치 확인 실패"
        except FileNotFoundError:
            return False, "✗ Git 미설치"
        except subprocess.TimeoutExpired:
            return False, "✗ Git 확인 타임아웃"

    def run_full_validation(self, project_path: str = None) -> Dict:
        """
        전체 환경 검증 실행

        Args:
            project_path (str): 프로젝트 경로 (선택사항)

        Returns:
            Dict: 검증 결과 요약
        """
        print("\n" + "=" * 60)
        print("🔍 환경 검증 시작")
        print("=" * 60)

        # Python 버전 확인
        print("\n📌 Python 버전:")
        print("-" * 50)
        success, message = self.check_python_version()
        print(message)

        # Git 확인
        print("\n🔧 Git:")
        print("-" * 50)
        git_installed, git_message = self.check_git_installed()
        print(git_message)

        # 패키지 확인
        packages = self.check_required_packages()

        # 환경 변수 확인
        env_vars = self.check_environment_variables()

        # 프로젝트 구조 생성
        if project_path:
            self.create_project_structure(project_path)

        # 요약
        print("\n" + "=" * 60)
        print("📊 검증 결과 요약")
        print("=" * 60)
        print(f"✓ 통과: {len(packages) - sum(not v for v in packages.values())}/{len(packages)} 패키지")
        print(f"⚠ 경고: {len(self.warnings)}개")
        print(f"✗ 오류: {len(self.errors)}개")

        if self.warnings:
            print("\n⚠ 경고 사항:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if self.errors:
            print("\n✗ 오류 사항:")
            for error in self.errors:
                print(f"  - {error}")

        return {
            "python_version": success,
            "git_installed": git_installed,
            "packages": packages,
            "environment_variables": env_vars,
            "warnings": self.warnings,
            "errors": self.errors,
        }


class DependencyInstaller:
    """
    필수 패키지 설치를 담당하는 클래스입니다.
    """

    @staticmethod
    def install_package(package_name: str) -> bool:
        """
        pip을 사용하여 패키지 설치

        Args:
            package_name (str): 설치할 패키지 이름

        Returns:
            bool: 설치 성공 여부
        """
        try:
            print(f"설치 중: {package_name}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                print(f"✓ {package_name} 설치 완료")
                return True
            else:
                print(f"✗ {package_name} 설치 실패")
                return False

        except subprocess.TimeoutExpired:
            print(f"✗ {package_name} 설치 타임아웃")
            return False
        except Exception as e:
            print(f"✗ {package_name} 설치 오류: {str(e)}")
            return False

    @staticmethod
    def install_requirements(requirements_file: str) -> bool:
        """
        requirements.txt에서 패키지 설치

        Args:
            requirements_file (str): requirements.txt 파일 경로

        Returns:
            bool: 설치 성공 여부
        """
        if not os.path.exists(requirements_file):
            print(f"✗ {requirements_file} 파일을 찾을 수 없습니다")
            return False

        try:
            print(f"설치 중: {requirements_file}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", requirements_file],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                print(f"✓ 모든 패키지 설치 완료")
                return True
            else:
                print(f"✗ 패키지 설치 실패")
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("✗ 설치 타임아웃")
            return False
        except Exception as e:
            print(f"✗ 설치 오류: {str(e)}")
            return False


def example_basic_validation():
    """기본 환경 검증 예제"""
    print("\n" + "=" * 70)
    print("예제 1: 기본 환경 검증")
    print("=" * 70)

    validator = EnvironmentValidator()
    results = validator.run_full_validation()

    print("\n결과 데이터:")
    print(json.dumps(
        {
            "python_ok": results["python_version"],
            "git_ok": results["git_installed"],
            "errors_count": len(results["errors"]),
        },
        indent=2,
    ))


def example_with_project_setup():
    """프로젝트 구조까지 포함한 환경 설정 예제"""
    print("\n" + "=" * 70)
    print("예제 2: 프로젝트 구조 생성 포함")
    print("=" * 70)

    validator = EnvironmentValidator()
    project_path = "./ai_project"

    results = validator.run_full_validation(project_path=project_path)

    if not results["errors"]:
        print("\n✓ 환경 설정 완료!")
        print(f"프로젝트 경로: {project_path}")


def example_package_check():
    """개별 패키지 확인 예제"""
    print("\n" + "=" * 70)
    print("예제 3: 개별 패키지 확인")
    print("=" * 70)

    validator = EnvironmentValidator()

    test_packages = ["requests", "langchain", "numpy", "unknown_package"]

    print("\n개별 패키지 확인:")
    print("-" * 50)

    for package in test_packages:
        is_installed, message = validator.check_package_installed(package)
        print(message)


def example_custom_validation():
    """커스텀 검증 로직 예제"""
    print("\n" + "=" * 70)
    print("예제 4: 커스텀 환경 변수 검증")
    print("=" * 70)

    # 테스트용 환경 변수 설정
    test_vars = {
        "PROJECT_NAME": "AI_Engineering",
        "LOG_LEVEL": "INFO",
        "DEBUG": "False",
    }

    print("\n환경 변수 설정:")
    print("-" * 50)

    for key, value in test_vars.items():
        os.environ[key] = value
        print(f"설정: {key}={value}")

    print("\n환경 변수 확인:")
    print("-" * 50)

    for key in test_vars.keys():
        value = os.getenv(key)
        if value:
            print(f"✓ {key}={value}")
        else:
            print(f"✗ {key} 미설정")


if __name__ == "__main__":
    """메인 실행 영역"""

    print("\n" + "#" * 70)
    print("# Week 2: 환경 설정 및 검증")
    print("#" * 70)

    # 예제 1: 기본 환경 검증
    example_basic_validation()

    # 예제 2: 프로젝트 구조 생성
    # example_with_project_setup()

    # 예제 3: 개별 패키지 확인
    example_package_check()

    # 예제 4: 커스텀 검증
    example_custom_validation()

    print("\n" + "#" * 70)
    print("# 모든 예제 완료")
    print("#" * 70)
