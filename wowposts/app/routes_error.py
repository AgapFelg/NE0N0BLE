# импорт необходимого
from flask import Blueprint, render_template
# db тут нужно, чтобы в случае чего откатить изменения в БД
from models import db

# объявление блюпринта для ошибок
error_bp = Blueprint('error', __name__, url_prefix='/error')

# хендлеры для ошибок, срабатывают, когда в ответе видят соответствующий код ответа HTTP
# выводит подготовленную страницу для 404 кода ответа
@error_bp.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

# выводит подготовленную страницу для 403 кода ответа
@error_bp.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

# выводит подготовленную страницу для 500 кода ответа
@error_bp.errorhandler(500)
def internal_error(e):
    # отказывает изменения в БД, нужно, чтобы ошибки при работе не навредили БД и тд
    db.session.rollback()
    return render_template('errors/500.html'), 500