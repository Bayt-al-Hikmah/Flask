from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/dashboard/<status>')
def dashboard(status = ""):

    return render_template('dashboard.html', user_status=status)