import streamlit as st
from google import genai
from PIL import Image
import time

# 1. 페이지 설정
st.set_page_config(page_title="쿠팡 실전형 상세페이지 생성기", layout="centered")

st.title("🛒 쿠팡 실전형 상세페이지 자동 생성기")
st.write("참고 사진의 스타일을 반영하여, 모바일에서 **글씨가 큼직하고 시원하게 읽히도록** 가독성을 극대화했습니다.")

# 2. API 키 설정 (에러 방지 처리 완료)
RAW_API_KEY = "AQ.Ab8RN6KnLuOC6DopKvRZ2LwQKWf2dhDqJepWBSMW8VniF27ziw"
API_KEY = RAW_API_KEY.strip().encode('ascii', 'ignore').decode('ascii')

# 3. 파일 업로드 및 텍스트 입력창
uploaded_file = st.file_uploader("알리 상품 이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
chinese_text = st.text_area("알리 상품 원본 텍스트(중국어/영어)", "45W超快充 10000mAh自带双线 充电宝 迷你便携")

# 4. 생성 버튼 및 최적화 빌드 로직
if st.button("🚀 큼직한 가독성형 상세페이지 HTML 생성하기"):
    if not API_KEY:
        st.error("API 키를 확인해주세요!")
    elif not uploaded_file:
        st.error("알리 상품 이미지를 업로드해주세요!")
    else:
        try:
            client = genai.Client(api_key=API_KEY)
            
            # 이미지 열기 및 자동 리사이징 (서버 과부하 및 토큰 초과 방지)
            img = Image.open(uploaded_file)
            img.thumbnail((1024, 1024))

            max_retries = 3
            response = None
            success = False

            with st.spinner("모바일 최적화 및 큼직한 폰트 스타일을 적용하여 HTML을 빌드 중입니다..."):
                for attempt in range(max_retries):
                    try:
                        prompt = f"""
                        당신은 30년 경력의 이커머스 전문 기획자이자 수석 웹 퍼블리셔입니다.
                        첨부된 알리익스프레스 상품 이미지와 원본 텍스트를 분석하여, 한국 쿠팡 모바일 쇼핑객의 구매 전환율을 극대화할 **완성된 모바일 상세페이지 HTML/CSS 소스코드**를 작성해주세요.

                        [매우 중요한 타이포그래피(폰트 크기) 및 디자인 규칙]
                        - 모바일 화면에서 스마트폰 사용자가 한눈에 읽기 쉽도록 **글씨 크기를 충분히 큼직하고 시원하게** 설정해주세요! (첨부된 참고 사진처럼 가독성이 극대화된 스타일)
                        - 주요 제목(Headings, h2/h3): 최소 20px ~ 24px 이상, 볼드체(bold) 적용
                        - 본문 설명 텍스트(p/span): 최소 15px ~ 16px 이상으로 설정하고, 줄간격(line-height)은 1.6 이상으로 넉넉하게 주어 절대 작아 보이거나 답답해 보이지 않게 하세요.
                        - 여백(Padding/Margin): 각 섹션마다 충분한 여백을 주어 깔끔하고 고급스러운 그리드 레이아웃을 구성하세요.

                        [요구사항]
                        1. 반드시 마크다운 코드 블록(```html ... ```) 형태로 전체 HTML 코드를 출력해주세요.
                        2. 모바일 가로폭 기준(최대 860px 고정, 반응형)으로 작성하세요.
                        3. 필수 포함 섹션:
                           - 최상단 시선을 사로잡는 강력한 후킹 배너 (큰 글씨)
                           - 고객의 페인 포인트 공감 및 속시원한 해결책 제시
                           - 3대 핵심 셀링 포인트 (큼직한 아이콘 및 강조 박스 디자인)
                           - 쿠팡 스타일의 깔끔한 스펙 요약 표 (글씨가 큼직한 Table)
                           - 구매 유도 마감 임박 및 신뢰 강조 클로징 카피
                        4. 인라인 CSS를 활용해 시각적으로 즉시 훌륭하게 보이도록 스타일링해주세요.

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
                        if "503" in str(api_err) or "UNAVAILABLE" in str(api_err) or "429" in str(api_err):
                            if attempt < max_retries - 1:
                                time.sleep(5)
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

                st.success("✅ 큼직하고 가독성 높은 상세페이지 HTML 코드가 완성되었습니다!")

                # 1. 웹 미리보기
                st.subheader("📱 모바일 상세페이지 미리보기")
                st.components.v1.html(html_code, height=700, scrolling=True)

                # 2. 파일 다운로드
                st.download_button(
                    label="💾 상세페이지 HTML 파일 다운로드",
                    data=html_code,
                    file_name="coupang_detail_page_large_font.html",
                    mime="text/html"
                )

                # 3. 소스코드 보기
                with st.expander("코드 소스 보기 (HTML 복사하기)"):
                    st.code(html_code, language="html")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}\n\n※ 서버 트래픽이 심할 경우 잠시 후 다시 버튼을 눌러주세요.")
