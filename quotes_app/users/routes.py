# db.engine.table_names() to list all table names in db.
# MoreInfoUser.__table__.create(db.session.bind) to add the MoreInfoUser table
# to the existing db.

from flask import (Blueprint, render_template, redirect, flash, request, url_for,
                    Markup)
from flask_login import login_user, logout_user, current_user, login_required
from quotes_app import db, bcrypt
from quotes_app.models import User, Post, Like, Comment, MoreInfoUser
from quotes_app.users.forms import (RegistrationForm, LoginForm, ResetRequestForm,
                                ResetPasswordForm, UpdateProfileForm)
from quotes_app.users.utils import (send_reset_token, get_best_posts_user,
                                get_recent_stars_user, get_posts_num_plc,
                                save_picture, remove_picture)
from quotes_app.main.utils import prepare_posts_display, update_like_table
from datetime import datetime as dt


users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    user1 = User.query.filter_by(username='qwer').first()
    user2 = User.query.filter_by(username='wert').first()
    user3 = User.query.filter_by(username='erty').first()
    user4 = User.query.filter_by(username='rtyu').first()
    user5 = User.query.filter_by(username='tyui').first()
    user6 = User.query.filter_by(username='yuio').first()
    user7 = User.query.filter_by(username='uiop').first()
    user8 = User.query.filter_by(username='asdf').first()
    user9 = User.query.filter_by(username='sdfg').first()
    user10 = User.query.filter_by(username='dfgh').first()
    post1 = Post(author='unknown', content='If you think nobody cares about you, try missing a couple of payments', posted_by=user1)
    post2 = Post(author='anonymous', content='The difference between stupidity and genius is that genius has its limits', posted_by=user2)
    post3 = Post(author='unknown', content='You can always tell when a man is well informed. His views are pretty much like your own', posted_by=user3)
    post4 = Post(author='anonymous', content='Here is something to think about: How come you never see a headline like Psychic Wins Lottery', posted_by=user4)
    post5 = Post(author='unknown', content='A lie gets halfway around the world before the truth has a chance to get its pants on', posted_by=user5)
    post6 = Post(author='anonymous', content='Never miss a good chance to shut up', posted_by=user6)
    post7 = Post(author='unknown', content='If you want your children to listen, try talking softly to someone else', posted_by=user7)
    post8 = Post(author='anonymous', content='A black cat crossing your path signifies that the animal is going somewhere', posted_by=user8)
    post9 = Post(author='unknown', content='If you think you are too small to make a difference, try sleeping with a mosquito', posted_by=user9)
    post10 = Post(author='anonymous', content='Education is what remains after one has forgotten what one has learned in school', posted_by=user10)
    db.session.add(post1)
    db.session.add(post2)
    db.session.add(post3)
    db.session.add(post4)
    db.session.add(post5)
    db.session.add(post6)
    db.session.add(post7)
    db.session.add(post8)
    db.session.add(post9)
    db.session.add(post10)
    db.session.commit()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
            password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # maybe somehow with just one .commit()?
        user = User.query.filter_by(username=form.username.data).first()
        about_user = MoreInfoUser(full_name=form.username.data, info_author=user)
        db.session.add(about_user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'info')
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
            flash('Login Unsuccessfull. Please check email or password', 'info')
    return render_template('login.html', title='Sign In', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# add a if not current_user.is_authenticated instead of login_required
# in every place where a flash message generated by login_required
# should be in the proper theme
@users.route("/user/<string:username>", methods=['GET', 'POST'])
@login_required
def user_profile(username):
    page = request.args.get('page', 1, type=int)
    post_id = request.args.get('star', type=int)
    user = User.query.filter_by(username=username).first_or_404()
    if post_id:
        update_like_table(current_user, post_id)
        return redirect(url_for('users.user_profile', username=username, page=page))
    about_user = MoreInfoUser.query.filter_by(info_author=user).first()
    posts, num_posts, num_likes, num_comments = get_posts_num_plc(user)
    posts = posts.paginate(page=page, per_page=5)
    posts_data = prepare_posts_display(posts, 8)
    best_posts = get_best_posts_user(user, 5)
    recent_stars = get_recent_stars_user(user, 5)
    background_image = url_for('static',
        filename='background_pics/' + about_user.background_pic)
    return render_template('user_profile.html', title=username, posts=posts,
        posts_data=posts_data, user=user, about_user=about_user,
        background_image=background_image, num_posts=num_posts,
        num_likes=num_likes, num_comments=num_comments, best_posts=best_posts,
        recent_stars=recent_stars)

@users.route("/user/<string:username>/update", methods=['GET', 'POST'])
@login_required
def update_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user != current_user:
        flash("You can't update this profile.", 'info')
        return redirect(url_for('main.home'))
    form = UpdateProfileForm()
    about_user = MoreInfoUser.query.filter_by(info_author=user).first()
    if form.validate_on_submit():
        # when error occurs during saving/removing pics, filenames in db records
        # can be wrong
        if form.profile_pic.data:
            profile_pic_file = save_picture(form.profile_pic.data, 1)
            remove_picture(current_user.image_file, 1)
            current_user.image_file = profile_pic_file
        if form.background_pic.data:
            background_pic_file = save_picture(form.background_pic.data, 2)
            remove_picture(about_user.background_pic, 2)
            about_user.background_pic = background_pic_file
        current_user.username = form.username.data
        current_user.email = form.email.data 
        about_user.full_name = form.full_name.data
        about_user.city = form.city.data
        about = form.about.data.strip(' \n  ,')
        about_user.about = Markup(about.replace('\n', '<br>')) # to make sure that won't be any malicious code in db
        about_user.last_update = dt.utcnow()
        db.session.commit()
        flash('Your account has been updated!', 'info')
        return redirect(url_for('users.user_profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.full_name.data = about_user.full_name
        form.city.data = about_user.city
        form.about.data = about_user.about.replace('<br>', '\n')
    _, num_posts, num_likes, num_comments = get_posts_num_plc(user)
    background_image = url_for('static',
        filename='background_pics/' + about_user.background_pic)
    return render_template('update_profile.html', user=user, title='Update Profile',
        about_user=about_user, background_image=background_image, form=form,
        num_posts=num_posts, num_likes=num_likes, num_comments=num_comments)

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_token(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password Reqeust', form=form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token!', 'info')
        redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
