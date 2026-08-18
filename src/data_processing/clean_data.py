import pandas as pd
import numpy as np
import re

IT_KEYWORDS = [
    "phân tích dữ liệu", "data analyst", "kỹ sư dữ liệu", "data engineer", "khoa học dữ liệu", "data scientist",
    "trí tuệ nhân tạo", "ai engineer", "học máy", "machine learning", "học sâu", "deep learning", "mlops",
    "xử lý ngôn ngữ tự nhiên", "nlp", "thị giác máy tính", "computer vision", "front-end", "frontend",
    "back-end", "backend", "full stack", "fullstack", "phần mềm", "software", "java ", " java", ".net",
    "python", "php", "node", "android", "ios", "flutter", "c++", "c#", "golang", "ruby", "kiểm thử",
    "qa engineer", "qc engineer", "tester", "automation test", "manual test", "devops", "điện toán đám mây",
    "cloud", "sre", "site reliability", "an toàn thông tin", "an ninh mạng", "security", "kiểm thử xâm nhập",
    "penetration", "pentest", "soc analyst", "incident response", "quản trị hệ thống", "system admin",
    "sysadmin", "system engineer", "quản trị mạng", "network", "quản trị cơ sở dữ liệu", "dba",
    "phân tích nghiệp vụ", "business analyst", " ba ", "phân tích hệ thống", "system analyst", "quản lý sản phẩm",
    "product manager", "pm", "product owner", "po", "quản lý dự án cntt", "project manager", "it project",
    "scrum master", "thiết kế giao diện", "trải nghiệm người dùng", "ui designer", "ux designer", "ui/ux",
    "it support", "it helpdesk", "hỗ trợ cntt", "hỗ trợ kỹ thuật", "blockchain", "web3", "nhúng", "embedded",
    "firmware", "iot", "game developer", "thiết kế game", "game designer", "solution architect", "giải pháp",
    "software architect", "tech lead", "technical lead", "trưởng nhóm kỹ thuật", "principal engineer", "staff engineer"
]


def rename_columns_and_init(df):
    column_mapping = {
        'id': 'job_id', 'comp': 'company_name', 'size': 'company_size',
        'level': 'job_level', 'exp': 'experience_year', 'type': 'job_type',
        'remote': 'is_remote', 'post_date': 'posted_date', 'url': 'job_url'
    }
    df = df.rename(columns=column_mapping)
    df = df.dropna(subset=['title', 'company_name'])
    return df


def filter_it_jobs(df):
    """Lọc các Job IT dựa trên bộ từ khóa chuẩn (Logic từ remove_job_not_it.py)"""

    def is_it_job(title):
        if pd.isna(title): return False
        return any(keyword in str(title).lower() for keyword in IT_KEYWORDS)

    return df[df['title'].apply(is_it_job)].copy()


