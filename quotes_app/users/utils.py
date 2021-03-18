import os
import secrets
from PIL import Image
from flask import url_for, current_app
from sqlalchemy import func
from quotes_app import mail
from flask_mail import Message
from quotes_app.models import Like, Post, Comment


def send_reset_token(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
    sender='noreply@sagesay.com', recipients=[user.email])
    msg.body = f'''To reset your password visit the following link:
{url_for('users.reset_password', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


# by stars. If not enough,the newest posts without stars are added
def get_best_posts_user(user, size):

    sub_query = Like.query.with_entities(Like.post_id,
        func.count(Like.user_id).label('sum_likes')).group_by(Like.post_id).subquery()
    posts = Post.query.filter_by(posted_by=user).with_entities(Post)\
        .join(sub_query, Post.id==sub_query.c.post_id, isouter=True)\
        .order_by(sub_query.c.sum_likes.desc(), Post.date_posted.desc()).limit(size).all()
    return posts


def get_recent_stars_user(user, size):
    sub_query = Like.query.filter_by(like_author=user)\
        .order_by(Like.date_like.desc()).limit(size).subquery()
    posts = Post.query.with_entities(Post).join(sub_query, Post.id==sub_query.c.post_id).all()
    return posts


def get_posts_num_plc(user):
    posts = Post.query.filter_by(posted_by=user)\
    .order_by(Post.date_posted.desc())
    num_posts = posts.all()
    num_posts = len(num_posts)
    num_likes = len(Like.query.filter_by(like_author=user).all())
    num_comments = len(Comment.query.filter_by(comment_author=user).all())
    return posts, num_posts, num_likes, num_comments


# mode 1 means profile picture, mode 2 means background
def save_picture(picture, mode):
    # can not be sure that all photos will have exclusive names.
    # Simple user_id could be better.
    # If not, token based on the username (all names are exclusive)
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    picture_fn = random_hex + f_ext

    if mode == 1:
        picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
        output_size = (256, 256)
        i = Image.open(picture)
        i.thumbnail(output_size)
        i.save(picture_path)
    elif mode == 2:
        picture_path = os.path.join(current_app.root_path, 'static/background_pics', picture_fn)
        output_size = (1352, 800)
        i = Image.open(picture)
        i.thumbnail(output_size)
        i.save(picture_path)
    else:
        return None
    return picture_fn


def remove_picture(picture, mode):
    if mode == 1 and picture != 'default.jpg':
        picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture)
        os.remove(picture_path)
    elif mode == 2 and picture != 'profile_bg.jpg':
        picture_path = os.path.join(current_app.root_path, 'static/background_pics', picture)
        os.remove(picture_path)
    else:
        return False
    return True
