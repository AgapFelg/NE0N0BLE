from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import Post, db, Comment
from forms import EditCommentForm

comment_bp = Blueprint('comment', __name__, url_prefix=('/comment'))

# маршрут добавления комментария
@comment_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    text = request.form.get('text')
    if text:
        comment = Comment(
            text=text,
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен', 'success')
    return redirect(url_for('detail_post', post_id=post.id))

# маршрут редактирования комментария
@comment_bp.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        abort(403)

    form = EditCommentForm(obj=comment)

    if form.validate_on_submit():
        form.populate_obj(comment)
        db.session.commit()
        flash('Комментарий изменен', 'success')
        return redirect(url_for('detail_post', post_id=comment.post_id))

    return render_template('comment/edit.html', comment=comment, form=form)

# маршрут удаления комментария
@comment_bp.route('/comment/<int:comment_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    if comment.author != current_user and not current_user.is_admin:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Комментарий удален успешно', 'info')
    return redirect(url_for('detail_post', post_id=post_id))