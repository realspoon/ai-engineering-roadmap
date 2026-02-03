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
from openai import OpenAI
from anthropic import Anthropic

# 환경 변수 로드
load_dotenv()


# ============================================
# 1. OpenAI GPT 기본 호출
# ============================================

def chat_with_gpt(message: str, model: str = "gpt-4o-mini") -> str:
    """
    OpenAI GPT 모델과 대화하는 기본 함수

    Args:
        message: 사용자 입력 메시지
        model: 사용할 모델 (기본값: gpt-4o-mini)

    Returns:
        AI 응답 텍스트
    """
    client = OpenAI()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "당신은 친절하고 도움이 되는 AI 어시스턴트입니다."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=0.7,  # 창의성 조절 (0~2)
        max_tokens=1000   # 최대 응답 길이
    )

    return response.choices[0].message.content


# ============================================
# 2. Anthropic Claude 기본 호출
# ============================================

def chat_with_claude(message: str, model: str = "claude-3-5-sonnet-20241022") -> str:
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
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=self.system_prompt,
            messages=self.history
        )

        return response.content[0].text

    def clear_history(self):
        """대화 히스토리 초기화"""
        self.history = []


# ============================================
# 4. 파라미터 실험
# ============================================

def experiment_temperature(message: str):
    """
    Temperature 파라미터에 따른 응답 차이 실험
    """
    client = OpenAI()
    temperatures = [0, 0.5, 1.0, 1.5]

    print(f"입력: {message}\n")
    print("=" * 50)

    for temp in temperatures:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message}],
            temperature=temp,
            max_tokens=100
        )

        print(f"\n[Temperature: {temp}]")
        print(response.choices[0].message.content)
        print("-" * 50)


# ============================================
# 5. 토큰 사용량 추적
# ============================================

def chat_with_usage_tracking(message: str) -> dict:
    """
    토큰 사용량을 추적하는 채팅 함수

    Returns:
        dict: 응답과 토큰 사용량 정보
    """
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}],
        temperature=0.7
    )

    return {
        "response": response.choices[0].message.content,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        },
        "model": response.model
    }


# ============================================
# 실행 예제
# ============================================

if __name__ == "__main__":
    # 예제 1: 기본 GPT 호출
    print("=== GPT 기본 호출 ===")
    response = chat_with_gpt("Python에서 리스트와 튜플의 차이점을 설명해주세요.")
    print(response)
    print()

    # 예제 2: 대화형 챗봇
    print("=== 대화형 챗봇 ===")
    bot = SimpleChatbot(provider="openai")

    # 첫 번째 질문
    response1 = bot.chat("판다스 DataFrame에서 결측치를 처리하는 방법을 알려주세요.")
    print(f"Q1 응답: {response1[:200]}...")

    # 후속 질문 (히스토리 유지)
    response2 = bot.chat("그 중에서 가장 추천하는 방법은 무엇인가요?")
    print(f"Q2 응답: {response2[:200]}...")
    print()

    # 예제 3: 토큰 사용량 추적
    print("=== 토큰 사용량 추적 ===")
    result = chat_with_usage_tracking("AI란 무엇인가요?")
    print(f"응답: {result['response'][:100]}...")
    print(f"토큰 사용량: {result['usage']}")
