from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from starchaos.config import Config
from flask_socketio import SocketIO
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
socketio = SocketIO()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

mail = Mail()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app, db)

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
