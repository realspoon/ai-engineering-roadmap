"""
Week 7: RAG 기초 - 완전한 RAG 파이프라인
=========================================
문서 로딩 → 청킹 → 임베딩 → 검색 → 생성

실행 전:
pip install langchain langchain-openai langchain-community
pip install chromadb sentence-transformers pypdf
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    DirectoryLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()


# ============================================
# 1. Document Loading (문서 로딩)
# ============================================

def load_documents(file_path: str) -> list:
    """
    파일 확장자에 따라 적절한 로더 사용

    지원 형식: .txt, .pdf, .md
    """
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.txt') or file_path.endswith('.md'):
        loader = TextLoader(file_path, encoding='utf-8')
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    documents = loader.load()
    print(f"로드된 문서 수: {len(documents)}")
    return documents


def load_directory(dir_path: str, glob_pattern: str = "**/*.txt") -> list:
    """
    디렉토리의 모든 문서 로딩
    """
    loader = DirectoryLoader(
        dir_path,
        glob=glob_pattern,
        loader_cls=TextLoader
    )
    documents = loader.load()
    print(f"로드된 문서 수: {len(documents)}")
    return documents


# ============================================
# 2. Text Splitting (청킹)
# ============================================

def split_documents(documents: list, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """
    문서를 적절한 크기의 청크로 분할

    Args:
        chunk_size: 청크 최대 크기 (문자 수)
        chunk_overlap: 청크 간 겹치는 부분 (문맥 유지)
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )

    chunks = text_splitter.split_documents(documents)
    print(f"생성된 청크 수: {len(chunks)}")
    return chunks


# ============================================
# 3. Embedding & Vector Store
# ============================================

def create_vectorstore(chunks: list, persist_directory: str = "./chroma_db") -> Chroma:
    """
    청크를 임베딩하고 벡터 스토어에 저장
    """
    # OpenAI 임베딩 모델
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Chroma 벡터 스토어 생성
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    print(f"벡터 스토어 생성 완료: {persist_directory}")
    return vectorstore


def load_vectorstore(persist_directory: str = "./chroma_db") -> Chroma:
    """
    기존 벡터 스토어 로드
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    print(f"벡터 스토어 로드 완료: {persist_directory}")
    return vectorstore


# ============================================
# 4. Retriever 설정
# ============================================

def create_retriever(vectorstore: Chroma, k: int = 4, search_type: str = "similarity"):
    """
    검색기 생성

    Args:
        k: 반환할 문서 수
        search_type: "similarity" 또는 "mmr" (다양성 고려)
    """
    if search_type == "mmr":
        # MMR: 관련성과 다양성의 균형
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": k, "fetch_k": k * 2}
        )
    else:
        # 기본 유사도 검색
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

    return retriever


# ============================================
# 5. RAG Chain 구성
# ============================================

def create_rag_chain(retriever):
    """
    완전한 RAG Chain 생성
    """
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # RAG 프롬프트 템플릿
    template = """당신은 주어진 컨텍스트를 기반으로 질문에 답변하는 AI 어시스턴트입니다.

컨텍스트에서 답을 찾을 수 없는 경우, "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답하세요.
추측하거나 컨텍스트에 없는 정보를 만들어내지 마세요.

## 컨텍스트
{context}

## 질문
{question}

## 답변"""

    prompt = ChatPromptTemplate.from_template(template)

    # 컨텍스트 포맷팅 함수
    def format_docs(docs):
        return "\n\n---\n\n".join(
            f"[출처: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}"
            for doc in docs
        )

    # RAG Chain 구성 (LCEL)
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | model
        | StrOutputParser()
    )

    return rag_chain


# ============================================
# 6. 완전한 RAG 시스템 클래스
# ============================================

