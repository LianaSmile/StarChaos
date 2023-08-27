from flask import flash, redirect, request, abort, Blueprint
from starchaos.comments.models import Comment
from starchaos import db
from flask_login import current_user, login_required

comments = Blueprint('comments', __name__)


@comments.route("/comment/<int:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user != current_user:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted!', 'success')
    return redirect(request.referrer)
