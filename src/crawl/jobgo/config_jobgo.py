import os

# Đường dẫn lưu file
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
csv_file = os.path.join(data_dir, "jobsgo_jobs.csv")

# Danh sách URL các chuyên mục IT để quét trực tiếp
category_urls = [
    "https://jobsgo.vn/viec-lam-cong-nghe-thong-tin.html",
]

# Số trang tối đa muốn quét cho mỗi danh mục (để tránh quét vô tận)
max_pages_per_category = 35

# Cấu hình request
delay_min, delay_max = 1.5, 3.5
timeout, retry = 15, 3