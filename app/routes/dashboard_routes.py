from flask import Blueprint, jsonify
from sqlalchemy import func
from ..models.database import db
from ..models.job_posting import JobPosting
from ..models.skills_dict import SkillsDict, job_skill

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/top-skills', methods=['GET'])
def get_top_skills():
    results = db.session.query(
        SkillsDict.skill_name,
        func.count(job_skill.c.job_id).label('job_count')
    ).join(job_skill, SkillsDict.skill_id == job_skill.c.skill_id)\
     .group_by(SkillsDict.skill_name)\
     .order_by(func.count(job_skill.c.job_id).desc())\
     .limit(10).all()

    data = [{"skill_name": row[0], "job_count": row[1]} for row in results]
    return jsonify({"status": "success", "top_skills": data}), 200


@dashboard_bp.route('/salary-by-level', methods=['GET'])
def get_salary_by_level():
    eff_min = func.coalesce(JobPosting.salary_min, JobPosting.salary_max)
    eff_max = func.coalesce(JobPosting.salary_max, JobPosting.salary_min)
    avg_salary = (eff_min + eff_max) / 2

    results = db.session.query(
        JobPosting.job_level,
        func.avg(avg_salary).label('avg_salary')
    ).filter(
        eff_min.isnot(None), # Chỉ cần có 1 trong 2 là tính được
        JobPosting.job_level.isnot(None),
        JobPosting.job_level != ''
    ).group_by(JobPosting.job_level)\
     .order_by(func.avg(avg_salary).desc()).all()

    data = [{"job_level": row[0], "avg_salary_million_vnd": round(row[1] / 1000000, 1) if row[1] else 0} for row in results]
    return jsonify({"status": "success", "salary_by_level": data}), 200


@dashboard_bp.route('/job-type-distribution', methods=['GET'])
def get_job_type_distribution():
    results = db.session.query(
        JobPosting.job_type,
        func.count(JobPosting.job_id).label('count')
    ).filter(JobPosting.job_type.isnot(None))\
     .group_by(JobPosting.job_type)\
     .order_by(func.count(JobPosting.job_id).desc()).all()

    data = [{"job_type": row[0], "count": row[1]} for row in results]
    return jsonify({"status": "success", "job_type_distribution": data}), 200


@dashboard_bp.route('/top-locations', methods=['GET'])
def get_top_locations():
    results = db.session.query(
        JobPosting.location,
        func.count(JobPosting.job_id).label('count')
    ).filter(JobPosting.location.isnot(None))\
     .group_by(JobPosting.location)\
     .order_by(func.count(JobPosting.job_id).desc())\
     .limit(5).all()

    data = [{"location": row[0], "count": row[1]} for row in results]
    return jsonify({"status": "success", "top_locations": data}), 200