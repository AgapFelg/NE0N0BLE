# импорт необходимых модулей
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from config import Config
# импорт веркзеурга
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
# импорт моделей
from models import User, Post, Comment, Like, Follow
from datetime import datetime
import os

# создание экземпляра конфига
config = Config()
# создание экземпляра приложения
app = Flask(__name__)
# конфигурация приложения
app.config['SQLALCHEMY_DATABASE_URI'] = config.database_uri
app.config['SECRET_KEY'] = config.secret_key
app.config['UPLOAD_FOLDER'] = 'static/uploads'
# инициализация БД
db = SQLAlchemy(app)
# инициализация логин манагера
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('home'))
        flash("НЕверный email или пароль", 'danger')
    return render_template('auth/login.html')

# логаут
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# регистрация
@app.route('/register', methods=['GET', 'POST']))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        hash_of_password = generate_password_hash(request.form['password'])
        user = User(username=request.form['username'], email=request.form['email'],
                    password_hash=hash_of_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Регистрация выполнена', 'success')
            return redirect(url_for('login'))
        except:
            flash('Регистрация не выполнена', 'danger')
    return render_template('auth/register.html')
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
    return f'user: {username}'

# Маршрут для подписки на пользователя
@app.route('/user/<username>/follow', methods=['POST'])
def follow(username):
    return f'follow on {username}'

# Маршрут для редактирования профиля
@app.route('/user/<username>/edit', methods=['POST'])
def user_edit(username):
    return f'edititng profile of {username}'
#====#====#====#
# МАРШРУТЫ РАБОТЫ С ПОСТАМИ
# маршрут создания поста
@app.route('/post/create', methods=['GET', 'POST'])
def create_post():
    return 'create post'

# маршрут детализации поста
@app.route('/post/<int:post_id>')
def detail_post(post_id):
    return f'post #{post_id}'

# маршрут редактирования поста
@app.route('/post/<int:post_id>/edit', methods=['POST'])
def edit_post(post_id):
    return f'rditing post #{post_id}'
#====#====#====#
# МАРШРУТЫ РАБОТЫ С КОММЕНТАРИЯМИ
# маршрут добавления комментария
@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    return f'add comment to post #{post_id}'

# маршрут редактирования комментария
@app.route('/comment/<int:comment_id>/edit', methods=['POST'])
def edit_comment(comment_id):
    return f'editing comment #{comment_id}'

# маршрут удаления комментария
@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    return f'deleting comment #{comment_id}'
# маршрут удаления поста
#====#====#====#
# МАРШРУТ ДЛЯ ПОИСКА ПО ПОСТАМ
@app.route('/search?q=<query>')
def search(query):
    return f'results on {query}'
# -------------------------

# запуск приложения
if __name__ == '__main__':
    app.run()