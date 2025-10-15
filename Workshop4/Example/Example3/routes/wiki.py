from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.forms import PageForm
from utils.funcs import login_required
from utils.funcs import with_db
from models.page import Page
wiki_bp = Blueprint('wiki', __name__)

@wiki_bp.route('/wiki/<page_name>')
@with_db
def view_page(db,page_name = ""):
    page = Page.find_by_title(db,page_name)
    if not page:
        flash('Page not Found!', 'danger')
        return redirect(url_for('main.index'))
    return render_template('wiki_page.html', page=page, page_name=page_name)


@wiki_bp.route('/create', methods=['GET', 'POST'])
@login_required
@with_db
def create_page(db):
    form = PageForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        content = form.content.data
        Page.create(db,title, content)
        flash('Page created successfully!', 'success')
        return redirect(url_for('wiki.view_page', page_name=title))
    return render_template('create_page.html', form=form)