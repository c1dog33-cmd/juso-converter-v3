import streamlit as st
from google import genai
from PIL import Image
import time
import base64

# 1. 페이지 설정
st.set_page_config(page_title="쿠팡 실전형 상세페이지 생성기", layout="centered")

st.title("🛒 쿠팡 실전형 상세페이지 자동 생성기")
st.write("알리 상품 사진을 올리면, **실제 상품 이미지가 HTML 코드 안에 자동으로 쏙쏙 박혀서** 완성됩니다!")

# 2. API 키 설정 (에러 방지 처리 완료)
RAW_API_KEY = "AQ.Ab8RN6KnLuOC6DopKvRZ2LwQKWf2dhDqJepWBSMW8VniF27ziw"
API_KEY = RAW_API_KEY.strip().encode('ascii', 'ignore').decode('ascii')

# 3. 파일 업로드 및 텍스트 입력창
uploaded_file = st.file_uploader("알리 상품 이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
chinese_text = st.text_area("알리 상품 원본 텍스트(중국어/영어)", "45W超快充 10000mAh自带双线 充电宝 迷你便携")

# 4. 생성 버튼 및 이미지 자동 삽입 빌드 로직
if st.button("🚀 실제 이미지가 포함된 상세페이지 HTML 생성하기"):
    if not API_KEY:
        st.error("API 키를 확인해주세요!")
    elif not uploaded_file:
        st.error("알리 상품 이미지를 업로드해주세요!")
    else:
        try:
            client = genai.Client(api_key=API_KEY)
            img = Image.open(uploaded_file)

            # 업로드한 이미지를 웹 호환 Base64 데이터 URI로 변환
            bytes_data = uploaded_file.getvalue()
            b64_encoded = base64.b64encode(bytes_data).decode('utf-8')
            mime_type = uploaded_file.type if uploaded_file.type else "image/jpeg"
            img_data_uri = f"data:{mime_type};base64,{b64_encoded}"

            max_retries = 3
            response = None
            success = False

            with st.spinner("상품 이미지를 분석하고 HTML에 직접 삽입하여 빌드 중입니다..."):
                for attempt in range(max_retries):
                    try:
                        prompt = f"""
                        당신은 30년 경력의 이커머스 전문 기획자이자 수석 웹 퍼블리셔입니다.
                        제공된 알리익스프레스 상품 이미지와 원본 텍스트를 분석하여, 한국 쿠팡 모바일 쇼핑객의 구매 전환율을 극대화할 **완성된 모바일 상세페이지 HTML/CSS 소스코드**를 작성해주세요.

                        [매우 중요한 이미지 삽입 규칙]
                        - 사용자가 업로드한 실제 상품 이미지의 웹 데이터 주소(Data URI)는 다음과 같습니다:
                        "{img_data_uri}"
                        - 상세페이지 HTML 내에서 상품의 핵심 사진이 들어가야 할 위치에 (<img src="{img_data_uri}">) 태그를 적극적으로 활용하여, 실제 제품 사진이 상세페이지 디자인 속에 완벽하게 어우러지도록 배치해주세요.

                        [요구사항]
                        1. 반드시 마크다운 코드 블록(```html ... ```) 형태로 전체 HTML 코드를 출력해주세요.
                        2. 모바일 가로폭 기준(최대 860px 고정, 깔끔한 반응형)으로 작성하세요.
                        3. 필수 포함 섹션:
                           - 최상단 시선을 사로잡는 강력한 후킹 배너 및 실제 상품 이미지 배치
                           - 고객의 페인 포인트 공감 및 해결책 제시
                           - 3대 핵심 셀링 포인트 (실제 상품 이미지 및 시각적 강조 디자인)
                           - 쿠팡 스타일의 깔끔한 스펙 요약 표 (Table)
                           - 구매 유도 클로징 카피
                        4. 텍스트는 세련된 한국어 마케팅 카피로 작성하고 인라인 CSS로 스타일링하세요.

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
                        if "503" in str(api_err) or "UNAVAILABLE" in str(api_err):
                            if attempt < max_retries - 1:
                                time.sleep(3)
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

                st.success("✅ 실제 상품 이미지가 포함된 상세페이지가 완성되었습니다!")

                # 1. 웹 미리보기
                st.subheader("📱 모바일 상세페이지 미리보기 (이미지 포함)")
                st.components.v1.html(html_code, height=700, scrolling=True)

                # 2. 파일 다운로드
                st.download_button(
                    label="💾 이미지 포함 상세페이지 HTML 파일 다운로드",
                    data=html_code,
                    file_name="coupang_detail_page_with_image.html",
                    mime="text/html"
                )

                # 3. 소스코드 보기
                with st.expander("코드 소스 보기 (HTML 복사하기)"):
                    st.code(html_code, language="html")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}\n\n※ 서버 트래픽이 심할 경우 잠시 후 다시 시도해 주세요.")
