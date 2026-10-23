def juso_gov_converter(keyword, original_zip=""):
    if not keyword or pd.isna(keyword):
        return keyword
        
    kw_str = str(keyword).strip()
    kw_str = preprocess_attached_dong(kw_str)
    
    for target_key, override_addr in SPECIAL_EXCEPTIONS.items():
        if target_key in kw_str:
            return override_addr
            
    parens = re.findall(r'\([^)]+\)', kw_str)
    for p in parens:
        kw_str = kw_str.replace(p, "").strip()
    paren_str = parens[-1] if parens else ""

    tail_detail = ""
    m_detail = re.search(r'(\d+동\s*\d+호.*|[A-Z가-힣]\s*동\s*\d+호.*|\d+\s*호.*)', kw_str)
    if m_detail:
        tail_detail = m_detail.group(1).strip()
        kw_str = kw_str[:m_detail.start()].strip()

    has_jibun_pattern = bool(re.search(r'([가-힣]+(시|도))\s+([가-힣]+(시|군|구)?(\s+[가-힣]+구)?)\s+([가-힣]+(동|읍|면|리))\s+\d+', kw_str))
    
    base_road_addr = ""
    tail_part = ""
    
    if has_jibun_pattern:
        m_jibun = re.search(r'([가-힣]+동\s*\d+(?:-\d+)?)', kw_str)
        if m_jibun:
            end_pos = m_jibun.end()
            api_query_part = kw_str[:end_pos].strip()
            tail_part = kw_str[end_pos:].strip()
        else:
            api_query_part = kw_str
            tail_part = ""

        base_road_addr = api_query_part
        
        url = "https://www.juso.go.kr/addrlink/addrLinkApi.do"
        params = {
            "confmKey": JUSO_CONFIRM_KEY,
            "currentPage": 1,
            "countPerPage": 5,
            "keyword": api_query_part,
            "resultType": "json"
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                res = response.json()
                juso_list = res.get('results', {}).get('juso', [])
                if juso_list:
                    road_addr = juso_list[0].get('roadAddr', '')
                    if road_addr:
                        base_road_addr = road_addr
        except Exception:
            pass
            
        if not base_road_addr:
            base_road_addr = api_query_part
    else:
        base_road_addr = kw_str

    parts = [base_road_addr]
    if tail_part and tail_part not in base_road_addr:
        parts.append(tail_part)
    if paren_str:
        parts.append(paren_str)
    if tail_detail:
        parts.append(tail_detail)

    final_str = ' '.join(parts)
    final_str = remove_duplicate_words(final_str)
    final_str = remove_stray_province(final_str)
    final_str = re.sub(r'\(\s*\)', '', final_str)
    return ' '.join(final_str.split())
