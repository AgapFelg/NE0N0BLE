# импорт необходимых модулей
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import Config
# импорт веркзеурга
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from models import db
# импорт модулей, которые нужны для создания форм
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
import time

# Сначала создаем экземпляры расширений
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)

    # Загрузка конфигурации
    config = Config()
    app.config['SQLALCHEMY_DATABASE_URI'] = config.database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = config.secret_key
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    # Инициализация расширений с приложением
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    csrf.init_app(app)

    return app


# !!!!#!!!!#!!!!#
# Ф О Р М Ы, ПОТОМ ВЫНЕСТИ В ОТДЕЛЬНЫЙ ФАЙЛ
# !!!!#!!!!#!!!!#
# форма для логина
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('ПОДТВЕРДИТЬ')

# форма для регистрации
class RegistrationForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Нужно повторить пароль', validators=[DataRequired(), EqualTo('password', message="Пароли должны совпадать")])
    submit = SubmitField('Зарегистрироваться')

# форма для создания поста
class CreatePostForm(FlaskForm):
    text = TextAreaField('ТЕКСТ СООБЩЕНИЯ', validators=[DataRequired()])
    image = FileField('ИЗОБРАЖЕНИЕ')
    submit = SubmitField('ОПУБЛИКОВАТЬ СООБЩЕНИЕ')

# форма для редактирования поста
class EditPostForm(FlaskForm):
    text = TextAreaField('ТЕКСТ СООБЩЕНИЯ', validators=[DataRequired()])
    image = FileField('ИЗОБРАЖЕНИЕ | ОПЦИОНАЛЬНО')
    submit = SubmitField('ИЗМЕНИТЬ СООБЩЕНИЕ')

# форма редоактирования профиля
class EditProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message="Обязательное поле"),
        Length(min=3, max=25, message="Длина от 3 до 25 символов")
    ])
    biography = TextAreaField('Биография', validators=[Optional()])
    avatar = FileField('Аватар', validators=[Optional()])
    current_password = PasswordField('Текущий пароль', validators=[Optional()])
    new_password = PasswordField('Новый пароль', validators=[Optional()])
    confirm_password = PasswordField('Подтверждение пароля', validators=[Optional()])

# формя для комментария
class CommentForm(FlaskForm):
    text = TextAreaField('КОММЕНТАРИЙ', validators=[DataRequired()])
    submit = SubmitField('ОТПРАВИТЬ КОММЕНТАРИЙ')

# форма для редактирования комментарий
class EditCommentForm(FlaskForm):
    text = TextAreaField('ИЗМЕНЕННЫЙ КОММЕНТАРИЙ', validators=[DataRequired()])
    submit = SubmitField('ОБНОВИТЬ')

# Создаем приложение
app = create_app()

# Теперь импортируем модели после создания app и db
from models import User, Post, Comment, Like, Follow

@app.shell_context_processor
def make_shell_context():
    return{
        'db': db,
        'User': User,
        'Post': Post,
        'Comment': Comment,
        'Like': Like,
        'Follow': Follow
    }

#МАРШРУТ ДЛЯ КАСТОМНЫХ ОШИБОК
#--------ДОБАВИТЬ МАРШРУТ
#***************************

# МАРШРУТ ДЛЯ ЗАГРУЗКИ ФАЙЛОВ
@app.route('/upload')
def upload_file():
    return 'uploading file'
#====#====#====#
# МАРШРУТЫ ДЛЯ РАБОТЫ С ЛОГИНОМ РЕГИСТРАЦИЕЙ И ТД
# маршрут логина
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# логин
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('НЕВЕРНО', 'danger')
    return render_template('auth/login.html', form=form)

# логаут
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('ДОСТУП К СИСТЕМЕ ПОЛУЧЕН', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)
#====#====#====#
# БАЗОВЫЕ МАРШРУТЫ
# основной маршрут
@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
    return render_template('index.html', posts=posts)

# маршрут в котором будут показываться посты только пользователей, на которых оформлена подписка
@app.route('/feed')
@login_required
def feed():
    followed_ids = [f.followed_id for f in current_user.following]
    posts = Post.query.filter(Post.user_id.in_(followed_ids)).order_by(Post.created_at.desc()).all()
    return render_template('feed.html', posts=posts)

# маршрут "о нас"
@app.route('/about')
def about():
    return render_template('about.html')
