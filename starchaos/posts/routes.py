from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from starchaos import db
from starchaos.comments.models import Comment
from starchaos.posts.forms import (
    PostForm
)
from starchaos.posts.models import Post
from starchaos.users.utils import save_image

posts = Blueprint('posts', __name__)


@posts.route('/post/<int:post_id>', methods=['POST', 'GET'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc())

    if request.method == 'POST':
        content = request.form.get('comment_content')
        if content:
            new_comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
            db.session.add(new_comment)
            db.session.commit()
            flash('Your comment is added!', 'success')
        return redirect(url_for('posts.post', post_id=post_id))

    return render_template('post.html', title='Post', post=post, comments=comments)


@posts.route('/post/<int:post_id>/update', methods=['POST', 'GET'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.content = form.content.data
        if form.picture.data:
            post_image = save_image(form.picture.data, (1500, 1500), 'post_images')
            post.image = post_image
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.content.data = post.content
    return render_template('update_post.html', title='Update Post', post=post, form=form)


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.index'))
