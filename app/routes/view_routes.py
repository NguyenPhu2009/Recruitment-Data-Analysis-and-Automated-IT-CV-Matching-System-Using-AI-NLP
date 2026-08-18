from flask import Blueprint, render_template, session, redirect, url_for
from ..models.cv_matching_history import CVMatchingHistory

view_bp = Blueprint('views', __name__)


@view_bp.route('/')
def home():
    return render_template('index.html')


@view_bp.route('/dashboard')
def dashboard():
    return render_template('pages/dashboard.html')


@view_bp.route('/auth')
def auth():
    # Nếu đã đăng nhập thì không cần vào lại trang auth
    if session.get('user_id'):
        return redirect(url_for('views.match'))
    return render_template('pages/auth.html')


@view_bp.route('/match')
def match():
    return render_template('pages/match.html')


@view_bp.route('/history')
def history():
    user_id = session.get('user_id')

    # Nếu chưa đăng nhập, chuyển hướng về trang đăng nhập
    if not user_id:
        return redirect(url_for('views.auth'))

    # Truy vấn trực tiếp lịch sử của user (Không còn phụ thuộc vào bảng Job_Postings)
    history_records = CVMatchingHistory.query.filter_by(user_id=user_id) \
        .order_by(CVMatchingHistory.analyzed_at.desc()).all()

    return render_template('pages/history.html', history_list=history_records)