def process_title(df):
    """Kết hợp dọn rác (Colab) + Chuẩn hóa danh xưng tiếng Anh (clean_data_pipeline.py)"""

    def clean_text(title):
        if pd.isna(title) or not str(title).strip(): return ""
        title = str(title).strip()

        # 1. Logic dọn rác (Từ Colab)
        title = re.sub(r'(?i)^[a-z0-9\.]+\s*-\s*', '', title)  # Mã phòng ban
        title = re.sub(r'\[.*?\]', '', title)
        title = re.sub(r'(?i)(\-?\s*(ID|MSCV)\s*\d+.*)', '', title)
        title = re.sub(r'\(\d+[A-Z]+\d+\)', '', title)
        title = re.sub(r'(?i)(\-?\s*(thu nhập|lương|upto|up to|usd|\$).*)', '', title)
        title = re.sub(r'(?i)(\-?\s*(tại|ở|kcn|kcx|vsip)\s+.*)', '', title)
        urgency_words = ['đi làm ngay', 'nhận việc ngay', 'tuyển gấp', 'gấp', 'không yêu cầu kinh nghiệm',
                         'mới ra trường', 'nhận fresher', 'nghỉ t7 cn', 'nghỉ thứ 7', 'nghỉ t7', 'nghỉ thứ bảy']
        for word in urgency_words: title = re.sub(rf'(?i)\-?\s*\b{word}\b.*', '', title)
        title = re.sub(r'(?i)\b(nam/nữ|nam|nữ)\b\s+', '', title)
        title = re.sub(r'(?i)\(?\s*làm việc\s*$', '', title)
        title = re.sub(r'\([^)]*$', '', title)
        title = title.strip(" -/|,*()_:")

        # 2. Logic NLP Mapping (Từ clean_data_pipeline.py)
        title = re.sub(r'(?i)Phân Tích Dữ cycle', 'Phân Tích Dữ Liệu', title)
        title = re.sub(r'(?i)tuyển dụng\s+', '', title)
        title = re.sub(r'(?i)\-\s*khối dữ liệu|\-\s*khối pháp chế và tuân thủ|\-\s*khối quản trị rủi ro', '', title)
        title = re.sub(r'(?i)\-\s*ngành food', '(F&B)', title)

        if re.search(r'(?i)phát hiện gian lận', title): return "Fraud Data Analyst"
        if re.search(r'(?i)dữ liệu tuân thủ', title): return "Compliance Data Analyst"
        if re.search(r'(?i)Physical Security|CCTV|Sales Manager', title): return "TO_BE_DELETED"

        is_intern = bool(re.search(r'(?i)thực tập sinh|thực tập|\bintern\b|\binternship\b', title))
        title = re.sub(r'(?i)thực tập sinh|thực tập|\bintern\b|\binternship\b', '', title).strip()

        title = re.sub(r'(?i)chuyên viên chính|chuyên viên cao cấp|cấp cao', 'Senior ', title)
        title = re.sub(r'(?i)trưởng phòng|quản lý|trưởng ban', 'Manager ', title)
        title = re.sub(r'(?i)trưởng nhóm', 'Lead ', title)
        title = re.sub(r'(?i)lập trình viên\s+([a-zA-Z\+\#\.]+)', r'\1 Developer', title)
        title = re.sub(r'(?i)kỹ sư\s+([a-zA-Z\+\#\.]+)', r'\1 Engineer', title)

        mapping = {
            r'(?i)kiểm thử phần mềm|nhân viên kiểm thử|kiểm thử viên|nhân viên tester': 'Software Tester',
            r'(?i)quản trị hệ thống mạng và máy chủ|quản trị hệ thống|khai thác và quản trị hệ thống': 'System Administrator',
            r'(?i)quản trị mạng và bảo mật|quản trị mạng': 'Network Administrator',
            r'(?i)phân tích nghiệp vụ|phân tích kinh doanh': 'Business Analyst',
            r'(?i)phân tích dữ liệu|phân tích khách hàng cá nhân|phân tích khách hàng doanh nghiệp': 'Data Analyst',
            r'(?i)kỹ sư dữ liệu': 'Data Engineer',
            r'(?i)khoa học dữ liệu': 'Data Scientist'
        }
        for vi, en in mapping.items(): title = re.sub(vi, en, title)
        for p in [r'(?i)^nhân\s*viên\s+', r'(?i)^chuyên\s*viên\s+', r'(?i)^kỹ\s*sư\s+',
                  r'(?i)^lập\s*trình\s*viên\s+']: title = re.sub(p, '', title)

        if is_intern and not re.search(r'(?i)intern', title): title += " Intern"

        # In hoa chữ cái đầu và chuẩn hóa từ khóa IT
        title = title.title()
        it_keywords = {r'\bIt\b': 'IT', r'\bAi\b': 'AI', r'\bUi/Ux\b': 'UI/UX', r'\bBa\b': 'BA', r'\bC\+\+\b': 'C++',
                       r'\bC#\b': 'C#', r'\b\.Net\b': '.NET', r'\bSql\b': 'SQL'}
        for wrong, right in it_keywords.items(): title = re.sub(wrong, right, title, flags=re.IGNORECASE)

        return re.sub(r'^[-/|\s]+|[-/|\s]+$', '', title).strip()

    df['title'] = df['title'].apply(clean_text)
    df = df[df['title'] != 'TO_BE_DELETED']
    return df


