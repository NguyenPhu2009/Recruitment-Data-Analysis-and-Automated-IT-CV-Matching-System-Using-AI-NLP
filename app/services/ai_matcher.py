import os
import pickle
import re
import numpy as np
# ĐỔI TỪ FastText SANG KeyedVectors
from gensim.models import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity

# Sửa lại tên file cho đúng với file bạn đã train (.kv)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FASTTEXT_PATH = os.path.join(BASE_DIR, 'models_repository', 'fasttext_model.kv')
TFIDF_PATH = os.path.join(BASE_DIR, 'models_repository', 'tfidf_model.pkl')


class AIModelLoader:
    """Singleton Pattern để Lazy Load Model (Giải quyết lỗi OOM RAM)"""
    _fasttext_wv = None
    _tfidf = None

    @classmethod
    def get_fasttext(cls):
        if cls._fasttext_wv is None and os.path.exists(FASTTEXT_PATH):
            print("⏳ Lazy Loading: Đang nạp KeyedVectors vào RAM...")
            # DÙNG KeyedVectors ĐỂ LOAD FILE .kv
            cls._fasttext_wv = KeyedVectors.load(FASTTEXT_PATH)
        return cls._fasttext_wv

    @classmethod
    def get_tfidf(cls):
        if cls._tfidf is None and os.path.exists(TFIDF_PATH):
            print("⏳ Lazy Loading: Đang nạp TF-IDF Vectorizer vào RAM...")
            with open(TFIDF_PATH, 'rb') as f:
                cls._tfidf = pickle.load(f)
        return cls._tfidf


def preprocess_for_model(text: str) -> list:
    """Tiền xử lý văn bản: giữ lại các từ khóa đặc thù IT trước khi xóa ký tự đặc biệt"""
    if not text:
        return []
    text = text.lower()
    # Giữ nguyên các token đặc thù IT
    text = re.sub(r'c#', 'c_sharp', text)
    text = re.sub(r'c\+\+', 'cplusplus', text)
    text = re.sub(r'\.net', 'dotnet', text)
    text = re.sub(r'node\.js', 'nodejs', text)

    # Xóa ký tự không phải chữ/số
    text = re.sub(r'[^a-z0-9_a-záàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ\s]', ' ', text)
    tokens = text.split()
    return [t for t in tokens if len(t) > 1]


def calculate_semantic_similarity(cv_text: str, jd_text: str, matched_skills: list = None) -> dict:
    if matched_skills is None:
        matched_skills = []

    # Lấy đối tượng vector (đã load sẵn qua Singleton)
    wv_model = AIModelLoader.get_fasttext()
    tfidf_vectorizer = AIModelLoader.get_tfidf()

    if not cv_text or not jd_text or wv_model is None:
        return {"score": 0.0, "method": "none", "oov_rate": 0.0}

    cv_tokens = preprocess_for_model(cv_text)
    jd_tokens = preprocess_for_model(jd_text)

    # BƯỚC FIX LỖI: Lọc bỏ các từ khóa Hard-match (skill_score) đã khớp
    filtered_cv = [t for t in cv_tokens if t not in matched_skills]
    filtered_jd = [t for t in jd_tokens if t not in matched_skills]

    # Nếu sau khi lọc không còn từ nào để so sánh
    if not filtered_cv or not filtered_jd:
        return {"score": 0.0, "method": "none", "oov_rate": 0.0}

    # BỎ ".wv" VÌ BẢN THÂN wv_model ĐÃ LÀ KEYEDVECTORS
    cv_oov = sum(1 for t in filtered_cv if t not in wv_model.key_to_index)
    jd_oov = sum(1 for t in filtered_jd if t not in wv_model.key_to_index)

    avg_oov = ((cv_oov / len(filtered_cv)) + (jd_oov / len(filtered_jd))) / 2

    # Logic tự động chuyển đổi mô hình
    if avg_oov <= 0.30:
        # BỎ ".wv" VÌ BẢN THÂN wv_model ĐÃ LÀ KEYEDVECTORS
        distance = wv_model.wmdistance(filtered_cv, filtered_jd)

        if distance == float('inf'):
            semantic_score = 0.0
        else:
            # Quy đổi Distance thành Similarity Score (0-100)
            semantic_score = (1 / (1 + distance)) * 100
        method_used = "wmd_fasttext"
    else:
        # Tỷ lệ OOV cao (>30%) -> Fallback sang TF-IDF
        if tfidf_vectorizer:
            cv_joined = ' '.join(filtered_cv)
            jd_joined = ' '.join(filtered_jd)
            tfidf_matrix = tfidf_vectorizer.transform([cv_joined, jd_joined])
            semantic_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100
        else:
            semantic_score = 0.0
        method_used = "tfidf_fallback"

    return {
        "score": round(max(0.0, min(100.0, semantic_score)), 1),  # Chặn ngưỡng 0-100
        "method": method_used,
        "oov_rate": round(float(avg_oov * 100), 1)
    }