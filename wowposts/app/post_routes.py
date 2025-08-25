from flask import Blueprint, redirect, url_for, render_template, flash, current_app, abort, request
from flask_login import login_required, current_user
from models import Post, db, Comment
from forms import CreatePostForm, CommentForm, EditPostForm
import os
from werkzeug.utils import secure_filename
import time

post_bp = Blueprint('post', __name__, url_prefix=('/post'))

# маршрут создания поста
@post_bp.route('/post/create', methods=['GET', 'POST'])
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
@post_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
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
@post_bp.route('/post/<int:post_id>/delete', methods=['POST'])
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