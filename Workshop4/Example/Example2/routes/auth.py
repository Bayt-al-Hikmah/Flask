from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from forms.auth import RegistrationForm, LoginForm
from argon2 import PasswordHasher
from utils.funcs import with_db

ph = PasswordHasher()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
@with_db
def register(db):
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        cursor = db.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('auth.register'))
        hashed_passoword = ph.hash(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, avatar) VALUES (?, ?, ?)",
            (username, hashed_passoword , None)
        )
        db.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
@with_db
def login(db):
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        cursor = db.cursor()
        cursor.execute("SELECT username,password_hash FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and ph.verify(user["password_hash"], password) :
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