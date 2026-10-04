import streamlit as st
from google import genai
from PIL import Image
import time

# 1. 페이지 설정
st.set_page_config(page_title="쿠팡 스마트폰 케이스 상세페이지 생성기", layout="centered")

st.title("🛒 쿠팡 스마트폰 케이스 상세페이지 자동 생성기")
st.write("안전한 오픈 웹 운영을 위해 **사용자 개별 API 키 입력 방식**이 적용되었습니다.")

# 2. 사용자 개별 API 키 입력 받기 (보안 강화)
user_api_key = st.text_input("Gemini API 키를 입력하세요", type="password", placeholder="AI Studio에서 발급받은 키를 입력하세요")
st.caption("💡 타인에게 키가 노출되지 않도록 입력 시 마스킹 처리됩니다. (본인 키를 넣고 사용하세요)")

# 3. 파일 업로드 및 텍스트 입력창
uploaded_file = st.file_uploader("알리 상품 이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
chinese_text = st.text_area("알리 상품 원본 텍스트(중국어/영어)", "투명 에어쿠션 방탄 젤리 케이스, 황변 방지, 정밀 버튼감")

# 4. 생성 버튼 및 맞춤형 디자인 빌드 로직
if st.button("🚀 폰케이스 전문 상세페이지 HTML 생성하기"):
    # 입력된 API 키 정제
    clean_api_key = user_api_key.strip().encode('ascii', 'ignore').decode('ascii') if user_api_key else ""

    if not clean_api_key:
        st.error("상세페이지를 생성하려면 본인의 Gemini API 키를 입력해주세요!")
    elif not uploaded_file:
        st.error("알리 상품 이미지를 업로드해주세요!")
    else:
        try:
            client = genai.Client(api_key=clean_api_key)
            
            # 이미지 열기 및 자동 리사이징
            img = Image.open(uploaded_file)
            img.thumbnail((1024, 1024))

            max_retries = 3
            response = None
            success = False

            with st.spinner("프리미엄 폰케이스 상세페이지 디자인 스타일로 HTML을 빌드 중입니다..."):
                for attempt in range(max_retries):
                    try:
                        prompt = f"""
                        당신은 30년 경력의 모바일 액세서리 이커머스 전문 기획자이자 수석 웹 퍼블리셔입니다.
                        첨부된 알리익스프레스 스마트폰 케이스 이미지와 원본 텍스트를 분석하여, 한국 쿠팡 모바일 쇼핑객의 구매 전환율을 극대화할 **완성된 모바일 상세페이지 HTML/CSS 소스코드**를 작성해주세요.

                        [디자인 가이드라인 (참고 사진 스타일 반영)]
                        1. **전체 톤앤매너**: 깔끔한 화이트 배경(#ffffff)에 은은한 연회색/소프트 파스텔 박스(#f8f9fa)를 활용하여 모던하고 고급스러운 그리드 레이아웃을 구성하세요.
                        2. **타이포그래피**: 
                           - 메인 타이틀: 굵고 세련된 폰트 (최소 22px~24px, 진한 차콜/블랙 컬러)
                           - 서브 설명 및 디테일 포인트: 15px~16px, 줄간격 1.6 이상으로 넉넉하고 시원하게 배치하여 가독성을 극대화하세요.
                        3. **필수 섹션 구성 (폰케이스 특화)**:
                           - [상단 배너]: 제품명과 슬로건을 담은 프리미엄 후킹 영역 (예: CRYSTAL CLEAR PRO 등)
                           - [에어쿠션 및 모서리 보호]: 충격 흡수 구조를 시각적으로 강조하는 설명 박스
                           - [정밀 버튼감 및 포트 설계]: 디테일한 설계 포인트를 짚어주는 기능성 강조 섹션
                           - [황변 방지 및 투명도]: 지속력 높은 소재와 변색 방지 장점을 보여주는 비교/강조 섹션
                           - [스펙 요약 (INFORMATION)]: 쿠팡 스타일의 깔끔하고 정돈된 2단 스펙 테이블
                        4. 모바일 가로폭 기준(최대 860px 고정, 반응형)으로 인라인 CSS를 활용해 즉시 완벽하게 렌더링되도록 작성해주세요.

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

                st.success("✅ 프리미엄 폰케이스 스타일 상세페이지가 완성되었습니다!")

                # 1. 웹 미리보기
                st.subheader("📱 모바일 상세페이지 미리보기")
                st.components.v1.html(html_code, height=700, scrolling=True)

                # 2. 파일 다운로드
                st.download_button(
                    label="💾 상세페이지 HTML 파일 다운로드",
                    data=html_code,
                    file_name="phone_case_detail_page.html",
                    mime="text/html"
                )

                # 3. 소스코드 보기
                with st.expander("코드 소스 보기 (HTML 복사하기)"):
                    st.code(html_code, language="html")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}\n\n※ API 키가 올바른지 확인하거나 잠시 후 다시 시도해 주세요.")
