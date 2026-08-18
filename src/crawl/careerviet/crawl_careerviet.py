import csv, time, random, re, os, json
from datetime import datetime
from bs4 import BeautifulSoup
from curl_cffi import requests as req
from src.crawl.careerviet import config_careerviet as cfg


def get_html(url):
    profiles = ["chrome124", "chrome120", "edge122"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://careerviet.vn/",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    for a in range(cfg.retries):
        try:
            r = req.get(url, impersonate=random.choice(profiles), headers=headers, timeout=cfg.timeout)
            if r.status_code == 200: return r.text
        except:
            pass
        time.sleep((a + 1) * 2)
    return None


def clean_text(text):
    """Hàm dọn dẹp các ký tự khoảng trắng thừa, đặc biệt là lỗi \xa0 (NBSP) gây lệch font"""
    if not text or not isinstance(text, str):
        return text
    return re.sub(r'\s+', ' ', text.replace('\xa0', ' ').replace('&nbsp;', ' ')).strip()


def parse_job(html, url, job_id):
    soup = BeautifulSoup(html, "html.parser")

    # Fallback Data từ JSON-LD Schema (Dùng bổ trợ nếu giao diện hiển thị thiếu)
    schema_data = {}
    schema_tag = soup.find("script", id="job-posting-schema")
    if schema_tag and schema_tag.string:
        try:
            schema_data = json.loads(schema_tag.string)
        except:
            pass

    def get_tr_td(label_text):
        """Hàm bóc tách thông tin dành cho các layout bảng (cũ)"""
        for t in soup.find_all("td", class_="name"):
            if label_text.lower() in t.get_text(strip=True).lower():
                nxt = t.find_next_sibling("td", class_="content")
                if nxt:
                    text_content = nxt.get_text(separator=" ", strip=True)
                    text_content = re.sub(r'Bản đồ.*$', '', text_content, flags=re.IGNORECASE).strip()
                    return text_content
        return None

    def get_section(keyword):
        """Bóc tách các phần Mô tả công việc, Yêu cầu công việc"""
        h_tag = soup.find(["h2", "h3", "h4"], class_="detail-title", string=re.compile(keyword, re.IGNORECASE))
        if h_tag and (content_div := h_tag.find_next_sibling("div")):
            if lis := content_div.find_all("li"):
                return ". ".join([li.get_text(separator=" ", strip=True) for li in lis])
            return content_div.get_text(separator=". ", strip=True)
        return None

    # 1. Title & Company
    title_tag = soup.find("div", class_="title")
    title = title_tag.get_text(strip=True) if title_tag else schema_data.get("title")
    if not title: return None

    comp_tag = soup.find("a", class_="company")
    comp = comp_tag.get_text(strip=True) if comp_tag else None
    if not comp and schema_data.get("hiringOrganization"):
        comp = schema_data["hiringOrganization"].get("name")

    # 2. Location (comp_loc & job_loc giống nhau chỉ có 1 thẻ a)
    loc_tag = soup.select_one(".job-detail-content p a")
    comp_loc = clean_text(loc_tag.get_text(strip=True)) if loc_tag else None
    if not comp_loc:
        comp_loc = clean_text(get_tr_td("Địa điểm"))
    job_loc = comp_loc

    # 3. Các thuộc tính None theo yêu cầu
    qty = None
    jt = None  # type
    skill = None

    # 4. Trích xuất Cấp bậc, Lương, Kinh nghiệm, Hạn nộp, Ngày đăng (Quét layout cũ)
    sal = clean_text(get_tr_td("Lương"))
    dl = clean_text(get_tr_td("Hết hạn nộp"))
    level = clean_text(get_tr_td("Cấp bậc"))
    post_date = clean_text(get_tr_td("Ngày cập nhật"))

    exp = None
    exp_p = soup.find("p", string=re.compile("Số năm kinh nghiệm:"))
    if exp_p:
        exp = clean_text(exp_p.get_text(strip=True).replace("Số năm kinh nghiệm:", ""))

    # --- BỘ QUÉT THÔNG MINH CHO GIAO DIỆN MỚI ---
    info_lis = soup.select(".job-detail-content .bg-blue ul li")
    for li in info_lis:
        p_tag = li.find("p")
        if not p_tag:
            continue

        val = clean_text(p_tag.get_text(separator=" ", strip=True))
        if not val:
            continue

        em_tag = li.find("em")
        em_class = " ".join(em_tag.get("class", [])).lower() if em_tag else ""

        span_tag = li.find("span")
        span_text = clean_text(span_tag.get_text(strip=True)).lower() if span_tag else ""

        # Clone thẻ li để tách nhãn (label) không dính vào giá trị (val)
        clone_li = BeautifulSoup(str(li), 'html.parser')
        if clone_li.p: clone_li.p.decompose()
        label = clean_text(clone_li.get_text(separator=" ", strip=True)).lower() + " " + span_text
        val_lower = val.lower()

        # Nhận dạng Lương
        if "lương" in label or "usd" in em_class or "money" in em_class or \
                "cạnh tranh" in val_lower or "canh tranh" in val_lower or "thỏa" in val_lower or "thoả" in val_lower or "vnd" in val_lower:
            sal = val

        # Nhận dạng Hết hạn nộp (Dựa vào chữ hoặc calendar check)
        elif "hạn nộp" in label or "hết hạn" in label or "calendar-check" in em_class:
            dl = val

        # Nhận dạng Ngày cập nhật / Ngày đăng
        elif "cập nhật" in label or "ngày đăng" in label or ("calendar" in em_class and "check" not in em_class):
            post_date = val

        # Bắt Regex ngày tháng chuẩn nếu label không rõ ràng
        elif re.search(r'\d{2}/\d{2}/\d{4}', val):
            if not dl:
                dl = val
            elif not post_date:
                post_date = val

        # Nhận dạng Kinh nghiệm (Chỉ dựa vào chữ để tránh nhầm lẫn)
        elif "kinh nghiệm" in label or "kinh nghiem" in label or \
                re.search(r'\d+\s*(năm|nam|tháng|thang)', val_lower) or val_lower in ["chưa có", "không yêu cầu",
                                                                                      "chưa có kinh nghiệm"]:
            exp = val

        # Nhận dạng Cấp bậc
        elif "cấp bậc" in label or "cap bac" in label or "account" in em_class or "user" in em_class or \
                val_lower in ["nhân viên", "nhan vien", "trưởng phòng", "quản lý", "giám đốc", "phó giám đốc",
                              "thực tập sinh", "intern"]:
            if "chính thức" not in val_lower and "chinh thuc" not in val_lower:
                level = val

    # Fallback cho post_date từ schema nếu trên giao diện không có
    if not post_date and schema_data.get("datePosted"):
        raw_date = schema_data.get("datePosted")
        if "T" in raw_date:
            # Chỉ lấy phần YYYY-MM-DD
            post_date = raw_date.split("T")[0]

    # 5. Phân tích Ngành nghề và Phúc lợi
    cate = clean_text(schema_data.get("industry") or get_tr_td("Ngành nghề"))

    benefit = None
    benefit_ul = soup.find("ul", class_="welfare-list")
    if benefit_ul:
        benefit = ". ".join([clean_text(li.get_text(strip=True)) for li in benefit_ul.find_all("li")])
    if not benefit:
        benefit = clean_text(schema_data.get("jobBenefits"))

    # 6. Biến logic
    remote_flag = False
    nego_flag = bool(sal and (
            "thoả thuận" in sal.lower() or "cạnh tranh" in sal.lower() or "canh tranh" in sal.lower() or "thỏa thuận" in sal.lower()))

    # 7. Lấy mô tả & Yêu cầu công việc
    desc = clean_text(get_section("Mô tả Công việc"))
    req = clean_text(get_section("Yêu Cầu Công Việc"))

    return {
        "id": job_id,
        "title": clean_text(title),
        "cate": cate,
        "comp": clean_text(comp),
        "size": None,
        "comp_loc": comp_loc,
        "job_loc": job_loc,
        "level": level,
        "exp": exp,
        "qty": qty,
        "type": jt,
        "remote": remote_flag,
        "salary": sal,
        "nego": nego_flag,
        "desc": desc,
        "req": req,
        "benefit": benefit,
        "skill": skill,
        "hours": clean_text(schema_data.get("workHours")),
        "deadline": dl,
        "post_date": post_date,
        "source": "CareerViet",
        "crawled_at": datetime.now().strftime("%Y-%m-%d"),
        "url": url
    }


def run():
    cols = [
        "id", "title", "cate", "comp", "size", "comp_loc", "job_loc",
        "level", "exp", "qty", "type", "remote", "salary", "nego",
        "desc", "req", "benefit", "skill", "hours", "deadline", "post_date",
        "source", "crawled_at", "url"
    ]

    file_exists = os.path.isfile(cfg.csv_file)
    total = 0

    if file_exists:
        with open(cfg.csv_file, "r", encoding="utf-8-sig") as f_read:
            total = sum(1 for _ in f_read) - 1
            total = max(0, total)

    with open(cfg.csv_file, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        if not file_exists:
            writer.writeheader()

        seen = set()

        categories = [
            "https://careerviet.vn/viec-lam/cntt-phan-mem-c1-vi.html",
            "https://careerviet.vn/viec-lam/cntt-phan-cung-mang-c63-vi.html",
            "https://careerviet.vn/viec-lam/business-analyst-k-vi.html"
        ]

        max_pages = 40

        for cat_url in categories:
            base_part = cat_url.replace("-vi.html", "")

            for n in range(1, max_pages + 1):
                if n == 1:
                    page_url = cat_url
                else:
                    page_url = f"{base_part}-trang-{n}-vi.html"

                print(f"\n-> Đang quét Danh mục: {page_url}")

                html = get_html(page_url)
                if not html:
                    print("   [!] Không tải được hoặc bị chặn. Chuyển sang danh mục khác.")
                    break

                soup = BeautifulSoup(html, "html.parser")

                job_links = []
                for a in soup.find_all("a", class_="job_link", href=True):
                    href = a.get("href")
                    if href.startswith("/"):
                        href = "https://careerviet.vn" + href

                    clean_url = href.split("?")[0]
                    if clean_url not in seen:
                        job_links.append(clean_url)
                        seen.add(clean_url)

                if not job_links:
                    print("   [!] Không còn job nào. Đã vét sạch danh mục này!")
                    break

                print(f"   [v] Tìm thấy {len(job_links)} URL. Bắt đầu cào chi tiết...")

                for job_url in job_links:
                    if (detail_html := get_html(job_url)) and (data := parse_job(detail_html, job_url, total + 1)):
                        writer.writerow(data)
                        f.flush()
                        os.fsync(f.fileno())

                        total += 1
                        print(f"ĐÃ LƯU: ID {data['id']} - {data['title'][:40]}...")

                    time.sleep(random.uniform(cfg.delay_min, cfg.delay_max))

    print(f"\n=== Tổng cộng đã lưu: {total} bản ghi từ CareerViet ===")


if __name__ == "__main__":
    run()