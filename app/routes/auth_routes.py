import re
from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.database import db
from ..models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not full_name or not email or not password:
        return jsonify({"status": "error", "message": "Vui lòng điền đầy đủ thông tin!"}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"status": "error", "message": "Định dạng Email không hợp lệ!"}), 400

    if len(password) < 6:
        return jsonify({"status": "error", "message": "Mật khẩu phải có tối thiểu 6 ký tự!"}), 400

    if confirm_password and password != confirm_password:
        return jsonify({"status": "error", "message": "Mật khẩu nhập lại không khớp!"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"status": "error", "message": "Email này đã được đăng ký!"}), 409

    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(
        full_name=full_name,
        email=email,
        password_hash=hashed_pw
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Đăng ký tài khoản thành công!",
            "user_id": new_user.user_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Lỗi hệ thống: {str(e)}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({"status": "error", "message": "Vui lòng nhập Email và Mật khẩu!"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"status": "error", "message": "Email hoặc mật khẩu không chính xác!"}), 401

    session['user_id'] = user.user_id
    session['user_email'] = user.email
    session['user_name'] = user.full_name

    return jsonify({
        "status": "success",
        "message": "Đăng nhập thành công!",
        "user": {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Đã đăng xuất thành công!"}), 200


@auth_bp.route('/me', methods=['GET'])
def check_me():
    if 'user_id' in session:
        return jsonify({
            "is_logged_in": True,
            "user": {
                "user_id": session['user_id'],
                "full_name": session.get('user_name'),
                "email": session.get('user_email')
            }
        }), 200
    return jsonify({"is_logged_in": False}), 200


@auth_bp.route('/reset-password-demo', methods=['POST'])
def reset_password_demo():
    data = request.get_json() or {}

    email = data.get('email', '').strip().lower()
    new_password = data.get('new_password', '')

    if not email or not new_password:
        return jsonify({"status": "error", "message": "Vui lòng nhập email và mật khẩu mới!"}), 400

    if len(new_password) < 6:
        return jsonify({"status": "error", "message": "Mật khẩu phải có tối thiểu 6 ký tự!"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"status": "error", "message": "Email không tồn tại trong hệ thống!"}), 404

    try:
        hashed_pw = generate_password_hash(new_password, method='pbkdf2:sha256')
        user.password_hash = hashed_pw
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Mật khẩu đã được cập nhật thành công!"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Lỗi hệ thống: {str(e)}"}), 500