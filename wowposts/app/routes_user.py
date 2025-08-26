from flask import Blueprint, render_template, abort, jsonify, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, Post, db, Follow
from forms import EditProfileForm

user_bp = Blueprint('user', __name__, url_prefix='/user')

# маршрут профиля пользователя
@user_bp.route('/user/<username>')
def show_user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    liked_post_ids = []
    if current_user.is_authenticated:
        liked_post_ids = [like.post_id for like in current_user.likes]
    liked_posts = [like.post for like in user.likes]
    return render_template('user/profile.html',
                           user=user,
                           posts=posts,
                           liked_post_ids=liked_post_ids,
                           liked_posts=liked_posts)  # Добавляем это

# Маршрут для подписки на пользователя
@user_bp.route('/user/<int:user_id>/follow', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        return jsonify({'success': False, 'message': 'НЕЛЬЗЯ ПОДПИСАТЬСЯ НА СЕБЯ'}), 400
    existing_follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user.id).first()
    if existing_follow:
        db.session.delete(existing_follow)
        action = 'unfollow'
    else:
        new_follow = Follow(follower_id=current_user.id, followed_id=user.id)
        db.session.add(new_follow)
        action = 'follow'
    db.session.commit()
    return jsonify({
        'success': True,
        'action': action,
        'followers_count': len(user.followers),
        'user_id': user.id  # Добавляем ID пользователя для обновления всех кнопок
    })

# Маршрут для редактирования профиля
@user_bp.route('/user/<username>/edit', methods=['GET', 'POST'])
def user_edit(username):
    if current_user.username != username:
        abort(403)
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        try:
            current_user.username = form.username.data
            current_user.biography = form.biography.data
            if form.avatar.data:
                filename = secure_filename(f'avatar_{current_user.id}.{form.avatar.data.filename.split('.')[-1]}')
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'avatars', filename)
                form.avatar.data.save(filepath)
                current_user.avatar=filename
            if form.new_password.data:
                if check_password_hash(current_user.password_hash, form.current_password.data):
                    current_user.password_hash = generate_password_hash(form.new_password.data)
                else:
                    flash('НЕВЕРНЫЙ КОД ДОСТУПА', 'danger')
                    return redirect(url_for('user_edit', username=username))
            db.session.commit()
            flash('ДАННЫЕ ИЗМЕНЕНЫ', 'success')
            return redirect(url_for('show_user_profile', username=current_user.username))
        except Exception as e:
            db.session.rollback()
            flash(f'ОШИБКА ОБНОВЛЕНИЯ ДАННЫХ: {str(e)}', 'danger')
    return render_template('user/edit.html', form=form)