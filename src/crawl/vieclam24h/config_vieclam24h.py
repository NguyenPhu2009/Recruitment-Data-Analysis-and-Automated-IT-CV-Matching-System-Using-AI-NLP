import os

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(data_dir, exist_ok=True)
csv_file = os.path.join(data_dir, "vieclam24h_jobs3.csv")

delay_min, delay_max = 1.5, 3.0
timeout, retries = 15, 3
