# Week 22: 멀티모달 분석 (Multimodal Data Analysis: CSV, Excel, PDF, Images)

## 학습 목표
- 다양한 파일 형식 자동 처리 및 통합
- PDF 텍스트/테이블 추출 및 분석
- 이미지 데이터 처리 및 메타데이터 추출
- 멀티포맷 데이터 통합 분석

## O'Reilly 리소스
- "Python Data Science Handbook" - 데이터 입출력
- "Introduction to Python for Data Analysis"
- "Computer Vision with OpenCV"
- O'Reilly PDF Processing Guide

## 핵심 개념

### 1. 다중 파일 형식 처리
```python
import pandas as pd
import numpy as np
from pathlib import Path

class DataLoader:
    def __init__(self):
        self.data = {}
        self.metadata = {}

    def load_csv(self, filepath, **kwargs):
        """CSV 파일 로드"""
        try:
            df = pd.read_csv(filepath, **kwargs)
            self.data[Path(filepath).stem] = df
            self.metadata[Path(filepath).stem] = {
                'format': 'csv',
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.to_dict()
            }
            return df
        except Exception as e:
            print(f"CSV 로드 오류: {e}")
            return None

    def load_excel(self, filepath, sheet_name=None, **kwargs):
        """Excel 파일 로드"""
        try:
            if sheet_name is None:
                xls = pd.ExcelFile(filepath)
                sheet_names = xls.sheet_names
                dfs = {}
                for sheet in sheet_names:
                    df = pd.read_excel(filepath, sheet_name=sheet, **kwargs)
                    dfs[sheet] = df
                    self.data[f"{Path(filepath).stem}_{sheet}"] = df
                return dfs
            else:
                df = pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)
                self.data[Path(filepath).stem] = df
                return df
        except Exception as e:
            print(f"Excel 로드 오류: {e}")
            return None

    def load_json(self, filepath, **kwargs):
        """JSON 파일 로드"""
        try:
            df = pd.read_json(filepath, **kwargs)
            self.data[Path(filepath).stem] = df
            return df
        except Exception as e:
            print(f"JSON 로드 오류: {e}")
            return None

    def load_parquet(self, filepath, **kwargs):
        """Parquet 파일 로드"""
        try:
            df = pd.read_parquet(filepath, **kwargs)
            self.data[Path(filepath).stem] = df
            return df
        except Exception as e:
            print(f"Parquet 로드 오류: {e}")
            return None

    def auto_load(self, filepath, **kwargs):
        """자동 형식 감지 및 로드"""
        suffix = Path(filepath).suffix.lower()

        if suffix == '.csv':
            return self.load_csv(filepath, **kwargs)
        elif suffix in ['.xlsx', '.xls']:
            return self.load_excel(filepath, **kwargs)
        elif suffix == '.json':
            return self.load_json(filepath, **kwargs)
        elif suffix == '.parquet':
            return self.load_parquet(filepath, **kwargs)
        else:
            print(f"지원하지 않는 형식: {suffix}")
            return None
```

### 2. PDF 처리
```python
import PyPDF2
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

class PDFProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pages = []
        self.tables = []
        self.text = ""

    def extract_text(self):
        """PDF에서 텍스트 추출"""
        text_content = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                text_content.append({
                    'page': page_num + 1,
                    'text': text
                })
                self.text += text + "\n"

        self.pages = text_content
        return text_content

    def extract_tables(self):
        """PDF에서 테이블 추출"""
        tables = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                if page_tables:
                    for table_idx, table in enumerate(page_tables):
                        df = pd.DataFrame(table[1:], columns=table[0])
                        tables.append({
                            'page': page_num + 1,
                            'table_index': table_idx,
                            'data': df
                        })

        self.tables = tables
        return tables

    def extract_metadata(self):
        """PDF 메타데이터 추출"""
        metadata = {}

        with pdfplumber.open(self.pdf_path) as pdf:
            metadata['total_pages'] = len(pdf.pages)
            metadata['document_info'] = pdf.metadata

        return metadata

    def extract_images(self, output_dir='./extracted_images'):
        """PDF에서 이미지 추출"""
        import os

        os.makedirs(output_dir, exist_ok=True)
        images = convert_from_path(self.pdf_path)

        image_paths = []
        for page_num, image in enumerate(images):
            image_path = f"{output_dir}/page_{page_num + 1}.png"
            image.save(image_path)
            image_paths.append(image_path)

        return image_paths

    def ocr_pdf(self):
        """OCR을 통한 스캔 PDF 처리"""
        images = convert_from_path(self.pdf_path)
        ocr_text = []

        for page_num, image in enumerate(images):
            text = pytesseract.image_to_string(image, lang='kor+eng')
            ocr_text.append({
                'page': page_num + 1,
                'text': text
            })

        return ocr_text

    def combine_tables_to_dataframe(self):
        """추출된 모든 테이블을 통합"""
        if not self.tables:
            self.extract_tables()

        combined_df = pd.concat(
            [table['data'] for table in self.tables],
            ignore_index=True
        )

        return combined_df
```

