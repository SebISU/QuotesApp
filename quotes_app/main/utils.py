from datetime import timedelta, datetime as dt
from quotes_app import db
from sqlalchemy import func
from flask import abort
from flask_login import current_user
from quotes_app.models import User, Like, Post


def prepare_posts_display(posts, size):
    '''Converts posts to list of lists containing
    [user(for image) x n, post, isStarred(true/false)] records
    size = how many users to display images to take
    '''
    posts_data = []
    for post in posts:
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


def prepare_posts(search, sort):
    # n -> new, t -> top, tr -> trending
    if sort not in ['n', 't', 'tr']:
        abort(400)
    if search:
        posts = Post.query.filter(Post.content.like("%{}%".format(search)))
    else:
        posts = Post.query
    if sort == 'n':
        posts = posts.order_by(Post.date_posted.desc()).all()
    elif sort == 't':
        sub_query = Like.query.with_entities(Like.post_id,
            func.count(Like.user_id).label('sum_likes')).group_by(Like.post_id).subquery()
        posts = posts.with_entities(Post).join(sub_query,Post.id==sub_query.c.post_id,
            isouter=True).order_by(sub_query.c.sum_likes.desc(),
            Post.date_posted.desc()).all()
    else:
        time_window = dt.utcnow() - timedelta(days=7)
        sub_query = Like.query.filter(Like.date_like >= time_window)\
            .with_entities(Like.post_id, func.count(Like.user_id).label('sum_likes'))\
            .group_by(Like.post_id).subquery()
        sub_query2 = Like.query.with_entities(Like.post_id,
            func.count(Like.user_id).label('sum_likes2')).group_by(Like.post_id).subquery()
        posts = posts.with_entities(Post)\
            .join(sub_query, Post.id==sub_query.c.post_id, isouter=True)\
            .join(sub_query2, Post.id==sub_query2.c.post_id, isouter=True)\
            .order_by(sub_query.c.sum_likes.desc(), sub_query2.c.sum_likes2.desc(),
            Post.date_posted.desc()).all()
    return posts

def prepare_num_pages(posts, page, per_page):
    if not is_valid_page(posts, page, per_page):
        abort(400)
    len_posts = len(posts)
    max_page = len_posts//per_page if len_posts % per_page == 0 else len_posts//per_page + 1
    if max_page == 0:
        return []
    num_pages = [page]
    if page - 1 > 0:
        num_pages.insert(0, page - 1)
    if page - 2 > 0:
        num_pages.insert(0, page - 2)
    if page - 3 > 0:
        if page - 4 > 0:
            num_pages.insert(0, None)
            num_pages.insert(0, 1)
        else:
            num_pages.insert(0, 1)
    if page + 1 <= max_page:
        num_pages.append(page + 1)
    if page + 2 <= max_page:
        num_pages.append(page + 2)
    if page + 3 <= max_page:
        if page + 4 <= max_page:
            num_pages.append(None)
            num_pages.append(max_page)
        else:
            num_pages.append(max_page)
    return num_pages

def is_valid_page(posts, page, per_page):
    len_posts = len(posts)
    print(len(posts))
    if page <= 0 or per_page <= 0 or (len_posts == 0 and page != 1):
        return False
    if len_posts % per_page == 0:
        if len_posts // per_page < page and len_posts > 0:
            return False
    else:
        if len_posts // per_page + 1 < page:
            return False
    return True

# by stars. If not enough,the newest posts without stars are added
def get_best_posts(size):
    sub_query = Like.query.with_entities(Like.post_id,
        func.count(Like.user_id).label('sum_likes')).group_by(Like.post_id).subquery()
    posts = Post.query.with_entities(Post).join(sub_query,
        Post.id==sub_query.c.post_id,isouter=True).order_by(sub_query.c.sum_likes.desc(),
        Post.date_posted.desc()).limit(size).all()
    return posts


# by stars  (last 7 days). By all stars if not enough adages
def get_trending(size):
    time_window = dt.utcnow() - timedelta(days=7)
    sub_query = Like.query.filter(Like.date_like >= time_window)\
        .with_entities(Like.post_id, func.count(Like.user_id).label('sum_likes'))\
        .group_by(Like.post_id).subquery()
    sub_query2 = Like.query.with_entities(Like.post_id,
        func.count(Like.user_id).label('sum_likes2')).group_by(Like.post_id).subquery()
    posts = Post.query.with_entities(Post)\
        .join(sub_query, Post.id==sub_query.c.post_id, isouter=True)\
        .join(sub_query2, Post.id==sub_query2.c.post_id, isouter=True)\
        .order_by(sub_query.c.sum_likes.desc(), sub_query2.c.sum_likes2.desc(),
        Post.date_posted.desc()).limit(size).all()
    return posts

def update_like_table(user, post_id):
    like = Like.query.filter_by(like_author=user, post_id=post_id).first()
    if like:
        db.session.delete(like)
    else:
        like = Like(like_author=user, post_id=post_id)
        db.session.add(like)
    db.session.commit()
