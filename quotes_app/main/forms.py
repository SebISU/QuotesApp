from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class SearchForm(FlaskForm):
    content = StringField('Search')
    submit = SubmitField('Go')