def process_company_name(df):
    """Kết hợp logic Colab và clean_company_pipeline.py"""

    def clean_comp(name):
        if pd.isna(name) or not str(name).strip(): return ""
        name = re.sub(r'\s+', ' ', str(name)).strip()
        name = re.sub(r'(?i)\s+Pro Company$', '', name)

        if re.search(r'(?i)^Bảo Mật$|^Chương Trình Học Viện Công Nghệ$|^Công ty Technology VN$',
                     name): return "TO_BE_DELETED"

        name = re.sub(r'(?i)\bTrách Nhiệm Hữu Hạn\b|\bTnhh\b', 'TNHH', name)
        name = re.sub(r'(?i)\bCố Phần\b|\bCổ phần\b|\bCổ Phần\b|\bCTCP\b|\bCp\b', 'CP', name)
        name = re.sub(r'(?i)\bThương Mại Cổ Phần\b|\bThương Mại CP\b|\bTmcp\b', 'TMCP', name)
        name = re.sub(r'(?i)\bMột Thành Viên\b|\bMtv\b', 'MTV', name)
        name = re.sub(r'(?i)\s+Company Limited$', '', name).strip()
        name = re.sub(r'(?i)\s+Corporation$', '', name).strip()

        name = name.title()
        abbrs = {r'\bCp\b': 'CP', r'\bTnhh\b': 'TNHH', r'\bMtv\b': 'MTV', r'\bTmcp\b': 'TMCP', r'\bFpt\b': 'FPT',
                 r'\bVnpt\b': 'VNPT', r'\bIt\b': 'IT'}
        for abbr, upper in abbrs.items(): name = re.sub(abbr, upper, name)
        return re.sub(r'^[-,\s]+|[-,\s]+$', '', name).strip()

    df['company_name'] = df['company_name'].apply(clean_comp)
    df = df[df['company_name'] != 'TO_BE_DELETED']
    return df


def process_company_size(df):
    def clean_size(text):
        if pd.isna(text): return None
        text = str(text).strip()
        text = re.sub(r'(?i).*?quy mô\s*:\s*', '', text).strip()
        if text.lower() in ['chưa cập nhật', 'đang cập nhật', 'không xác định', 'nan', 'null', '']: return None
        return text

    if 'company_size' in df.columns: df['company_size'] = df['company_size'].apply(clean_size)
    return df


def process_location(df):
    if 'job_loc' in df.columns and 'comp_loc' in df.columns:
        df['location'] = df['job_loc'].combine_first(df['comp_loc'])

    loc_mapping = {'hcm': 'Hồ Chí Minh', 'hồ chí minh': 'Hồ Chí Minh', 'hn': 'Hà Nội', 'hà nội': 'Hà Nội',
                   'đà nẵng': 'Đà Nẵng'}

    def map_loc(text):
        text = str(text).lower()
        for key, value in loc_mapping.items():
            if key in text: return value
        return "Khác"

    if 'location' in df.columns: df['location'] = df['location'].apply(map_loc)
    return df


def process_job_level(df):
    if 'job_level' in df.columns:
        df['job_level'] = df['job_level'].astype(str).str.strip().str.capitalize()
        df['job_level'] = df['job_level'].replace('Nan', None)
    return df


def process_experience(df):
    """Suy diễn kinh nghiệm từ cột Yêu cầu và Mô tả (Colab logic)"""

    def parse_exp(row):
        raw_exp = str(row.get('experience_year', '')).lower()
        jd_text = str(row.get('req', '')).lower() + " " + str(row.get('desc', '')).lower()

        if re.search(r'\b[1-2]\s*(?:năm|year)\s*(?:kinh nghiệm|exp|làm việc)', jd_text) or re.search(
            r'(?:ít nhất|tối thiểu|từ|yêu cầu)\s*[1-2]\s*(?:năm|year)', jd_text): return '1-3 năm'
        if re.search(r'\b[3-4]\s*(?:năm|year)\s*(?:kinh nghiệm|exp|làm việc)', jd_text) or re.search(
            r'(?:ít nhất|tối thiểu|từ|yêu cầu)\s*[3-4]\s*(?:năm|year)', jd_text): return '3-5 năm'
        if re.search(r'\b[5-9]\s*(?:năm|year)\s*(?:kinh nghiệm|exp|làm việc)', jd_text) or re.search(
            r'(?:ít nhất|tối thiểu|từ|yêu cầu)\s*[5-9]\s*(?:năm|year)', jd_text): return '5+ năm'

        if re.search(r'[1-2]\s*(năm|year)', raw_exp): return '1-3 năm'
        if re.search(r'[3-4]\s*(năm|year)', raw_exp): return '3-5 năm'
        if re.search(r'[5-9]\s*(năm|year)', raw_exp): return '5+ năm'
        return 'Không yêu cầu kinh nghiệm'

    if 'experience_year' in df.columns: df['experience_year'] = df.apply(parse_exp, axis=1)
    return df


