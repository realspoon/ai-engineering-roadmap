"""
Week 12: Custom Tools Implementation
API, 파일, 데이터베이스 연동 등 다양한 Custom Tool 구현
"""

import json
import os
import sqlite3
import requests
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
import csv
from io import StringIO


@dataclass
class ToolResult:
    """도구 실행 결과"""
    success: bool
    data: Any
    message: str
    timestamp: str


class BaseTool(ABC):
    """도구의 기본 클래스"""

    def __init__(self, name: str, description: str, version: str = "1.0"):
        self.name = name
        self.description = description
        self.version = version
        self.call_count = 0

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """도구 실행"""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """JSON Schema 형식의 도구 정의"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "parameters": {}
        }

    def get_info(self) -> Dict[str, Any]:
        """도구 정보"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "call_count": self.call_count
        }


class APITool(BaseTool):
    """HTTP API 호출 도구"""

    def __init__(self, name: str = "api_client", base_url: str = ""):
        super().__init__(
            name,
            "RESTful API를 호출합니다",
            "1.0"
        )
        self.base_url = base_url
        self.session = requests.Session()

    def execute(self, method: str = "GET", endpoint: str = "", params: Dict = None,
                data: Dict = None, headers: Dict = None) -> ToolResult:
        """API 호출 실행"""
        self.call_count += 1

        try:
            url = f"{self.base_url}{endpoint}" if self.base_url else endpoint

            # 기본 헤더 설정
            default_headers = {"Content-Type": "application/json"}
            if headers:
                default_headers.update(headers)

            # HTTP 요청
            if method.upper() == "GET":
                response = self.session.get(url, params=params, headers=default_headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=default_headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=default_headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=default_headers)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")

            response.raise_for_status()

            # 응답 파싱
            try:
                response_data = response.json()
            except:
                response_data = response.text

            return ToolResult(
                success=True,
                data=response_data,
                message=f"API 호출 성공 (상태 코드: {response.status_code})",
                timestamp=datetime.now().isoformat()
            )

        except requests.exceptions.RequestException as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"API 호출 실패: {str(e)}",
                timestamp=datetime.now().isoformat()
            )

    def get_schema(self) -> Dict[str, Any]:
        """API Tool의 JSON Schema"""
        schema = super().get_schema()
        schema["parameters"] = {
            "method": {
                "type": "string",
                "description": "HTTP 메서드 (GET, POST, PUT, DELETE)",
                "enum": ["GET", "POST", "PUT", "DELETE"]
            },
            "endpoint": {
                "type": "string",
                "description": "API 엔드포인트"
            },
            "params": {
                "type": "object",
                "description": "쿼리 파라미터"
            },
            "data": {
                "type": "object",
                "description": "요청 바디 데이터"
            }
        }
        return schema


class FileTool(BaseTool):
    """파일 조작 도구"""

    def __init__(self, name: str = "file_manager", base_path: str = "./"):
        super().__init__(
            name,
            "파일을 읽고 쓰고 관리합니다",
            "1.0"
        )
        self.base_path = base_path

    def execute(self, operation: str = "read", filepath: str = "", content: str = "",
                append: bool = False) -> ToolResult:
        """파일 작업 실행"""
        self.call_count += 1

        try:
            full_path = os.path.join(self.base_path, filepath)

            if operation.lower() == "read":
                if not os.path.exists(full_path):
                    return ToolResult(
                        success=False,
                        data=None,
                        message=f"파일을 찾을 수 없습니다: {filepath}",
                        timestamp=datetime.now().isoformat()
                    )

                with open(full_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()

                return ToolResult(
                    success=True,
                    data=file_content,
                    message=f"파일 읽기 성공: {filepath}",
                    timestamp=datetime.now().isoformat()
                )

            elif operation.lower() == "write":
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                mode = 'a' if append else 'w'

                with open(full_path, mode, encoding='utf-8') as f:
                    f.write(content)

                return ToolResult(
                    success=True,
                    data={"filepath": filepath, "bytes_written": len(content.encode('utf-8'))},
                    message=f"파일 쓰기 성공: {filepath}",
                    timestamp=datetime.now().isoformat()
                )

            elif operation.lower() == "list":
                if not os.path.exists(full_path):
                    return ToolResult(
                        success=False,
                        data=None,
                        message=f"디렉토리를 찾을 수 없습니다: {filepath}",
                        timestamp=datetime.now().isoformat()
                    )

                files = os.listdir(full_path)
                return ToolResult(
                    success=True,
                    data=files,
                    message=f"디렉토리 목록 조회 성공: {len(files)}개 항목",
                    timestamp=datetime.now().isoformat()
                )

            elif operation.lower() == "delete":
                if os.path.exists(full_path):
                    os.remove(full_path)
                    return ToolResult(
                        success=True,
                        data={"deleted": filepath},
                        message=f"파일 삭제 성공: {filepath}",
                        timestamp=datetime.now().isoformat()
                    )
                else:
                    return ToolResult(
                        success=False,
                        data=None,
                        message=f"파일을 찾을 수 없습니다: {filepath}",
                        timestamp=datetime.now().isoformat()
                    )

            else:
                return ToolResult(
                    success=False,
                    data=None,
                    message=f"지원하지 않는 작업: {operation}",
                    timestamp=datetime.now().isoformat()
                )

        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"파일 작업 실패: {str(e)}",
                timestamp=datetime.now().isoformat()
            )

    def get_schema(self) -> Dict[str, Any]:
        """FileTool의 JSON Schema"""
        schema = super().get_schema()
        schema["parameters"] = {
            "operation": {
                "type": "string",
                "description": "파일 작업 (read, write, list, delete)",
                "enum": ["read", "write", "list", "delete"]
            },
            "filepath": {
                "type": "string",
                "description": "파일 경로"
            },
            "content": {
                "type": "string",
                "description": "쓰기 작업 시 파일 내용"
            },
            "append": {
                "type": "boolean",
                "description": "추가 모드 여부"
            }
        }
        return schema


