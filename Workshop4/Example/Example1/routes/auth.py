from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from forms.auth import RegistrationForm, LoginForm
from argon2 import PasswordHasher

ph = PasswordHasher()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        if username in current_app.users:
            flash('Username already exists!', 'danger')
            return redirect(url_for('auth.register'))
        hashed_password = ph.hash(password)
        current_app.users[username] = {'password': password, 'avatar': None}
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        user = current_app.users.get(username)
        if user and ph.verify(user['password'], password) :
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))