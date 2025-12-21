## Objectives
- Using Hashed Password For More Protection 
- Introduce **SQLite** as a simple, file-based database.
- Interact with a database using raw SQL, then with a simple class, and finally with an **ORM (SQLAlchemy)**.
## Hashed Passwords
Storing passwords in plain text is a serious security risk if an attacker gains access to our database, all user credentials could be exposed. To protect passwords, we use **one-way hashing functions**, which transform a password into a hash that cannot be reversed, even by the developers.    
When a user logs in, their input is hashed and compared to the stored hash. If the hashes match, the login is successful; otherwise, access is denied.  
For this workshop, we will use the **Argon2** hashing algorithm, which is currently considered one of the most secure and modern password hashing methods. To use it in Python, install the `argon2-cffi` package:
```
pip install argon2-cffi
```
### Editing The Auth Route
We will continue from the codebase we built in the previous lecture. To implement the new approach of **hashing and securely storing passwords**, we need to update our `auth.py` routes to apply this method.  
**`routes/auth.py`**
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from utils.forms import RegistrationForm, LoginForm
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
        current_app.users[username] = {'password': hashed_password, 'avatar': None}
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
```
First, we import the `PasswordHasher` class from the **argon2** package and create an instance of it using `ph = PasswordHasher()`.  
Next, we update the register function. Instead of storing the password directly, we now call `ph.hash(password)` to generate a secure hash before saving it to the database. This ensures that passwords are stored safely and cannot be easily compromised.    
We also modify the login function to use `ph.verify(user['password'], password)`, which checks whether the entered password matches the stored hash. If the verification is successful, the user is granted access.    
No changes are needed to our templates or other routes. With these updates, our application is now more secure, as user passwords are safely stored using modern hashing practices.
## Working with SQLite
Storing users in memory (just in the server’s RAM) is convenient for quick prototyping, but it has a major limitation: all data is lost whenever the server restarts because RAM is volatile. For any real-world application, we need persistent storage a way to save data that survives server restarts. This is where a database comes in. A database provides a structured and reliable way to store, manage, and retrieve data, ensuring that users’ information is safe and always accessible.  
We’ll use **SQLite**, a lightweight, file-based database ideal for learning and small to medium-sized applications. SQLite’s advantages include:

- **Serverless**: No separate server process is required.
- **File-Based**: Data is stored in a single file (e.g., database.db).
- **Built-in**: Available in Python via the sqlite3 package.
### Creating the Database
We define a schema for our SQLite database to store user information. The schema includes a user table with fields for id, username, and password_hash.  
**`schema.sql`:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    avatar TEXT

);

CREATE TABLE pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL
);
```
### Initialize the Database  
We run the schema to create the database file:  
First we connect and create the database file  
```shell
sqlite3 database.db 
```
Now we will be inside the `sqlite` terminal , we run the following command to create our table 
```shell
.read schema.sql
```
Then we quit the sqlite terminal using
```shell
.quit
```
This creates database.db with the user table, ready for use.
### Connect Flask with SQLite
Python comes with a built-in library called `sqlite3` that lets us talk to SQLite directly. We connect to the database, run SQL commands, and then close the connection.    
We start by connecting to our database with:   `conn = sqlite3.connect("database.db")`, This opens a connection to the file `database.db`. If the file doesn’t exist yet, SQLite will create it for us.
Next, we create a cursor: `cur = conn.cursor()` The cursor is like our tool for navigating the database. It lets us send commands (SQL queries) and read results, Once we have the cursor, we can start running commands using `cur.execute()`.   
### Helper Decorator
We will create a helper decorator to manage the database connection efficiently. This decorator is added to the `funcs.py` file for better organization and reusability.  
**``utils/funcs.py``**
```python
from functools import wraps
from flask import redirect, url_for, session, flash
import magic
from pathlib import Path
from werkzeug.utils import secure_filename
import uuid
import sqlite3

# Allowed extensions and MIME types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/gif'}

# Upload folder
UPLOAD_DIR = Path('./uploads/avatars')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('You must be logged in to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(file):
    if not allowed_file(file.filename):
        return False,''
    mime_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    if mime_type not in ALLOWED_MIME_TYPES:
        return False,''
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file_path = UPLOAD_DIR / filename
    file.save(file_path)
    return True,filename

def with_db(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db = sqlite3.connect("./database.db")
        db.row_factory = sqlite3.Row 
        try:
            return f(db, *args, **kwargs)
        finally:
            db.close()
    return decorated_function

```
The new decorator `with_db(f)` manages the connection to the database for any route that performs database operations.
- It connects to the database using `sqlite3.connect("./database.db")`.
- The database connection (`db`) is then passed to the decorated function.
- Finally, after the function finishes executing, the connection is automatically closed using `db.close()`, ensuring that resources are properly released.
### Updating routes
Now we need to update our routes to use the database instead of the in-memory storage.
**`routes/auth.py`**
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.forms import RegistrationForm, LoginForm
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
```
In this version of our authentication routes, we’ve introduced the **`with_db`** decorator to manage database connections automatically. This decorator opens a connection before the route function runs and closes it afterward, ensuring clean and safe database handling without repeating connection logic in every route.  
Inside the `register` and `login` routes, the handler functions now receive a `db` parameter the active database connection provided by the decorator. We use it to create a cursor, execute SQL queries, and commit changes when necessary.  
- In the **`register`** route, we check whether a username already exists, hash the password using **Argon2**, and insert the new user into the database.
- In the **`login`** route, we retrieve the stored hashed password and verify it using `ph.verify()`. If the verification succeeds, we store the username in the session and grant access.

Notice that we use `?` as placeholders when passing parameters to our SQL queries. This approach, known as **parameterized querying**, prevents SQL injection by ensuring that user input is never directly inserted into the query string. Instead, the database safely escapes and processes the values, keeping our application secure.    
We also call **`db.commit()`** after making changes to the database, such as when inserting a new user. This step is essential because it **saves the modifications permanently**. Without calling `commit()`, the changes would only exist temporarily in memory and be lost once the connection closes.  
**`routes/wiki.py`**
```python
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
        author = session['user']
        cursor = db.cursor()
        cursor.execute("InSERT INTO pages (title, content) VALUES (?, ?)", (title, content))
        db.commit()
        flash('Page created successfully!', 'success')
        return redirect(url_for('wiki.view_page', page_name=title))
    return render_template('create_page.html', form=form)
