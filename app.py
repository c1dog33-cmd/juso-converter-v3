import streamlit as st
import pandas as pd
import openpyxl
import io
import re
import hmac
import hashlib
import time
import requests

st.set_page_config(page_title="사무실 및 쿠팡그로스 통합 정산 시스템", layout="wide")

st.title("🏢 사무실 우편/택배 & 쿠팡그로스 통합 정산 대시보드")
st.write("사무실 자체 배송 폼 업로드 및 쿠팡 윙(WING) Open API 자동 연동을 통한 통합 정산 프로그램입니다.")

tab1, tab2 = st.tabs(["🏢 사무실 우편/택배 정산", "📦 쿠팡그로스 정산 (API 연동)"])

with tab1:
    st.subheader("1. 사무실 우편·등기·택배 파일 업로드 및 누적 정산")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_master = st.file_uploader("📂 기존 통합 관리 엑셀 파일 업로드 (.xlsx)", type=["xlsx"], key="master")
    with col2:
        uploaded_daily = st.file_uploader("📄 오늘 출고/우편배송 폼 파일 업로드 (.xls / .xlsx)", type=["xls", "xlsx"], key="daily")

    target_date = st.date_input("📅 정산 적용 출고 일자 선택", key="date_office")

    if st.button("🚀 사무실 정산 및 대시보드 자동 업데이트 실행", type="primary", key="btn_office"):
        if uploaded_master is None or uploaded_daily is None:
            st.error("기존 통합 엑셀 파일과 오늘의 출고 폼 파일을 모두 업로드해 주세요!")
        else:
            try:
                wb = openpyxl.load_workbook(uploaded_master)
                ws_log = wb['출고세부일지']
                ws_daily = wb['일별판매표']
                
                if uploaded_daily.name.endswith('.xls'):
                    df_daily = pd.read_excel(uploaded_daily, sheet_name=0, engine='xlrd')
                else:
                    df_daily = pd.read_excel(uploaded_daily, sheet_name=0)
                    
                date_str = target_date.strftime("%Y-%m-%d")
                
                # 중복 날짜 행 삭제 (덮어쓰기 기능)
                rows_to_delete = []
                for r in range(4, ws_log.max_row + 1):
                    row_date = ws_log.cell(row=r, column=1).value
                    if row_date and str(row_date).startswith(date_str):
                        rows_to_delete.append(r)
                for r in reversed(rows_to_delete):
                    ws_log.delete_rows(r)
                    
                next_row = ws_log.max_row + 1
                if next_row < 4:
                    next_row = 4
                    
                max_p_row = 35
                
                for idx, row in df_daily.iterrows():
                    recipient = row.get('수취인명', '')
                    opt = str(row.get('선택정보', '')).strip()
                    
                    qty_raw = row.get('Unnamed: 6', 1) if 'Unnamed: 6' in row else 1
                    qty = 1
                    try:
                        if pd.notna(qty_raw):
                            qty = int(float(str(qty_raw).strip()))
                    except:
                        qty = 1
                    
                    has_film = False
                    if '+필름' in opt or '필름' in opt:
                        has_film = True
                        
                    clean_model = opt.replace('+필름', '').replace('필름', '').strip()
                    clean_model = re.sub(r'\[\d+\]', '', clean_model).strip()
                    clean_model = clean_model.replace(' 택배', '').strip()
                    
                    if clean_model == 'A20/A30':
                        model = 'A20/30'
                    elif clean_model in ['노트10플러스', '노트10']:
                        model = '노트10플러스'
                    elif clean_model == 'S10 5G':
                        model = 'S10'
                    else:
                        model = clean_model
                        
                    if '[2]' in opt:
                        qty = 2
                    elif '[3]' in opt:
                        qty = 3
                        
                    ship_type = '우편(1개)'
                    if qty == 2 or '우편(2개)' in opt:
                        ship_type = '우편(2개)'
                    elif has_film:
                        ship_type = '등기(필름)'
                    elif '택배' in opt:
                        ship_type = '택배'
                        
                    curr_row = next_row + idx
                    ws_log.cell(row=curr_row, column=1, value=date_str)
                    ws_log.cell(row=curr_row, column=2, value=recipient)
                    ws_log.cell(row=curr_row, column=3, value=opt)
                    ws_log.cell(row=curr_row, column=4, value=model)
                    ws_log.cell(row=curr_row, column=5, value=ship_type)
                    ws_log.cell(row=curr_row, column=6, value=qty)
                    
                    ws_log.cell(row=curr_row, column=7, value=f'=IF(E{curr_row}="등기(필름)", 4900, IF(E{curr_row}="우편(1개)", VLOOKUP(D{curr_row}, 상품단가표!$B$4:$G${max_p_row}, 3, FALSE), IF(E{curr_row}="우편(2개)", VLOOKUP(D{curr_row}, 상품단가표!$B$4:$G${max_p_row}, 4, FALSE)/2, IF(E{curr_row}="등기", VLOOKUP(D{curr_row}, 상품단가표!$B$4:$G${max_p_row}, 5, FALSE), VLOOKUP(D{curr_row}, 상품단가표!$B$4:$G${max_p_row}, 6, FALSE)))))')
                    ws_log.cell(row=curr_row, column=8, value=f'=IF(E{curr_row}="등기(필름)", VLOOKUP(D{curr_row}, 상품단가표!$B$4:$G${max_p_row}, 2, FALSE) + 1200, VLOOKUP(D{curr_row}, 상품단가표!$B$4:$G${max_p_row}, 2, FALSE))')
                    ws_log.cell(row=curr_row, column=9, value=f'=IF(OR(E{curr_row}="등기(필름)", E{curr_row}="등기"), 1800, IF(E{curr_row}="우편(1개)", 590, IF(E{curr_row}="우편(2개)", 710, 2600)))')
                    ws_log.cell(row=curr_row, column=10, value=f'=F{curr_row}*G{curr_row}')
                    ws_log.cell(row=curr_row, column=11, value=f'=F{curr_row}*H{curr_row}')
                    ws_log.cell(row=curr_row, column=12, value=f'=I{curr_row}')
                    ws_log.cell(row=curr_row, column=13, value=f'=J{curr_row}-K{curr_row}-L{curr_row}')
                    
                    for c in range(1, 14):
                        cell = ws_log.cell(row=curr_row, column=c)
                        cell.font = openpyxl.styles.Font(name='맑은 고딕', size=10)
                        cell.border = openpyxl.styles.Border(left=openpyxl.styles.Side(style='thin', color='BFBFBF'),
                                                             right=openpyxl.styles.Side(style='thin', color='BFBFBF'),
                                                             top=openpyxl.styles.Side(style='thin', color='BFBFBF'),
                                                             bottom=openpyxl.styles.Side(style='thin', color='BFBFBF'))
                        if c in [6, 7, 8, 9, 10, 11, 12, 13]:
                            cell.alignment = openpyxl.styles.Alignment(horizontal='right', vertical='center')
                            cell.number_format = '#,##0'
                        else:
                            cell.alignment = openpyxl.styles.Alignment(horizontal='center', vertical='center')

                output = io.BytesIO()
                wb.save(output)
                output.seek(0)
                
                st.success(f"🎉 성공적으로 반영되었습니다! ({date_str} 기준 {len(df_daily)}건 처리 완료)")
                st.download_button(
                    label="📥 정산 완료된 엑셀 파일 다운로드하기",
                    data=output,
                    file_name=f"사무실_통합정산관리표_{date_str}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"처리 중 오류가 발생했습니다: {e}")

with tab2:
    st.subheader("📦 쿠팡 윙(WING) 로켓그로스 API 자동 연동 및 정산")
    st.write("발급받으신 쿠팡 API 키를 입력하시면, 로켓그로스 판매 내역을 자동으로 불러올 수 있습니다.")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        vendor_id = st.text_input("업체코드 (Vendor ID)", type="default")
    with col_b:
        access_key = st.text_input("Access Key", type="password")
    with col_c:
        secret_key = st.text_input("Secret Key", type="password")
        
    start_dt = st.date_input("조회 시작일", key="coupang_start")
    end_dt = st.date_input("조회 종료일", key="coupang_end")
    
    if st.button("🔄 로켓그로스 데이터 자동 조회", type="primary"):
        if not vendor_id or not access_key or not secret_key:
            st.error("업체코드, Access Key, Secret Key를 모두 입력해 주세요!")
        else:
            try:
                def generate_signature(method, path, query=""):
                    datetime_str = time.strftime('%y%m%d', time.gmtime()) + 'T' + time.strftime('%H%M%S', time.gmtime()) + 'Z'
                    message = datetime_str + method.upper() + path + (query if query else "")
                    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
                    authorization = f"CEA algorithm=HmacSHA256, access-key={access_key}, signed-date={datetime_str}, signature={signature}"
                    return authorization

                method = "GET"
                # 로켓그로스 전용 API 경로로 수정 완료
                path = f"/v2/providers/rg_open_api/apis/api/v1/vendors/{vendor_id}/rg/orders"
                query = f"createdAtFrom={start_dt.strftime('%Y-%m-%d')}&createdAtTo={end_dt.strftime('%Y-%m-%d')}"
                
                auth_header = generate_signature(method, path, query)
                headers = {
                    "Authorization": auth_header,
                    "Content-Type": "application/json",
                    "X-Requested-By": vendor_id,
                    "X-MARKET": "KR"
                }
                
                url = f"https://api-gateway.coupang.com{path}?{query}"
                
                with st.spinner("쿠팡 로켓그로스 서버에서 데이터를 불러오는 중입니다..."):
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        st.success("🎉 쿠팡 로켓그로스 데이터를 성공적으로 불러왔습니다!")
                        st.json(data)
                    else:
                        st.warning(f"쿠팡 API 응답 코드: {response.status_code}. 입력하신 업체코드와 키를 다시 확인해주세요. (응답: {response.text})")
            except Exception as e:
                st.error(f"API 연동 중 오류 발생: {e}")
