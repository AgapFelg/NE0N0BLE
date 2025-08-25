# импорт необходимого
from flask import Blueprint, render_template
from models import db

error_bp = Blueprint('error', __name__, url_prefix='/error')

# хендлеры для ошибок, в описании не нуждаются
@error_bp.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@error_bp.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@error_bp.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('errors/500.html'), 500