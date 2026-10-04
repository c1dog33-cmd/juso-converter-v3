import streamlit as st
from google import genai
from PIL import Image

# 1. 웹페이지 제목 및 설명 설정
st.title("🛒 알리 ➡️ 쿠팡 상세페이지 자동 생성기")
st.write("알리익스프레스 상품 이미지와 텍스트를 넣으면 쿠팡 맞춤형 상세페이지 기획안을 만들어 줍니다.")

# 2. 사이트 내에서 API 키 입력받기 (또는 st.secrets 사용 가능)
api_key = st.text_input("Gemini API Key를 입력하세요", type="password")

# 3. 파일 업로드 및 텍스트 입력창 만들기
uploaded_file = st.file_uploader("알리 상품 이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
chinese_text = st.text_area("알리 상품 원본 텍스트(중국어 또는 영어)를 입력하세요", "45W超快充 10000mAh自带双线 充电宝 迷你便携")

# 4. 버튼을 누르면 실행되는 로직
if st.button("상세페이지 기획안 생성하기"):
    if not api_key:
        st.error("API 키를 먼저 입력해주세요!")
    elif not uploaded_file:
        st.error("알리 상품 이미지를 업로드해주세요!")
    else:
        try:
            # Gemini 클라이언트 초기화
            client = genai.Client(api_key=api_key)
            img = Image.open(uploaded_file)

            with st.spinner("AI가 알리 상품을 분석하고 쿠팡 스타일 기획안을 작성중입니다..."):
                prompt = f"""
                당신은 쿠팡 전문 베스트셀러 상세페이지 기획자입니다.
                아래 제공된 알리익스프레스 상품의 원본 텍스트와 이미지를 분석하여,
                한국 쿠팡 고객의 구매 심리를 자극할 수 있는 매력적인 상세페이지 기획안을 작성해 주세요.

                [알리익스프레스 원본 텍스트]
                {chinese_text}

                [출력 양식]
                1. 최상단 후킹 카피 (고객의 시선을 사로잡는 문구)
                2. 핵심 셀링 포인트 3가지 (기능 및 장점 상세 설명)
                3. 추천 타겟 고객
                4. 쿠팡 요약 스펙 정리
                """

                # Gemini 2.5 Flash 모델 호출
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[img, prompt]
                )

                st.success("✅ 상세페이지 기획안이 완성되었습니다!")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
