# импорт необходимпого
from flask import Blueprint, render_template, abort, jsonify, flash, redirect, url_for, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, Post, db, Follow
from forms import EditProfileForm
import os

# объявление блюпринта
user_bp = Blueprint('user', __name__, url_prefix='/user')

# маршрут профиля пользователя
@user_bp.route('/user/<username>')
def show_user_profile(username):
    # из БД получается пользователь по юзернейму
    user = User.query.filter_by(username=username).first_or_404()
    # получение из БД постов пользователя по его айдишнику и сортировка
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    # инициализация переменной для хранения лайкнутых постов
    liked_post_ids = []
    # проверка того, авторизован ли пользователь
    # если авторизован, то получение айди постов записи в бд текущего пользователя
    if current_user.is_authenticated:
        liked_post_ids = [like.post_id for like in current_user.likes]
    # тоже получение списка лайкнутых постов, НО уже для того пользователя
    # в чей профиль совершен переход (вкладка "ЛАЙКИ" в профиле)
    liked_posts = [like.post for like in user.likes]
    # рендер хтмл с передачей данных
    return render_template('user/profile.html',
                           user=user,
                           posts=posts,
                           liked_post_ids=liked_post_ids,
                           liked_posts=liked_posts)

# маршрут для подписки на пользователя
@user_bp.route('/user/<int:user_id>/follow', methods=['POST'])
# необходим логин
@login_required
def follow(user_id):
    # получение пользователя по юзер айди
    user = User.query.get_or_404(user_id)
    # если пользователь на которого собираются подписаться является пользователем, который хочет подписаться
    # то не дает и выводит сообщение
    if user == current_user:
        return jsonify({'success': False, 'message': 'НЕЛЬЗЯ ПОДПИСАТЬСЯ НА СЕБЯ'}), 400
    # проверка того, подписан ли пользователь, или нет, с помощью получения записи из БД
    existing_follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user.id).first()
    # если запись была получена, то происходит отписка, удаление записи о подписке
    if existing_follow:
        db.session.delete(existing_follow)
        action = 'unfollow'
    # если запись не была получена (пользователь не подписан), то
    # создается запись о подписке (пользователь подписывается)
    else:
        new_follow = Follow(follower_id=current_user.id, followed_id=user.id)
        db.session.add(new_follow)
        action = 'follow'
    # сохранение изменений в БД
    db.session.commit()
    # передача json, необходима для корректного отображения в js
    return jsonify({
        'success': True,
        'action': action,
        'followers_count': len(user.followers),
        'user_id': user.id
    })

# маршрут для редактирования профиля
@user_bp.route('/user/<username>/edit', methods=['GET', 'POST'])
def user_edit(username):
    # если текущий пользователь это не пользователь, профиль которого будет редактироваться
    # то есть пользователь собирается редактировать не свой профиль, то его абортит
    if current_user.username != username:
        abort(403)
    # объявляется форма редактирования профиля
    form = EditProfileForm(obj=current_user)
    # если была нажата кнопка подтверждения в форме редактирования профиля
    if form.validate_on_submit():
        try:
            # имя пользователя в БД заменяется на   имя пользователя из формы
            current_user.username = form.username.data
            # биография в БД заменяется на биографию пользователя из формы
            current_user.biography = form.biography.data
            if form.avatar.data:
                # если поле с аватаром не пустое (происходит замена аватара), то
                # файлу нового аватара присваивается безопасное имя файла
                filename = secure_filename(f'avatar_{current_user.id}.{form.avatar.data.filename.split('.')[-1]}')
                # происходит формирование пути к файлу
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', filename)
                # аватар сохраняется в файловой системе сервера
                form.avatar.data.save(filepath)
                # в БД заносится имя аватара
                current_user.avatar=filename
            if form.new_password.data:
                # если в поле есть пароль (происходит смена пароля), то
                # пользователю в БД заносится новый хеш пароля
                # а если старый пароль неверный, то выводит ошибку
                if check_password_hash(current_user.password_hash, form.current_password.data):
                    current_user.password_hash = generate_password_hash(form.new_password.data)
                else:
                    flash('НЕВЕРНЫЙ КОД ДОСТУПА', 'danger')
                    # редиректит на страницу изменения профиля
                    return redirect(url_for('user.user_edit', username=username))
            # сохранения измений в БД
            db.session.commit()
            # выовод сообщения о том, что профиль изменен
            flash('ДАННЫЕ ИЗМЕНЕНЫ', 'success')
            # редиректит на страницу профиля пользователя
            return redirect(url_for('user.show_user_profile', username=current_user.username))
        # если во времяф редактирования профиля отлавливается исключение, то
        # изменения в БД откатываются и выводится сообщение о том, что
        # данные обновить не получилось
        except Exception as e:
            db.session.rollback()
            flash(f'ОШИБКА ОБНОВЛЕНИЯ ДАННЫХ: {str(e)}', 'danger')
    # рендер хтмл страницу редактирования профиля с формой
    return render_template('user/edit.html', form=form)