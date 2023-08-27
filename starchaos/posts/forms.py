from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    content = TextAreaField('', validators=[DataRequired()],
                            render_kw={"placeholder": "Write something here..."})
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')
