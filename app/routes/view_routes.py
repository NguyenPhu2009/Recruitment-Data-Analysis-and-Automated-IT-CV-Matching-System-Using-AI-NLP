from flask import Blueprint, render_template

view_bp = Blueprint('views', __name__)

@view_bp.route('/')
def home():
    return render_template('index.html')