from flask import Blueprint, render_template,request

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    submitted_name = None
    if request.method == 'POST':
        name = request.form.get('name')
        message = request.form.get('message')
        print(f'Received message from {name}: {message}')
        submitted_name = name

    return render_template('contact.html', submitted_name=submitted_name)