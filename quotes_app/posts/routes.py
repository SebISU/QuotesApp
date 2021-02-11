from flask import (Blueprint, render_template, redirect, flash, request, url_for,
                    Markup)
from flask_login import login_user, logout_user, current_user, login_required
from quotes_app import db
from quotes_app.models import User, Post, Like, Comment, LikeComment
from quotes_app.posts.forms import PostForm, CommentForm
from quotes_app.posts.utils import (prepare_post_display, prepare_comments_display,
                                    update_like_comment_table, get_best_comments_post,
                                    get_stats_post)
from quotes_app.main.utils import update_like_table
from datetime import datetime as dt

posts = Blueprint('posts', __name__)

@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        content = form.content.data.strip(' \n  ,')
        post = Post(author=form.author.data,
            content=Markup(content.replace('\n', '<br>')), posted_by=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been added!', 'info')
        return redirect(url_for('main.home'))
    return render_template('add_post.html', title='Add Post', form=form)

@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        content = form.content.data.strip(' \n  ,')
        comment = Comment(content=Markup(content.replace('\n', '<br>')),
            comment_author=current_user, comment_post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added.', 'info')
        # here must be redirect. If not you will render a template with the filled form,
        # even submitted. What is more, browser keeps state of the last request,
        # so if you refresh you will submit this form again.
        return redirect(url_for('posts.post', post_id=post.id))
    page = request.args.get('page', 1, type=int)
    comment_id = request.args.get('starc', type=int)
    post_id = request.args.get('starp', type=int)
    if post_id or comment_id:
        if post_id:
            update_like_table(current_user, post_id)
        elif comment_id:
            update_like_comment_table(current_user, comment_id)
        return redirect(url_for('posts.post', post_id=post.id, page=page))
    comments = Comment.query.filter_by(comment_post=post).order_by(Comment.date_comment.desc())\
        .paginate(page=page, per_page=10)
    post_data = prepare_post_display(post, 8)
    comments_data = prepare_comments_display(comments, 8)
    best_comments = get_best_comments_post(post, 5)
    stats = get_stats_post(post)
    return render_template('post.html', title='Adage Page', post_data=post_data, form=form,
        comments=comments, comments_data=comments_data, stats=stats,
        best_comments=best_comments)

@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.posted_by != current_user:
        flash('Only author can update a post.', 'info')
        return redirect(url_for('posts.post', post_id=post_id))
    form = PostForm()
    if form.validate_on_submit():
        content = form.content.data.strip(' \n  ,')
        post.content = Markup(content.replace('\n', '<br>'))
        post.author = form.author.data
        db.session.commit()
        flash('Your post has been updated.', 'info')
        return redirect(url_for('posts.post', post_id=post_id))
    elif request.method == 'GET':
        form.content.data = post.content.replace('<br>', '\n')
        form.author.data = post.author
    return render_template('update_post.html', title='Update Adage', form=form)

@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.posted_by != current_user:
        flash('Only author can delete a post.', 'info')
        return redirect(url_for('posts.post', post_id=post_id))
    comments = Comment.query.filter_by(comment_post=post)
    for comment in comments.all():
        LikeComment.query.filter_by(comment=comment).delete()
    comments.delete()
    Like.query.filter_by(like_post=post).delete()
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'info')
    return redirect(url_for('main.home'))

@posts.route("/comment/<int:comment_id>/update", methods=['GET','POST'])
@login_required
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = request.args.get('post_id', type=int)
    page = request.args.get('page', 1, type=int)
    if not post_id or not page:
        abort(400)
    if comment.comment_author != current_user:
        flash('Only author can update a comment.', 'info')
        return redirect(url_for('posts.post', post_id=post_id, page=page))
    form = CommentForm()
    if form.validate_on_submit():
        content = form.content.data.strip(' \n  ,')
        comment.content = Markup(content.replace('\n', '<br>'))
        db.session.commit()
        flash('Your comment has been updated.', 'info')
        return redirect(url_for('posts.post', post_id=post_id, page=page))
    elif request.method == 'GET':
        form.content.data = comment.content.replace('<br>', '\n')
    return render_template('update_comment.html', title='Update Comment', form=form)

@posts.route("/comment/<int:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.comment_author != current_user \
    and comment.comment_post.posted_by != current_user:
        flash('You can not delete this comment.', 'info')
        return redirect(url_for('posts.post', post_id=comment.post_id))
    post_id = comment.post_id
    LikeComment.query.filter_by(comment=comment).delete()
    db.session.delete(comment)
    db.session.commit()
    if comment.comment_author == current_user:
        flash('Your comment has been deleted!', 'info')
    else:
        flash('Comment has been deleted!', 'info')
    return redirect(url_for('posts.post', post_id=post_id))
