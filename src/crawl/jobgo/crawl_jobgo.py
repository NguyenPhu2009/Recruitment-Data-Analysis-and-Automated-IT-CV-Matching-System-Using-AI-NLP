import csv, time, random, re, os
from datetime import datetime
from bs4 import BeautifulSoup
from curl_cffi import requests as req
from src.crawl.jobgo import config_jobgo as cfg


def get_html(url):
    for a in range(cfg.retry):
        try:
            r = req.get(url, impersonate="chrome124", timeout=cfg.timeout)
            if r.status_code == 200:
                return r.text
        except:
            pass
        time.sleep(a * 2)
    return None


def parse_job(html, url):
    soup = BeautifulSoup(html, "html.parser")

    def text_by_label(label_text, target_tag="strong"):
        """
        Tìm kiếm trực tiếp text node để tránh lỗi bắt nhầm thẻ div cha.
        """
        # Lọc bỏ dấu hai chấm để Regex match an toàn hơn
        clean_label = label_text.replace(":", "").strip()
        pattern = re.compile(clean_label, re.IGNORECASE)

        # Tìm thẳng vào các chuỗi text (NavigableString)
        for text_node in soup.find_all(string=pattern):
            parent = text_node.parent  # Lùi ra thẻ bao bọc (thường là div hoặc span .text-muted)
            target = parent.find_next_sibling(target_tag)  # Lấy thẻ strong/span kế bên
            if target:
                return target.get_text(separator=", ", strip=True)
        return None

    def section_text(title_text):
        h3 = soup.find(["h3", "h2"], string=re.compile(title_text, re.IGNORECASE))
        if h3 and (div := h3.find_next_sibling("div")):
            if lis := div.find_all("li"):
                return ". ".join([li.get_text(separator=" ", strip=True) for li in lis])
            return div.get_text(separator=". ", strip=True)
        return None

    title_el = soup.select_one("h1.job-title")
    title = title_el.get_text(strip=True) if title_el else None
    if not title: return None

    apply_btn = soup.select_one("#btn-apply")
    job_id = apply_btn.get("data-jid") if apply_btn else (url.split("-")[-1].split(".")[0] if "-" in url else None)

    sal = text_by_label("Mức lương")
    jt = text_by_label("Loại hình")
    dl = text_by_label("Hạn nộp hồ sơ")
    posted = text_by_label("Ngày đăng tuyển")

    if dl:
        dl = dl.split("(")[0].strip()

    comp_name_el = soup.select_one("h6.fw-semibold")
    comp_name = comp_name_el.get_text(strip=True) if comp_name_el else None

    # Code đã được làm gọn đáng kể nhờ tối ưu hàm text_by_label
    return {
        "id": job_id,
        "title": title,
        "cate": text_by_label("Ngành nghề"),
        "comp": comp_name,
        "size": None,
        "comp_loc": text_by_label("Địa chỉ", target_tag="span"),
        "job_loc": text_by_label("Địa điểm"),
        "level": text_by_label("Cấp bậc"),
        "exp": text_by_label("Kinh nghiệm"),
        "qty": text_by_label("Số lượng tuyển"),
        "type": jt,
        "remote": bool(jt and any(kw in jt.lower() for kw in ["remote", "từ xa", "hybrid"])),
        "salary": sal,
        "nego": bool(sal and ("thoả thuận" in sal.lower() or "thỏa thuận" in sal.lower())),
        "desc": section_text("Mô tả công việc"),
        "req": section_text("Yêu cầu công việc"),
        "benefit": section_text("Quyền lợi được hưởng"),
        "skill": text_by_label("Kỹ năng"),
        "hours": text_by_label("Thời gian làm việc"),
        "deadline": dl,
        "post_date": posted,
        "source": "JobsGO",
        "crawled_at": datetime.now().strftime("%Y-%m-%d"),
        "url": url
    }


def get_job_links_from_category(html):
    """Trích xuất tất cả các link chi tiết việc làm từ trang danh mục"""
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.select("h3.job-title a"):
        href = a.get("href")
        if href:
            clean_href = href.split("?")[0]
            if clean_href.startswith("http"):
                links.append(clean_href)
    return list(set(links))


def run():
    cols = [
        "id", "title", "cate", "comp", "size", "comp_loc", "job_loc",
        "level", "exp", "qty", "type", "remote", "salary", "nego",
        "desc", "req", "benefit", "skill", "hours", "deadline", "post_date",
        "source", "crawled_at", "url"
    ]

    file_exists = os.path.isfile(cfg.csv_file)
    seen = set()
    total = 0

    with open(cfg.csv_file, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        if not file_exists:
            writer.writeheader()

        for cat_url in cfg.category_urls:
            print(f"\n--- Đang quét danh mục: {cat_url.split('/')[-1]} ---")

            for page in range(1, cfg.max_pages_per_category + 1):
                page_url = f"{cat_url}?page={page}" if page > 1 else cat_url
                print(f"-> Đọc trang: {page_url}")

                cat_html = get_html(page_url)
                if not cat_html:
                    break

                job_links = get_job_links_from_category(cat_html)

                if not job_links:
                    print("Không tìm thấy thêm tin nào. Chuyển danh mục khác.")
                    break

                for job_url in job_links:
                    if job_url in seen:
                        continue
                    seen.add(job_url)

                    html = get_html(job_url)
                    if html and (data := parse_job(html, job_url)):
                        writer.writerow(data)
                        f.flush()
                        os.fsync(f.fileno())

                        total += 1
                        print(f"Đã lưu: {data['title'][:40]}... (Total: {total})")

                    time.sleep(random.uniform(cfg.delay_min, cfg.delay_max))

    print(f"\n[Hoàn thành] Đã thu thập tổng cộng: {total} record IT từ các danh mục của JobsGO!")


if __name__ == "__main__":
    run()