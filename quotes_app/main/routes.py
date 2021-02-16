from flask import render_template, request, flash, Blueprint, redirect, url_for
from flask_login import current_user
from quotes_app.models import Post, Like
from quotes_app.main.utils import (prepare_posts_display, get_best_posts,
            get_trending, update_like_table, is_valid_page, prepare_posts,
            prepare_num_pages)
from quotes_app.main.forms import SearchForm
from quotes_app.config import PER_PAGE, BEST_TREND


main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
    schform = SearchForm()
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('srt', 'n', type=str)
    if schform.schsubmit.data and schform.validate_on_submit():
        if schform.query.data != '':
            return redirect(url_for('main.home', sch=schform.query.data))
        else:
            return redirect(url_for('main.home', page=page, srt=sort))
    post_id = request.args.get('star', type=int)
    search = request.args.get('sch', type=str)
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
    num_pages = prepare_num_pages(posts, page, PER_PAGE)
    posts_data = prepare_posts_display(posts[(page-1)*PER_PAGE:page*PER_PAGE], 10)
    best_posts = get_best_posts(BEST_TREND)
    trend_posts = get_trending(BEST_TREND)
    if search:
        schform.query.data = search
    return render_template('main/home.html', posts_data=posts_data, num_pages=num_pages, 
        schform=schform, best_posts=best_posts, trend_posts=trend_posts, page=page,
        search=search, sort=sort)


@main.route("/about", methods=['GET', 'POST'])
def about():
    schform = SearchForm()
    if schform.schsubmit.data and schform.validate_on_submit():
        if schform.query.data != '':
            return redirect(url_for('main.home', sch=schform.query.data))
        else:
            return redirect(url_for('main.about'))
    return render_template('main/about.html', schform=schform)


@main.route("/terms", methods=['GET', 'POST'])
def terms():
    schform = SearchForm()
    if schform.schsubmit.data and schform.validate_on_submit():
        if schform.query.data != '':
            return redirect(url_for('main.home', sch=schform.query.data))
        else:
            return redirect(url_for('main.terms'))
    return render_template('main/terms.html', schform=schform)
