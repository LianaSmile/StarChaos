from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import emit, join_room
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from starchaos import bcrypt, db, socketio
from starchaos.posts.models import Post
from starchaos.users.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    RequestResetForm,
    ResetPasswordForm,
    ChangePasswordForm
)
from starchaos.posts.forms import PostForm
from starchaos.users.models import User, Message
from starchaos.users.utils import save_image, send_reset_email, get_random_users_not_friends

users = Blueprint('users', __name__)


@users.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(full_name=form.full_name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'The account has been created! You can now log in!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/profile', defaults={'full_name': None}, methods=['POST', 'GET'])
@users.route('/profile/<string:full_name>', methods=['POST', 'GET'])
@login_required
def profile(full_name):
    if not full_name:
        full_name = current_user.full_name
    post_form = PostForm()
    if post_form.validate_on_submit():
        post = Post(content=post_form.content.data, author=current_user)
        if post_form.picture.data:
            post_image = save_image(post_form.picture.data, (1500, 1500), 'post_images')
            post.image = post_image
        db.session.add(post)
        db.session.commit()

        flash('Your post has been created!', 'success')
        return redirect(url_for('users.profile', _anchor='iq-top-navbar'))

    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(full_name=full_name).first_or_404()
    friends = user.friends.all()
    random_users = get_random_users_not_friends(user, num_users=10)
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=5)
    return render_template('profile.html', title='Profile', post_form=post_form, posts=posts, user=user,
                           friends=friends, random_users=random_users)


@users.route('/update', methods=['POST', 'GET'])
@login_required
def update():
    form = UpdateAccountForm()
    password_form = ChangePasswordForm()
    _pass = True
    if 'submit' in request.form and request.form['submit'] == 'Update':
        if form.validate_on_submit():
            if form.picture.data:
                profile_image = save_image(form.picture.data, (500, 500), 'profile_images')
                current_user.profile_image = profile_image
            if form.bg_picture.data:
                profile_bg_image = save_image(form.bg_picture.data, (1500, 1500), 'profile_images')
                current_user.bg_image = profile_bg_image
            current_user.full_name = form.full_name.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('users.profile'))
    if 'submit' in request.form and request.form['submit'] == 'Change Password':
        _pass = False
        if password_form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(password_form.new_password.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('users.profile'))

    if request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email

    return render_template('update.html', title='Update Profile', form=form, password_form=password_form, _pass=_pass)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        return render_template('mail_confirm.html', email=form.email.data)
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@users.route("/add_friend/<int:user_id>", methods=["POST"])
@login_required
def add_friend(user_id):
    user = User.query.get(user_id)
    if user:
        current_user.add_friend(user)
        flash(f"You are now friends with {user.full_name}!", "success")
    return redirect(request.referrer)


@users.route("/remove_friend/<int:user_id>", methods=["POST"])
@login_required
def remove_friend(user_id):
    user = User.query.get(user_id)
    if user:
        current_user.remove_friend(user)
        flash(f"You are no longer friends with {user.full_name}.", "info")
    return redirect(request.referrer)


@users.route("/chat/<int:receiver_id>")
@login_required
def chat(receiver_id):
    sender = current_user
    receiver = User.query.get(receiver_id)
    messages = Message.query.filter(
        ((Message.sender_id == sender.id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == sender.id))
    ).all()
    return render_template('chat.html', sender=sender, receiver=receiver, messages=messages)


@users.route("/delete_messages/<int:receiver_id>", methods=['POST'])
@login_required
def delete_messages(receiver_id):
    sender_id = current_user.id
    Message.query.filter(
        ((Message.sender_id == sender_id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == sender_id))
    ).delete()
    db.session.commit()
    return redirect(url_for('users.chats'))


@users.route("/chats")
@login_required
def chats():
    u = aliased(User)
    m = aliased(Message)

    subquery = (
        db.session.query(u.id.label('user_id'), func.max(m.date_posted).label('max_date'))
        .join(m, (u.id == m.sender_id) | (u.id == m.receiver_id))
        .filter((m.sender_id == current_user.id) | (m.receiver_id == current_user.id))
        .filter(u.id != current_user.id)
        .group_by(u.id)
        .distinct(u.id)
        .subquery()
    )

    users_with_messages = (
        db.session.query(u)
        .join(subquery, u.id == subquery.c.user_id)
        .order_by(subquery.c.max_date.desc())
        .all()
    )

    return render_template('chats.html', messaged_users=users_with_messages)


@socketio.on('private_message')
@login_required
def handle_private_message(data):
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    content = data['content']

    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.session.add(message)
    db.session.commit()

    emit('response', {'sender_id': sender_id, 'content': content,
                      'date': message.date_posted.strftime('%Y-%m-%d %H:%M')}, room=sender_id)
    emit('response', {'sender_id': sender_id, 'content': content,
                      'date': message.date_posted.strftime('%Y-%m-%d %H:%M')}, room=receiver_id)


@socketio.on('join')
@login_required
def handle_join(data):
    room = data['room']
    join_room(room)
