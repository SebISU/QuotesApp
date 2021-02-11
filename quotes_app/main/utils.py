from datetime import timedelta, datetime as dt
from quotes_app import db
from sqlalchemy import func
from flask_login import current_user
from quotes_app.models import User, Like, Post


def prepare_posts_display(posts, size):
    '''Converts posts to list of lists containing
    [user(for image) x n, post, isStarred(true/false)] records
    size = how many users to display images to take
    '''

    posts_data = []
    for post in posts.items:
        post_info = []
        likes = Like.query.filter_by(like_post=post).limit(size).all()
        for like in likes:
            post_info.append(User.query.get(like.user_id))
        post_info.append(post)
        starred = None
        if current_user.is_authenticated:
            starred = Like.query.filter_by(like_post=post, like_author=current_user).first()
        if starred:
            post_info.append(True)
        else:
            post_info.append(False)
        posts_data.append(post_info)
    return posts_data

# by stars. If not enough,the oldest posts without stars are added
def get_best_posts(size):
    posts = Like.query.with_entities(Like.post_id, func.count(Like.user_id))\
        .group_by(Like.post_id).order_by(func.count(Like.user_id).desc()).limit(size).all()
    prep_posts = []
    for item in posts:
        post = Post.query.get(item[0])
        prep_posts.append(post)
    if len(prep_posts) < size:
        prep_posts = prep_posts + Post.query.filter(Post.id.\
            notin_([item.id for item in prep_posts])).order_by(Post.date_posted).\
            limit(size-len(prep_posts)).all()
    return prep_posts

# by stars  (last 7 days). If not enough, adages without stars posted in the last 7 days are added
def get_trending(size):
    time_window = dt.utcnow() - timedelta(days=7)
    posts = Like.query.filter(Like.date_like >= time_window).with_entities(Like.post_id,
        func.count(Like.user_id)).group_by(Like.post_id).order_by(func.count(Like.user_id)\
        .desc()).limit(size).all()
    prep_posts = []
    for item in posts:
        post = Post.query.get(item[0])
        prep_posts.append(post)
    if len(prep_posts) < size:
        prep_posts = prep_posts + Post.query.filter(Post.date_posted >= time_window,
            Post.id.notin_([item.id for item in prep_posts])).order_by(Post.date_posted).\
            limit(size-len(prep_posts)).all()
    return prep_posts


def update_like_table(user, post_id):
    like = Like.query.filter_by(like_author=user, post_id=post_id).first()
    if like:
        db.session.delete(like)
    else:
        like = Like(like_author=user, post_id=post_id)
        db.session.add(like)
    db.session.commit()
