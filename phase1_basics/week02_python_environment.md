# Week 2: Python 환경 및 필수 라이브러리

## 🎯 학습 목표

1. AI 개발을 위한 Python 환경 구축
2. 가상환경 관리 (venv, conda)
3. 핵심 라이브러리 (pandas, numpy) 복습
4. 개발 환경 (Jupyter, VSCode) 설정

---

## 📚 O'Reilly 리소스

| 유형 | 제목 | 저자 | 학습 범위 |
|------|------|------|----------|
| 📚 Book | [Python for Data Analysis, 3rd Ed](https://www.oreilly.com/library/view/python-for-data/9781098104023/) | Wes McKinney | Chapter 4-7 |
| 📚 Book | [Fluent Python, 2nd Ed](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) | Luciano Ramalho | Chapter 1-2 |

---

## 📖 핵심 개념

### 1. 가상환경 관리

```bash
# venv 사용
python -m venv ai_env
source ai_env/bin/activate  # Linux/Mac
ai_env\Scripts\activate     # Windows

# conda 사용
conda create -n ai_env python=3.11
conda activate ai_env
```

### 2. 필수 패키지

```bash
# requirements.txt
langchain>=0.2.0
langchain-openai>=0.1.0
langchain-community>=0.2.0
openai>=1.0.0
anthropic>=0.20.0
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0
jupyter>=1.0.0
```

### 3. 프로젝트 구조

```
my_ai_project/
├── .env                 # API 키 (git 제외)
├── .gitignore
├── requirements.txt
├── src/
│   ├── __init__.py
│   └── main.py
├── notebooks/
│   └── exploration.ipynb
└── tests/
    └── test_main.py
```

---

## 💻 실습 과제

### 과제 1: 환경 설정 자동화

```python
# setup_check.py
import sys

def check_environment():
    """환경 설정 검증"""
    print(f"Python: {sys.version}")

    required = ['pandas', 'numpy', 'openai', 'langchain']
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✓ {pkg} 설치됨")
        except ImportError:
            print(f"✗ {pkg} 미설치")

if __name__ == "__main__":
    check_environment()
```

### 과제 2: pandas 데이터 분석 복습

```python
import pandas as pd
import numpy as np

# 데이터 로딩
df = pd.read_csv('data.csv')

# 기본 탐색
df.head()
df.info()
df.describe()

# 데이터 정제
df.dropna()
df.fillna(method='ffill')
df.drop_duplicates()

# 그룹 분석
df.groupby('category').agg({'sales': ['sum', 'mean']})
```

### 과제 3: Jupyter Notebook 설정

- Jupyter Lab 설치 및 실행
- 확장 프로그램 설치
- 커널 관리

---

## ✅ 주간 체크포인트

```
□ 가상환경 생성 및 활성화 가능
□ requirements.txt로 패키지 일괄 설치 가능
□ .env 파일로 환경변수 관리 가능
□ pandas로 기본 데이터 분석 가능
□ Jupyter Notebook 활용 가능
```

---

[← Week 1](./week01_llm_fundamentals.md) | [Week 3 →](./week03_prompt_basics.md)