```
Just like we did with the `auth.py` routes, we’ve added the **`with_db`** decorator here as well. This allows our wiki routes to automatically handle the database connection instead of using in-memory data storage.  
Now, both the **`view_page`** and **`create_page`** routes interact directly with the database retrieving and storing page content persistently.   
**`routes/profile.py`**
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, session,  send_from_directory 
from utils.forms import UploadForm
from utils.funcs import login_required, upload_file,with_db 
from pathlib import Path


profile_bp = Blueprint('profile', __name__)
UPLOAD_DIR = Path('./uploads/avatars')

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@with_db
def profile(db):
    form = UploadForm()
    username = session['user']
    cursor = db.cursor()
    cursor.execute("SELECT avatar FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    avatar_path = user["avatar"]
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files.get('avatar')
        if not file or file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('profile.profile'))
        status,filename = upload_file(file)
        if not status:
            flash('Only image files are allowed (.png, .jpg, .jpeg, .gif).', 'danger')
            return redirect(url_for('profile.profile'))
        cursor.execute("UPDATE users SET avatar = ? WHERE username = ?", (filename, username))
        db.commit()
        flash('Avatar uploaded successfully!', 'success')
        return redirect(url_for('profile.profile'))
    return render_template('profile.html', form=form, user=user, avatar_path=avatar_path)

@profile_bp.route('/avatars/<filename>')
@login_required
def get_avatar(filename):
    return send_from_directory(UPLOAD_DIR, filename)
```
### Edit Templates
All our other templates remain the same we only need to update the `wiki_page.html` file.  Since we no longer use the `page.html_content` attribute, we replace it with `page.content`.   
**`wiki_page.html`**
```html
{% extends "layout.html" %}
{% block content %}
<h1>{{ page_name }}</h1>
<p><em>By: {{ page.author }}</em></p>
<hr>
<div>
    {{ page.content | safe }}
</div>
{% endblock %}
```
Finally, in our `app.py`, we can remove the `app.users` and `app.pages` variables they are no longer needed since all user and page data are now stored and managed in the database.
**`app.py`**
```python
import os
from dotenv import load_dotenv
from flask import Flask
from flask_session import Session
from datetime import timedelta
from routes import auth, main, wiki, profile,errors
from flask_ckeditor import CKEditor

load_dotenv()
  
app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.getenv('SESSION_SECRET'),
    SESSION_TYPE='filesystem',             # Use server-side sessions
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
    SESSION_COOKIE_SECURE=True,            # Only send over HTTPS
    SESSION_COOKIE_HTTPONLY=True,          # Prevent access from JavaScript
    SESSION_COOKIE_SAMESITE='Lax'          # Helps prevent CSRF
)

# Initialize Flask-Session
Session(app)

# Initialize CKEditor
ckeditor = CKEditor(app)

# Register the blueprin
app.register_blueprint(auth.auth_bp)
app.register_blueprint(main.main_bp)
app.register_blueprint(wiki.wiki_bp)
app.register_blueprint(profile.profile_bp)
app.register_blueprint(errors.errors_bp)

if __name__ == '__main__':
    app.run(debug=True, port=3000)
```
## Refactoring with a User Class
So far, our logic works we can register users, log them in, and talk to the database. But we quickly notice a problem: we are **mixing Python with raw SQL** directly inside our routes. Every time we want to add a new feature, like checking if a user exists or creating a new one, we end up writing `cur.execute(...)` again and again.  
This creates two big issues. First, it breaks the **DRY principle** (Don’t Repeat Yourself). If we need the same query in multiple routes, we repeat it everywhere, which makes the code harder to maintain. Second, it ties our route logic too closely with database details, so the business logic (what the app does) gets mixed with the data logic (how it’s stored).  
The better way is to **encapsulate** database operations inside classes. Each class represents a table (`User`, `Snippet`, etc.), and each method inside that class handles one operation, like finding a user by username or creating a new record. This way, our routes only call clean Python methods, while the SQL stays hidden in one place
### Creating Classess
We start by creating a new folder called **`models`**. Inside it, we create a `users.py` file, where we define a **User** class to handle all database queries related to users, and a **Page** class to manage queries related to wiki pages. This helps organize our code and separate database logic from route handling.  
**`models/user.py`**
```python
class User:
    @staticmethod
    def create(db,username, password):
        cur = db.cursor()
        cur.execute("INSERT INTO user (username, password_hash) VALUES (?, ?)",
                    (username, password))
        db.commit()

    @staticmethod
    def update_avatar(db,filename,username):
        cur = db.cursor()
        cur.execute("UPDATE users SET avatar = ? WHERE username = ?", (filename, username))
        db.commit()

    @staticmethod
    def find_by_username(db,username):
        cur = db.cursor()
        cur.execute("SELECT * FROM user WHERE username = ?", (username,))
        user = cur.fetchone()
        return user
```
We created the **`User`** class to interact with the **`user`** table in our database.  
It includes two **static methods**, meaning we can call them directly on the class without creating an instance.
- **`create(db, username, password)`**  This method inserts a new user into the database. It prepares a parameterized SQL query to safely store the username and hashed password, then commits the transaction.
- **`update_avatar(db,filename,username)`** This method update the avatar path.
- **`find_by_username(db, username)`** This method retrieves a user’s record from the database by their username and returns it.

