"""
Week 16: RAG Assistant - Streamlit Main Application
Streamlit 기반의 RAG 어시스턴트 사용자 인터페이스
"""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime

from .config import Config, get_config, ConfigManager
from .agent import RAGAgent, Document


# 로깅 설정
logger = logging.getLogger(__name__)


class StreamlitRAGApp:
    """Streamlit RAG 애플리케이션"""

    def __init__(self):
        self.config: Config = get_config()
        self.agent: RAGAgent = RAGAgent(self.config)
        self.conversation_history: List[Dict[str, Any]] = []
        self.documents_loaded: bool = False

    def initialize(self) -> None:
        """애플리케이션 초기화"""
        logger.info("Initializing Streamlit RAG App")

        # 문서 로드 시도
        try:
            chunks = self.agent.load_documents_from_directory()
            if chunks > 0:
                self.documents_loaded = True
                logger.info(f"Loaded {chunks} chunks from documents")
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")

    def render_header(self) -> None:
        """헤더 렌더링"""
        # Streamlit을 사용하지 않고 텍스트 기반으로 구현
        print("="*60)
        print("🤖 RAG Assistant - Streamlit Application")
        print("="*60)
        print(f"Environment: {self.config.environment}")
        print(f"Debug Mode: {self.config.debug}")

    def render_sidebar(self) -> Dict[str, Any]:
        """사이드바 렌더링"""
        print("\n[Sidebar Controls]")

        sidebar_state = {
            "show_stats": True,
            "show_settings": False,
            "show_docs": True,
            "top_k": self.config.rag.top_k,
            "similarity_threshold": self.config.rag.similarity_threshold
        }

        print(f"Top K Results: {sidebar_state['top_k']}")
        print(f"Similarity Threshold: {sidebar_state['similarity_threshold']}")

        return sidebar_state

    def render_main_content(self) -> None:
        """메인 콘텐츠 렌더링"""
        print("\n[Main Content]")

        if not self.documents_loaded:
            print("⚠️  No documents loaded yet. Please add documents to get started.")
            return

        print(f"✓ Documents loaded successfully")
        print(f"  - Total documents: {self.agent.get_stats()['total_documents']}")
        print(f"  - Total chunks: {self.agent.get_stats()['total_chunks']}")

    def render_chat_interface(self) -> None:
        """채팅 인터페이스 렌더링"""
        print("\n[Chat Interface]")
        print("Simulating chat interaction...")

        # 샘플 대화
        sample_queries = [
            "Python이란 무엇인가?",
            "머신러닝 기초",
            "RAG는 어떻게 작동하나요?"
        ]

        for i, query in enumerate(sample_queries, 1):
            print(f"\n{i}. User: {query}")

            response = self.agent.generate_response(query)
            print(f"   Assistant: {response['response'][:100]}...")

            self.conversation_history.append({
                "type": "user",
                "content": query,
                "timestamp": datetime.now().isoformat()
            })

            self.conversation_history.append({
                "type": "assistant",
                "content": response['response'],
                "timestamp": datetime.now().isoformat()
            })

    def render_stats(self) -> None:
        """통계 렌더링"""
        print("\n[Statistics]")

        stats = self.agent.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    def render_settings(self) -> None:
        """설정 렌더링"""
        print("\n[Settings]")

        print(f"Vector DB Type: {self.config.vector_db.type.value}")
        print(f"Embedding Model: {self.config.embedding.model.value}")
        print(f"Chunk Size: {self.config.rag.chunk_size}")
        print(f"Top K: {self.config.rag.top_k}")
        print(f"Cache Enabled: {self.config.rag.enable_cache}")

    def render_documents_panel(self) -> None:
        """문서 패널 렌더링"""
        print("\n[Documents Panel]")

        if not self.agent.documents:
            print("No documents loaded yet.")
            return

        print(f"Total documents: {len(self.agent.documents)}")
        print("\nDocument list:")
        for doc_id, doc in list(self.agent.documents.items())[:5]:
            print(f"  - {doc.source} ({len(doc.content)} characters)")

        if len(self.agent.documents) > 5:
            print(f"  ... and {len(self.agent.documents) - 5} more documents")

    def upload_documents(self, files: List[str]) -> int:
        """문서 업로드"""
        print(f"\nUploading {len(files)} files...")

        documents = []
        for filename in files:
            try:
                # 파일 내용 시뮬레이션
                content = f"Sample content from {filename}"
                doc = Document(
                    id=filename.replace('.', '_'),
                    content=content,
                    source=filename
                )
                documents.append(doc)
            except Exception as e:
                logger.error(f"Error uploading {filename}: {str(e)}")

        if documents:
            chunks = self.agent.add_documents(documents)
            print(f"✓ Successfully uploaded {len(documents)} documents ({chunks} chunks)")
            self.documents_loaded = True
            return chunks

        return 0

    def process_query(self, query: str) -> Dict[str, Any]:
        """쿼리 처리"""
        response = self.agent.generate_response(query)

        self.conversation_history.append({
            "type": "user",
            "content": query,
            "timestamp": datetime.now().isoformat()
        })

        self.conversation_history.append({
            "type": "assistant",
            "content": response['response'],
            "timestamp": datetime.now().isoformat()
        })

        return response

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """대화 히스토리 조회"""
        return self.conversation_history

    def clear_conversation(self) -> None:
        """대화 초기화"""
        self.conversation_history.clear()
        self.agent.clear_cache()
        logger.info("Conversation cleared")

    def export_conversation(self) -> str:
        """대화 내보내기"""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "config": self.config.to_dict(),
            "conversation": self.conversation_history,
            "stats": self.agent.get_stats()
        }

        return json.dumps(export_data, ensure_ascii=False, indent=2)

    def run(self) -> None:
        """애플리케이션 실행"""
        self.initialize()
        self.render_header()

        # 사이드바
        sidebar_state = self.render_sidebar()

        # 메인 콘텐츠
        self.render_main_content()

        # 채팅 인터페이스
        self.render_chat_interface()

        # 통계
        self.render_stats()

        # 설정
        self.render_settings()

        # 문서 패널
        self.render_documents_panel()

        # 대화 내보내기
        print("\n[Export Conversation]")
        export = self.export_conversation()
        print(f"Exported {len(export)} characters of conversation data")

        print("\n" + "="*60)
        print("✓ Application completed successfully")
        print("="*60)


