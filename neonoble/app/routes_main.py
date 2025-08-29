# импорт необходимых модулей
from flask import Blueprint, request, render_template
from flask_login import current_user, login_required
from models import Post

# объявление блюпринта
main_bp = Blueprint('main', __name__)

# index.html
@main_bp.route('/')
def home():
    # получение из аргументов запроса пользователя номера страницы(по умолчанию 1)
    page = request.args.get('page', 1, type=int)
    # получение списка постов, с пагинацией, по 6 постов (строк таблицы) на 1 страницу
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=6)
    # инициализация переменной для хранения списка постов, которые лайкнул пользователь
    # нужно, чтобы корректно отображать лайки
    liked_post_ids = []
    # проверяет авторизован ли пользователь
    if current_user.is_authenticated:
        # если авторизован, то получает список лайкнутых постов
        liked_post_ids = [like.post_id for like in current_user.likes]
    # рендерится хтмл для главной страницы с отсылкой списка постов и лайкнутых постов
    return render_template('index.html', posts=posts, liked_post_ids=liked_post_ids)

# маршрут в котором будут показываться посты только пользователей, на которых оформлена подписка
@main_bp.route('/feed')
# необходим логин
@login_required
def feed():
    # получения списка тех, на кого подписан
    followed_ids = [f.followed_id for f in current_user.following]
    # получение постов, авторами которых являются те, на кого пользователь подписан и сортировка
    posts = Post.query.filter(Post.user_id.in_(followed_ids)).order_by(Post.created_at.desc()).all()
    # получение списка лайкнутых постов, нужно для отображения лайков
    liked_post_ids = [like.post_id for like in current_user.likes]
    # рендерит страницу, передает посты и список лайкнутых постов
    return render_template('feed.html', posts=posts, liked_post_ids=liked_post_ids)