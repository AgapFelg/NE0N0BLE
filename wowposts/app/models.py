# импорт модуля для работы с SQLALCHEMY
from flask_login import UserMixin
# импорт дейт тайм для тайм стампов
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# модель пользователей
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    # основные колонки
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    avatar = db.Column(db.String(200)) # сюда надо будет сувать путь к файлу аватара
    biography = db.Column(db.String(3000))

    # отношения
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', backref='followed', lazy=True)
    following = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy=True)

# модель постов
class Post(db.Model):
    __tablename__ = 'posts'
    # основные колонки
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200)) # сюда надо будет сувать путь к файлу имейджа в посте
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # отношения
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')

# модель комментариев
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

# модель лайков
class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # ограничение, чтобы один юзер мог лайкнуть пост только один раз
    __teble_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_like'),)

# модель для подписок
class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # ограничение, чтобы один юзер мог иметь только одну подписпку на другого пользователя (чтобы Леша не был подписан на Петю 5 раз)
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)