### 3. 이미지 데이터 처리
```python
import cv2
from PIL import Image
import matplotlib.pyplot as plt

class ImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.metadata = {}

    def extract_metadata(self):
        """이미지 메타데이터 추출"""
        pil_image = Image.open(self.image_path)

        self.metadata = {
            'format': pil_image.format,
            'size': pil_image.size,
            'mode': pil_image.mode,
            'exif': pil_image.getexif() if hasattr(pil_image, 'getexif') else None
        }

        return self.metadata

    def extract_features(self):
        """이미지 특성 추출"""
        # 색상 히스토그램
        hist = cv2.calcHist([self.image], [0, 1, 2], None, [256, 256, 256],
                            [0, 256, 0, 256, 0, 256])

        # 이미지 통계
        mean_color = cv2.mean(self.image)
        std_color = cv2.deviation(self.image)

        features = {
            'histogram': hist.flatten().tolist()[:100],  # 샘플
            'mean_color_bgr': list(mean_color[:3]),
            'shape': self.image.shape
        }

        return features

    def detect_objects(self):
        """객체 감지 (간단한 엣지 감지)"""
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)

        return {
            'edge_map': edges,
            'edge_count': np.count_nonzero(edges)
        }

    def analyze_text_in_image(self):
        """이미지 내 텍스트 감지 및 추출"""
        try:
            text = pytesseract.image_to_string(self.image_rgb, lang='kor+eng')
            return {'text': text}
        except Exception as e:
            return {'error': str(e)}

    def generate_summary(self):
        """이미지 종합 분석"""
        return {
            'metadata': self.extract_metadata(),
            'features': self.extract_features(),
            'objects': self.detect_objects(),
            'text': self.analyze_text_in_image()
        }
```

### 4. 멀티모달 데이터 통합
```python
class MultimodalDataIntegrator:
    def __init__(self):
        self.data_loader = DataLoader()
        self.pdf_processor = None
        self.image_processor = None
        self.integrated_data = {}

    def load_all_files(self, directory_path):
        """디렉토리의 모든 파일 로드"""
        path = Path(directory_path)

        for file in path.iterdir():
            if file.suffix.lower() in ['.csv', '.xlsx', '.xls', '.json']:
                self.data_loader.auto_load(str(file))
            elif file.suffix.lower() == '.pdf':
                pdf_proc = PDFProcessor(str(file))
                pdf_proc.extract_text()
                pdf_proc.extract_tables()
                self.integrated_data[file.stem + '_pdf'] = {
                    'text': pdf_proc.text,
                    'tables': pdf_proc.tables
                }
            elif file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                img_proc = ImageProcessor(str(file))
                self.integrated_data[file.stem + '_image'] = img_proc.generate_summary()

    def create_unified_dataframe(self):
        """모든 데이터를 통합 데이터프레임으로"""
        dfs = []

        # CSV/Excel 데이터
        for key, df in self.data_loader.data.items():
            df['source'] = key
            dfs.append(df)

        # PDF 테이블
        for key, data in self.integrated_data.items():
            if 'tables' in data:
                for table in data['tables']:
                    df = table['data'].copy()
                    df['source'] = key
                    dfs.append(df)

        if dfs:
            unified_df = pd.concat(dfs, ignore_index=True, sort=False)
            return unified_df

        return None

    def generate_multimodal_report(self):
        """멀티모달 데이터 종합 리포트"""
        report = {
            'data_sources': list(self.data_loader.data.keys()),
            'pdf_sources': [k for k in self.integrated_data.keys() if 'pdf' in k],
            'image_sources': [k for k in self.integrated_data.keys() if 'image' in k],
            'total_records': sum(len(df) for df in self.data_loader.data.values()),
            'metadata': self.data_loader.metadata
        }

        return report
```

## 실습 과제

### Task 1: 다양한 파일 형식 처리
```python
# 예시 사용
loader = DataLoader()
df_csv = loader.auto_load('data.csv')
df_excel = loader.auto_load('data.xlsx')
df_json = loader.auto_load('data.json')
```

### Task 2: PDF 자동 처리
- 텍스트 추출
- 테이블 감지 및 구조화
- OCR 처리 (스캔 문서)

### Task 3: 멀티모달 통합
```python
# 예시 사용
integrator = MultimodalDataIntegrator()
integrator.load_all_files('./data_directory')
unified_df = integrator.create_unified_dataframe()
report = integrator.generate_multimodal_report()
```

## 주간 체크포인트

- [ ] CSV/Excel/JSON/Parquet 로드 구현
- [ ] 자동 형식 감지 기능
- [ ] PDF 텍스트 추출
- [ ] PDF 테이블 추출 및 구조화
- [ ] 이미지 메타데이터 추출
- [ ] 이미지 특성 추출
- [ ] 멀티모달 데이터 통합
- [ ] 통합 리포트 생성

## 학습 성과 기준
- [ ] 10개 이상 파일 형식 처리 성공률 > 95%
- [ ] PDF 테이블 추출 정확도 > 85%
- [ ] 멀티모달 데이터 통합 완결성 > 90%
