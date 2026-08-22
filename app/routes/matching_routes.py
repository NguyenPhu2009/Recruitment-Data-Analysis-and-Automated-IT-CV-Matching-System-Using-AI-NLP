import os
import json
import uuid  # Thêm thư viện tạo chuỗi độc nhất
from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
from ..utils.db_connector import DatabaseConnector
from ..models.cv_matching_history import CVMatchingHistory
from ..services.cv_extractor import extract_text_from_cv

from ..services.ai_matcher import calculate_semantic_similarity
from ..services.skill_extractor import extract_skills_from_text, extract_matched_and_missing_skills

matching_bp = Blueprint('matching', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@matching_bp.route('/match-cv', methods=['POST'])
def match_cv():
    db_conn = DatabaseConnector()

    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Không tìm thấy file CV!"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "File rỗng!"}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"status": "error", "message": "Hệ thống chỉ chấp nhận file định dạng .PDF!"}), 400

    jd_text = request.form.get('jd_text', type=str)
    if not jd_text or len(jd_text.strip()) < 10:
        return jsonify({"status": "error", "message": "Vui lòng dán Mô tả công việc (JD) hợp lệ!"}), 400

    job_title = request.form.get('job_title', 'Vị trí tùy chỉnh')

    # BƯỚC UPDATE: Xử lý an toàn tên file và chống ghi đè
    original_filename = file.filename
    safe_name = secure_filename(original_filename)
    if not safe_name:
        safe_name = "cv_upload.pdf"  # Fallback nếu tên file toàn tiếng Việt bị xóa trắng

    unique_filename = f"{uuid.uuid4().hex}_{safe_name}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

    file.save(filepath)

    try:
        cv_text = extract_text_from_cv(filepath)
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

    if not cv_text or len(cv_text.strip()) < 50:
        return jsonify({
            "status": "error",
            "message": "Không thể trích xuất văn bản từ PDF này. Vui lòng upload file PDF dạng text (không phải ảnh scan)."
        }), 400

    # 1. Trích xuất kỹ năng On-the-fly từ JD tự nhập
    jd_skills = extract_skills_from_text(jd_text)

    # 2. Lọc kỹ năng khớp / thiếu
    matched_skills, missing_skills = extract_matched_and_missing_skills(cv_text, jd_skills)

    # 3. Chấm điểm Semantic
    ai_result = calculate_semantic_similarity(cv_text, jd_text, matched_skills)

    skill_score = round((len(matched_skills) / len(jd_skills) * 100), 1) if jd_skills else 70.0
    semantic_score = ai_result.get("score", 0.0)
    exp_score = 75.0

    overall_score = round(0.6 * skill_score + 0.3 * semantic_score + 0.1 * exp_score, 1)

    # 4. Lưu lịch sử
    user_id = session.get('user_id')

    if user_id:
        try:
            history_record = CVMatchingHistory(
                user_id=user_id,
                job_title=job_title,
                job_jd=jd_text,
                cv_filename=original_filename,  # UPDATE: Lưu tên gốc để UI hiện tiếng Việt đẹp mắt
                overall_score=overall_score,
                skill_score=skill_score,
                exp_score=exp_score,
                matched_skills=json.dumps(matched_skills, ensure_ascii=False),
                missing_skills=json.dumps(missing_skills, ensure_ascii=False)
            )
            db_conn.save_matching_record(history_record)
        except Exception as e:
            print(f"Lỗi lưu lịch sử: {e}")

    response_data = {
        "status": "success",
        "overall_score": overall_score,
        "skill_score": skill_score,
        "semantic_score": semantic_score,
        "exp_score": exp_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "method_used": ai_result.get("method", "wmd_fasttext"),
        "oov_rate": ai_result.get("oov_rate", 0.0)
    }

    if ai_result.get("method") == "tfidf_fallback":
        response_data[
            "warning"] = "Tỷ lệ từ vựng ngoài từ điển (OOV) cao, hệ thống tự động sử dụng phương án dự phòng TF-IDF để đảm bảo độ chính xác."

    return jsonify(response_data), 200


@matching_bp.route('/history', methods=['GET'])
def get_history():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Vui lòng đăng nhập để xem lịch sử cá nhân!"}), 401

    records = CVMatchingHistory.query.filter_by(user_id=user_id) \
        .order_by(CVMatchingHistory.analyzed_at.desc()).all()

    history_list = []
    for r in records:
        history_list.append({
            "result_id": r.result_id,
            "job_title": r.job_title if r.job_title else "Vị trí tùy chỉnh",
            "job_jd": r.job_jd if r.job_jd else "Không có dữ liệu JD",
            "company_name": "Tùy chỉnh",
            "cv_filename": r.cv_filename,
            "overall_score": r.overall_score,
            "skill_score": r.skill_score,
            "exp_score": r.exp_score,
            "matched_skills": json.loads(r.matched_skills) if r.matched_skills else [],
            "missing_skills": json.loads(r.missing_skills) if r.missing_skills else [],
            "analyzed_at": r.analyzed_at.strftime('%d/%m/%Y %H:%M') if r.analyzed_at else None
        })

    return jsonify({"status": "success", "history": history_list}), 200