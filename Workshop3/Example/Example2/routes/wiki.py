import markdown
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, abort
from utils.forms import PageForm
from utils.funcs import login_required

wiki_bp = Blueprint('wiki', __name__)

@wiki_bp.route('/wiki/<page_name>')
def view_page(page_name = ""):
    page = current_app.pages.get(page_name)
    if not page:
        flash('Page not Found!', 'danger')
        return redirect(url_for('main.index'))
    if page.get('is_markdown', False):
        page['html_content'] = markdown.markdown(page['content'])
    else:
        page['html_content'] = page['content']  
    return render_template('wiki_page.html', page=page, page_name=page_name)

@wiki_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_page():
    form = PageForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        content = form.content.data
        author = session['user']
        current_app.pages[title] = {'content': content, 'author': author, 'is_markdown': True}
        flash('Page created successfully!', 'success')
        return redirect(url_for('wiki.view_page', page_name=title))
        
    return render_template('create_page.html', form=form)