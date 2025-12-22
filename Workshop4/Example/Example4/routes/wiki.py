from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from forms.pageForm import PageForm
from utils.funcs import login_required
from models.page import Page
from models.user import User
from models import db

wiki_bp = Blueprint('wiki', __name__)

@wiki_bp.route('/wiki/<page_name>')
def view_page(page_name = ""):
    page = db.session.query(Page).filter_by(title=page_name).first()
    if not page:
        flash('Page not Found!', 'danger')
        return redirect(url_for('main.index'))
    return render_template('wiki_page.html', page=page, page_name=page_name)


@wiki_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_page():
    form = PageForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        content = form.content.data
        user = db.session.query(User).filter_by(username=session['user']).first()
        new_wiki = Page(title=title, content=content,author=user)
        db.session.add(new_wiki)
        db.session.commit()
        flash('Page created successfully!', 'success')
        return redirect(url_for('wiki.view_page', page_name=title))
    return render_template('create_page.html', form=form)