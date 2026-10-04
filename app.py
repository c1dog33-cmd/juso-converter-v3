import streamlit as st
from google import genai
from PIL import Image
import time

# 1. 페이지 설정
st.set_page_config(page_title="쿠팡 실전형 상세페이지 생성기", layout="centered")

st.title("🛒 쿠팡 실전형 상세페이지 자동 생성기")
st.write("서버 과부하(503) 및 토큰 초과 에러를 방지하기 위해 **이미지 자동 최적화(리사이징)** 기능이 적용되었습니다.")

# 2. API 키 설정 (에러 방지 처리 완료)
RAW_API_KEY = "AQ.Ab8RN6KnLuOC6DopKvRZ2LwQKWf2dhDqJepWBSMW8VniF27ziw"
API_KEY = RAW_API_KEY.strip().encode('ascii', 'ignore').decode('ascii')

# 3. 파일 업로드 및 텍스트 입력창
uploaded_file = st.file_uploader("알리 상품 이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
chinese_text = st.text_area("알리 상품 원본 텍스트(중국어/영어)", "45W超快充 10000mAh自带双线 充电宝 迷你便携")

# 4. 생성 버튼 및 최적화 빌드 로직
if st.button("🚀 실전 상세페이지 HTML 생성하기"):
    if not API_KEY:
        st.error("API 키를 확인해주세요!")
    elif not uploaded_file:
        st.error("알리 상품 이미지를 업로드해주세요!")
    else:
        try:
            client = genai.Client(api_key=API_KEY)
            
            # 이미지 열기 및 자동 리사이징 (서버 과부하 및 토큰 초과 방지)
            img = Image.open(uploaded_file)
            img.thumbnail((1024, 1024)) # 해상도를 최적화 크기로 조절

            max_retries = 3
            response = None
            success = False

            with st.spinner("이미지를 최적화하고 쿠팡 스타일 HTML 상세페이지를 빌드 중입니다..."):
                for attempt in range(max_retries):
                    try:
                        prompt = f"""
                        당신은 30년 경력의 이커머스 전문 기획자이자 수석 웹 퍼블리셔입니다.
                        첨부된 알리익스프레스 상품 이미지와 원본 텍스트를 분석하여, 한국 쿠팡 모바일 쇼핑객의 구매 전환율을 극대화할 **완성된 모바일 상세페이지 HTML/CSS 소스코드**를 작성해주세요.

                        [요구사항]
                        1. 반드시 마크다운 코드 블록(```html ... ```) 형태로 전체 HTML 코드를 출력해주세요.
                        2. 모바일 가로폭 기준(최대 860px 고정, 깔끔한 반응형)으로 작성하세요.
                        3. 필수 포함 섹션:
                           - 최상단 시선을 사로잡는 강력한 후킹 배너
                           - 고객의 페인 포인트 공감 및 속시원한 해결책 제시
                           - 3대 핵심 셀링 포인트 (시각적 강조 디자인)
                           - 쿠팡 스타일의 깔끔한 스펙 요약 표 (Table)
                           - 구매 유도 마감 임박 및 신뢰 강조 클로징 카피
                        4. 텍스트는 세련된 한국어 마케팅 카피로 작성하고 인라인 CSS로 시각적으로 훌륭하게 스타일링하세요.

                        [알리 원본 텍스트]
                        {chinese_text}
                        """

                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=[img, prompt]
                        )
                        success = True
                        break

                    except Exception as api_err:
                        # 503 또는 429 에러 발생 시 대기 후 자동 재시도
                        if "503" in str(api_err) or "UNAVAILABLE" in str(api_err) or "429" in str(api_err):
                            if attempt < max_retries - 1:
                                time.sleep(5) # 5초 대기 후 재시도
                                continue
                            else:
                                raise api_err
                        else:
                            raise api_err

            if success and response:
                raw_text = response.text

                # HTML 코드 추출
                if "```html" in raw_text:
                    html_code = raw_text.split("```html")[1].split("```")[0].strip()
                elif "```" in raw_text:
                    html_code = raw_text.split("```")[1].split("```")[0].strip()
                else:
                    html_code = raw_text

                st.success("✅ 실전 상세페이지 HTML 코드가 성공적으로 완성되었습니다!")

                # 1. 웹 미리보기
                st.subheader("📱 모바일 상세페이지 미리보기")
                st.components.v1.html(html_code, height=700, scrolling=True)

                # 2. 파일 다운로드
                st.download_button(
                    label="💾 상세페이지 HTML 파일 다운로드",
                    data=html_code,
                    file_name="coupang_detail_page.html",
                    mime="text/html"
                )

                # 3. 소스코드 보기
                with st.expander("코드 소스 보기 (HTML 복사하기)"):
                    st.code(html_code, language="html")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}\n\n※ 서버 트래픽이 심할 경우 잠시 후 다시 버튼을 눌러주세요.")
