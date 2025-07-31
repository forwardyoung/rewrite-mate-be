import streamlit as st
import asyncio
import sys
import os

# 현재 디렉토리를 Python 경로에 추가 (app 폴더 import를 위해)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services import RewriteService
from app.schemas import RewriteRequest, ContextType

# 페이지 설정
st.set_page_config(
    page_title="영어 리라이팅 도구",
    page_icon="✍️",
    layout="wide"
)

# 사이드바 너비 조정을 위한 CSS
st.markdown("""
    <style>
    /* 사이드바 너비 조정 */
    .css-1d391kg {
        width: 28rem;
    }
    .css-1544g2n {
        width: 28rem;
    }
    section[data-testid="stSidebar"] {
        width: 28rem !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 28rem !important;
    }

    /* 메인 컨텐츠 영역 조정 */
    .main .block-container {
        padding-left: 2rem;
        max-width: none;
    }

    /* 마크다운 요소들 간격 조정 */
    .stMarkdown h3 {
        margin-bottom: 0.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# 환경 변수 로드
from dotenv import load_dotenv

load_dotenv()

# 환경 변수 확인 또는 Streamlit에서 입력받기
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    st.warning("ANTHROPIC_API_KEY가 설정되지 않았습니다!")
    api_key = st.text_input("Anthropic API Key를 입력하세요:", type="password")
    if not api_key:
        st.stop()
    else:
        os.environ['ANTHROPIC_API_KEY'] = api_key

# 세션 상태 초기화
if 'rewrite_service' not in st.session_state:
    st.session_state.rewrite_service = RewriteService()

# 메인 UI
st.title("✍️ 영어 리라이팅 도구")
st.markdown("AI로 영어 문장을 다양한 스타일로 리라이팅해보세요!")

# 사이드바 - 상황 선택
with st.sidebar:
    st.header("설정")
    context_options = {
        "비즈니스 이메일 📧": "business-email",
        "학술적 글쓰기 🎓": "academic",
        "일상 대화 💬": "casual"
    }

    selected_context = st.selectbox(
        "상황을 선택하세요:",
        options=list(context_options.keys())
    )

    context_value = context_options[selected_context]

    # 선택된 상황에 따른 톤 옵션 표시
    available_tones = st.session_state.rewrite_service.get_available_tones(context_value)

    tone_options = {}
    for tone_name, tone_info in available_tones.items():
        tone_options[f"{tone_info['icon']} {tone_name}"] = tone_name

    selected_tone_display = st.selectbox(
        "톤을 선택하세요:",
        options=list(tone_options.keys())
    )

    selected_tone = tone_options[selected_tone_display]

    # 선택된 톤 설명 표시
    if selected_tone in available_tones:
        st.caption(f"💡 {available_tones[selected_tone]['description']}")

# 메인 영역
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 원문 입력")
    input_text = st.text_area(
        "리라이팅할 영어 문장을 입력하세요:",
        height=150,
        placeholder="예: I want to discuss this matter with you."
    )

    rewrite_button = st.button(
        "🚀 리라이팅하기",
        type="primary",
        use_container_width=True
    )

with col2:
    st.subheader("✨ 리라이팅 결과")

    if rewrite_button and input_text.strip():
        with st.spinner("AI가 리라이팅 중입니다..."):
            try:
                # 비동기 함수 실행
                request = RewriteRequest(
                    text=input_text.strip(),
                    context=ContextType(context_value),
                    tone=selected_tone
                )

                # 비동기 함수를 동기적으로 실행
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(
                    st.session_state.rewrite_service.analyze_and_rewrite(request)
                )
                loop.close()

                # 결과 표시
                st.success("리라이팅 완료!")

                print(response, '응답')

                # 단일 결과 표시 (versions 대신 직접 접근)
                st.markdown(f"### {response.tone_icon} {response.tone_name}")

                st.markdown(
                    f"""
                    <div style='white-space: pre-wrap; font-size: 1.06em; background: #f7f7fa; border-radius: 6px; padding: 4px 10px 8px 10px; margin-top: -20px; margin-bottom: 5px; word-break: break-all;'>
                    {response.rewritten_text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.caption("텍스트를 드래그해 복사하세요.")

                # 설명에서 번호를 불릿 포인트로 변환
                formatted_explanation = response.explanation

                # 번호 패턴을 불릿 포인트로 변환
                import re

                # 1. 또는 1) 패턴을 * 로 변환
                formatted_explanation = re.sub(r'^\s*\d+\.\s*', '* ', formatted_explanation, flags=re.MULTILINE)
                formatted_explanation = re.sub(r'^\s*\d+\)\s*', '* ', formatted_explanation, flags=re.MULTILINE)

                st.markdown(f"**💡 설명**")
                st.markdown(f"{formatted_explanation}")
                st.markdown("---")

            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")

    elif rewrite_button and not input_text.strip():
        st.warning("영어 문장을 입력해주세요!")

# 하단 정보
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <small>Claude 4 Sonnet을 사용한 AI 리라이팅 도구</small>
    </div>
    <div style='text-align: center; color: #999; margin-top: 10px; font-size: 0.85em;'>
        GitHub: <a href="https://github.com/forwardyoung" target="_blank" style="color: #999; text-decoration: none;">&#x1F517; forwardyoung</a>
    </div>
    """
    ,
    unsafe_allow_html=True
)