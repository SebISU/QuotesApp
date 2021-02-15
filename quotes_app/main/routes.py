from flask import render_template, request, flash, Blueprint, redirect, url_for
from flask_login import current_user
from quotes_app.models import Post, Like
from quotes_app.main.utils import (prepare_posts_display, get_best_posts,
            get_trending, update_like_table, is_valid_page, prepare_posts,
            prepare_num_pages)
from quotes_app.main.forms import SearchForm


main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
    schform = SearchForm()
    if schform.validate_on_submit():
        if schform.content.data != '':
            return redirect(url_for('main.home', sch=schform.content.data))
    post_id = request.args.get('star', type=int)
    page = request.args.get('page', 1, type=int)
    search = request.args.get('sch', type=str)
    sort = request.args.get('srt', 'n', type=str)
    if post_id:
        if current_user.is_authenticated:
            update_like_table(current_user, post_id)
        else:
            flash('Please log in to give a star.', 'info')
        if search:
            return redirect(url_for('main.home', page=page, sch=search, srt=sort))
        else:
            return redirect(url_for('main.home', page=page, srt=sort))
    posts = prepare_posts(search, sort)
    num_pages = prepare_num_pages(posts, page, 5)
    posts_data = prepare_posts_display(posts[(page-1)*5:page*5], 10)
    best_posts = get_best_posts(5)
    trend_posts = get_trending(5)
    if search:
        schform.content.data = search
    return render_template('home.html', posts_data=posts_data, num_pages=num_pages, 
        schform=schform, best_posts=best_posts, trend_posts=trend_posts, page=page,
        search=search, sort=sort)


@main.route("/about", methods=['GET', 'POST'])
def about():
    schform = SearchForm()
    if schform.validate_on_submit():
        if schform.content.data != '':
            return redirect(url_for('main.home', sch=schform.content.data))
    return render_template('about.html', schform=schform)


@main.route("/terms", methods=['GET', 'POST'])
def terms():
    schform = SearchForm()
    if schform.validate_on_submit():
        if schform.content.data != '':
            return redirect(url_for('main.home', sch=schform.content.data))
    return render_template('terms.html', schform=schform)
