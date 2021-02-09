from imghdr import what
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField,
                    BooleanField, TextAreaField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from quotes_app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
        validators=[DataRequired(), Length(min=4, max=30)])
    confirm_password = PasswordField('Confirm Password',
        validators=[DataRequired(), Length(min=4, max=30),
        EqualTo('password', 'Passwords must match!')])
    accept_terms = BooleanField('I agree to')
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Choose a different one!')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Choose a different one!')

    def validate_accept_terms(self, accept_terms):
        if accept_terms.data is False:
            raise ValidationError('Accept terms of service.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
        validators=[DataRequired(), Length(min=4, max=30)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Login')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first!')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
        validators=[DataRequired(), Length(min=4, max=30)])
    confirm_password = PasswordField('Confirm Password',
        validators=[DataRequired(), Length(min=4, max=30),
        EqualTo('password', 'Passwords must match!')])
    submit = SubmitField('Reset Password')


class UpdateProfileForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_pic = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    background_pic = FileField('Update Background Image', validators=[FileAllowed(['jpg', 'png'])])
    full_name = StringField('Full Name',
        validators=[DataRequired(), Length(min=1, max=120)])
    city = StringField('City',
        validators=[DataRequired(), Length(min=1, max=90)])
    about = TextAreaField('About', validators=[DataRequired()])
    submit = SubmitField('Update')

    # custom validators to check if user with such fields values can be created
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Choose a different one!')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Choose a different one!')

    def validate_profile_pic(self, profile_pic):
        if profile_pic.data:
            profile_stream = profile_pic.data.stream
            header = profile_stream.read(512)
            profile_stream.seek(0)
            format = what(None, header)
            if not format or format not in ['jpg', 'png', 'jpeg']:
                raise ValidationError('Uploaded profile picture is malformed or wrong file format!')

    def validate_background_pic(self, background_pic):
        if background_pic.data:
            background_stream = background_pic.data.stream
            header = background_stream.read(512)
            background_stream.seek(0)
            format = what(None, header)
            if not format or format not in ['jpg', 'png', 'jpeg']:
                raise ValidationError('Uploaded background image is malformed or wrong file format!')
