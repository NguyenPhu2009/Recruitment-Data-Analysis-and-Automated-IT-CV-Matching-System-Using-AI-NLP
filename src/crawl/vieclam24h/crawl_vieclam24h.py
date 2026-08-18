import csv, time, random, re, os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from curl_cffi import requests as req
from src.crawl.vieclam24h import config_vieclam24h as cfg

# =====================================================================
# KHỞI TẠO SESSION & BƠM HEADERS GIẢ LẬP TRÌNH DUYỆT THẬT
# Giúp giữ Cookie qua các trang, chống bị Server Vieclam24h chặn ở page 7+
# =====================================================================
session = req.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://vieclam24h.vn/"
})


def get_html(url):
    profiles = ["chrome124", "chrome120", "edge122"]
    for a in range(cfg.retries):
        try:
            r = session.get(url, impersonate=random.choice(profiles), timeout=cfg.timeout)
            if r.status_code == 200:
                return r.text
            elif r.status_code == 404:
                return "404_NOT_FOUND"  # Báo hiệu hết trang thực sự
        except Exception as e:
            pass
        # Nếu bị lỗi mạng hoặc block, nghỉ ngơi lâu hơn để Server nhả IP
        time.sleep((a + 1) * 3)
    return None


def parse_job(html, url, job_id):
    """Bóc tách thông minh, nhận job_id tự tăng từ vòng lặp truyền vào"""
    soup = BeautifulSoup(html, "html.parser")

    # ==========================================
    # 1. CÁC HÀM HELPER BÓC TÁCH DỮ LIỆU
    # ==========================================
    def get_by_label(label_text):
        for tag in soup.find_all("div"):
            text = tag.get_text(strip=True)
            if text == label_text or text == f"{label_text}:":
                if (nxt := tag.find_next_sibling("div")):
                    return nxt.get_text(separator=" ", strip=True).replace(" / ", ", ")

        for tag in soup.find_all("span"):
            if label_text in tag.get_text(strip=True):
                if tag.parent:
                    full_text = tag.parent.get_text(separator=" ", strip=True)
                    return full_text.replace(tag.get_text(strip=True), "").strip()
        return None

    def get_section(keyword):
        h_tag = soup.find(["h2", "h3", "h4"], string=re.compile(keyword, re.IGNORECASE))
        if h_tag and (content_div := h_tag.find_next_sibling("div")):
            if lis := content_div.find_all("li"):
                return ". ".join([li.get_text(separator=" ", strip=True) for li in lis])
            return content_div.get_text(separator=". ", strip=True)
        return None

    # ==========================================
    # 2. XỬ LÝ CÁC TRƯỜNG DỮ LIỆU
    # ==========================================
    # Tiêu đề
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else None
    if not title: return None

    # Công ty
    comp_tag = soup.find("title")
    comp = comp_tag.get_text(strip=True).split(" tại ")[
        -1].strip() if comp_tag and " tại " in comp_tag.get_text() else None
    if not comp:
        comp_a = soup.find("a", href=re.compile("danh-sach-tin-tuyen-dung-cong-ty"))
        comp = comp_a.get_text(strip=True) if comp_a else None

    # Các thuộc tính phụ thuộc
    sal = get_by_label("Mức lương")
    jt = get_by_label("Hình thức làm việc")
    dl = get_by_label("Hạn nộp hồ sơ")  # Được đẩy lên trước để phục vụ cho post_date
    job_loc = get_section("Địa điểm làm việc") or get_by_label("Khu vực tuyển")

    # Xử lý thời gian đăng tin (Có Fallback 30 ngày)
    post_date = get_by_label("Ngày cập nhật") or get_by_label("Ngày đăng")
    if not post_date and dl:
        try:
            dl_obj = datetime.strptime(dl, "%d/%m/%Y")
            post_date = (dl_obj - timedelta(days=30)).strftime("%d/%m/%Y")
        except:
            post_date = None

    # ==========================================
    # 3. TRẢ VỀ KẾT QUẢ ĐÃ SẮP XẾP THEO COLUMNS
    # ==========================================
    return {
        "id": job_id,
        "title": title,
        "cate": get_by_label("Ngành nghề"),
        "comp": comp,
        "size": get_by_label("Quy mô"),
        "comp_loc": get_by_label("Địa chỉ"),
        "job_loc": job_loc,
        "level": get_by_label("Cấp bậc"),
        "exp": get_by_label("Yêu cầu kinh nghiệm") or get_by_label("Kinh nghiệm"),
        "qty": get_by_label("Số lượng tuyển"),

        "type": jt,
        "remote": bool(jt and any(kw in jt.lower() for kw in ["remote", "từ xa", "hybrid"])),
        "salary": sal,
        "nego": bool(sal and ("thoả thuận" in sal.lower() or "thỏa thuận" in sal.lower())),

        "desc": get_section("Mô tả công việc"),
        "req": get_section("Yêu cầu công việc"),
        "benefit": get_section("Quyền lợi"),
        "skill": None,
        "hours": None,

        "deadline": dl,
        "post_date": post_date,
        "source": "Vieclam24h",
        "crawled_at": datetime.now().strftime("%Y-%m-%d"),
        "url": url
    }


