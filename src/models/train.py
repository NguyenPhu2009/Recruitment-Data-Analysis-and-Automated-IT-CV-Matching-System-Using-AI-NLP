import os
import re
import pyodbc
import numpy as np
import unicodedata
import pickle
from collections import Counter
from gensim.models.fasttext import load_facebook_model
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from underthesea import word_tokenize


def load_stopwords(filepath):
    print(f"⏳ Đang nạp danh sách từ dừng từ '{filepath}'...")
    if not os.path.exists(filepath):
        print(f"⚠️ Cảnh báo: Không tìm thấy file {filepath}. Sẽ bỏ qua bước lọc stopwords.")
        return set()
    with open(filepath, 'r', encoding='utf-8') as f:
        stopwords = set(line.strip().replace(' ', '_') for line in f if line.strip())
    print(f"✅ Đã nạp {len(stopwords)} từ dừng.")
    return stopwords


def get_data_from_sql_server():
    print("⏳ [1/6] Đang kết nối SQL Server Data Warehouse...")
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=NGUYENANPHU\\MAYAO;"
        "Database=ATS_Database;"
        "Trusted_Connection=yes;"
    )
    conn = pyodbc.connect(conn_str)

    # Ép pyodbc đọc chuẩn UTF-16LE cho NVARCHAR và xử lý đúng dữ liệu Tiếng Việt
    conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-16le')
    conn.setdecoding(pyodbc.SQL_CHAR, encoding='windows-1258')
    conn.setencoding(encoding='utf-16le')

    cursor = conn.cursor()
    # Chỉ lấy các dòng có dữ liệu req và desc
    query = "SELECT title, [req], [desc] FROM Job_Postings WHERE [req] IS NOT NULL AND [desc] IS NOT NULL"
    cursor.execute(query)
    rows = cursor.fetchall()

    corpus = []
    for row in rows:
        title = row[0] if row[0] else ""
        req = row[1] if row[1] else ""
        desc = row[2] if row[2] else ""
        corpus.append(f"{title} {req} {desc}")

    cursor.close()
    conn.close()
    print(f"✅ Đã tải thành công {len(corpus)} bản ghi tin tuyển dụng.")
    return corpus


def clean_text_level2(text, stopwords):
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)

    text = re.sub(r'(?i)c#', 'c_sharp', text)
    text = re.sub(r'(?i)c\+\+', 'c_plus_plus', text)
    text = re.sub(r'(?i)\.net', 'dotnet', text)
    text = re.sub(r'(?i)node\.js', 'nodejs', text)
    text = re.sub(r'(?i)react\.js', 'reactjs', text)
    text = re.sub(r'(?i)vue\.js', 'vuejs', text)

    segmented_text = word_tokenize(text, format="text")
    segmented_text = segmented_text.lower()

    tokens = re.findall(r'[\w_]+', segmented_text)
    it_keywords = {'c_sharp', 'c_plus_plus', 'dotnet', 'nodejs', 'reactjs', 'vuejs', 'it'}

    final_tokens = []
    for t in tokens:
        if t in it_keywords or (t not in stopwords and len(t) > 1):
            final_tokens.append(t)

    return final_tokens


def diagnose_vocab(processed_corpus, model, oov_words_to_check):
    print("\n" + "=" * 60)
    print("🔍 CHẨN ĐOÁN VOCAB (FASTTEXT)")
    print("=" * 60)

    all_tokens = [t for doc in processed_corpus for t in doc]
    freq = Counter(all_tokens)

    print(f"Tổng số token (có lặp): {len(all_tokens)}")
    print(f"Số từ vựng duy nhất (unique): {len(freq)}")
    print(f"Số từ vựng model ghi nhận chính xác: {len(model.wv.key_to_index)}")
    print(f"Số câu (document) trong corpus: {len(processed_corpus)}")

    print("\n--- Khả năng xử lý OOV của FastText ---")
    for w in oov_words_to_check:
        count = freq.get(w, 0)
        # Điểm mạnh của FastText: Có thể sinh ra vector cho từ OOV nhờ sub-words
        has_vector = w in model.wv
        print(f"  '{w}': xuất hiện {count} lần | Có vector: {has_vector}")

    print("=" * 60 + "\n")