**`models/page.py`**
```python
class Page:
    @staticmethod
    def create(db,title, content):
        cur = db.cursor()
        cur.execute("INSERT INTO pages (title, content) VALUES (?, ?)", (title, content))
        db.commit()

    @staticmethod
    def find_by_title(db,page_name):
        cur = db.cursor()
        cur.execute("SELECT content FROM pages WHERE title = ?", (page_name,))
	    page = cur.fetchone()
        return page
```
We also created a **`Page`** class to handle all interactions with the **`pages`** table in the database.  
Like the `User` class, it uses **static methods**, so we can call them directly without creating a class instance.
- **`create(db, title, content)`** This method adds a new wiki page to the database by inserting its title and content, then commits the transaction to save the changes.  
- **`find_by_title(db, page_name)`** This method retrieves a page’s content from the database based on its title and returns it.
### Editing Routes
Now, we update our route blueprints to use the new classes we created. This allows our routes to interact with the database through the **User** and **Page** models, keeping the logic cleaner and more organized.  
**`routes/auth.py`**
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.forms import RegistrationForm, LoginForm
from argon2 import PasswordHasher
from utils.funcs import with_db
from models.user import User

ph = PasswordHasher()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
@with_db
def register(db):
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        existing_user = User.find_by_username(db,username)
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('auth.register'))
        hashed_passoword = ph.hash(password)
        User.create(db,username, hashed_passoword)
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
        user = User.find_by_username(db,username)
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
```
We start by importing the **`User`** class from `models.user`.    Whenever we need to create a new user, we now call **`User.create()`**, and when we need to retrieve a user, we use **`User.find_by_username()`**. By moving the SQL logic into the model, our route code becomes much cleaner and easier to maintain.    
**`routes/profile.py`**
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, session,  send_from_directory 
from utils.forms import UploadForm
from utils.funcs import login_required, upload_file,with_db 
from models.user import User
from pathlib import Path

profile_bp = Blueprint('profile', __name__)
UPLOAD_DIR = Path('./uploads/avatars')

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@with_db
def profile(db):
    form = UploadForm()
    username = session['user']
    user = User.find_by_username(db,username)
    avatar_path = user["avatar"]
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files.get('avatar')
        if not file or file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('profile.profile'))
        status,filename = upload_file(file)
        if not status:
            flash('Only image files are allowed (.png, .jpg, .jpeg, .gif).', 'danger')
            return redirect(url_for('profile.profile'))
        User.update_avatar(db,filename,username)
        flash('Avatar uploaded successfully!', 'success')
        return redirect(url_for('profile.profile'))
    return render_template('profile.html', form=form, user=user, avatar_path=avatar_path)

@profile_bp.route('/avatars/<filename>')
@login_required
def get_avatar(filename):
    return send_from_directory(UPLOAD_DIR, filename)
```
Same as we did for ``auth.py``, Here we use **`User.find_by_username()`** here to retrieve user data. and to update the user’s avatar, we call **`User.update_avatar()`**, keeping all database operations neatly handled within the model and maintaining clean, organized route logic.
**`routes/wiki.py`**
```python
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
```
Finally, in the `wiki.py` routes, we import the **`Page`** class from `models.page`. We use **`Page.find_by_title()`** to retrieve page information and **`Page.create()`** to add new wiki pages to the database.  
## Using SQLAlchemy 
While our earlier `User` and `Page` classes helped organize our database queries, we were still manually writing SQL, which can quickly become difficult to maintain as the project grows. Switching to another database engine like PostgreSQL or MySQL would also mean rewriting large portions of SQL code.  
Managing relationships such as linking users to their wiki pages  introduces extra complexity and repetitive SQL statements.  
This is where **SQLAlchemy 2.0**, the modern, powerful ORM for Python, comes in. It allows us to define our database structure as Python classes (called models) and interact with the database using clean, object-oriented code instead of raw SQL queries.   
We’ll start by installing the necessary packages to work with **SQLAlchemy 2.0**, which provides a modern, efficient, and type-safe ORM layer for our Flask application.
```
pip install sqlalchemy flask-sqlalchemy
```
### Configuring SQLAlchemy 
We first create a file called `models/__init__.py` and place the following code inside it to initialize SQLAlchemy independently of the Flask app:
**``models/__init__.py``**
```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```
Then integrate **SQLAlchemy** into our application, we first need to configure it, We do this by adding the following lines to our `app.py` file:
```python
from models import db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
```
We start by telling **SQLAlchemy** where our database is located using:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
```
Here, we’re using a **SQLite** database stored locally in a file named `database.db`.  
The prefix `sqlite:///` indicates that the database file is located in the same directory as our Flask application.  
If we later decide to switch to another database system such as **PostgreSQL** or **MySQL** we only need to update this URI.   
For example:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@localhost/dbname"
```
Next, we set:
```python
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
```
This line disables **SQLAlchemy’s modification tracking system**, which monitors every object change and emits signals whenever something is updated in the database session.

While this feature can be useful for advanced event handling, it also adds unnecessary overhead and slows down the application if we don’t need it.

By setting it to `False`, we improve performance and prevent SQLAlchemy from showing warnings about unused tracking features.  
Finally, we initialize SQLAlchemy by creating a database instance and linking it to our Flask app using:
```python 
db.init_app(app)
```
This line sets up the **connection between Flask and SQLAlchemy**, allowing our application to interact with the database easily.   
By doing this, we can now define database models (like `User` and `Page`) as Python classes that automatically map to database tables.
In short, `db.init_app(app)` initializes the ORM, manages the connection, and gives us all the tools to create, query, and manage our data using clean Python code instead of raw SQL.
### Creating The SQLAlchemy Models
We modife our model files so now it use the SQLAlchemy 
**``models/user.py``**
```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from moderls import db

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    avatar: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Relationship: One user -> many pages
    pages: Mapped[list["Page"]] = relationship("Page", back_populates="author")
