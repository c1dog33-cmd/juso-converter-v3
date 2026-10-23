import io
import re
import urllib.parse
import openpyxl
import pandas as pd
import requests
import streamlit as st
from openpyxl.styles import Font

# 🚀 행정안전부 도로명주소 오픈 API 승인키 적용 완료
JUSO_CONFIRM_KEY = "U01TX0FVVEgyMDI2MTAyMzE3MDUxMjEyMDgzMzI="  

def fix_zipcode(val):
    if pd.isna(val) or val is None:
        return ""
    val_str = str(val).split('.')[0].strip()
    return val_str.zfill(5) if val_str else ""

def remove_illegal_chars(val):
    if isinstance(val, str):
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', val)
    return val

# --- [ 행정안전부 주소정보누리집 API 연동 주소 변환 엔진 ] ---
def juso_gov_converter(keyword):
    if not keyword or pd.isna(keyword):
        return keyword
        
    kw_str = str(keyword).strip()
    
    # 1. 괄호 원본 분리 (예: 아파트 이름 등)
    parens = re.findall(r'\([^)]+\)', kw_str)
    for p in parens:
        kw_str = kw_str.replace(p, "").strip()
    paren_str = parens[-1] if parens else ""

    # 2. 상세 동·호수 분리 (예: 101동 202호 등)
    tail_detail = ""
    m_detail = re.search(r'(\d+동\s*\d+호.*|[A-Z가-힣]\s*동\s*\d+호.*|\d+\s*호.*)', kw_str)
    if m_detail:
        tail_detail = m_detail.group(1).strip()
        kw_str = kw_str[:m_detail.start()].strip()

    # 3. 행정안전부 주소 API 호출하여 도로명주소로 변환
    url = "https://www.juso.go.kr/addrlink/addrLinkApi.do"
    params = {
        "confmKey": JUSO_CONFIRM_KEY,
        "currentPage": 1,
        "countPerPage": 1,
        "keyword": kw_str,
        "resultType": "json"
    }
    
    base_road_addr = kw_str
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            res = response.json()
            common = res.get('results', {}).get('common', {})
            if common.get('errorCode') == '0':
                juso_list = res.get('results', {}).get('juso', [])
                if juso_list:
                    road_addr = juso_list[0].get('roadAddr', '')
                    if road_addr:
                        base_road_addr = road_addr
    except Exception:
        pass

    # 4. 최종 주소 조립: [도로명주소] + [기존 괄호] + [상세 동호수]
    parts = [base_road_addr]
    if paren_str and paren_str not in base_road_addr:
        parts.append(paren_str)
    if tail_detail:
        parts.append(tail_detail)

    final_str = ' '.join(parts)
    return ' '.join(final_str.split())

# --- [ Streamlit 웹 UI 실행 부문 ] ---
st.set_page_config(page_title="주소 변환기", page_icon="🏛️", layout="centered")

st.title("🏛️ 구주소 -> 신주소(도로명) 엑셀 자동 변환기")
st.write("엑셀 파일을 업로드하시면 구주소가 도로명주소로 깔끔하게 변환됩니다.")

uploaded_file = st.file_uploader("변환할 엑셀 파일(.xlsx, .xls)을 업로드하세요", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception:
        df = pd.read_excel(uploaded_file, engine='xlrd')

    st.write("### 📄 업로드 데이터 미리보기 (상위 5건)")
    st.dataframe(df.head())

    if 'excel_data' not in st.session_state:
        st.session_state.excel_data = None

    if st.button("🚀 주소 변환 시작"):
        with st.spinner("주소를 도로명주소로 변환하는 중입니다. 잠시만 기다려주세요..."):
            if '우편번호' in df.columns:
                df['우편번호'] = df['우편번호'].apply(fix_zipcode)

            if '배송지' in df.columns:
                progress_bar = st.progress(0)
                total = len(df)
                
                converted_addrs = []
                for i, row in df.iterrows():
                    res = juso_gov_converter(row['배송지'])
                    converted_addrs.append(res)
                    progress_bar.progress((i + 1) / total)
                    
                df['배송지'] = converted_addrs
            else:
                st.warning("[주의] 엑셀 파일에서 '배송지' 컬럼을 찾을 수 없습니다.")

            for col in df.columns:
                df[col] = df[col].apply(remove_illegal_chars)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
                worksheet = writer.sheets['Sheet1']
                
                # 열 너비 및 폰트 서식 정리
                for col in worksheet.columns:
                    max_len = 0
                    col_letter = openpyxl.utils.get_column_letter(col[0].column)
                    for cell in col:
                        val = str(cell.value or '')
                        length = sum(2 if ord(char) > 127 else 1 for char in val)
                        if length > max_len:
                            max_len = length
                    worksheet.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 80)

                font_size_8 = Font(size=9)
                for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1, max_col=len(df.columns)):
                    worksheet.row_dimensions[row[0].row].height = 18
                    for cell in row:
                        cell.font = font_size_8
                        
                if '우편번호' in df.columns:
                    zip_col_idx = df.columns.get_loc('우편번호') + 1
                    for row in range(2, worksheet.max_row + 1):
                        worksheet.cell(row=row, column=zip_col_idx).number_format = '@'

            st.session_state.excel_data = output.getvalue()
        st.success("🎉 주소 변환이 완료되었습니다!")

    if st.session_state.excel_data is not None:
        st.download_button(
            label="📥 변환된 엑셀 파일 다운로드",
            data=st.session_state.excel_data,
            file_name="도로명주소_변환완료.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
