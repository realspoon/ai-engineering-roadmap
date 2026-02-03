"""
Data Loader Module
다양한 파일 형식(CSV, Excel, JSON, PDF)을 로드하는 통합 데이터 로더
"""

import pandas as pd
import json
import PyPDF2
from typing import Union, Dict, Any, List
import os
from pathlib import Path
import logging
from abc import ABC, abstractmethod

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoaderBase(ABC):
    """데이터 로더 기본 클래스"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

    @abstractmethod
    def load(self) -> pd.DataFrame:
        """데이터 로드 (구현 필수)"""
        pass

    def validate(self) -> bool:
        """파일 유효성 검사"""
        return self.file_path.exists() and self.file_path.stat().st_size > 0


class CSVLoader(DataLoaderBase):
    """CSV 파일 로더"""

    def load(self, encoding: str = 'utf-8', **kwargs) -> pd.DataFrame:
        """CSV 파일 로드"""
        try:
            logger.info(f"CSV 파일 로드 중: {self.file_path}")
            df = pd.read_csv(self.file_path, encoding=encoding, **kwargs)
            logger.info(f"성공: {len(df)} 행, {len(df.columns)} 열 로드됨")
            return df
        except Exception as e:
            logger.error(f"CSV 로드 실패: {str(e)}")
            raise


class ExcelLoader(DataLoaderBase):
    """Excel 파일 로더"""

    def load(self, sheet_name: Union[str, int] = 0, **kwargs) -> pd.DataFrame:
        """Excel 파일 로드"""
        try:
            logger.info(f"Excel 파일 로드 중: {self.file_path}")
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, **kwargs)
            logger.info(f"성공: {len(df)} 행, {len(df.columns)} 열 로드됨")
            return df
        except Exception as e:
            logger.error(f"Excel 로드 실패: {str(e)}")
            raise

    def get_sheet_names(self) -> List[str]:
        """Excel 파일의 모든 시트명 반환"""
        try:
            xls = pd.ExcelFile(self.file_path)
            return xls.sheet_names
        except Exception as e:
            logger.error(f"시트명 조회 실패: {str(e)}")
            raise


class JSONLoader(DataLoaderBase):
    """JSON 파일 로더"""

    def load(self, **kwargs) -> Union[pd.DataFrame, Dict[str, Any]]:
        """JSON 파일 로드"""
        try:
            logger.info(f"JSON 파일 로드 중: {self.file_path}")

            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 딕셔너리 리스트인 경우 DataFrame으로 변환
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                df = pd.DataFrame(data)
                logger.info(f"성공: {len(df)} 행, {len(df.columns)} 열 로드됨")
                return df
            elif isinstance(data, dict):
                logger.info("JSON 데이터를 딕셔너리로 반환합니다")
                return data
            else:
                raise ValueError("지원하지 않는 JSON 형식입니다")
        except Exception as e:
            logger.error(f"JSON 로드 실패: {str(e)}")
            raise


class PDFLoader(DataLoaderBase):
    """PDF 파일 로더"""

    def load(self, extract_text: bool = True, extract_tables: bool = False) -> Dict[str, Any]:
        """PDF 파일 로드"""
        try:
            logger.info(f"PDF 파일 로드 중: {self.file_path}")

            result = {
                'file_path': str(self.file_path),
                'total_pages': 0,
                'text': '',
                'tables': []
            }

            with open(self.file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                result['total_pages'] = len(pdf_reader.pages)

                if extract_text:
                    text_content = []
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        text_content.append(text)
                    result['text'] = '\n'.join(text_content)

                logger.info(f"성공: {result['total_pages']} 페이지 로드됨")

            return result
        except Exception as e:
            logger.error(f"PDF 로드 실패: {str(e)}")
            raise


class DataLoaderFactory:
    """데이터 로더 팩토리 클래스"""

    _loaders = {
        '.csv': CSVLoader,
        '.xlsx': ExcelLoader,
        '.xls': ExcelLoader,
        '.json': JSONLoader,
        '.pdf': PDFLoader
    }

    @classmethod
    def create_loader(cls, file_path: str) -> DataLoaderBase:
        """파일 형식에 따라 적절한 로더 생성"""
        file_extension = Path(file_path).suffix.lower()

        if file_extension not in cls._loaders:
            raise ValueError(f"지원하지 않는 파일 형식: {file_extension}")

        loader_class = cls._loaders[file_extension]
        return loader_class(file_path)


class UniversalDataLoader:
    """통합 데이터 로더"""

    def __init__(self):
        self.loaded_data = {}

    def load_file(self, file_path: str, **kwargs) -> Union[pd.DataFrame, Dict[str, Any]]:
        """파일을 자동 형식 감지하여 로드"""
        try:
            loader = DataLoaderFactory.create_loader(file_path)
            data = loader.load(**kwargs)

            # 로드된 데이터 저장
            file_name = Path(file_path).name
            self.loaded_data[file_name] = data

            return data
        except Exception as e:
            logger.error(f"파일 로드 실패: {str(e)}")
            raise

    def load_multiple_files(self, directory: str, pattern: str = '*') -> Dict[str, Any]:
        """디렉토리에서 여러 파일 로드"""
        directory_path = Path(directory)

        if not directory_path.is_dir():
            raise NotADirectoryError(f"디렉토리가 아닙니다: {directory}")

        results = {}

        for file_path in directory_path.glob(pattern):
            if file_path.is_file():
                try:
                    logger.info(f"로딩 중: {file_path.name}")
                    data = self.load_file(str(file_path))
                    results[file_path.name] = data
                except Exception as e:
                    logger.warning(f"파일 로드 스킵: {file_path.name} - {str(e)}")

        return results

    def get_data_info(self, file_name: str) -> Dict[str, Any]:
        """로드된 데이터의 정보 반환"""
        if file_name not in self.loaded_data:
            raise KeyError(f"로드되지 않은 파일: {file_name}")

        data = self.loaded_data[file_name]

        if isinstance(data, pd.DataFrame):
            return {
                'type': 'DataFrame',
                'rows': len(data),
                'columns': len(data.columns),
                'column_names': data.columns.tolist(),
                'dtypes': data.dtypes.to_dict(),
                'memory_usage': data.memory_usage(deep=True).sum() / 1024**2  # MB
            }
        else:
            return {
                'type': type(data).__name__,
                'keys': list(data.keys()) if isinstance(data, dict) else None
            }


# 사용 예제
if __name__ == "__main__":
    # 샘플 데이터 생성
    sample_data = {
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'salary': [50000, 60000, 70000]
    }

    # CSV 샘플 파일 생성
    df_sample = pd.DataFrame(sample_data)
    csv_path = '/tmp/sample.csv'
    df_sample.to_csv(csv_path, index=False)

    # 데이터 로더 테스트
    loader = UniversalDataLoader()

    # CSV 파일 로드
    print("=== CSV 파일 로드 ===")
    df = loader.load_file(csv_path)
    print(df)
    print()

    # 데이터 정보 조회
    print("=== 데이터 정보 ===")
    info = loader.get_data_info('sample.csv')
    print(json.dumps(info, indent=2, ensure_ascii=False))
