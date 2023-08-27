from flask import render_template, request, Blueprint
from starchaos.posts.models import Post
from flask_login import login_required

main = Blueprint('main', __name__)


@main.route("/", methods=['POST', 'GET'])
@main.route("/index", methods=['POST', 'GET'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('index.html', posts=posts)
