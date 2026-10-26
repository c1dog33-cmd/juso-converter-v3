import io
import re
import openpyxl
import pandas as pd
import streamlit as st
from openpyxl.styles import Font

def fix_zipcode(val):
    if pd.isna(val) or val is None:
        return ""
    val_str = str(val).split('.')[0].strip()
    return val_str.zfill(5) if val_str else ""

def remove_illegal_chars(val):
    if isinstance(val, str):
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', val)
    return val

def remove_duplicate_parentheses(addr_str):
    if not addr_str:
        return addr_str
    parts = re.split(r'(\([^)]+\))', addr_str)
    seen = set()
    new_parts = []
    for part in parts:
        if part.startswith('(') and part.endswith(')'):
            normalized = re.sub(r'\s+', '', part)
            if normalized in seen:
                continue
            seen.add(normalized)
            new_parts.append(part)
        else:
            new_parts.append(part)
    return ''.join(new_parts)

# --- [ 주소 완벽 스마트 정제 엔진 (API 오류 방지 및 구조 최적화) ] ---
def smart_address_cleaner(keyword):
    if not keyword or pd.isna(keyword):
        return keyword
        
    s = str(keyword).strip()
    
    # 1. 중복된 주소나 문장이 반복되는 경우 제거 (예: 동일 텍스트가 두 번 들어간 경우)
    words = s.split()
    if len(words) > 6 and words[:len(words)//2] == words[len(words)//2:]:
        s = ' '.join(words[:len(words)//2])

    # 2. 괄호(메모, 법정동 등) 분리
    parens = re.findall(r'\([^)]+\)', s)
    for p in parens:
        s = s.replace(p, "").strip()
    paren_str = parens[-1] if parens else ""

    # 3. 상세 동·호수 및 층수 분리 (예: 101동 1002호, 606호, 3층 등)
    tail_detail = ""
    m_detail = re.search(r'(\d+동\s*\d+호.*|[A-Z가-힣]\s*동\s*\d+호.*|\d+\s*호.*|\d+층.*)', s)
    if m_detail:
        tail_detail = m_detail.group(1).strip()
        s = s[:m_detail.start()].strip()

    # 동, 호수 사이에 띄어쓰기가 안 된 경우 자동 보정 (예: 107동109호 -> 107동 109호)
    if tail_detail:
        tail_detail = re.sub(r'(\d+동)(\d+호)', r'\1 \2', tail_detail)
        tail_detail = re.sub(r'([A-Z가-힣]\s*동)(\d+호)', r'\1 \2', tail_detail)

    # 4. 최종 조립: [기본 주소] + [상세 동호수/층] + [괄호 메모]
    parts = [s]
    if tail_detail and tail_detail not in s:
        parts.append(tail_detail)
    if paren_str and paren_str not in ' '.join(parts):
        parts.append(paren_str)

    final_str = ' '.join(parts)
    final_str = remove_duplicate_parentheses(final_str)
    return ' '.join(final_str.split())

def clean_product_name(val):
    if pd.isna(val) or not str(val).strip():
        return val
    s = str(val).strip()
    
    has_film = False
    if ('풀액정필름2장' in s or '추가액정필름' in s) and '필요없음' not in s and ('풀액정' in s or '액정필름' in s):
        has_film = True

    target_texts = [s]
    if '//' in s: target_texts.insert(0, s.split('//')[-1])
    if '모델선택:' in s: target_texts.insert(0, s.split('모델선택:')[-1])
    if '/' in s: target_texts.insert(0, s.split('/')[-1])

    smartphone_match = None
    for t in target_texts:
        smartphone_match = re.search(r'(S\s*10\s*5G|S\s*10\s*플러스|S\s*20\s*플러스|S\s*20\s*울트라|S\s*22\s*플러스|S\s*22\s*울트라|노트\s*10\s*플러스|노트\s*20\s*울트라|노트\s*20\s*플러스|노트\s*\d+\s*울트라|노트\s*\d+\s*플러스|노트\s*\d+|S\s*\d+(?:\s*플러스|\s*울트라|\s*5G|\s*엣지)?|A\s*\d+|Z\s*(?:플립|폴드)\s*\d*|와이드\s*\d+|N\s*\d+|V\s*50S|V\s*50|V\s*\d+|벨벳|윙)', t, re.IGNORECASE)
        if smartphone_match: break

    if not smartphone_match:
        smartphone_match = re.search(r'(S\s*10\s*5G|S\s*10\s*플러스|S\s*20\s*플러스|S\s*20\s*울트라|S\s*22\s*플러스|S\s*22\s*울트라|노트\s*10\s*플러스|노트\s*20\s*울트라|노트\s*20\s*플러스|노트\s*\d+\s*울트라|노트\s*\d+\s*플러스|노트\s*\d+|S\s*\d+(?:\s*플러스|\s*울트라|\s*5G|\s*엣지)?|A\s*\d+|Z\s*(?:플립|폴드)\s*\d*|와이드\s*\d+|N\s*\d+|V\s*50S|V\s*50|V\s*\d+|벨벳|윙)', s, re.IGNORECASE)

    if smartphone_match:
        raw_model = smartphone_match.group(1).replace(" ", "").upper()
        if raw_model == 'S105G': target_model = 'S10 5G'
        elif raw_model == 'S10플러스': target_model = 'S10플러스'
        elif raw_model == 'S20플러스': target_model = 'S20플러스'
        elif raw_model == 'S22플러스': target_model = 'S22플러스'
        elif raw_model == '노트10플러스': target_model = '노트10플러스'
        elif raw_model in ['N960', 'SM-N960']: target_model = '노트9'
        elif raw_model == 'V50S': target_model = 'V50S'
        elif raw_model == 'V50': target_model = 'V50'
        elif raw_model == '노트20울트라': target_model = '노트20울트라'
        elif raw_model == '와이드5': target_model = 'A22'
        elif raw_model == '와이드6': target_model = 'A13'
        else: target_model = raw_model

        qty = 1
        if '☞' in s:
            parts = s.split('☞')
            after = parts[1].strip() if len(parts) > 1 else ""
            qty_match = re.match(r'^(\d+)\s*(EA|개)?', after, re.IGNORECASE)
            if qty_match: qty = int(qty_match.group(1))
        
        res = f"{target_model}[{qty}]" if qty > 1 else target_model
        if has_film: res += " +필름"
        if '택배' in s or '택배배송' in s: res += " 택배"
        return res
    
    if '케이스' not in s:
        res = s
        if has_film: res += " +필름"
        return res
    
    qty = 1
    if '☞' in s:
        parts = s.split('☞')
        base = parts[0].strip()
        after = parts[1].strip() if len(parts) > 1 else ""
        qty_match = re.match(r'^(\d+)\s*(EA|개)?', after, re.IGNORECASE)
        if qty_match: qty = int(qty_match.group(1))
    else:
        base = s
        
    if '모델선택:' in base:
        parts = base.split('모델선택:')
        target = parts[-1].strip()
        if '/' in target: target = target.split('/')[0].strip()
        if ',' in target: target = target.split(',')[0].strip()
    else:
        sub_parts = re.split(r'[/]{1,2}', base)
        target = sub_parts[-1].strip() if len(sub_parts) > 1 else base
        
    target = re.sub(r'\([^)]*\)', '', target).strip()
    target = re.sub(r'케이스', '', target)
    target = re.sub(r'풀액정', '', target)
    target = re.sub(r'2장', '', target)
    target = re.sub(r'클리어', '', target)
    target = re.sub(r'투명', '', target)
    target = re.sub(r'갤럭시', '', target)
    target = ' '.join(target.split())
    
    if target == '와이드5': target = 'A22'
    elif target == '와이드6': target = 'A13'
    
    result_str = f"{target}[{qty}]" if qty > 1 else target
    if '택배' in s or '택배배송' in s: result_str = f"{result_str} 택배"
    if has_film: result_str = f"{result_str} +필름"
        
    return result_str

# --- [ Streamlit 웹 UI 실행 부문 ] ---
st.set_page_config(page_title="스마트 주소 및 상품명 정제기", page_icon="🏛️", layout="centered")

st.title("🏛️ 스마트 주소 및 상품명 엑셀 자동 정제기")
st.write("엑셀 파일을 업로드하시면 주소 오탈자, 동·호수 띄어쓰기, 건물명 및 상품명이 완벽하게 정리됩니다.")

uploaded_file = st.file_uploader("변환할 엑셀 파일(.xlsx, .xls, .xlsb)을 업로드하세요", type=["xlsx", "xls", "xlsb"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception:
        try:
            df = pd.read_excel(uploaded_file, engine='xlrd')
        except Exception as e:
            st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
            df = None

    if df is not None:
        st.write("### 📄 업로드 데이터 미리보기 (상위 5건)")
        st.dataframe(df.head())

        if 'excel_data' not in st.session_state:
            st.session_state.excel_data = None

        if st.button("🚀 주소 및 상품명 정제 시작"):
            with st.spinner("데이터를 깔끔하게 정리하는 중입니다..."):
                if '우편번호' in df.columns:
                    df['우편번호'] = df['우편번호'].apply(fix_zipcode)

                if '선택정보' in df.columns:
                    df['선택정보'] = df['선택정보'].apply(clean_product_name)
                elif len(df.columns) >= 5:
                    col_name_e = df.columns[4]
                    df[col_name_e] = df[col_name_e].apply(clean_product_name)

                if '배송지' in df.columns:
                    progress_bar = st.progress(0)
                    total = len(df)
                    
                    cleaned_addrs = []
                    for i, row in df.iterrows():
                        res = smart_address_cleaner(row['배송지'])
                        cleaned_addrs.append(res)
                        progress_bar.progress((i + 1) / total)
                        
                    df['배송지'] = cleaned_addrs
                else:
                    st.warning("[주의] 엑셀 파일에서 '배송지' 컬럼을 찾을 수 없습니다.")

                for col in df.columns:
                    df[col] = df[col].apply(remove_illegal_chars)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                    worksheet = writer.sheets['Sheet1']
                    
                    for col in worksheet.columns:
                        max_len = 0
                        col_letter = openpyxl.utils.get_column_letter(col[0].column)
                        for cell in col:
                            val = str(cell.value or '')
                            length = sum(2 if ord(char) > 127 else 1 for char in val)
                            if length > max_len:
                                max_len = length
                        worksheet.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 80)

                    font_size_8 = Font(size=8)
                    for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1, max_col=len(df.columns)):
                        worksheet.row_dimensions[row[0].row].height = 18
                        for cell in row:
                            cell.font = font_size_8
                            
                    if '우편번호' in df.columns:
                        zip_col_idx = df.columns.get_loc('우편번호') + 1
                        for row in range(2, worksheet.max_row + 1):
                            worksheet.cell(row=row, column=zip_col_idx).number_format = '@'

                st.session_state.excel_data = output.getvalue()
            st.success("🎉 주소 및 상품명 정리가 완료되었습니다!")

        if st.session_state.excel_data is not None:
            st.download_button(
                label="📥 정제된 엑셀 파일 다운로드",
                data=st.session_state.excel_data,
                file_name="주소_상품명_스마트정제완료.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
