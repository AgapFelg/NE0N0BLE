# импорт необходимого из flask
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Like, Post, db

# инициализация блюпринта для разных маршрутов
some_bp = Blueprint('some', __name__)

# МАРШРУТ ДЛЯ ЗАГРУЗКИ ФАЙЛОВ
@some_bp.route('/upload')
def upload_file():
    return 'uploading file'

# МАРШРУТ ДЛЯ ЛАЙКОВ
@some_bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post.id
    ).first()
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        new_like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(new_like)
        liked = True
    db.session.commit()
    updated_post = Post.query.get(post_id)
    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': len(updated_post.likes)
    })

