from utils.forms import SearchForm
from flask import Blueprint,render_template,current_app as app

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET', 'POST'])
def search():
    Quotes = []
    form = SearchForm()
    if form.validate_on_submit():
        author = form.author.data
        Quotes = [quote for quote in app.Quotes if quote['author'] == author]
        return render_template('search.html', form=form, Quotes=Quotes)
    return render_template('search.html', form=form, Quotes=Quotes)