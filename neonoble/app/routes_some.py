# импорт необходимого из flask
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Like, Post, db

# инициализация блюпринта для разных маршрутов
some_bp = Blueprint('some', __name__)

# маршрут для загрузки файлов
@some_bp.route('/upload')
def upload_file():
    return 'uploading file'

# маршрут для лайков, принимает только POST, привязан к айдишнику поста
@some_bp.route('/like/<int:post_id>', methods=['POST'])
# необходим логин
@login_required
def like(post_id):
    # получение поста из БД
    post = Post.query.get_or_404(post_id)
    # получение записи из БД о лайке конкретного пользователя на конкретный пост
    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post.id
    ).first()
    # если лайк уже стоит, то удаляется запись о лайке из бд (снимается лайк)
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    # если лайк не стоит, то создается новая запись о лайке в БД (ставится лайк)
    else:
        new_like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(new_like)
        liked = True
    # сохранение изменений в БД
    db.session.commit()
    # еще раз получаем пост, для того, чтобы получить актуальное количество лайков
    updated_post = Post.query.get(post_id)
    # возвращается json с данными о лайке и тд, для успешного отображения с помощью js
    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': len(updated_post.likes)
    })