```
We changed the  **`User`** model to use SQLAlchemy First we  inherits from `db.Model`, meaning it maps directly to a database table. The line `__tablename__ = "users"` tells SQLAlchemy that this model corresponds to a table named `users`.    
Each attribute in the class represents a column in that table. 
- The `id` column is defined with `mapped_column(primary_key=True)`, making it the table’s primary key  a unique, auto-incrementing integer that identifies each user. 
- The `username` column is a string (up to 50 characters) that must be unique and non-empty, ensuring that no two users share the same username. 
- The `password_hash` column stores each user’s hashed password and cannot be null. 
- The `avatar` column is optional and stores the filename or path to the user’s avatar image.
- the `pages` attribute establishes a one-to-many relationship between the `User` and `Page` models, using `relationship("Page", back_populates="author")`. 

The one-to-many relationship between the `User` and `Page` means that a single user can have multiple wiki pages, and on the other side, each page will reference its author through the `author` field in the `Page` model.  
**``models/page.py``**
```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from moderls import db

class Page(db.Model):
    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)

    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship("User", back_populates="pages")
```
We also edit the **`Page`** model to use **SQLAlchemy 2.0**, following the same modern ORM style as the `User` model. First, it inherits from `db.Model`, which means it maps directly to a database table. The line `__tablename__ = "pages"` tells SQLAlchemy that this model corresponds to a table named `pages`.  
Each attribute in the class represents a column in that table:
- The `id` column is defined with `mapped_column(primary_key=True)`, making it the table’s primary key  a unique, auto-incrementing integer that identifies each page.
- The `title` column is a string (up to 100 characters) that must be unique and non-empty, ensuring that no two pages share the same title.
- The `content` column stores the main text of the wiki page and cannot be null.
- The `author_id` column is defined as a **foreign key** (`ForeignKey("users.id")`), meaning it references the `id` column from the `users` table. This creates a link between each page and its author.
- The `author` attribute establishes the other side of the one-to-many relationship using `relationship("User", back_populates="pages")`.

This relationship connects each `Page` to a specific `User`, allowing us to easily access the author of any page (for example, `page.author.username`) or list all pages belonging to a user (using `user.pages`).  
### Initialize The Database
After defining our models, we need to **initialize the database** so that SQLAlchemy can create the corresponding tables.  To do this, we create a new file named **`index.py`** with the following code:  
**`index.py`**
```python
from app import app, db