class SimpleRAG:
    """
    간단한 RAG 시스템 구현
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.retriever = None
        self.chain = None
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def index_documents(self, file_paths: list[str], chunk_size: int = 1000):
        """
        문서 인덱싱 (오프라인 단계)
        """
        all_chunks = []

        for file_path in file_paths:
            print(f"Processing: {file_path}")

            # 1. 문서 로드
            documents = load_documents(file_path)

            # 2. 청크 분할
            chunks = split_documents(documents, chunk_size=chunk_size)
            all_chunks.extend(chunks)

        # 3. 벡터 스토어 생성
        self.vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )

        # 4. 검색기 및 Chain 초기화
        self._initialize_chain()

        print(f"인덱싱 완료: {len(all_chunks)} 청크")

    def load(self):
        """
        기존 인덱스 로드
        """
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        self._initialize_chain()
        print("인덱스 로드 완료")

    def _initialize_chain(self):
        """
        검색기와 Chain 초기화
        """
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )
        self.chain = create_rag_chain(self.retriever)

    def query(self, question: str) -> str:
        """
        질문에 대한 답변 생성
        """
        if self.chain is None:
            raise ValueError("먼저 index_documents() 또는 load()를 호출하세요")

        return self.chain.invoke(question)

    def search(self, query: str, k: int = 4) -> list:
        """
        관련 문서 검색 (답변 생성 없이)
        """
        return self.vectorstore.similarity_search(query, k=k)


# ============================================
# 7. 샘플 문서 생성 및 테스트
# ============================================

def create_sample_documents():
    """테스트용 샘플 문서 생성"""

    sample_docs = {
        "company_policy.txt": """
# 회사 휴가 정책

## 연차 휴가
- 입사 1년 미만: 11일
- 입사 1년 이상: 15일
- 입사 3년 이상: 20일

## 병가
- 연간 최대 30일까지 유급 병가 사용 가능
- 3일 이상 연속 병가 시 진단서 필요

## 특별 휴가
- 결혼: 5일
- 출산: 배우자 10일
- 가족 사망: 3-5일
        """,

        "product_manual.txt": """
# 제품 사용 설명서

## 제품 개요
AI 데이터 분석 도구 v2.0은 자연어로 데이터를 분석할 수 있는 혁신적인 솔루션입니다.

## 주요 기능
1. 자연어 질의: 한국어로 질문하면 SQL 없이 데이터 분석
2. 자동 시각화: 분석 결과를 자동으로 차트로 변환
3. 인사이트 생성: AI가 핵심 인사이트를 자동 도출

## 시스템 요구사항
- Python 3.10 이상
- 메모리: 최소 8GB RAM
- 저장공간: 2GB 이상

## 설치 방법
pip install ai-data-analyzer
        """,

        "faq.txt": """
# 자주 묻는 질문 (FAQ)

Q: 무료 체험이 가능한가요?
A: 네, 14일간 모든 기능을 무료로 체험할 수 있습니다.

Q: 데이터는 어디에 저장되나요?
A: 모든 데이터는 AWS 서울 리전에 암호화되어 저장됩니다.

Q: 최대 처리 가능한 데이터 크기는?
A: Pro 플랜 기준 100GB까지 지원합니다.

Q: API 연동이 가능한가요?
A: 네, REST API와 Python SDK를 제공합니다.

Q: 고객 지원은 어떻게 받나요?
A: support@example.com 또는 실시간 채팅으로 문의 가능합니다.
        """
    }

    # 파일 생성
    os.makedirs("./sample_docs", exist_ok=True)
    file_paths = []

    for filename, content in sample_docs.items():
        filepath = f"./sample_docs/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        file_paths.append(filepath)

    return file_paths


# ============================================
# 실행 예제
# ============================================

if __name__ == "__main__":
    # 1. 샘플 문서 생성
    print("=== 샘플 문서 생성 ===")
    file_paths = create_sample_documents()
    print(f"생성된 파일: {file_paths}\n")

    # 2. RAG 시스템 초기화 및 인덱싱
    print("=== RAG 시스템 초기화 ===")
    rag = SimpleRAG(persist_directory="./sample_chroma_db")
    rag.index_documents(file_paths, chunk_size=500)
    print()

    # 3. 질의 테스트
    print("=== 질의 테스트 ===")

    questions = [
        "입사 2년차 직원의 연차 휴가는 며칠인가요?",
        "제품의 시스템 요구사항은 무엇인가요?",
        "무료 체험 기간은 얼마나 되나요?",
        "데이터는 어디에 저장되나요?",
    ]

    for q in questions:
        print(f"\nQ: {q}")
        answer = rag.query(q)
        print(f"A: {answer}")
        print("-" * 50)

    # 4. 관련 문서 검색 테스트
    print("\n=== 관련 문서 검색 ===")
    docs = rag.search("휴가 정책", k=2)
    for i, doc in enumerate(docs, 1):
        print(f"\n[문서 {i}]")
        print(f"출처: {doc.metadata.get('source', 'Unknown')}")
        print(f"내용: {doc.page_content[:200]}...")
