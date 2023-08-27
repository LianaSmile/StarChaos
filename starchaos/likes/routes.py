from flask import redirect, request, Blueprint
from starchaos.posts.models import Post
from starchaos import db
from flask_login import current_user, login_required

likes = Blueprint('likes', __name__)


@likes.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)
