from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from quotes_app.models import User


class PostForm(FlaskForm):
    author = StringField('Author', validators=[DataRequired(), Length(min=1, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
