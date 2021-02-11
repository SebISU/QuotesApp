from quotes_app import db
from flask_login import current_user
from sqlalchemy import func
from quotes_app.models import User, Post, Like, Comment, LikeComment


def prepare_post_display(post, size):
    '''Converts posts to list of lists containing
    [user(for image) x n, post, isStarred(true/false)] records
    size = how many users to display images to take
    '''
    post_info = []
    likes = Like.query.filter_by(like_post=post).limit(size).all()
    for like in likes:
        post_info.append(User.query.get(like.user_id))
    post_info.append(post)
    starred = None
    starred = Like.query.filter_by(like_post=post, like_author=current_user).first()
    if starred:
        post_info.append(True)
    else:
        post_info.append(False)
    return post_info

def prepare_comments_display(comments, size):
    '''Converts comments to list of lists containing
    [user(for image) x n, comment, isStarred(true/false)] records
    size = how many users to display images to take
    '''
    comments_data = []
    for comment in comments.items:
        comment_info = []
        likes = LikeComment.query.filter_by(comment=comment).limit(size).all()
        for like in likes:
            comment_info.append(User.query.get(like.user_id))
        comment_info.append(comment)
        starred = None
        starred = LikeComment.query.filter_by(comment=comment, like_comment_author=current_user).first()
        if starred:
            comment_info.append(True)
        else:
            comment_info.append(False)
        comments_data.append(comment_info)
    return comments_data

def update_like_comment_table(user, comment_id):
    like = LikeComment.query.filter_by(like_comment_author=user, comment_id=comment_id).first()
    if like:
        db.session.delete(like)
    else:
        like = LikeComment(like_comment_author=user, comment_id=comment_id)
        db.session.add(like)
    db.session.commit()

def get_best_comments_post(post, size):
    comments  = Comment.query.filter_by(comment_post=post).all()
    num_likes_list = []
    for comment in comments:
        num_likes = len(LikeComment.query.filter_by(comment=comment).all())
        num_likes_list.append([comment, num_likes])
    num_likes_list.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in num_likes_list[:size]]

def get_stats_post(post):
    """Returns a list of post stats
    return format ->  global rank, num_of_likes, num_of_comments
    """
    posts = Like.query.with_entities(Like.post_id, func.count(Like.user_id))\
        .group_by(Like.post_id).order_by(func.count(Like.user_id).desc()).all()
    glob_rank = len(posts) + 1
    num_likes = 0
    for x in range(len(posts)):
        if posts[x][0] == post.id:
            glob_rank = x + 1
            num_likes = posts[x][1]
            break
    num_comments = len(Comment.query.filter_by(comment_post=post).all())
    return glob_rank, num_likes, num_comments
