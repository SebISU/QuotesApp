from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
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

