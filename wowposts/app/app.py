# импорт необходимых модулей
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# создание экземпляра БД
db = SQLAlchemy()
# создание экземпляра приложения
app = Flask(__name__)

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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return 'POST-method'
    else:
        return 'login-form'

# маршрут логаута
@app.route('/logout')
def logout():
    return redirect(url_for('login'))

# маршрут регистрации
@app.route('/register')
def register():
    return 'register-form'
#====#====#====#
# БАЗОВЫЕ МАРШРУТЫ
# основной маршрут
@app.route('/')
def home():
    return 'home'

# маршрут в котором будут показываться посты только пользователей, на которых оформлена подписка
@app.route('/feed')
def feed():
    return 'feed'

# маршрут "о нас"
@app.route('/about')
def about():
    return 'about us'
#====#====#====#
# МАРШРУТЫ РАБОТЫ С ПРОФИЛЕМ
# маршрут профиля пользователя
@app.route('/user/<username>')# НУЖНО СДЕЛАТЬ ЧТОБЫ ПОЛЬЗОВАТЕЛЬ МОГ
# РЕДАКТИРОВАТЬ ПРОФИЛЬ
def show_user_profile(username):
    return f'user: {username}'

# Маршрут для подписки на пользователя
@app.route('/user/<username>/follow')
def follow(username):
    return f'follow on {username}'

# Маршрут для редактирования профиля
@app.route('/user/<username>/edit')
def user_edit(username):
    return f'edititng profile of {username}'
#====#====#====#
# МАРШРУТЫ РАБОТЫ С ПОСТАМИ
# маршрут создания поста
@app.route('/post/create')
def create_post():
    return 'create post'

# маршрут детализации поста
@app.route('/post/<int:post_id>')
def detail_post(post_id):
    return f'post #{post_id}'

# маршрут редактирования поста
@app.route('/post/<int:post_id>/edit')
def edit_post(post_id):
    return f'rditing post #{post_id}'
#====#====#====#
# МАРШРУТЫ РАБОТЫ С КОММЕНТАРИЯМИ
# маршрут добавления комментария
@app.route('/post/<int:post_id>/comment')
def add_comment(post_id):
    return f'add comment to post #{post_id}'

# маршрут редактирования комментария
@app.route('/comment/<int:comment_id>/edit')
def edit_comment(comment_id):
    return f'editing comment #{comment_id}'

# маршрут удаления комментария
@app.route('/comment/<int:comment_id>/delete')
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