def run():
    # Cấu hình danh mục và phân trang
    categories = [
        "https://vieclam24h.vn/viec-lam-it-phan-cung-mang-o7.html?page={n}"
    ]
    max_pages = 100

    cols = [
        "id", "title", "cate", "comp", "size", "comp_loc", "job_loc",
        "level", "exp", "qty", "type", "remote", "salary", "nego",
        "desc", "req", "benefit", "skill", "hours", "deadline", "post_date",
        "source", "crawled_at", "url"
    ]

    file_exists = os.path.isfile(cfg.csv_file)
    total = 0

    # Tiếp nối ID nếu file đã tồn tại
    if file_exists:
        with open(cfg.csv_file, "r", encoding="utf-8-sig") as f_read:
            total = sum(1 for _ in f_read) - 1
            total = max(0, total)

    with open(cfg.csv_file, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        if not file_exists:
            writer.writeheader()

        seen = set()

        for cat_url in categories:
            for n in range(1, max_pages + 1):
                page_url = cat_url.format(n=n)
                print(f"\n-> Đang quét Danh mục: {page_url}")

                html = get_html(page_url)

                # Check mã 404 hoặc bị chặn liên tục
                if html == "404_NOT_FOUND":
                    print("   [!] Đã hết trang dữ liệu hợp lệ (Server 404). Chuyển danh mục.")
                    break
                elif not html:
                    print("   [!] Không tải được hoặc bị chặn. Chuyển sang danh mục khác.")
                    break

                soup = BeautifulSoup(html, "html.parser")

                raw_job_count = 0
                job_links = []

                # Bóc tách Link
                for a in soup.find_all("a", attrs={"data-job-id": True}):
                    href = a.get("href")
                    if href:
                        raw_job_count += 1
                        if href.startswith("/"):
                            href = "https://vieclam24h.vn" + href

                        clean_url = href.split("?")[0]
                        if clean_url not in seen:
                            job_links.append(clean_url)
                            seen.add(clean_url)

                # SỬA LỖI LOGIC: Chỉ break nếu trang web THỰC SỰ không có job nào.
                # Nếu trang có job, nhưng trùng (job_links = 0) thì ta vẫn tiếp tục sang trang sau.
                if raw_job_count == 0:
                    print("   [!] Trang này không chứa job nào nữa. Đã vét sạch danh mục!")
                    break

                if not job_links:
                    print(f"   [-] Các tin trên trang này đều đã quét. Chuyển sang trang {n + 1}...")
                    continue

                print(f"   [v] Tìm thấy {len(job_links)} URL IT MỚI. Bắt đầu cào chi tiết...")

                # Quét chi tiết từng Link
                for job_url in job_links:
                    if (detail_html := get_html(job_url)) and detail_html != "404_NOT_FOUND":
                        data = parse_job(detail_html, job_url, total + 1)
                        if data:
                            writer.writerow(data)
                            f.flush()
                            os.fsync(f.fileno())

                            total += 1
                            print(f"ĐÃ LƯU: ID {data['id']} - {data['title'][:40]}...")

                    time.sleep(random.uniform(cfg.delay_min, cfg.delay_max))

    print(f"\n=== Tổng cộng đã lưu: {total} bản ghi IT ===")


if __name__ == "__main__":
    run()