with app.app_context():
    db.create_all()
```

This script imports the Flask application and the SQLAlchemy instance from `app.py`, then runs `db.create_all()` inside the application context.  
The **application context** (`with app.app_context():`) is necessary because Flask extensions like SQLAlchemy need access to the app’s configuration such as the database URI  while performing operations.  
Running this script once will automatically generate the **users** and **pages** tables in our `database.db` file based on the models we defined earlier.
### Editing The Routes
Finally we edit our routes so they use the SQLAlchemy  
**`routes/auth.py`**
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.forms import RegistrationForm, LoginForm
from argon2 import PasswordHasher
from models.user import User
from models import db

ph = PasswordHasher()

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        existing_user = db.session.query(User).filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('auth.register'))
        hashed_password = ph.hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        user = db.session.query(User).filter_by(username=username).first()
        if user and ph.verify(user.password_hash, password) :
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
```
We removed the `with_db` decorator since **SQLAlchemy** now handles opening and closing database connections automatically. In the `register` and `login` routes, instead of manually executing SQL, we use `db.session.query(User).filter_by(...)` to find users and `db.session.add()` + `db.session.commit()` to create new ones. This makes our code cleaner, safer, and fully ORM-based.
**`routes/profile.py`**
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, session,  send_from_directory 
from utils.forms import UploadForm
from utils.funcs import login_required, upload_file
from models.user import User
from pathlib import Path
from models import db

profile_bp = Blueprint('profile', __name__)

UPLOAD_DIR = Path('./uploads/avatars')

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UploadForm()
    username = session['user']
    user = db.session.query(User).filter_by(username=username).first()
    avatar_path = user.avatar
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files.get('avatar')
        if not file or file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('profile.profile'))
        status,filename = upload_file(file)
        if not status:
            flash('Only image files are allowed (.png, .jpg, .jpeg, .gif).', 'danger')
            return redirect(url_for('profile.profile'))
        user.avatar = filename
        db.session.commit()
        flash('Avatar uploaded successfully!', 'success')
        return redirect(url_for('profile.profile'))
    return render_template('profile.html', form=form, user=user, avatar_path=avatar_path)

@profile_bp.route('/avatars/<filename>')
@login_required
def get_avatar(filename):
    return send_from_directory(UPLOAD_DIR, filename)
```
Here too we removed the `with_db` decorator. To update the user, we now use and modify the `avatar` attribute directly, followed by `db.session.commit()` to save changes. 
**`routes/wiki.py`**
```python
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.forms import PageForm
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
```
Finally, we updated our wiki routes to use SQLAlchemy. In `view_page`, we fetch the page with `db.session.query(Page).filter_by(title=page_name).first()`, returning a `Page` object for the template. In `create_page`, we get the current user, create a new `Page` linked to that user, and save it using `db.session.add()` and `db.session.commit()`. 