from flask import Blueprint, render_template, request, session

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def not_found_error(e):
    username = session.get('user', None)
    return render_template(
        '404.html',
        title='Page Not Found',
        username=username,
        message="The page you’re looking for doesn’t exist.",
        url=request.path
    ), 404


@errors_bp.app_errorhandler(500)
def internal_error(e):
    username = session.get('user', None)
    return render_template(
        '500.html',
        title='Server Error',
        username=username,
        message="Something went wrong on our end. Please try again later."
    ), 500