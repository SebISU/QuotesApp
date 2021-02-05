from flask import Blueprint, render_template, redirect, flash, request, url_for
from flask_login import login_user, logout_user, current_user, login_required
from quotes_app import db
from quotes_app.models import User, Post, Like, Comment
from quotes_app.posts.forms import PostForm
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

