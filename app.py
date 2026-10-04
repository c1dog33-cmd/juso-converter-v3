import os
from google import genai
from google.genai import types
from PIL import Image

# 1. API 클라이언트 초기화 (구글 AI Studio에서 발급받은 API 키 입력)
# 또는 환경 변수(GEMINI_API_KEY)에 설정해 둘 수 있습니다.
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

def generate_coupang_detail_page(image_path, chinese_text):
    """
    알리익스프레스 이미지와 중국어 원본 텍스트를 받아 
    쿠팡 맞춤형 상세페이지 기획안을 생성하는 함수
    """
    # 이미지 불러오기
    try:
        img = Image.open(image_path)
    except Exception as e:
        return f"이미지 파일을 열 수 없습니다: {e}"

    # 프롬프트 작성 (지시사항)
    prompt = f"""
    당신은 쿠팡 전문 베스트셀러 상세페이지 기획자입니다.
    아래 제공된 알리익스프레스 상품의 중국어 원본 텍스트와 이미지를 분석하여,
    한국 쿠팡 고객의 구매 심리를 자극할 수 있는 매력적인 상세페이지 기획안을 작성해 주세요.

    [알리익스프레스 중국어 원본 텍스트]
    {chinese_text}

    [출력 양식]
    1. 최상단 후킹 카피 (고객의 시선을 사로잡는 문구)
    2. 핵심 셀링 포인트 3가지 (기능 및 장점 상세 설명)
    3. 추천 타겟 고객
    4. 쿠팡 요약 스펙 정리
    """

    # Gemini 2.5 Flash 모델 호출 (비전 기능 활용)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[img, prompt]
    )

    return response.text

# --- [사용 예시] ---
if __name__ == "__main__":
    # 테스트할 알리 이미지 경로와 중국어 설명 입력
    image_file = "ali_product_sample.jpg"  # 알리에서 다운받은 이미지 파일명
    raw_chinese_desc = "45W超快充 10000mAh自带双线 充电宝 迷你便携"  # 알리 상세페이지의 중국어 텍스트
    
    result = generate_coupang_detail_page(image_file, raw_chinese_desc)
    
    print("=== [쿠팡 상세페이지 자동 생성 결과] ===")
    print(result)
