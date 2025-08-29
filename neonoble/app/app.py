# импорт необходимых модулей
# импорт модулей флоаск, которые необходимы для написания приложения
# Flask - основной модуль, render_template - для рендеринга и отправки хтмл страницы на основе шаблона
# redirect - для редиректа, request - для работы с запросами от клиентов, url_for для генерации URI, например для
# редиректа, или для правильной работы кнопок в шаблонах, flash - для уведомлений, jsonify - для предоставлении
# информации в формате JSON, abort - для отмены, current_app для работы с данными текущего приложения
# например, для получения юзернейма и статуса юзера
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, current_app
# импорт модуля flask_login для работы с авторизацией, LoginManager - класс, в котором реализована основная логика работы
# с авторизироваными пользователями, login_user - авторизовать пользователя, logout_user - деавторизовать юзера
# login_required - декоратор, который указывает на необходимость для исполнения маршрута быть авторизированым
# current_user - для получения информации о текущем авторизированноим пользователе веб приложения
# AnonymousUserMixin - класс для неавторизированных пользователей
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, AnonymousUserMixin
# модуль для работы с БД
from flask_sqlalchemy import SQLAlchemy
# модуль для CSRF защиты
from flask_wtf.csrf import CSRFProtect
# из конфига импорт класса конфига
from config import Config
# импорт веркзеурга
# генерация и проверка хеша пароля
from werkzeug.security import generate_password_hash, check_password_hash
# для безопасного сохранения файлов (в имени файла может быть угроза)
from werkzeug.utils import secure_filename
# для работы со временем
from datetime import datetime
# для работы с операционной системой, сохранения файлов, создания папок для загрузок
import os
# из модуля с моделями БД импорт бдшки
from models import db
# для работы со временем
import time
# импорт форм
from forms import LoginForm, RegistrationForm, CreatePostForm, EditPostForm, EditProfileForm, CommentForm, EditCommentForm

# Сначала создаем экземпляры расширений
login_manager = LoginManager()
csrf = CSRFProtect()
# класс, который присваивает анонимному пользователю методы
# is_following и is_followed_by, нужно для того,чтобы
# не возникало ошибки, когда неавторизованный пользователь переходит на профиль пользователя
# flask пытается у пользователя узнать, подписан он или нет и выдает ошибку
class AnonymousUser(AnonymousUserMixin):
    def is_following(self, user):
        return False

    def is_followed_by(self, user):
        return False
# регистрация вышеописанного класса анонимного пользователя
login_manager.anonymous_user = AnonymousUser

# функция создания приложения
def create_app():
    # инициализация приложения
    app = Flask(__name__)

    # Загрузка конфигурации
    config = Config()
    # присваивание конфига приложения значений из конфигурации
    app.config['SQLALCHEMY_DATABASE_URI'] = config.database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = config.secret_key
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    # Инициализация расширений с приложением
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    csrf.init_app(app)

    # импорт и регистрацию блюпринтов
    # блюпринт логина, регистрации и логаута
    from routes_auth import auth_bp
    app.register_blueprint(auth_bp)
    # блюпринт комментариев
    from routes_comment import comment_bp
    app.register_blueprint(comment_bp)
    # блюпринт ерроров
    from routes_error import error_bp
    app.register_blueprint(error_bp)
    # / блюпринт
    from routes_main import main_bp
    app.register_blueprint(main_bp)
    # блюпринт постов
    from routes_post import post_bp
    app.register_blueprint(post_bp)
    # блюпринт с разным всяким
    from routes_some import some_bp
    app.register_blueprint(some_bp)
    # блюпринт с маршрутами юзера
    from routes_user import user_bp
    app.register_blueprint(user_bp)

    # возвращение экземпляра нашего приложения
    return app

# создаем приложение
app = create_app()

# теперь импортируем модели после создания app и db
from models import User, Post, Comment, Like, Follow
# создаем контекст процессор, он нужен для безошибочной работе БД
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

# для логина
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# запуск приложения
if __name__ == '__main__':
    # для того, чтобы БД работала хорошо
    with app.app_context():
        db.create_all()
    # запуск приложения с включенным дебагером
    app.run(debug=True)