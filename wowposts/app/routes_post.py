# импорт необходимых модулей
from flask import Blueprint, redirect, url_for, render_template, flash, current_app, abort, request
from flask_login import login_required, current_user
from models import Post, db, Comment
from forms import CreatePostForm, CommentForm, EditPostForm
import os
from werkzeug.utils import secure_filename
import time

# объявление блюпринта
post_bp = Blueprint('post', __name__, url_prefix=('/post'))

# маршрут создания поста
@post_bp.route('/post/create', methods=['GET', 'POST'])
# необходим логин
@login_required
def create_post():
    # инициализация формы
    form = CreatePostForm()
    # если нажата кнопка подтверждения в форме
    if form.validate_on_submit():
        # заносятся данные о посте в БД
        post = Post(
            text=form.text.data,
            author=current_user
        )
        # если был прикреплен файл изображение
        if form.image.data:
            # получение изображения из поля
            image = form.image.data
            # тут перечисляются допустимые расширения файла изображения
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            # присваивание безопасного файла имени, чтобы предотвратить использование недопустимых символов в именах файлов
            filename = secure_filename(image.filename)
            # проверяется расширение файла
            if '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                # присваивание уникального имени файла в файловой системе ОС
                unique_filename = f"{current_user.id}_{int(time.time())}.{filename.rsplit('.', 1)[1].lower()}"
                # получение названия папки для загрузок из конфига приложения
                upload_folder = current_app.config['UPLOAD_FOLDER']
                # создает папку для загрузок, если отсутствует
                os.makedirs(upload_folder, exist_ok=True)
                # заканчивается работа над составлением пути для загрузки файла
                # получается пусть до папки для загрузок+подкаталог posts+ плюс файлнейм
                # например /site/app/static/uploads/posts_12345678.png
                image_path = os.path.join(upload_folder, 'posts', unique_filename)
                # сохранение файла
                image.save(image_path)
                # занесение в БД к посту пути к файлу изображения
                post.image = unique_filename
        # добавление изменений в БД
        db.session.add(post)
        # сохранение изменений в БД
        db.session.commit()
        # вывод сообщения о том, что сообщение добавлено
        flash('СООБЩЕНИЕ ДОБАВЛЕНО В СИСТЕМУ', 'success')
        # редирект на главную страницу
        return redirect(url_for('main.home'))
    # рендер страницы создания поста и прикладывание формы
    return render_template('post/create.html', form=form)

# маршрут детализации поста
@post_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def detail_post(post_id):
    # получение из БД поста по айди
    post = Post.query.get_or_404(post_id)
    # создание формы комментария
    form = CommentForm()
    # если была нажата кнопка подтверждения при создании комментария
    if form.validate_on_submit():
        comment = Comment(
            text=form.text.data,
            user_id=current_user.id,
            post_id=post.id
        )
        # добавление изменений в БД
        db.session.add(comment)
        # сохранение изменений в БД
        db.session.commit()
        # вывод сообщения о том, что добавлен комментарий
        flash('Комментарий добавлен', 'success')
        #
        return redirect(url_for('post.detail_post', post_id=post.id))
    return render_template('post/detail.html', post=post, form=form)

# маршрут редактирования поста
@post_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
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
                    # удаляет изображение
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], 'posts', post.image))
                except OSError:
                    # если отлавливается ошибка ОС при попытке удалить изображение, то пропускается
                    pass
            # Сохраняем новое изображение
            filename = secure_filename(form.image.data.filename)
            unique_filename = f"{post.id}_{int(time.time())}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'posts', unique_filename)
            form.image.data.save(filepath)
            post.image = unique_filename
        # Обработка удаления изображения
        if 'remove_image' in request.form and request.form['remove_image'] == '1':
            if post.image:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], 'posts', post.image))
                except OSError:
                    pass
            post.image = None
        db.session.commit()
        flash('Пост успешно обновлен', 'success')
        return redirect(url_for('post.detail_post', post_id=post.id))
    return render_template('post/edit.html', post=post, form=form)

# маршрут удаления поста
@post_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and not current_user.is_admin:
        abort(403)
    if post.image:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], 'posts', post.image))
    db.session.delete(post)
    db.session.commit()
    flash('Пост делитнут', 'info')
    return redirect(url_for('main.home'))