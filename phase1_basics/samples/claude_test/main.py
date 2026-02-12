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

# ============================================
# 3. 대화 히스토리가 있는 챗봇
# ============================================

class SimpleChatbot:
    """대화 히스토리를 유지하는 간단한 챗봇"""

    def __init__(self, provider: str = "openai"):
        """
        Args:
            provider: "openai" 또는 "anthropic"
        """
        self.provider = provider
        self.history = []
        self.system_prompt = "당신은 데이터 분석 전문가입니다. 사용자의 데이터 관련 질문에 친절하게 답변합니다."

        if provider == "openai":
            self.client = OpenAI()
        else:
            self.client = Anthropic()

    def chat(self, message: str) -> str:
        """
        메시지를 보내고 응답을 받음 (히스토리 유지)
        """
        # 히스토리에 사용자 메시지 추가
        self.history.append({"role": "user", "content": message})

        if self.provider == "openai":
            response = self._chat_openai()
        else:
            response = self._chat_anthropic()

        # 히스토리에 AI 응답 추가
        self.history.append({"role": "assistant", "content": response})

        return response

    def _chat_openai(self) -> str:
        """OpenAI API 호출"""
        messages = [{"role": "system", "content": self.system_prompt}] + self.history

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )

        return response.choices[0].message.content

    def _chat_anthropic(self) -> str:
        """Anthropic API 호출"""
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=self.system_prompt,
            messages=self.history
        )

        return response.content[0].text

    def clear_history(self):
        """대화 히스토리 초기화"""
        self.history = []

def main():
    print("Hello from api-test!")
    print(chat_with_claude("너의 이름을 알려줘."))

    # 예제 2: 대화형 챗봇
    print("=== 대화형 챗봇 ===")
    bot = SimpleChatbot(provider="anthropic")

    # 첫 번째 질문
    response1 = bot.chat("판다스 DataFrame에서 결측치를 처리하는 방법을 짧게 알려주세요.")
    print(f"Q1 응답: {response1[:200]}...")

    # 후속 질문 (히스토리 유지)
    response2 = bot.chat("그 중에서 가장 추천하는 방법은 무엇인가요?")
    print(f"Q2 응답: {response2[:200]}...")
    print()    

"""
Claude API 기본 예제 - Hello World
"""

if __name__ == "__main__":
    main()
