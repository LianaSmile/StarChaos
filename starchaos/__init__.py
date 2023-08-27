from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from starchaos.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from starchaos.users.routes import users
    from starchaos.posts.routes import posts
    from starchaos.comments.routes import comments
    from starchaos.likes.routes import likes
    from starchaos.main.routes import main
    from starchaos.errors.hadlers import errors

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(comments)
    app.register_blueprint(likes)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
