from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.forms import PageForm
from utils.funcs import login_required
from utils.funcs import with_db

wiki_bp = Blueprint('wiki', __name__)

@wiki_bp.route('/wiki/<page_name>')
@with_db
def view_page(db,page_name = ""):
    cursor = db.cursor()
    cursor.execute("SELECT content FROM pages WHERE title = ?", (page_name,))
    page = cursor.fetchone()
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
        cursor = db.cursor()
        cursor.execute("INSERT INTO pages (title, content) VALUES (?, ?)", (title, content))
        db.commit()
        flash('Page created successfully!', 'success')
        return redirect(url_for('wiki.view_page', page_name=title))
    return render_template('create_page.html', form=form)