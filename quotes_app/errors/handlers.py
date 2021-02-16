from flask import Blueprint, render_template
from quotes_app.main.forms import SearchForm


errors = Blueprint('errors', __name__)


@errors.app_errorhandler(400)
def error_400(error):
    schform = SearchForm()
    if schform.schsubmit.data and schform.validate_on_submit():
        if schform.query.data != '':
            return redirect(url_for('main.home', sch=schform.query.data))
        else:
            return redirect(url_for('errors.error_400'))
    return render_template('errors/400.html', schform=schform), 400

@errors.app_errorhandler(403)
def error_403(error):
    schform = SearchForm()
    if schform.schsubmit.data and schform.validate_on_submit():
        if schform.query.data != '':
            return redirect(url_for('main.home', sch=schform.query.data))
        else:
            return redirect(url_for('errors.error_403'))
    return render_template('errors/403.html', schform=schform), 403

@errors.app_errorhandler(404)
def error_404(error):
    schform = SearchForm()
    if schform.schsubmit.data and schform.validate_on_submit():
        if schform.query.data != '':
            return redirect(url_for('main.home', sch=schform.query.data))
        else:
            return redirect(url_for('errors.error_404'))
    return render_template('errors/404.html', schform=schform), 404

@errors.app_errorhandler(405)
def error_405(error):
    schform = SearchForm()
    if schform.schsubmit.data and schform.validate_on_submit():
        if schform.query.data != '':
            return redirect(url_for('main.home', sch=schform.query.data))
        else:
            return redirect(url_for('errors.error_405'))
    return render_template('errors/404.html', schform=schform), 405

@errors.app_errorhandler(500)
def error_500(error):
    schform = SearchForm()
    if schform.schsubmit.data and schform.validate_on_submit():
        if schform.query.data != '':
            return redirect(url_for('main.home', sch=schform.query.data))
        else:
            return redirect(url_for('errors.error_500'))
    return render_template('errors/404.html', schform=schform), 500
