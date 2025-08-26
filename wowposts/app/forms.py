# импорт модулей, которые нужны для создания форм
from flask_wtf import FlaskForm
# импорт типов полей
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
# импорт валидации
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

# форма для логина, емейл, пароль и кнопка подтвержлдения
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('ПОДТВЕРДИТЬ')

# форма для регистрации, имя пользователя, емейл, пароль, подтверждение пароля и подтверждение
class RegistrationForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    # тут проверяется, одинаковое ли значение в обоих полях и если оно отличается, то сообщается, что пароли должны совпадать
    confirm_password = PasswordField('Нужно повторить пароль', validators=[DataRequired(), EqualTo('password', message="Пароли должны совпадать")])
    submit = SubmitField('Зарегистрироваться')

# форма для создания поста, поле для текста, для изображения и кнопка подтверждения
class CreatePostForm(FlaskForm):
    text = TextAreaField('ТЕКСТ СООБЩЕНИЯ', validators=[DataRequired()])
    image = FileField('ИЗОБРАЖЕНИЕ')
    submit = SubmitField('ОПУБЛИКОВАТЬ СООБЩЕНИЕ')

# форма для редактирования поста, поле для текста, для изображения и кнопка подтверждения
class EditPostForm(FlaskForm):
    text = TextAreaField('ТЕКСТ СООБЩЕНИЯ', validators=[DataRequired()])
    image = FileField('ИЗОБРАЖЕНИЕ | ОПЦИОНАЛЬНО')
    submit = SubmitField('ИЗМЕНИТЬ СООБЩЕНИЕ')

# форма редоактирования профиля, имя пользователя, биография пользователя
# аватар пользователя, а также для смены пароля
# нынешний пароль, новый пароль и подтверждение нового пароля
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

# формя для комментария, текст и кнопка для подтверждения
class CommentForm(FlaskForm):
    text = TextAreaField('КОММЕНТАРИЙ', validators=[DataRequired()])
    submit = SubmitField('ОТПРАВИТЬ КОММЕНТАРИЙ')

# форма для редактирования комментарий, аналогично форме для комментария
class EditCommentForm(FlaskForm):
    text = TextAreaField('ИЗМЕНЕННЫЙ КОММЕНТАРИЙ', validators=[DataRequired()])
    submit = SubmitField('ОБНОВИТЬ')