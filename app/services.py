# app/services.py
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from .config import settings
from .schemas import RewriteRequest, RewriteResponse, RewriteVersion
import json
import re
from typing import List, Dict


class RewriteService:
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다!")

        self.llm = ChatAnthropic(
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            model="claude-sonnet-4-20250514",  # Claude 4 Sonnet
            temperature=0.7
        )

        # 상황별 기본 말투 (하나씩만)
        self.context_default_tone = {
            "business-email": {
                "name": "정중한",
                "icon": "🤝",
                "description": "일반적인 업무 상황에 적합한 정중하고 전문적인 톤"
            },
            "academic": {
                "name": "학술적",
                "icon": "🎓",
                "description": "논문이나 연구서에 적합한 객관적이고 전문적인 톤"
            },
            "casual": {
                "name": "친근한",
                "icon": "😊",
                "description": "일상 대화에 적합한 편안하고 친근한 톤"
            }
        }

    async def analyze_and_rewrite(self, request: RewriteRequest) -> RewriteResponse:
        """선택한 상황에 맞는 말투로 리라이팅"""
        try:
            # 해당 상황의 기본 말투 정보 가져오기
            tone_info = self.context_default_tone[request.context.value]

            # Claude에게 리라이팅 요청
            rewrite_prompt = self._create_rewrite_prompt(
                request.text,
                request.context.value,
                tone_info
            )

            response = await self.llm.ainvoke(rewrite_prompt)

            return RewriteResponse(
                original_text=request.text,
                context=request.context.value
            )

        except Exception as e:
            print(f"Claude API 에러: {e}")
            # 에러 시 기본 응답 반환
            return self._get_fallback_response(request)

    def _create_rewrite_prompt(self, text: str, context: str, tone_info: Dict) -> str:
        """Claude용 프롬프트 생성 (단일 말투)"""
        prompt = f"""
당신은 전문 영어 글쓰기 튜터입니다. 다음 영어 문장을 {context} 상황에 맞는 {tone_info['name']} 스타일로 리라이팅해주세요.

원문: "{text}"
상황: {context}
요청 스타일: {tone_info['name']} ({tone_info['description']})

다음 형식으로 정확히 답변해주세요:

리라이팅: [리라이팅된 문장]
설명: [왜 이렇게 바꿨는지 구체적으로 설명]

원문보다 자연스럽고 적절한 표현으로 개선해주세요.
"""
        return prompt

    def _parse_claude_response(self, response_text: str, tone_info: Dict) -> RewriteVersion:
        """Claude 응답을 파싱해서 RewriteVersion으로 변환"""
        try:
            # 정규식으로 리라이팅된 텍스트와 설명 추출
            rewrite_pattern = r'리라이팅:\s*(.+?)(?:\n|$)'
            explanation_pattern = r'설명:\s*(.+?)(?:\n|$)'

            rewrite_match = re.search(rewrite_pattern, response_text, re.DOTALL)
            explanation_match = re.search(explanation_pattern, response_text, re.DOTALL)

            rewritten_text = rewrite_match.group(1).strip() if rewrite_match else "[파싱 오류]"
            explanation = explanation_match.group(1).strip() if explanation_match else "응답 파싱 중 오류가 발생했습니다."

            return RewriteVersion(
                name=tone_info['name'],
                icon=tone_info['icon'],
                text=rewritten_text,
                explanation=explanation
            )

        except Exception as e:
            print(f"응답 파싱 에러: {e}")
            return self._get_default_version(tone_info)

    def _get_default_version(self, tone_info: Dict) -> RewriteVersion:
        """파싱 실패 시 기본 버전"""
        return RewriteVersion(
            name=tone_info['name'],
            icon=tone_info['icon'],
            text="[Claude API 응답 파싱 중 오류 발생]",
            explanation="응답을 처리하는 중 문제가 발생했습니다."
        )

    def _get_fallback_response(self, request: RewriteRequest) -> RewriteResponse:
        """에러 시 대체 응답"""
        tone_info = self.context_default_tone.get(
            request.context.value,
            self.context_default_tone["business-email"]
        )

        return RewriteResponse(
            original_text=request.text,
            context=request.context.value,
            usage_tips=["서비스 일시 중단 중입니다. 잠시 후 다시 시도해주세요."]
        )