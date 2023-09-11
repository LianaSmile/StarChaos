from flask import render_template, request, Blueprint, redirect, url_for
from starchaos.posts.models import Post
from flask_login import login_required, current_user
from starchaos import db

main = Blueprint('main', __name__)


@main.route("/", methods=['POST', 'GET'])
@main.route("/index", methods=['POST', 'GET'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('index.html', posts=posts)


@main.route('/theme/<string:_theme>')
@login_required
def theme(_theme):
    if _theme == 'light':
        current_user.theme = _theme
        db.session.commit()
    if _theme == 'dark':
        current_user.theme = _theme
        db.session.commit()
    return redirect(request.referrer)
