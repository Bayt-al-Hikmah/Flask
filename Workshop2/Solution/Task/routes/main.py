from flask import Blueprint, render_template,current_app as app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    Quotes = app.Quotes
    return render_template('index.html', Quotes=Quotes)
