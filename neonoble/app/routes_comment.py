# импорт необходимого
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import Post, db, Comment
from forms import EditCommentForm

# объявление блюпринта
comment_bp = Blueprint('comment', __name__, url_prefix=('/comment'))

# маршрут добавления комментария
@comment_bp.route('/post/<int:post_id>/comment', methods=['POST'])
# необходим логин
@login_required
def add_comment(post_id):
    # получение поста из БД
    post = Post.query.get_or_404(post_id)
    # получение текста из формы
    text = request.form.get('text')
    # если текст присутствует в форме
    if text:
        # создание нового комментария в БД
        comment = Comment(
            text=text,
            user_id=current_user.id,
            post_id=post.id
        )
        # добавление изменений в БД
        db.session.add(comment)
        # сохранение изменений в БД
        db.session.commit()
        # вывод сообщения о том, что комментарий добавлен
        flash('Комментарий добавлен', 'success')
    # редиректит на сформированный url_for url поста на который был добавлен комментарий
    return redirect(url_for('post.detail_post', post_id=post.id))

# маршрут редактирования комментария
@comment_bp.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
# необходим логин
@login_required
def edit_comment(comment_id):
    # получение комментария из БД по его айди
    comment = Comment.query.get_or_404(comment_id)
    # проверка того, является ли пользователь автором комментария, если не является, то абортит
    if comment.author != current_user:
        abort(403)
    # объявление формы
    form = EditCommentForm(obj=comment)
    # если было подтверждена форма
    if form.validate_on_submit():
        # заполняет атрибуты (ячейки таблицы) текущего комментария данными из формы
        form.populate_obj(comment)
        # сохранение изменения
        db.session.commit()
        # вывод сообщения об изменении
        flash('Комментарий изменен', 'success')
        # редиректит на полученный url_for url для поста
        return redirect(url_for('post.detail_post', post_id=comment.post_id))
    # рендеринг хтмл страницы изменения комментария с передачей комменатрия, который будет редактироваться
    return render_template('comment/edit.html', comment=comment, form=form)

# маршрут удаления комментария
@comment_bp.route('/comment/<int:comment_id>/delete', methods=['GET', 'POST'])
# необходим логин
@login_required
def delete_comment(comment_id):
    # получения комментария из БД
    comment = Comment.query.get_or_404(comment_id)
    # получения айди поста по комментарию
    post_id = comment.post_id
    # если пользователь, который пытается удалить комменатрий, не является автором поста, то его абортит
    if comment.author != current_user:
        abort(403)
    # удаления записи из БД
    db.session.delete(comment)
    # сохранение изменений
    db.session.commit()
    # вывод сообщения об успешном удалении комментария
    flash('Комментарий удален успешно', 'info')
    # редиректит на полученный url_for url для конкретного поста
    return redirect(url_for('post.detail_post', post_id=post_id))