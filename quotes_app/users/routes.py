from flask import Blueprint, render_template, redirect, flash, request, url_for
from flask_login import login_user, logout_user, current_user, login_required
from quotes_app import db, bcrypt
from quotes_app.models import User, Post, Like, Comment
from quotes_app.users.forms import (RegistrationForm, LoginForm, ResetRequestForm,
                                ResetPasswordForm)
from quotes_app.users.utils import send_reset_token
from datetime import datetime as dt


users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
            password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Sign Up', form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessfull. Please check email or password', 'quotes')
    return render_template('login.html', title='Sign In', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# check how finding recent stars works
@users.route("/user/<string:username>")
@login_required
def user_profile(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(posted_by=user)\
        .order_by(Post.date_posted.desc())
    num_posts = posts.all()
    num_posts = len(num_posts)
    num_likes = len(Like.query.filter_by(like_author=user).all())
    num_comments = len(Comment.query.filter_by(comment_author=user).all())
    posts = posts.paginate(page=page, per_page=5)
    posts_data = []
    for post in posts.items:
        post_info = []
        likes = Like.query.filter_by(like_post=post).limit(8).all()
        for like in likes:
            post_data.append(User.query.get(like.user_id))
        post_info.append(post)
        posts_data.append(post_info)
    return render_template('user_profile.html', title=username, posts=posts, user=user,
        num_posts=num_posts, num_likes=num_likes, num_comments=num_comments)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_token(user)
        flash('An email has been sent with instructions to reset your password.', 'quotes')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password Reqeust', form=form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token!', 'quotes')
        redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'quotes')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
