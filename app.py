import streamlit as st
from google import genai
from PIL import Image

# 1. 페이지 설정
st.set_page_config(page_title="쿠팡 실전형 상세페이지 생성기", layout="centered")

st.title("🛒 쿠팡 실전형 상세페이지 자동 생성기")
st.write("30년 기획·개발 노하우를 담아, 쿠팡 모바일 환경에 최적화된 HTML 상세페이지 소스를 즉시 빌드합니다.")

# 2. API 키 설정 (에러 방지 처리 완료)
RAW_API_KEY = "AQ.Ab8RN6KnLuOC6DopKvRZ2LwQKWf2dhDqJepWBSMW8VniF27ziw"
API_KEY = RAW_API_KEY.strip().encode('ascii', 'ignore').decode('ascii')

# 3. 파일 업로드 및 텍스트 입력창
uploaded_file = st.file_uploader("알리 상품 이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
chinese_text = st.text_area("알리 상품 원본 텍스트(중국어/영어)", "45W超快充 10000mAh自带双线 充电宝 迷你便携")

# 4. 생성 버튼 및 실전 HTML 빌드 로직
if st.button("🚀 실전 상세페이지 HTML 및 소스 생성하기"):
    if not API_KEY:
        st.error("API 키를 확인해주세요!")
    elif not uploaded_file:
        st.error("알리 상품 이미지를 업로드해주세요!")
    else:
        try:
            client = genai.Client(api_key=API_KEY)
            img = Image.open(uploaded_file)

            with st.spinner("30년 노하우를 담아 모바일 최적화 상세페이지 HTML 코드를 빌드 중입니다..."):
                prompt = f"""
                당신은 30년 경력의 이커머스 전문 기획자이자 수석 웹 퍼블리셔입니다.
                제공된 알리익스프레스 상품 이미지와 원본 텍스트를 분석하여, 한국 쿠팡 모바일 쇼핑객의 구매 전환율을 극대화할 **완성된 모바일 상세페이지 HTML/CSS 소스코드**를 작성해주세요.

                [요구사항]
                1. 반드시 마크다운 코드 블록(```html ... ```) 형태로 전체 HTML 코드를 출력해주세요.
                2. 모바일 가로폭 기준(최대 860px 고정, 깔끔한 반응형)으로 작성하세요.
                3. 필수 포함 섹션:
                   - 최상단 시선을 사로잡는 강력한 후킹 배너 (컬러풀한 배경, 대형 카피)
                   - 고객의 페인 포인트(불편함) 공감 및 속시원한 해결책 제시
                   - 3대 핵심 셀링 포인트 (아이콘 박스 및 시각적 강조 디자인)
                   - 쿠팡 스타일의 깔끔한 스펙 요약 표 (Table)
                   - 구매를 유도하는 마감 임박 및 신뢰 강조 클로징 카피
                4. 텍스트는 모두 세련된 한국어 마케팅 카피로 직접 번역 및 창작하고, 인라인 CSS를 활용해 시각적으로 즉시 훌륭하게 보이도록 스타일링해주세요.

                [알리 원본 텍스트]
                {chinese_text}
                """

                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=[img, prompt]
                )

                raw_text = response.text

                # HTML 코드 추출
                if "```html" in raw_text:
                    html_code = raw_text.split("```html")[1].split("```")[0].strip()
                elif "```" in raw_text:
                    html_code = raw_text.split("```")[1].split("```")[0].strip()
                else:
                    html_code = raw_text

                st.success("✅ 실전 상세페이지 HTML 코드가 성공적으로 완성되었습니다!")

                # 1. 화면에서 바로 웹으로 미리보기 제공
                st.subheader("📱 모바일 상세페이지 미리보기")
                st.components.v1.html(html_code, height=700, scrolling=True)

                # 2. 파일 다운로드 버튼 제공
                st.download_button(
                    label="💾 상세페이지 HTML 파일 다운로드",
                    data=html_code,
                    file_name="coupang_detail_page.html",
                    mime="text/html"
                )

                # 3. 소스코드 직접 보기용 탭
                with st.expander("코드 소스 보기 (HTML 복사하기)"):
                    st.code(html_code, language="html")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e} (※ 503 에러가 발생할 경우 서버 트래픽 문제이므로 1분 뒤에 다시 버튼을 눌러주세요!)")
