# из фласка, блюпринт для создания блюпринтов (введения модульности), редирект для перенаправления на страциы, url_for для формирования url,
# flash для сообщений, render_template - для рендеринга и отправки хтмл
from flask import Blueprint, redirect, url_for, flash, render_template
# необходимо для работы с логином и сессией пользователя
from flask_login import current_user, login_user, login_required, logout_user
# для составления и проверки хеша пароля
from werkzeug.security import check_password_hash, generate_password_hash
# импорт модели user для взаимодей2ствия с пользователями, а также db для работы с БД, которая не описана в моделях
from models import User, db
# импорт необходимых форм
from forms import LoginForm, RegistrationForm

# объявление блюпринта, присваивание ему имени и url префикса
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# логин
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # если пользователь авторизирован, то его редиректит на главную страницу
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    # объявление формы для логина
    form = LoginForm()
    # происходит если заполнена форма и нажата кнопка подтверждения
    if form.validate_on_submit():
        # получение пользователя из модели по емейлу, получение первого результата
        user = User.query.filter_by(email=form.email.data).first()
        # если пользователь найден и если check_password_hash после проверки хеша пароля возвращает true, то происходит
        if user and check_password_hash(user.password_hash, form.password.data):
            # логинит пользователя
            login_user(user)
            # редиректит на главную страницу
            return redirect(url_for('main.home'))
        # если не получается войти, то говорит, что неверно введено
        flash('НЕВЕРНО', 'danger')
        # рендерит хтмл логина с формой логина
    return render_template('auth/login.html', form=form)

# логаут
@auth_bp.route('/logout')
# необходимо, чтобы пользователь был авторизоварн
@login_required
def logout():
    # происходит разлогинивание пользователя и редиректит на главную страницу
    logout_user()
    return redirect(url_for('main.home'))

# регистрация
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Если пользователь авторизован, то его перенаправляет на главную страницу
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    # инициализация формы регистрации
    form = RegistrationForm()
    # если в форме была нажата кнопка подтверждения
    if form.validate_on_submit():
        # генерация хеша пароля из значения формы
        hashed_password = generate_password_hash(form.password.data)
        # создание нового пользователя
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        # добавление нового пользователя
        db.session.add(user)
        # коммит изменений
        db.session.commit()
        # вывод сообщения
        flash('ДОСТУП К СИСТЕМЕ ПОЛУЧЕН', 'success')
        # после регистрации редиректит на страницу логина
        return redirect(url_for('auth.login'))
    # рендер хтмл страницы регистрации
    return render_template('auth/register.html', form=form)