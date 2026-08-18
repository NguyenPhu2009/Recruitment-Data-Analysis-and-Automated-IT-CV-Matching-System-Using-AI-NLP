import re
from app.models.database import db
from app.models.skills_dict import SkillsDict

# Biến toàn cục để cache từ điển kỹ năng, tránh query DB nhiều lần
_SKILLS_CACHE = []


def get_all_skills_from_dict():
    """Load từ điển kỹ năng từ CSDL vào RAM (chỉ chạy 1 lần)"""
    global _SKILLS_CACHE
    if not _SKILLS_CACHE:
        try:
            # Lấy tất cả tên kỹ năng từ DB
            skills = SkillsDict.query.all()
            _SKILLS_CACHE = [s.skill_name for s in skills]
        except Exception as e:
            print(f"Lỗi load Skills_Dict: {e}")
            # Danh sách dự phòng nếu chưa có DB
            _SKILLS_CACHE = ["Python", "Java", "C++", "C#", ".NET", "ReactJS", "Node.js", "AWS", "Docker", "SQL",
                             "Machine Learning"]
    return _SKILLS_CACHE


def extract_skills_from_text(text: str) -> list:
    """Trích xuất danh sách kỹ năng từ một đoạn Text bất kỳ (JD hoặc CV)"""
    if not text:
        return []

    text_lower = text.lower()
    found_skills = []
    all_skills = get_all_skills_from_dict()

    for skill in all_skills:
        skill_lower = skill.lower()
        escaped_skill = re.escape(skill_lower)

        # FIX LOGIC REGEX CHO CẢ ĐẦU VÀ CUỐI
        # Nếu bắt đầu bằng chữ/số -> dùng \b. Nếu bắt đầu bằng ký tự đặc biệt (.NET) -> dùng (?<!\w)
        prefix = r'\b' if re.match(r'^\w', skill_lower) else r'(?<!\w)'

        # Nếu kết thúc bằng chữ/số -> dùng \b. Nếu kết thúc bằng ký tự đặc biệt (C++, C#) -> dùng (?!\w)
        suffix = r'\b' if re.search(r'\w$', skill_lower) else r'(?!\w)'

        pattern = prefix + escaped_skill + suffix

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return found_skills


def extract_matched_and_missing_skills(cv_text: str, jd_skills: list) -> tuple:
    """Hàm cũ của bạn đã được tối ưu lại Regex"""
    if not cv_text or not jd_skills:
        return [], jd_skills

    cv_text_lower = cv_text.lower()
    matched_skills = []
    missing_skills = []

    for skill in jd_skills:
        skill_lower = skill.lower()
        escaped_skill = re.escape(skill_lower)

        # Áp dụng Regex đã fix
        prefix = r'\b' if re.match(r'^\w', skill_lower) else r'(?<!\w)'
        suffix = r'\b' if re.search(r'\w$', skill_lower) else r'(?!\w)'
        pattern = prefix + escaped_skill + suffix

        if re.search(pattern, cv_text_lower):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    return matched_skills, missing_skills