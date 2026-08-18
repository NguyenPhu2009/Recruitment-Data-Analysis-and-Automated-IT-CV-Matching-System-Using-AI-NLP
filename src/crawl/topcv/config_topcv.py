import os

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
csv_file = os.path.join(data_dir, "topcv_jobs.csv")

sitemap_count = 258
sitemap_url = "https://www.topcv.vn/sitemap/jobs_{n}.xml"

delay_min, delay_max = 1.5, 3.0
timeout, retry = 15, 3

it_keyword = [
    "it-", "-it", "developer", "dev-", "lap-trinh", "lap-trinh-vien",
    "programmer", "software", "phan-mem", "backend", "frontend",
    "full-stack", "fullstack", "devops", "qa-qc", "tester", "kiem-thu",
    "data-engineer", "data-analyst", "data-scientist", "khoa-hoc-du-lieu",
    "he-thong", "system-admin", "quan-tri-mang", "network-admin",
    "security", "bao-mat", "cloud", "ai-engineer", "machine-learning",
    "mobile", "android", "ios", "web-developer", "cong-nghe-thong-tin",
    "kien-truc-su", "erp", "sap-", "dba-", "ui-ux", "game", "blockchain", "embedded"
]