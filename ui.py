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
                    context=ContextType(context_value)
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

                # 각 버전을 동적 탭으로 표시
                if response.versions:
                    tabs = st.tabs([f"{v.icon} {v.name}" for v in response.versions])

                    for i, (tab, version) in enumerate(zip(tabs, response.versions)):
                        with tab:
                            st.markdown(f"### {version.icon} {version.name}")

                            st.markdown(
                                f"""
                                <div style='white-space: pre-wrap; font-size: 1.06em; background: #f7f7fa; border-radius: 6px; padding: 8px 10px; margin-bottom: 5px; word-break: break-all;'>
                                {version.text}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            st.caption("텍스트를 드래그해 복사하세요.")

                            st.markdown(f"**💡 설명:** {version.explanation}")
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