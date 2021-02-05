from flask import render_template, request, Blueprint
from flask_login import current_user
from quotes_app.models import Post, Like
from quotes_app.main.utils import prepare_posts_display, get_best_posts, update_like_table


main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
    # add a get_best_posts feature
    post_id = request.args.get('star', type=int)
    if post_id and current_user.is_authenticated:
        update_like_table(current_user, post_id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    posts_data = prepare_posts_display(posts)
    return render_template('home.html', posts=posts, posts_data=posts_data)


@main.route("/about")
def about():

    return render_template('about.html')


@main.route("/terms")
def terms():

    return render_template('terms.html')
