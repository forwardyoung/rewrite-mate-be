# ✍️ 영어 리라이팅 도구 (AI 기반 문장 교정 서비스)

AI LLM API를 활용해 문맥과 상황에 맞는 영어 문장으로 리라이팅해주는 웹 도구입니다.  
사용자가 입력한 영어 문장을 상황(예: 비즈니스 이메일)과 원하는 톤(예: 정중한) 설정에 따라 자연스럽고 전문적으로 리라이팅해줍니다.

![example.gif](example.gif)

## 🛠 기술 스택

- **LLM API**: [Claude 4 Sonnet](https://www.anthropic.com/index/claude-4)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) – 프롬프트 생성 및 LLM API 호출 처리
- **Frontend**: [Streamlit](https://streamlit.io/) – 사용자 인터페이스(UI)
- **언어**: Python 3.11+

---

## ✨ 주요 기능

- ✅ 상황(비즈니스 이메일, 학술적 글쓰기, 일상 대화) 및 톤(정중한, 캐주얼, 간결한 등) 선택
- ✅ 영어 문장 입력 → Claude API를 통해 리라이팅 결과 반환
- ✅ 변경된 표현에 대한 설명 제공
- ✅ Streamlit 기반 직관적인 UI

---

## 🧠 사용 예시

```text
입력 문장: I wanna invite you to anniversary celebration.
상황: 비즈니스 이메일
톤: 정중한

결과: I would like to cordially invite you to our anniversary celebration.
설명: "I wanna" → "I would like to": 비격식적 표현을 정중하고 전문적으로 수정
