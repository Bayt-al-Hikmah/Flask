from utils.forms import ShareForm
from flask import Blueprint,redirect,url_for,render_template,current_app as app

share_bp = Blueprint('share', __name__)

@share_bp.route('/share', methods=['GET', 'POST'])
def share():
    form = ShareForm()
    if form.validate_on_submit():
        author = form.author.data
        quote = form.quote.data
        app.config['Quotes'].append({"quote": quote, "author": author})
        return redirect(url_for('main.index'))
    return render_template('share.html', form=form)
