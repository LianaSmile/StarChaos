from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from starchaos import bcrypt
from starchaos.users.models import User


class RegistrationForm(FlaskForm):
    full_name = StringField('Your Full Name', validators=[DataRequired(), Length(min=2, max=40)],
                            render_kw={"placeholder": "John Doe"})
    email = StringField('Email address', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "john@example.com"})
    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={"placeholder": "Enter your password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"placeholder": "Confirm your password"})
    submit = SubmitField('Sign Up')

    def validate_full_name(self, full_name):
        user = User.query.filter_by(full_name=full_name.data).first()
        if user:
            raise ValidationError('That full name is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "Enter your email"})
    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={"placeholder": "Enter your password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class UpdateAccountForm(FlaskForm):
    full_name = StringField('Your Full Name', validators=[DataRequired(), Length(min=2, max=40)],
                            render_kw={"placeholder": "John Doe"})
    email = StringField('Email address', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "john@example.com"})
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    bg_picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_full_name(self, full_name):
        if full_name.data != current_user.full_name:
            user = User.query.filter_by(full_name=full_name.data).first()
            if user:
                raise ValidationError('That full name is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class RequestResetForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "john@example.com"})
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no such email address registered. Register first!')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={"placeholder": "Enter your password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"placeholder": "Confirm your password"})
    submit = SubmitField('Reset Password')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()],
                                     render_kw={"placeholder": "Enter your current password"})
    new_password = PasswordField('New Password', validators=[DataRequired()],
                                 render_kw={"placeholder": "Enter a new password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')],
                                     render_kw={"placeholder": "Confirm the new password"})
    submit = SubmitField('Change Password')

    def validate_current_password(self, field):
        if not bcrypt.check_password_hash(current_user.password, field.data):
            raise ValidationError('The current password is not correct.')
