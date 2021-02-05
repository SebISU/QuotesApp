from quotes_app import db
from sqlalchemy import func
from flask_login import current_user
from quotes_app.models import User, Like



def prepare_posts_display(posts):
    '''Converts posts to list of lists containing
    [user(for image) x n, post, isStarred(true/false)] records
    '''
    posts_data = []
    for post in posts.items:
        post_info = []
        likes = Like.query.filter_by(like_post=post).limit(8).all()
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


# do it later. First you have to add posts and give likes to check
# if not enough likes take by comments later by date
def get_best_posts(size):
    # to get count & group_by
    # add order_by to queries to get the values with the best rate
    posts = Like.query.with_entities(Like.like_post, func.count(Like.like_post))\
        .group_by(Like.like_post).limit(size).all()
    # if len(posts) < size:
    return posts


def update_like_table(user, post_id):
    like = Like.query.filter_by(like_author=user, post_id=post_id).first()
    if like:
        db.session.delete(like)
    else:
        like = Like(like_author=user, post_id=post_id)
        db.session.add(like)
    db.session.commit()