#====#====#====#
# МАРШРУТЫ РАБОТЫ С ПРОФИЛЕМ
# маршрут профиля пользователя
@app.route('/user/<username>')
def show_user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    return render_template('user/profile.html', user=user, posts=posts)

# Маршрут для подписки на пользователя
@app.route('/user/<int:user_id>/follow', methods=['POST'])
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
        action='follow'
    db.session.commit()
    return jsonify({'success': True, 'action': action, 'followers_count': len(user.followers)})

# Маршрут для редактирования профиля
@app.route('/user/<username>/edit', methods=['GET', 'POST'])
def user_edit(username):
    print(f'!!!#@@##@$@#$@#$#@%$#@$@# {current_user.username}')
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
#====#====#====#
# МАРШРУТЫ РАБОТЫ С ПОСТАМИ
# маршрут создания поста
@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post(
            text=form.text.data,
            author=current_user
        )
        if form.image.data:
            image = form.image.data
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            filename = secure_filename(image.filename)
            if '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                unique_filename = f"{current_user.id}_{int(time.time())}.{filename.rsplit('.', 1)[1].lower()}"
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                image_path = os.path.join(upload_folder, 'posts', unique_filename)
                image.save(image_path)
                post.image = unique_filename
        db.session.add(post)
        db.session.commit()
        flash('СООБЩЕНИЕ ДОБАВЛЕНО В СИСТЕМУ', 'success')
        return redirect(url_for('home'))
    return render_template('post/create.html', form=form)

# маршрут детализации поста
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def detail_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            text=form.text.data,
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен', 'success')
        return redirect(url_for('detail_post', post_id=post.id))

    return render_template('post/detail.html', post=post, form=form)

# маршрут редактирования поста
@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = EditPostForm(obj=post)
    if form.validate_on_submit():
        post.text = form.text.data
        # Обработка изображения
        if form.image.data:
            # Удаляем старое изображение, если оно есть
            if post.image:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image))
                except OSError:
                    pass
            # Сохраняем новое изображение
            filename = secure_filename(form.image.data.filename)
            unique_filename = f"{post.id}_{int(time.time())}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            form.image.data.save(filepath)
            post.image = unique_filename
        # Обработка удаления изображения
        if 'remove_image' in request.form and request.form['remove_image'] == '1':
            if post.image:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image))
                except OSError:
                    pass
            post.image = None
        db.session.commit()
        flash('Пост успешно обновлен', 'success')
        return redirect(url_for('detail_post', post_id=post.id))
    return render_template('post/edit.html', post=post, form=form)

# маршрут удаления поста
@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and not current_user.is_admin:
        abort(403)
    if post.image:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'posts', post.image))
    db.session.delete(post)
    db.session.commit()
    flash('Пост делитнут', 'info')
    return redirect(url_for('home'))
#====#====#====#
# МАРШРУТЫ РАБОТЫ С КОММЕНТАРИЯМИ
# маршрут добавления комментария
@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    text = request.form.get('text')
    if text:
        comment = Comment(
            text=text,
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен', 'success')
    return redirect(url_for('detail_post', post_id=post.id))

# маршрут редактирования комментария
@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        abort(403)

    form = EditCommentForm(obj=comment)

    if form.validate_on_submit():
        form.populate_obj(comment)
        db.session.commit()
        flash('Комментарий изменен', 'success')
        return redirect(url_for('detail_post', post_id=comment.post_id))

    return render_template('comment/edit.html', comment=comment, form=form)

# маршрут удаления комментария
@app.route('/comment/<int:comment_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    if comment.author != current_user and not current_user.is_admin:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Комментарий удален успешно', 'info')
    return redirect(url_for('detail_post', post_id=post_id))
# маршрут удаления поста
#====#====#====#
# МАРШРУТ ДЛЯ ПОИСКА ПО ПОСТАМ
@app.route('/search')
def search(query):
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('home'))
    results = Post.query.filter(Post.text.ilike(f'%{query}%')).order_by(Post.created_at.desc()).all()
    return render_template('search.html', results=results, query=query)

#====#====#====#
# МАРШРУТ ДЛЯ ЛАЙКОВ
@app.route('/like/<int:post_id>', methods=['POST'])
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

#====#====#====#
# хендлеры-обработчики ошибок

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('errors/500.html'), 500
# -------------------------

# запуск приложения
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)