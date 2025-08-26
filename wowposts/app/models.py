# импорт модуля для работы с SQLALCHEMY
from flask_login import UserMixin
# импорт дейт тайм для тайм стампов
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# создание экземпляра БД, через него происходит работа с БД в моделях, а также он вызывается в других
# частях кода
db = SQLAlchemy()

# модель пользователей
class User(db.Model, UserMixin):
    # присваивание имени таблице
    __tablename__ = 'users'
    # основные колонки
    # айди, примари кей, числовое значение
    id = db.Column(db.Integer, primary_key=True)
    # имя пользователя, строка, максимум 50 символов, должно быть уникальным и не может быть пустым
    username = db.Column(db.String(50), unique=True, nullable=False)
    # емейл пользователя, строка, максимум 100 символов, должен быть уникальным и не может быть пустым
    email = db.Column(db.String(100), unique=True, nullable=False)
    # хеш пароля, 256 символов, соответствует длине хешированного значения используемого данным хеш-алгоритмом
    password_hash = db.Column(db.String(256), nullable=False)
    # проставляется таймстамп через datetime.now, сейчашный, когда был создан юзер
    created_at = db.Column(db.DateTime, default=datetime.now)
    avatar = db.Column(db.String(200)) # сюда надо будет сувать путь к файлу аватара
    # биография пользователя, строка, максимум три тысячи символов
    biography = db.Column(db.String(3000))

    # отношения
    # связь 1 ко многимм с постами
    # backref='author' автоматически добавит поле author в модель Post
    # lazy=True - данные подгружаются при обращении
    # cascade all delete-orphan - при удалении пользователя все его посты будут удалены
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    # также связь, но с комментариями и без каскадного удаления
    comments = db.relationship('Comment', backref='author', lazy=True)
    # связь с лайками
    likes = db.relationship('Like', backref='user', lazy=True)
    # подписчики данного пользователя, foreign_key указывает на столбец для связи
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', backref='followed', lazy=True)
    # подписки, на кого данный пользователь подписан, аналогично
    following = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy=True)
    # методы для работы с подписками
    # данный метод проверяет, подписан ли текущий пользователь на указанного
    def is_following(self, user):
        return Follow.query.filter_by(follower_id=self.id, followed_id=user.id).first() is not None
    # данный метод проверяет подписан ли указанный пользователь на текущего
    def is_followed_by(self, user):
        return Follow.query.filter_by(follower_id=self.id, followed_id=self.id).first() is not None
    # метод для создания подписки
    def follow(self, user):
        # создает подписку если подписки нет
        if not self.is_following(user):
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)
            db.session.commit()
    # удаление подписки
    def unfollow(self, user):
        follow = Follow.query.filter_by(follower_id=self.id, followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    @property
    def User(self, post_id):
        # проверяет, лайкнул ли пользователь пост
        return any(like.post_id == post_id for file in self.likes)

# модель постов
class Post(db.Model):
    __tablename__ = 'posts'
    # основные колонки
    # айдишник, число первичный ключ
    id = db.Column(db.Integer, primary_key=True)
    # текст, не может быть пустым
    text = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200)) # сюда надо будет сувать путь к файлу имейджа в посте
    # указывает время, когда был создан пост, данное значение индексируется
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    # айди пользователя, автора поста, внешний ключ
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # тут ссылка на автора
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False) # а тут ссылка на пост

# модель лайков
class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True) # айди лайка
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # ссылка на того, кто лайкнул
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False) # ссыдка на то, что лайкнул
    created_at = db.Column(db.DateTime, default=datetime.now)

    # ограничение, чтобы один юзер мог лайкнуть пост только один раз
    __teble_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_like'),)

# модель для подписок
class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # кто подписан
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # на кого подписан
    created_at = db.Column(db.DateTime, default=datetime.now)

    # ограничение, чтобы один юзер мог иметь только одну подписпку на другого пользователя (чтобы Леша не был подписан на Петю 5 раз)
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)