class DatabaseTool(BaseTool):
    """SQLite 데이터베이스 도구"""

    def __init__(self, name: str = "database_manager", db_path: str = ":memory:"):
        super().__init__(
            name,
            "SQLite 데이터베이스를 관리합니다",
            "1.0"
        )
        self.db_path = db_path
        self.conn = None
        self._connect()

    def _connect(self):
        """데이터베이스 연결"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def execute(self, query: str = "", operation: str = "execute",
                params: List = None) -> ToolResult:
        """데이터베이스 작업 실행"""
        self.call_count += 1

        try:
            if operation.lower() == "execute":
                cursor = self.conn.cursor()
                cursor.execute(query, params or [])
                self.conn.commit()

                return ToolResult(
                    success=True,
                    data={"rows_affected": cursor.rowcount},
                    message=f"쿼리 실행 성공 ({cursor.rowcount}행 영향)",
                    timestamp=datetime.now().isoformat()
                )

            elif operation.lower() == "query":
                cursor = self.conn.cursor()
                cursor.execute(query, params or [])
                rows = cursor.fetchall()

                # Row 객체를 딕셔너리로 변환
                results = [dict(row) for row in rows]

                return ToolResult(
                    success=True,
                    data=results,
                    message=f"쿼리 실행 성공 ({len(results)}행 반환)",
                    timestamp=datetime.now().isoformat()
                )

            elif operation.lower() == "create_table":
                cursor = self.conn.cursor()
                cursor.execute(query)
                self.conn.commit()

                return ToolResult(
                    success=True,
                    data={"table_created": True},
                    message="테이블 생성 성공",
                    timestamp=datetime.now().isoformat()
                )

            else:
                return ToolResult(
                    success=False,
                    data=None,
                    message=f"지원하지 않는 작업: {operation}",
                    timestamp=datetime.now().isoformat()
                )

        except sqlite3.Error as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"데이터베이스 오류: {str(e)}",
                timestamp=datetime.now().isoformat()
            )

    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()

    def get_schema(self) -> Dict[str, Any]:
        """DatabaseTool의 JSON Schema"""
        schema = super().get_schema()
        schema["parameters"] = {
            "query": {
                "type": "string",
                "description": "SQL 쿼리"
            },
            "operation": {
                "type": "string",
                "description": "작업 유형 (execute, query, create_table)",
                "enum": ["execute", "query", "create_table"]
            },
            "params": {
                "type": "array",
                "description": "쿼리 파라미터"
            }
        }
        return schema


class CSVTool(BaseTool):
    """CSV 파일 도구"""

    def __init__(self, name: str = "csv_manager"):
        super().__init__(
            name,
            "CSV 파일을 읽고 쓰고 변환합니다",
            "1.0"
        )

    def execute(self, operation: str = "read", filepath: str = "", data: List[Dict] = None,
                delimiter: str = ",") -> ToolResult:
        """CSV 작업 실행"""
        self.call_count += 1

        try:
            if operation.lower() == "read":
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter=delimiter)
                    rows = [dict(row) for row in reader]

                return ToolResult(
                    success=True,
                    data=rows,
                    message=f"CSV 파일 읽기 성공 ({len(rows)}행)",
                    timestamp=datetime.now().isoformat()
                )

            elif operation.lower() == "write":
                if not data:
                    return ToolResult(
                        success=False,
                        data=None,
                        message="쓰기 작업에는 데이터가 필요합니다",
                        timestamp=datetime.now().isoformat()
                    )

                fieldnames = list(data[0].keys())

                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
                    writer.writeheader()
                    writer.writerows(data)

                return ToolResult(
                    success=True,
                    data={"rows_written": len(data)},
                    message=f"CSV 파일 쓰기 성공 ({len(data)}행)",
                    timestamp=datetime.now().isoformat()
                )

            elif operation.lower() == "convert_to_json":
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter=delimiter)
                    rows = [dict(row) for row in reader]

                json_str = json.dumps(rows, ensure_ascii=False, indent=2)

                return ToolResult(
                    success=True,
                    data=json_str,
                    message=f"CSV를 JSON으로 변환 성공 ({len(rows)}행)",
                    timestamp=datetime.now().isoformat()
                )

            else:
                return ToolResult(
                    success=False,
                    data=None,
                    message=f"지원하지 않는 작업: {operation}",
                    timestamp=datetime.now().isoformat()
                )

        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"CSV 작업 실패: {str(e)}",
                timestamp=datetime.now().isoformat()
            )

    def get_schema(self) -> Dict[str, Any]:
        """CSVTool의 JSON Schema"""
        schema = super().get_schema()
        schema["parameters"] = {
            "operation": {
                "type": "string",
                "description": "CSV 작업 (read, write, convert_to_json)",
                "enum": ["read", "write", "convert_to_json"]
            },
            "filepath": {
                "type": "string",
                "description": "CSV 파일 경로"
            },
            "data": {
                "type": "array",
                "description": "쓰기 작업 시 데이터 (딕셔너리 배열)"
            },
            "delimiter": {
                "type": "string",
                "description": "구분자 (기본값: 쉼표)"
            }
        }
        return schema


class ToolKit:
    """도구 모음 관리자"""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool) -> None:
        """도구 등록"""
        self.tools[tool.name] = tool

    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """도구 실행"""
        tool = self.tools.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                data=None,
                message=f"도구를 찾을 수 없습니다: {tool_name}",
                timestamp=datetime.now().isoformat()
            )

        return tool.execute(**kwargs)

    def list_tools(self) -> Dict[str, Any]:
        """등록된 도구 목록"""
        return {
            name: {
                "name": tool.name,
                "description": tool.description,
                "version": tool.version,
                "call_count": tool.call_count
            }
            for name, tool in self.tools.items()
        }

    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """도구 스키마 조회"""
        tool = self.tools.get(tool_name)
        if not tool:
            return None
        return tool.get_schema()


def main():
    """메인 함수"""

    print("="*60)
    print("Custom Tools 데모")
    print("="*60)

    # ToolKit 생성
    toolkit = ToolKit()

    # API Tool 등록
    api_tool = APITool(base_url="https://jsonplaceholder.typicode.com")
    toolkit.register_tool(api_tool)

    # File Tool 등록
    file_tool = FileTool()
    toolkit.register_tool(file_tool)

    # Database Tool 등록
    db_tool = DatabaseTool(db_path=":memory:")
    toolkit.register_tool(db_tool)

    # CSV Tool 등록
    csv_tool = CSVTool()
    toolkit.register_tool(csv_tool)

    # 등록된 도구 목록
    print("\n등록된 도구:")
    for tool_name, info in toolkit.list_tools().items():
        print(f"  - {info['name']}: {info['description']}")

    # Database 도구 테스트
    print("\n[Database Tool 테스트]")
    create_result = db_tool.execute(
        query="CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)",
        operation="create_table"
    )
    print(f"테이블 생성: {create_result.message}")

    insert_result = db_tool.execute(
        query="INSERT INTO users (name, email) VALUES (?, ?)",
        operation="execute",
        params=["Alice", "alice@example.com"]
    )
    print(f"데이터 삽입: {insert_result.message}")

    query_result = db_tool.execute(
        query="SELECT * FROM users",
        operation="query"
    )
    print(f"데이터 조회: {query_result.message}")
    print(f"결과: {json.dumps(query_result.data, ensure_ascii=False, indent=2)}")

    # File Tool 테스트
    print("\n[File Tool 테스트]")
    write_result = file_tool.execute(
        operation="write",
        filepath="test.txt",
        content="Custom Tools 테스트 파일\n이것은 샘플 파일입니다."
    )
    print(f"파일 쓰기: {write_result.message}")

    read_result = file_tool.execute(
        operation="read",
        filepath="test.txt"
    )
    print(f"파일 읽기: {read_result.message}")
    print(f"내용: {read_result.data[:50]}...")

    # CSV Tool 테스트
    print("\n[CSV Tool 테스트]")
    csv_data = [
        {"이름": "Alice", "직급": "엔지니어", "급여": "80000"},
        {"이름": "Bob", "직급": "매니저", "급여": "90000"},
        {"이름": "Charlie", "직급": "개발자", "급여": "75000"}
    ]
    csv_write_result = csv_tool.execute(
        operation="write",
        filepath="employees.csv",
        data=csv_data
    )
    print(f"CSV 쓰기: {csv_write_result.message}")

    # 도구 통계
    print("\n[도구 통계]")
    for tool_name, tool in toolkit.tools.items():
        print(f"  {tool_name}: {tool.call_count}번 호출")

    # 정리
    if db_tool.conn:
        db_tool.close()


if __name__ == "__main__":
    main()
