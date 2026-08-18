import os

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(data_dir, exist_ok=True)
csv_file = os.path.join(data_dir, "careerviet_jobs.csv")

delay_min, delay_max = 2.0, 5.0
timeout, retries = 20, 5