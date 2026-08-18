import re

def extract_matched_and_missing_skills(cv_text: str, jd_skills: list) -> tuple:
    if not cv_text or not jd_skills:
        return [], jd_skills

    cv_text_lower = cv_text.lower()
    matched_skills = []
    missing_skills = []

    for skill in jd_skills:
        skill_lower = skill.lower()

        escaped_skill = re.escape(skill_lower)

        if re.search(r'\w$', skill_lower):
            pattern = r'\b' + escaped_skill + r'\b'
        else:
            pattern = r'\b' + escaped_skill

        if re.search(pattern, cv_text_lower):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    return matched_skills, missing_skills