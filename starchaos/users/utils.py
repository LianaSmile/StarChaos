import secrets
import os
from random import sample

from PIL import Image
from flask import url_for, current_app
from starchaos import mail, db
from flask_mail import Message

from starchaos.users.models import User


def get_random_users_not_friends(user, num_users=10):
    friends_ids = [friend.id for friend in user.friends]
    users_not_friends_ids = db.session.query(User.id).filter(~User.id.in_(friends_ids)).filter(
        User.id != user.id)
    total_users_not_friends = users_not_friends_ids.count()
    num_users = min(num_users, total_users_not_friends)
    random_user_ids = sample([id for (id,) in users_not_friends_ids.all()], num_users)
    random_users = User.query.filter(User.id.in_(random_user_ids)).all()
    return random_users


def save_image(form_picture, size, folder_name):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, f'static/images/{folder_name}', picture_fn)

    output_size = size
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn


def send_reset_email(user):
    text = '''To reset your password, visit the following link:
    {}

    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='kalpakchyanliana@gmail.com',
                  recipients=[user.email])
    url = url_for('users.reset_token', token=token, _external=True)
    msg.body = text.format(url)
    mail.send(msg)