# Sửa lại hàm test để nó gọi trực tiếp đối tượng model.wv (KeyedVectors)
def test_trained_model(wv_model, tfidf_model, stopwords, oov_threshold=0.3):
    print("\n⏳ [6/6] Đang chạy kiểm thử mô hình với cơ chế Fallback...")

    mock_cv = "Sinh viên CNTT đam mê lập trình ứng dụng Web. Thành thạo ngôn ngữ C# và nền tảng .NET. Có kinh nghiệm xây dựng RESTful API và kết nối SQL Server."
    mock_jd = "Tuyển dụng Backend Developer. Yêu cầu ứng viên biết lập trình C++ hoặc C# và ASP.NET. Có tư duy thiết kế hệ thống cơ sở dữ liệu quan hệ."

    cv_tokens = clean_text_level2(mock_cv, stopwords)
    jd_tokens = clean_text_level2(mock_jd, stopwords)

    print(f"\n🔹 Tokens trích xuất từ CV: {cv_tokens}")
    print(f"🔹 Tokens trích xuất từ JD: {jd_tokens}")

    # Chú ý: wv_model bây giờ là KeyedVectors
    cv_oov = sum(1 for t in cv_tokens if t not in wv_model.key_to_index)
    jd_oov = sum(1 for t in jd_tokens if t not in wv_model.key_to_index)

    avg_oov_ratio = ((cv_oov / len(cv_tokens) if cv_tokens else 1.0) + (
        jd_oov / len(jd_tokens) if jd_tokens else 1.0)) / 2

    print(f"\n💡 Tỷ lệ OOV trung bình: {avg_oov_ratio * 100:.2f}%")

    print("\n" + "=" * 50)
    if avg_oov_ratio <= oov_threshold:
        print("🎯 PHƯƠNG PHÁP SỬ DỤNG: FastText + Word Mover's Distance (WMD)")
        # Sửa lại wmdistance ở đây
        distance = wv_model.wmdistance(cv_tokens, jd_tokens)

        similarity_score = 1 / (1 + distance) if distance != float('inf') else 0.0
    else:
        print("🎯 PHƯƠNG PHÁP SỬ DỤNG: TF-IDF Fallback (Do OOV vượt ngưỡng)")
        cv_text = ' '.join(cv_tokens)
        jd_text = ' '.join(jd_tokens)
        tfidf_matrix = tfidf_model.transform([cv_text, jd_text])
        similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    print(f"🎯 KẾT QUẢ ĐÁNH GIÁ ĐỘ PHÙ HỢP: {similarity_score * 100:.2f}%")
    print("=" * 50)


def main():
    # 1. Load Stopwords
    stopwords = load_stopwords(
        r"D:\Recruitment-Data-Analysis-and-Automated-IT-CV-Matching-System-Using-AI-NLP\data\external\vietnamese-stopwords.txt")

    # 2. Get Data
    raw_corpus = get_data_from_sql_server()

    # 3. Clean Text
    print("⏳ [2/6] Đang thực hiện Tiền xử lý văn bản Cấp 2 (Underthesea NLP & Stopwords)...")
    processed_corpus = [clean_text_level2(doc, stopwords) for doc in raw_corpus]

    # 4. Load Pre-trained FastText & Fine-tune
    print("⏳ [3/6] Đang nạp mô hình Pre-trained FastText tiếng Việt (cc.vi.300.bin)...")
    fasttext_path = r"D:\Recruitment-Data-Analysis-and-Automated-IT-CV-Matching-System-Using-AI-NLP\data\external\cc.vi.300.bin"
    model = load_facebook_model(fasttext_path)

    print("⏳ [4/6] Đang Fine-tune từ vựng với dữ liệu IT...")
    model.build_vocab(processed_corpus, update=True)
    model.train(processed_corpus, total_examples=len(processed_corpus), epochs=30)

    # Đảm bảo thư mục tồn tại và lưu model
    os.makedirs(r"D:\Recruitment-Data-Analysis-and-Automated-IT-CV-Matching-System-Using-AI-NLP\models_repository",
                exist_ok=True)

    model_save_path = r"D:\Recruitment-Data-Analysis-and-Automated-IT-CV-Matching-System-Using-AI-NLP\models_repository\fasttext_model.kv"
    model.wv.save(model_save_path)
    # ---------------------------------------------------

    print(f"🎉 XUẤT MÔ HÌNH AI THÀNH CÔNG: Đã lưu tại '{model_save_path}'")

    # 5. Huấn luyện TF-IDF
    print("⏳ [5/6] Đang huấn luyện TF-IDF dự phòng...")
    tfidf = TfidfVectorizer()
    tfidf.fit([' '.join(tokens) for tokens in processed_corpus])
    tfidf_save_path = r"D:\Recruitment-Data-Analysis-and-Automated-IT-CV-Matching-System-Using-AI-NLP\models_repository\tfidf_model.pkl"
    with open(tfidf_save_path, 'wb') as f:
        pickle.dump(tfidf, f)
    print(f"🎉 XUẤT TF-IDF THÀNH CÔNG: Đã lưu tại '{tfidf_save_path}'")

    diagnose_vocab(
        processed_corpus, model,
        oov_words_to_check=['lập_trình', 'ứng_dụng', 'thành_thạo', 'ngôn_ngữ',
                            'nền_tảng', 'kinh_nghiệm', 'xây_dựng', 'kết_nối', 'nestjs']
    )

    test_trained_model(model.wv, tfidf, stopwords)


if __name__ == "__main__":
    main()