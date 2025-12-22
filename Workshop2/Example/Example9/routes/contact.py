from forms.contactForm import ContactForm
from flask import Blueprint,render_template

contact_bp = Blueprint('contact', __name__)
@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    submitted_name = None
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        message = form.message.data
        print(f'Received from {name}: {message}')
        submitted_name = name
        return render_template('contact.html', form=form,submitted_name = submitted_name)
    return render_template('contact.html', form=form,submitted_name = submitted_name)