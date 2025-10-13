from flask import Blueprint, render_template

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@profile_bp.route('/profile/<username>')
def profile(username="World"):
    return render_template('profile.html', username=username)