def create_streamlit_page():
    """Streamlit 페이지 생성 함수"""
    try:
        import streamlit as st
    except ImportError:
        print("Streamlit not installed. Running demo mode...")
        app = StreamlitRAGApp()
        app.run()
        return

    # Streamlit 페이지 설정
    config = get_config()
    st.set_page_config(
        page_title=config.streamlit.page_title,
        page_icon=config.streamlit.page_icon,
        layout=config.streamlit.layout,
        initial_sidebar_state=config.streamlit.initial_sidebar_state
    )

    # 초기화
    if "rag_app" not in st.session_state:
        st.session_state.rag_app = StreamlitRAGApp()
        st.session_state.rag_app.initialize()

    app = st.session_state.rag_app

    # 헤더
    st.title(f"{config.streamlit.page_icon} {config.streamlit.page_title}")

    # 사이드바
    with st.sidebar:
        st.header("⚙️ Settings")

        top_k = st.slider(
            "Top K Results",
            min_value=1,
            max_value=20,
            value=config.rag.top_k
        )

        threshold = st.slider(
            "Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=config.rag.similarity_threshold,
            step=0.1
        )

        # 문서 업로드
        st.header("📄 Documents")
        uploaded_files = st.file_uploader(
            "Upload documents",
            type=["txt", "md", "pdf"],
            accept_multiple_files=True
        )

        if uploaded_files:
            filenames = [f.name for f in uploaded_files]
            chunks = app.upload_documents(filenames)
            st.success(f"Uploaded {chunks} chunks from {len(uploaded_files)} files")

        # 통계
        if app.documents_loaded:
            st.header("📊 Statistics")
            stats = app.agent.get_stats()
            st.metric("Total Documents", stats['total_documents'])
            st.metric("Total Chunks", stats['total_chunks'])

    # 메인 콘텐츠
    st.header("💬 Chat Interface")

    # 대화 히스토리
    conversation = app.get_conversation_history()
    if conversation:
        st.subheader("Conversation History")
        for msg in conversation:
            with st.chat_message(msg['type']):
                st.write(msg['content'])

    # 사용자 입력
    user_input = st.chat_input("Ask a question...")

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("Thinking..."):
            response = app.process_query(user_input)

        with st.chat_message("assistant"):
            st.write(response['response'])

    # 하단 콘트롤
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Clear Conversation"):
            app.clear_conversation()
            st.rerun()

    with col2:
        if st.button("Export"):
            export_data = app.export_conversation()
            st.download_button(
                label="Download JSON",
                data=export_data,
                file_name=f"rag_conversation_{datetime.now().isoformat()}.json",
                mime="application/json"
            )


def main():
    """메인 함수"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # 데모 모드
        app = StreamlitRAGApp()
        app.run()
    else:
        # Streamlit 모드
        create_streamlit_page()


if __name__ == "__main__":
    main()
