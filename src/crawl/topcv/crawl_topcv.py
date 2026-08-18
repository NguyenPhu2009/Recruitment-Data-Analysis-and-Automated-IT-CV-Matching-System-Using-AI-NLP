import csv, time, random, re, os
from datetime import datetime
from bs4 import BeautifulSoup
from curl_cffi import requests as req
from src.crawl.topcv import config_topcv as cfg


def get_html(url):
    for a in range(cfg.retry):
        try:
            r = req.get(url, impersonate="chrome124", timeout=cfg.timeout)
            if r.status_code == 200: return r.text
        except:
            pass
        time.sleep(a * 2)
    return None


def parse_job(html, url):
    soup = BeautifulSoup(html, "html.parser")

    def text(sel, is_list=False):
        if not sel: return None
        els = soup.select(sel) if is_list else [soup.select_one(sel)]
        els = [e for e in els if e]
        return ". ".join([e.get_text(separator=" ", strip=True) for e in els]) if els else None

    def section(kw):
        h3 = soup.find(["h3", "h2"], string=re.compile(kw, re.IGNORECASE))
        if h3 and (div := h3.find_next_sibling("div")):
            if lis := div.find_all("li"):
                return ". ".join([li.get_text(separator=" ", strip=True) for li in lis])
            return div.get_text(separator=". ", strip=True)
        return None

    title = text("h1.job-detail__info--title")
    if not title: return None

    sal = text(".job-detail__info--section.section-salary .job-detail__info--section-content-value")
    jt = text(".box-general-group:nth-of-type(4) .box-general-group-info-value")
    dl = text(".job-detail__info--deadline-date")

    return {
        "id": url.split("/")[-1].split(".")[0] if "/" in url else None,
        "title": title,
        "cate": text(".job-detail__company--information-item.company-field .company-value"),
        "comp": text(".company-name-label"),
        "size": text(".job-detail__company--information-item.company-scale .company-value"),
        "comp_loc": text(".job-detail__company--information-item.company-address .company-value"),
        "job_loc": text(".job-detail__info--section.section-location .job-detail__info--section-content-value a"),
        "level": text(".box-general-group:nth-of-type(1) .box-general-group-info-value"),
        "exp": text(".job-detail__info--section-content-value"),
        "qty": text(".box-general-group:nth-of-type(3) .box-general-group-info-value"),

        "type": jt,
        "remote": bool(jt and any(kw in jt.lower() for kw in ["remote", "từ xa", "hybrid"])),
        "salary": sal,
        "nego": bool(sal and ("thoả thuận" in sal.lower() or "thỏa thuận" in sal.lower())),

        "desc": section("Mô tả công việc"),
        "req": section("Yêu cầu ứng viên"),
        "benefit": section("Quyền lợi"),
        "skill": text(".box-category.collapsed .box-category-tags"),
        "hours": text(".job-description__item .job-description__item--content-list", is_list=True),

        "deadline": dl.replace("Hạn nộp hồ sơ:", "").strip() if dl else None,
        "post_date": "",
        "source": "TopCV",
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

    with open(cfg.csv_file, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=cols)

        if not file_exists:
            writer.writeheader()

        seen = set()
        total = 0
        loc_pat = re.compile(r"<loc>\s*(.*?)\s*</loc>", re.IGNORECASE)

        for n in range(cfg.sitemap_count):
            url = cfg.sitemap_url.format(n=n)
            if not (xml := get_html(url)): continue

            for job_url in loc_pat.findall(xml):
                job_url = job_url.strip()
                if job_url in seen or not any(kw in job_url.lower() for kw in cfg.it_keyword):
                    continue
                seen.add(job_url)

                if (html := get_html(job_url)) and (data := parse_job(html, job_url)):
                    writer.writerow(data)
                    f.flush()
                    os.fsync(f.fileno())

                    total += 1
                    print(f"Đã lưu: {data['title'][:40]}... (Job số {total})")

                time.sleep(random.uniform(cfg.delay_min, cfg.delay_max))

    print(f"Tổng cộng: {total} record!")

if __name__ == "__main__":
    run()