def process_salary_and_nego(df):
    df['salary_min'] = np.nan
    df['salary_max'] = np.nan
    df['is_negotiable'] = False

    for index, row in df.iterrows():
        salary_text = str(row.get('salary', '')).lower().replace(',', '')
        is_nego_flag = str(row.get('nego', '')).strip().lower()
        is_nego = True if ('true' in is_nego_flag or is_nego_flag == '1' or any(
            w in salary_text for w in ['thỏa thuận', 'thương lượng', 'cạnh tranh', 'negotiable'])) else False

        df.at[index, 'is_negotiable'] = is_nego
        if is_nego: continue

        numbers = [float(n) for n in re.findall(r'\d+\.?\d*', salary_text)]
        multiplier = 1000000 if ('triệu' in salary_text or 'tr' in salary_text) else 1

        if len(numbers) >= 2:
            s_min, s_max = numbers[0] * multiplier, numbers[1] * multiplier
            df.at[index, 'salary_min'], df.at[index, 'salary_max'] = min(s_min, s_max), max(s_min, s_max)
        elif len(numbers) == 1:
            if 'lên đến' in salary_text or 'up to' in salary_text or 'tối đa' in salary_text:
                df.at[index, 'salary_max'] = numbers[0] * multiplier
            else:
                df.at[index, 'salary_min'] = numbers[0] * multiplier

    # Bổ sung logic SQL: Boolean cho SQL (True/False -> 1/0)
    df['is_negotiable'] = df['is_negotiable'].astype(int)
    return df


def process_job_type_and_remote(df):
    # Cột Job Type
    if 'job_type' in df.columns:
        def fix_type(text):
            text = str(text).strip().lower()
            if 'người' in text or text == 'nan' or 'toàn thời gian' in text or 'full' in text: return 'Toàn thời gian'
            if 'bán thời gian' in text or 'part' in text: return 'Bán thời gian'
            if 'thực tập' in text or 'intern' in text: return 'Thực tập'
            if 'tự do' in text or 'freelance' in text: return 'Tự do'
            if 'thời vụ' in text or 'hợp đồng' in text: return 'Thời vụ / Dự án'
            return text.capitalize()

        df['job_type'] = df['job_type'].apply(fix_type)

    # Cột Remote (Logic từ load_job_posting.py)
    if 'is_remote' in df.columns:
        df['is_remote'] = df['is_remote'].fillna(False).astype(int)
    return df


def process_dates(df):
    # Logic từ load_job_posting.py (Chuẩn hóa Format YYYY-MM-DD cho SQL)
    if 'posted_date' in df.columns:
        df['posted_date'] = pd.to_datetime(df['posted_date'], errors='coerce', format='mixed').dt.strftime('%Y-%m-%d')
        df = df.dropna(subset=['posted_date'])
    if 'crawled_at' in df.columns:
        df['crawled_at'] = pd.to_datetime(df['crawled_at'], errors='coerce', format='mixed').dt.strftime('%Y-%m-%d')
    return df


def process_nlp_texts(df):
    def clean_text_for_ai(text):
        if pd.isna(text): return None
        text = str(text).strip()
        text = text.replace('#NAME?', ' ')
        text = re.sub(r'^[\=\+\-\@]+', '', text)
        text = re.sub(r'http[s]?://\S+|www\.\S+|[\w\.-]+@[\w\.-]+', ' ', text)

        noise_phrases = [r'Để đảm bảo hồ sơ.*?(?:\.|$)', r'Chi tiết truy cập.*?(?:\.|$)', r'Nơi làm việc:.*?(?:\.|$)',
                         r'Cách thức ứng tuyển:.*?(?:\.|$)']
        for phrase in noise_phrases: text = re.sub(phrase, ' ', text, flags=re.IGNORECASE)

        text = re.sub(r'\[.*?\]', ' ', text)
        text = re.sub(r'[^\w\s\.\+\#\/\-]', ' ', text)  # Chống Emoji
        text = re.sub(r'\.{2,}', ' ', text)
        text = re.sub(r'\-{2,}', ' ', text)
        text = re.sub(r'(?<!\w)[\.\-\/](?!\w)', ' ', text)
        text = text.replace('\u200b', ' ')

        cleaned = " ".join(text.split())
        return cleaned if cleaned else None

    if 'desc' in df.columns: df['desc'] = df['desc'].apply(clean_text_for_ai)
    if 'req' in df.columns: df['req'] = df['req'].apply(clean_text_for_ai)
    df = df.dropna(subset=['desc', 'req'], how='all')
    return df


