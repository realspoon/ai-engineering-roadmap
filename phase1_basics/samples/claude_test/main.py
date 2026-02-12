"""
Week 1: LLM 기초 - 기본 챗봇 구현
================================
OpenAI와 Anthropic API를 사용한 기본 챗봇 예제

실행 전 필수 사항:
1. pip install openai anthropic python-dotenv
2. .env 파일에 API 키 설정
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# 환경 변수 로드
load_dotenv()

# ============================================
# 2. Anthropic Claude 기본 호출
# ============================================

def chat_with_claude(message: str, model: str = "claude-sonnet-4-20250514") -> str:
    """
    Anthropic Claude 모델과 대화하는 기본 함수

    Args:
        message: 사용자 입력 메시지
        model: 사용할 모델

    Returns:
        AI 응답 텍스트
    """
    client = Anthropic()

    response = client.messages.create(
        model=model,
        max_tokens=1000,
        system="당신은 친절하고 도움이 되는 AI 어시스턴트입니다.",
        messages=[
            {
                "role": "user",
                "content": message
            }
        ]
    )
    
    return response.content[0].text


def main():
    print("Hello from api-test!")
    print(chat_with_claude("너의 이름을 알려줘."))

"""
Claude API 기본 예제 - Hello World
"""

if __name__ == "__main__":
    main()
