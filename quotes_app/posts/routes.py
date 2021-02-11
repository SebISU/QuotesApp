from flask import (Blueprint, render_template, redirect, flash, request, url_for,
                    Markup)
from flask_login import login_user, logout_user, current_user, login_required
from quotes_app import db
from quotes_app.models import User, Post, Like, Comment, LikeComment
from quotes_app.posts.forms import PostForm, CommentForm
from quotes_app.posts.utils import (prepare_post_display, prepare_comments_display,
                                    update_like_comment_table)
from quotes_app.main.utils import update_like_table
from datetime import datetime as dt

posts = Blueprint('posts', __name__)

@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(author=form.author.data, content=form.content.data, posted_by=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been added!', 'quotes')
        return redirect(url_for('main.home'))
    return render_template('add_post.html', title='Add Post', form=form)

@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=Markup(form.content.data.replace('\n', '<br>')),
            comment_author=current_user, comment_post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added.', 'quotes')
        # here must be redirect. If not you will render a template with the filled form, even submitted.
        # what is more, browser keeps state of the last request so if you refresh you will submit this form again
        return redirect(url_for('posts.post', post_id=post.id))
    page = request.args.get('page', 1, type=int)
    comment_id = request.args.get('starc', type=int)
    post_id = request.args.get('starp', type=int)
    if post_id:
        update_like_table(current_user, post_id)
    if comment_id:
        update_like_comment_table(current_user, comment_id)
    comments = Comment.query.filter_by(comment_post=post).order_by(Comment.date_comment.desc())\
        .paginate(page=page, per_page=10)
    post_data = prepare_post_display(post, 8)
    comments_data = prepare_comments_display(comments, 8)
    return render_template('post.html', title='Adage Page', post_data=post_data, form=form,
        comments=comments, comments_data=comments_data)
