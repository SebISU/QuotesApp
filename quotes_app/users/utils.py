from flask import url_for
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


# by stars. If not enough,the oldest posts without stars are added
def get_best_posts_user(user, size):
    posts = Like.query.with_entities(Like.post_id, func.count(Like.user_id))\
        .group_by(Like.post_id).order_by(func.count(Like.user_id).desc()).all()
    prep_posts = []
    for item in posts:
        post = Post.query.get(item[0])
        if post.posted_by == user:
            prep_posts.append(post)
        if len(prep_posts) == size:
            return prep_posts
    prep_posts = prep_posts + Post.query.filter(Post.user_id == user.id, Post.id.\
            notin_([item.id for item in prep_posts])).order_by(Post.date_posted).\
            limit(size-len(prep_posts)).all()
    return prep_posts


def get_recent_stars_user(user, size):
    likes = Like.query.filter_by(like_author=user).order_by(Like.date_like.desc()).limit(size).all()
    posts = []
    for like in likes:
        posts.append(Post.query.get(like.post_id))
    return posts


def get_posts_num_plc(user):
    posts = Post.query.filter_by(posted_by=user)\
    .order_by(Post.date_posted.desc())
    num_posts = posts.all()
    num_posts = len(num_posts)
    num_likes = len(Like.query.filter_by(like_author=user).all())
    num_comments = len(Comment.query.filter_by(comment_author=user).all())
    return posts, num_posts, num_likes, num_comments
