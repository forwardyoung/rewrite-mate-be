# app/services.py
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from .config import settings
from .schemas import RewriteRequest, RewriteResponse
import json
import re
from typing import Dict


class RewriteService:
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다!")

        self.llm = ChatAnthropic(
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            model="claude-sonnet-4-20250514",  # Claude 4 Sonnet
            temperature=0.7
        )

        # 상황별 톤 옵션들 (각 상황마다 여러 선택지)
        self.context_tones = {
            "business-email": {
                "정중한": {
                    "icon": "🤝",
                    "description": "일반적인 업무 상황에 적합한 정중하고 전문적인 톤"
                },
                "격식있는": {
                    "icon": "👔",
                    "description": "중요한 비즈니스 미팅이나 공식 문서에 적합한 격식 있는 톤"
                },
                "간결한": {
                    "icon": "⚡",
                    "description": "빠른 업무 처리를 위한 간결하고 효율적인 톤"
                }
            },
            "academic": {
                "학술적": {
                    "icon": "🎓",
                    "description": "논문이나 연구서에 적합한 객관적이고 전문적인 톤"
                },
                "분석적": {
                    "icon": "🔍",
                    "description": "데이터와 근거를 중시하는 분석적이고 논리적인 톤"
                },
                "설명적": {
                    "icon": "📚",
                    "description": "복잡한 개념을 명확하게 설명하는 교육적인 톤"
                }
            },
            "casual": {
                "친근한": {
                    "icon": "😊",
                    "description": "일상 대화에 적합한 편안하고 친근한 톤"
                },
                "캐주얼한": {
                    "icon": "😎",
                    "description": "편안하고 자연스러운 일상적인 대화 톤"
                },
                "재미있는": {
                    "icon": "😄",
                    "description": "유머와 재미를 더한 활기찬 톤"
                }
            }
        }

    def get_available_tones(self, context: str) -> Dict[str, Dict]:
        """특정 상황에 사용 가능한 톤 옵션들 반환"""
        return self.context_tones.get(context, {})

    async def analyze_and_rewrite(self, request: RewriteRequest) -> RewriteResponse:
        """선택한 상황과 톤에 맞게 리라이팅"""
        try:
            # 선택된 상황과 톤의 정보 가져오기
            tone_info = self.context_tones[request.context.value][request.tone]

            # Claude에게 리라이팅 요청
            rewrite_prompt = self._create_rewrite_prompt(
                request.text,
                request.context.value,
                request.tone,
                tone_info
            )

            response = await self.llm.ainvoke(rewrite_prompt)

            # 디버깅: Claude의 실제 응답 확인
            print("=== Claude 원본 응답 ===")
            print(response.content)
            print("========================")

            # Claude 응답을 파싱
            rewritten_text, explanation = self._parse_claude_response(response.content)

            return RewriteResponse(
                original_text=request.text,
                context=request.context.value,
                rewritten_text=rewritten_text,
                explanation=explanation,
                tone_name=request.tone,
                tone_icon=tone_info['icon']
            )

        except Exception as e:
            print(f"Claude API 에러: {e}")
            return self._get_fallback_response(request)

    def _create_rewrite_prompt(self, text: str, context: str, tone_name: str, tone_info: Dict) -> str:
        """Claude용 프롬프트 생성"""
        prompt = f"""
당신은 전문 영어 글쓰기 튜터입니다. 다음 영어 문장을 {context} 상황에 맞는 {tone_name} 스타일로 리라이팅해주세요.

원문: "{text}"
상황: {context}
요청 톤: {tone_name} ({tone_info['description']})

아래 형식을 정확히 지켜서 답변해주세요. 다른 말은 추가하지 마세요:

리라이팅: [개선된 문장을 여기에 작성]
설명
[구체적인 변경 사항과 이유를 여기에 작성]

원문의 어떤 부분을 왜 바꿨는지 구체적으로 설명해주세요.
"""
        return prompt

    def _parse_claude_response(self, response_text: str) -> tuple[str, str]:
        """Claude 응답을 파싱해서 텍스트와 설명 반환"""
        try:
            # 디버깅용 출력
            print("=== 파싱 시도 중 ===")
            print(f"응답 길이: {len(response_text)}")
            print(f"응답 내용: {response_text}")
            print("========================")

            # 새로운 형식에 맞는 정규식
            rewrite_pattern = r'리라이팅:\s*(.+?)(?=\n설명|$)'
            explanation_pattern = r'설명\s*\n(.+?)(?:\n\n|$)'

            rewrite_match = re.search(rewrite_pattern, response_text, re.DOTALL | re.MULTILINE)
            explanation_match = re.search(explanation_pattern, response_text, re.DOTALL | re.MULTILINE)

            if rewrite_match:
                rewritten_text = rewrite_match.group(1).strip()
                print(f"✅ 리라이팅 추출 성공: {rewritten_text}")
            else:
                rewritten_text = "[파싱 오류 - 리라이팅 부분을 찾을 수 없음]"
                print("❌ 리라이팅 파싱 실패")

            if explanation_match:
                explanation = explanation_match.group(1).strip()
                print(f"✅ 설명 추출 성공: {explanation}")
            else:
                explanation = "응답 파싱 중 오류가 발생했습니다."
                print("❌ 설명 파싱 실패")

                # 대안 패턴들 시도 (기존 콜론 형식도 지원)
                alt_patterns = [
                    r'설명:\s*(.+?)(?:\n|$)',  # 기존 콜론 형식
                    r'설명\s+(.+?)(?:\n|$)',  # 공백만 있는 경우
                    r'이유\s*\n(.+?)(?:\n|$)',  # "이유" 사용
                    r'변경\s*사항\s*\n(.+?)(?:\n|$)'  # "변경사항" 사용
                ]

                for i, pattern in enumerate(alt_patterns):
                    alt_match = re.search(pattern, response_text, re.DOTALL | re.MULTILINE)
                    if alt_match:
                        explanation = alt_match.group(1).strip()
                        print(f"✅ 대안 패턴 {i + 1}로 설명 추출 성공: {explanation}")
                        break

            return rewritten_text, explanation

        except Exception as e:
            print(f"응답 파싱 에러: {e}")
            return "[Claude API 응답 파싱 중 오류 발생]", "응답을 처리하는 중 문제가 발생했습니다."

    def _get_fallback_response(self, request: RewriteRequest) -> RewriteResponse:
        """에러 시 대체 응답"""
        try:
            tone_info = self.context_tones[request.context.value][request.tone]
        except KeyError:
            # 기본값 사용
            tone_info = {"icon": "🤝"}
            tone_name = "정중한"
        else:
            tone_name = request.tone

        return RewriteResponse(
            original_text=request.text,
            context=request.context.value,
            rewritten_text="[서비스 일시 중단]",
            explanation="서비스에 일시적인 문제가 발생했습니다.",
            tone_name=tone_name,
            tone_icon=tone_info['icon']
        )