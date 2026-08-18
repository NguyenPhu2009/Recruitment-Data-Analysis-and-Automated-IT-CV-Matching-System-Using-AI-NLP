import os
import pickle
import re
import numpy as np
from gensim.models import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity

# Import hàm trích xuất kỹ năng (Giả định bạn đang để ở skill_extractor.py)
from app.services.skill_extractor import extract_skills_from_text

# Nếu có hàm tính kinh nghiệm: from app.services.cv_extractor import extract_experience

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

    cv_oov = sum(1 for t in filtered_cv if t not in wv_model.key_to_index)
    jd_oov = sum(1 for t in filtered_jd if t not in wv_model.key_to_index)

    avg_oov = ((cv_oov / len(filtered_cv)) + (jd_oov / len(filtered_jd))) / 2

    # Logic tự động chuyển đổi mô hình
    if avg_oov <= 0.30:
        distance = wv_model.wmdistance(filtered_cv, filtered_jd)
        if distance == float('inf'):
            semantic_score = 0.0
        else:
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
        "score": round(max(0.0, min(100.0, semantic_score)), 1),
        "method": method_used,
        "oov_rate": round(float(avg_oov * 100), 1)
    }


class AIMatchingEngine:
    """Lớp điều phối toàn bộ luồng xử lý Match CV"""

    def analyze_matching(self, cv_text: str, job_jd_text: str) -> dict:
        if not cv_text or not job_jd_text:
            return {
                "overall_score": 0.0,
                "skill_score": 0.0,
                "semantic_score": 0.0,
                "exp_score": 0.0,
                "matched_skills": [],
                "missing_skills": [],
                "method_used": "none",
                "oov_rate": 0.0
            }

        # 1. Trích xuất kỹ năng On-the-fly từ CV và JD
        jd_skills = extract_skills_from_text(job_jd_text)
        cv_skills = extract_skills_from_text(cv_text)

        # 2. Tính Skill Score (Trọng số: 60%)
        jd_skills_set = set(jd_skills)
        cv_skills_set = set(cv_skills)

        matched_skills = list(jd_skills_set & cv_skills_set)
        missing_skills = list(jd_skills_set - cv_skills_set)

        if len(jd_skills_set) > 0:
            skill_score = (len(matched_skills) / len(jd_skills_set)) * 100
        else:
            skill_score = 0.0

        # 3. Tính Semantic Score (Trọng số: 30%)
        semantic_result = calculate_semantic_similarity(cv_text, job_jd_text, matched_skills)
        semantic_score = semantic_result["score"]

        # 4. Tính Exp Score (Trọng số: 10%) - Giả lập hoặc gọi hàm nếu có
        # exp_cv = extract_experience(cv_text)
        # exp_jd = extract_experience(job_jd_text)
        exp_score = 100.0  # Tạm gán, cập nhật lại nếu bạn đã xử lý xong hàm trích xuất kinh nghiệm

        # 5. Tổng hợp Overall Score
        overall_score = (0.6 * skill_score) + (0.3 * semantic_score) + (0.1 * exp_score)

        return {
            "overall_score": round(overall_score, 1),
            "skill_score": round(skill_score, 1),
            "semantic_score": semantic_score,
            "exp_score": exp_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "method_used": semantic_result["method"],
            "oov_rate": semantic_result["oov_rate"]
        }


# Khởi tạo biến engine để gọi ở file route (ai_engine.analyze_matching...)
ai_engine = AIMatchingEngine()