def deduplicate_and_sort_jobs(df):
    """Logic Khử trùng lặp (duplicate.py) và Sắp xếp (sort_company.py & sort_title.py)"""
    # 1. Khử trùng lặp
    df['temp_title'] = df['title'].astype(str).str.lower().str.strip()
    df['temp_comp'] = df['company_name'].astype(str).str.lower().str.strip()
    df['temp_loc'] = df['location'].astype(str).str.lower().str.strip()

    if 'salary_min' in df.columns:
        df = df.sort_values(by=['salary_min'], na_position='last')

    df = df.drop_duplicates(subset=['temp_title', 'temp_comp', 'temp_loc'], keep='first').copy()
    df = df.drop(columns=['temp_title', 'temp_comp', 'temp_loc'])

    # 2. Sắp xếp theo tên công ty và Cấp phát ID (từ 1 đến N)
    df = df.sort_values(by=['company_name'], key=lambda col: col.astype(str).str.lower(), na_position='last')
    df['job_id'] = range(1, len(df) + 1)
    df = df.sort_values(by='job_id', ascending=True).reset_index(drop=True)
    return df


def finalize_columns(df):
    target_columns = [
        'job_id', 'title', 'company_name', 'company_size', 'location',
        'job_level', 'experience_year', 'salary_min', 'salary_max',
        'is_negotiable', 'job_type', 'is_remote', 'posted_date',
        'source', 'crawled_at', 'job_url', 'desc', 'req'
    ]
    for col in target_columns:
        if col not in df.columns: df[col] = None
    df = df[target_columns]
    return df.replace({np.nan: None})


# =============================================================================
# PIPELINE ORCHESTRATOR
# =============================================================================

def run_full_etl_pipeline(raw_path, clean_path):
    print("🚀 Bắt đầu quá trình ETL Pipeline Toàn Diện...")
    df = pd.read_csv(raw_path, encoding='utf-8')

    df = rename_columns_and_init(df)
    print("✅ [1] Đã chuẩn hóa tên cột.")

    df = filter_it_jobs(df)
    print("✅ [2] Đã lọc toàn bộ Job IT (Loại bỏ Kế toán, Ngân hàng...).")

    df = process_title(df)
    print("✅ [3] Đã làm sạch và chuẩn hóa danh xưng Chức danh (Title).")

    df = process_company_name(df)
    print("✅ [4] Đã làm sạch tên Công ty (Xóa rác scraping, viết tắt chuẩn).")

    df = process_company_size(df)
    df = process_location(df)
    df = process_job_level(df)
    print("✅ [5] Đã xử lý Quy mô, Địa điểm, Cấp bậc.")

    df = process_experience(df)
    print("✅ [6] Đã phân tích suy luận số năm Kinh nghiệm từ JD Text.")

    df = process_salary_and_nego(df)
    df = process_job_type_and_remote(df)
    print("✅ [7] Đã trích xuất số liệu Lương, Hình thức làm việc.")

    df = process_dates(df)
    print("✅ [8] Đã chuẩn hóa định dạng Ngày tháng (YYYY-MM-DD cho SQL).")

    df = process_nlp_texts(df)
    print("✅ [9] Đã làm sạch Văn bản NLP (Xóa Emojis, Ký tự lạ, HTML).")

    df = deduplicate_and_sort_jobs(df)
    print("✅ [10] Đã xóa trùng lặp và cấp lại Job_ID theo chuẩn hệ thống.")

    df_final = finalize_columns(df)
    print("✅ [11] Đã chốt Schema 18 cột và loại bỏ dữ liệu Null rác.")

    # Lưu kết quả
    df_final.to_csv(clean_path, index=False, encoding='utf-8-sig')
    print(f"\n🎉 HOÀN TẤT! Dữ liệu đã lưu tại: {clean_path}")
    print(f"📊 Tổng số Job cuối cùng: {len(df_final)}")

# Gọi hàm thực thi
# run_full_etl_pipeline('data/raw/all_jobs.csv', 'data/processed/cleaned_jobs.csv')