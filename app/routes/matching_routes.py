import os
import json
import re
from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
from ..utils.db_connector import DatabaseConnector
from ..models.skills_dict import SkillsDict
from ..models.cv_matching_history import CVMatchingHistory
from ..services.cv_extractor import extract_text_from_cv

from ..services.ai_matcher import calculate_semantic_similarity
from ..services.skill_extractor import extract_matched_and_missing_skills

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

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    cv_text = extract_text_from_cv(filepath)
    if os.path.exists(filepath):
        os.remove(filepath)

    if not cv_text or len(cv_text.strip()) < 50:
        return jsonify({
            "status": "error",
            "message": "Không thể trích xuất văn bản từ PDF này. Vui lòng upload file PDF dạng text (không phải ảnh scan)."
        }), 400

    all_skills = SkillsDict.query.all()
    jd_text_lower = jd_text.lower()
    jd_skills = []
    for s in all_skills:
        if s.normalized_form and re.search(r'\b' + re.escape(s.normalized_form) + r'\b', jd_text_lower):
            jd_skills.append(s.skill_name)

    matched_skills, missing_skills = extract_matched_and_missing_skills(cv_text, jd_skills)

    ai_result = calculate_semantic_similarity(cv_text, jd_text, matched_skills)

    skill_score = round((len(matched_skills) / len(jd_skills) * 100), 1) if jd_skills else 70.0
    semantic_score = ai_result.get("score", 0.0)
    exp_score = 75.0

    overall_score = round(0.6 * skill_score + 0.3 * semantic_score + 0.1 * exp_score, 1)

    suggestion = "CV của bạn rất xuất sắc và khớp với hầu hết các yêu cầu kỹ năng của vị trí này. Hãy tự tin ứng tuyển!"
    if missing_skills:
        top_missing = missing_skills[:3]
        suggestion = f"Bổ sung kiến thức và kinh nghiệm thực hành về {', '.join(top_missing)} sẽ giúp bạn tăng đáng kể độ phù hợp với vị trí này."

    user_id = session.get('user_id')

    # FIX: Cập nhật đúng tên biến theo Model mới và thêm job_jd
    history_record = CVMatchingHistory(
        user_id=user_id,
        job_title=request.form.get('job_title', 'Vị trí tùy chỉnh'),
        job_jd=jd_text,
        cv_filename=filename,
        overall_score=overall_score,
        skill_score=skill_score,
        exp_score=exp_score,
        matched_skills=json.dumps(matched_skills, ensure_ascii=False),
        missing_skills=json.dumps(missing_skills, ensure_ascii=False)
    )

    db_conn.save_matching_record(history_record)

    response_data = {
        "status": "success",
        "overall_score": overall_score,
        "skill_score": skill_score,
        "semantic_score": semantic_score,
        "exp_score": exp_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestion": suggestion,
        "method_used": ai_result.get("method", "wmd_fasttext"),
        "oov_rate": ai_result.get("oov_rate", 0.0)
    }

    if ai_result.get("method") == "tfidf_fallback":
        response_data["warning"] = "Tỷ lệ từ vựng ngoài từ điển (OOV) cao, hệ thống tự động sử dụng phương án dự phòng TF-IDF để đảm bảo độ chính xác."

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