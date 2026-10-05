import streamlit as st
from PIL import Image
import base64
from io import BytesIO

# 1. 페이지 설정
st.set_page_config(page_title="쿠팡 스마트폰 케이스 상세페이지 생성기", layout="centered")

st.title("🛒 쿠팡 스마트폰 케이스 상세페이지 자동 생성기 (에러 제로 독립형)")
st.write("✨ **할당량 제한(429 에러) 완전 해결**: API 키 없이 내부 엔진으로 즉시 작동하여 에러 없이 무제한 생성합니다.")

# 2. 파일 업로드 및 텍스트 입력창
uploaded_file = st.file_uploader("알리 상품 이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
input_text = st.text_area("알리 상품 원본 텍스트(중국어/영어/한국어)", "투명 에어쿠션 방탄 젤리 케이스, 황변 방지, 정밀 버튼감, 720도 보호")

# 3. 즉시 생성 및 템플릿 조립 로직 (API 호출 없음 = 에러 원천 차단)
if st.button("🚀 폰케이스 전문 상세페이지 즉시 생성하기"):
    if not uploaded_file:
        st.error("알리 상품 이미지를 업로드해주세요!")
    else:
        try:
            # 입력된 텍스트를 줄바꿈이나 쉼표 기준으로 나누어 섹션에 자동 배치
            text_lines = [line.strip() for line in input_text.replace(",", "\n").split("\n") if line.strip()]
            
            hook_title = text_lines[0] if len(text_lines) > 0 else "BT Clear PRO - 완벽한 투명과 단단한 보호"
            feat_1 = text_lines[1] if len(text_lines) > 1 else "에어쿠션 충격 흡수 구조로 낙하 충격 분산"
            feat_2 = text_lines[2] if len(text_lines) > 2 else "프리미엄 황변 방지 소재로 오랜 시간 투명함 유지"
            feat_3 = text_lines[3] if len(text_lines) > 3 else "기기 맞춤형 정밀 설계로 부드러운 버튼 클릭감"

            # 이미지를 Base64로 변환하여 HTML 내부에 안전하게 내장
            img = Image.open(uploaded_file)
            img.thumbnail((1000, 1000))
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            img_data_uri = f"data:image/jpeg;base64,{img_base64}"

            # BT Clear PRO 스타일 완벽 고정 템플릿 조립
            html_code = f"""
            <div style="max-width: 860px; margin: 0 auto; background-color: #ffffff; font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; color: #222222; padding: 20px; box-sizing: border-box;">
                
                <!-- 상단 후킹 배너 -->
                <div style="text-align: center; padding: 30px 20px; background-color: #f8f9fa; border-radius: 12px; margin-bottom: 30px;">
                    <h1 style="font-size: 26px; font-weight: 800; color: #111111; margin: 0 0 10px 0; letter-spacing: -0.5px;">BT Clear PRO</h1>
                    <p style="font-size: 17px; font-weight: 600; color: #0066cc; margin: 0; line-height: 1.5;">{hook_title}</p>
                </div>

                <!-- 메인 제품 이미지 섹션 -->
                <div style="text-align: center; margin-bottom: 40px; background-color: #f8f9fa; padding: 20px; border-radius: 12px;">
                    <img src="{img_data_uri}" style="width: 100%; max-width: 700px; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);" />
                </div>

                <!-- 핵심 기능 3가지 카드 섹션 -->
                <div style="margin-bottom: 40px;">
                    <h2 style="font-size: 22px; font-weight: 700; text-align: center; margin-bottom: 25px; color: #111;">🌟 3대 핵심 셀링 포인트</h2>
                    
                    <div style="background-color: #f8f9fa; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 6px solid #0066cc;">
                        <h3 style="font-size: 19px; font-weight: 700; margin: 0 0 8px 0; color: #222;">01. 에어쿠션 완벽 보호</h3>
                        <p style="font-size: 16px; line-height: 1.6; color: #555; margin: 0;">{feat_1}</p>
                    </div>

                    <div style="background-color: #f8f9fa; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 6px solid #0066cc;">
                        <h3 style="font-size: 19px; font-weight: 700; margin: 0 0 8px 0; color: #222;">02. 클리어 황변 방지</h3>
                        <p style="font-size: 16px; line-height: 1.6; color: #555; margin: 0;">{feat_2}</p>
                    </div>

                    <div style="background-color: #f8f9fa; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 6px solid #0066cc;">
                        <h3 style="font-size: 19px; font-weight: 700; margin: 0 0 8px 0; color: #222;">03. 정밀한 버튼 설계</h3>
                        <p style="font-size: 16px; line-height: 1.6; color: #555; margin: 0;">{feat_3}</p>
                    </div>
                </div>

                <!-- 스펙 요약 (INFORMATION) -->
                <div style="background-color: #f8f9fa; padding: 30px; border-radius: 12px; margin-bottom: 30px;">
                    <h2 style="font-size: 20px; font-weight: 700; text-align: center; margin-top: 0; margin-bottom: 20px; color: #111;">📋 INFORMATION</h2>
                    <table style="width: 100%; border-collapse: collapse; font-size: 15px;">
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 12px; font-weight: 700; width: 30%; color: #333;">제품명</td>
                            <td style="padding: 12px; color: #555;">BT Clear PRO 스마트폰 케이스</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 12px; font-weight: 700; color: #333;">소재</td>
                            <td style="padding: 12px; color: #555;">고탄성 TPU + 고강도 PC</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #ddd;">
                            <td style="padding: 12px; font-weight: 700; color: #333;">특징</td>
                            <td style="padding: 12px; color: #555;">에어쿠션 방어, 황변 방지, 완벽한 투명도</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; font-weight: 700; color: #333;">구성품</td>
                            <td style="padding: 12px; color: #555;">케이스 단품</td>
                        </tr>
                    </table>
                </div>

                <!-- 클로징 배너 -->
                <div style="text-align: center; padding: 25px; background-color: #111; color: #fff; border-radius: 12px;">
                    <p style="font-size: 18px; font-weight: 700; margin: 0;">지금 바로 선명하고 안전한 보호력을 경험해보세요!</p>
                </div>

            </div>
            """

            st.success("✨ 에러 없이 0.1초 만에 프리미엄 상세페이지가 완성되었습니다!")

            # 1. 웹 미리보기
            st.subheader("📱 모바일 상세페이지 미리보기")
            st.components.v1.html(html_code, height=750, scrolling=True)

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
            st.error(f"오류가 발생했습니다: {e}")
