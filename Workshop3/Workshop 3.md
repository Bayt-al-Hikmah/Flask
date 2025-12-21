## Objectives
- Implement user **registration, login, and logout** functionality using Flask's built-in `session`.
- Build a simple wiki app where users can create and view pages.
- Handle **rich text** input safely using Markdown.
- Allow users to **upload files** and manage them securely.
- Handling Server Errors and None Found Pages
- Explore the evolution of CSS: from component classes to **utility-first frameworks**.

## User Authentication
Authentication is the process of verifying a user’s identity confirming that someone really is who they claim to be before granting them access to an application. It forms the backbone of security in web systems, preventing unauthorized access to data and functionality, it is a foundational aspect of web applications, ensuring that only authorized individuals can access certain features or data. 
In this wokrshop we will create wiki app, authentication allows us to track who creates content and secure sensitive actions like creating pages or uploading files.
### Simulating Our Database
Since we’re not using a database yet, we’ll simulate user and page storage with Python dictionaries. In a real application, we would replace this with a database like PostgreSQL or MongoDB using an ORM like SQLAlchemy. Simulating a database with in-memory objects is a common practice during development. It allows us to focus on application logic without the overhead of database setup. However, this data will be **lost when the server restarts**, so it's not suitable for production.    
To create our in-memory "database," we'll attach dictionaries to our main Flask application object.  
**`app.py`:**
```python
from flask import Flask

app = Flask(__name__)

# Simulated in-memory "database"
app.users = {}  # e.g., {'username': {'password': 'password123', 'avatar': None}}
app.pages = {}  # e.g., {'HomePage': {'content': 'Welcome!', 'author': 'admin'}}
```
This simple dictionary structure mimics key-value storage: users are indexed by username, and pages by their titles.  
To access these dictionaries from our route blueprints, we need to import a special object called `current_app`. This object provides a reference to the active Flask application, allowing us to access shared variables such as `current_app.users` and `current_app.pages` from anywhere in the app.
### The Flask Session
How does our app remember who’s logged in across requests? Flask uses a **`session`** object to store user data between requests. By default, Flask keeps session data in a cryptographically signed cookie on the client’s browser, making the server itself stateless. However, for better security and scalability, we can store sessions on the server using the **Flask-Session** extension.  
### Install required packages:
We’ll begin by installing the necessary packages:
```shell
pip install Flask Flask-WTF python-dotenv Markdown Flask-Session
```
These packages provide the following functionality:
- **Flask:**  The core web framework that powers our application.
- **Flask-WTF:** Simplifies form creation and validation, and includes built-in protection against CSRF attacks.
- **python-dotenv:** Loads environment variables from a `.env` file, making configuration management easier and more secure.
- **Markdown** Allows us to safely convert Markdown content into HTML for display on our wiki pages.
- **Flask-Session:** Enables server-side session management, providing better security and flexibility than Flask’s default client-side sessions.
### Creating the Routes with Blueprints
We create a `routes` folder, and inside it, we add our first file named `auth.py`. This file will handle user authentication routes, including login, logout, and registration functionality.  
**`routes/auth.py`:**
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from utils.forms import RegistrationForm, LoginForm
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
        if user and user['password'] == password:
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
    #session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
```

**GET /register**
When a user visits `/register`, the server renders the registration page. We create an instance of our `RegistrationForm` and pass it to the template. The template will use this form object to render the input fields and display any validation errors.  
**POST /register**  
When the registration form is submitted:
1. **Validation**: `Flask-WTF` automatically validates the incoming data based on the rules we defined in the `RegistrationForm` class (e.g., username length, required password). If validation fails, the `register.html` template is re-rendered, and `Flask-WTF` automatically displays the errors next to the corresponding fields.  
2. **Duplicate Check**: The server checks if the username already exists in our `current_app.users` dictionary. If so, it uses `flash()` to create a message that will be displayed to the user and redirects back to the registration page.
3. **User Creation**: If the username is new, the user is added to our in-memory dictionary.
4. **Feedback and Redirect**: A success message is flashed, and the user is redirected to the `/login` page.

**GET /login**
This route renders the `login.html` template, passing it a `LoginForm` instance. It also displays any **flashed messages** (like "Registration successful!").  
**POST /login**  
When the login form is submitted:
1. **Validation**: `Flask-WTF` validates that the `username` and `password` fields are not empty.
2. **User Lookup & Password Verification**: The server looks up the user and checks if the submitted password matches the stored one.
3. **Successful Login**: If credentials are correct, the user's information (just the username) is stored in the Flask `session` object: `session['user'] = {'username': username}`. The user is then redirected to the home page (`/`).
4. **Failed Login**: If credentials fail, an error message is flashed, and the user is redirected back to the `/login` page.  

**GET /logout**  
When a user visits `/logout`, we simply remove their data from the session using `session.destroy()`. This effectively logs them out. They are then redirected to the login page.  

**`routes/main.py`**
```python
from flask import Blueprint, render_template
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():

    return render_template('index.html')
```
Now we create our second route file, which defines the main blueprint handling the core routes of our application.
#### The Flash Function
Flask’s **`flash()`** function provides a simple way to display one-time messages to users after an action, such as registration, login, or logout. When `flash(message, category)` is called, Flask stores the message in the user’s session so it can be retrieved and displayed on the next rendered page typically after a redirect they are cleared automatically after being displayed once.   
Each message can include a category like `"success"`, `"info"`, or `"danger"`, which is often used in templates to style messages with different colors (for example, using Bootstrap alert classes). This makes `flash()` ideal for giving users immediate feedback, such as confirming a successful login, warning about invalid credentials, or notifying them that they’ve been logged out.
### Creating Forms
Now, let’s create a `utils` folder, and inside it, add a `forms.py` module. This file will define our `RegistrationForm` and `LoginForm` classes, which handle user input validation and make form processing in Flask simpler and more secure.
**`utils/forms.py`**
```python
from wtforms import StringField, PasswordField, validators
from flask_wtf import FlaskForm

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=25)])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6)])

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
```
In the `forms.py` module, we define two form classes — one for registration and one for login. Both forms inherit from `FlaskForm`, which integrates WTForms with Flask to simplify form handling and validation. Each form contains two input fields: a `StringField` for the username and a `PasswordField` for the password.  
The **`RegistrationForm`** applies two types of validators:
- `DataRequired()` ensures that both fields are not left empty.
- `Length(min, max)` restricts the username to 3–25 characters and requires the password to be at least 6 characters long.


The **`LoginForm`**, on the other hand, only checks that both fields are filled in using the `DataRequired()` validator, since we don’t need to enforce length limits during login.
### Create Templates
We start by creating then `_navbar.html` the `_footer.html` and the ``layout.html`` templates, we create the `templates` and inside it we create another folder  `partials` inside it we create the `_footer.html` and `_navbar.html`.  
**`templates/partials/_navbar.html`:**
```html
<header class="site-header">
    <div class="container header-inner">
        <a class="brand" href="{{ url_for('main.index') }}">MyApp</a>
        <nav class="main-nav">
            {% if session.user %}
                <span class="greet">Hello, {{ session.user }}</span>
                <a href="{{ url_for('auth.logout') }}" class="nav-link">Logout</a>
            {% else %}
                <a href="{{ url_for('auth.login') }}" class="nav-link">Login</a>
                <a href="{{ url_for('auth.register') }}" class="nav-link">Register</a>
            {% endif %}
        </nav>
    </div>
</header>
```
This defines the navigation bar  that will appear on all our web pages.  
**`templates/partials/_footer.html`:**
```html
<footer class="site-footer">
    <div class="container">
        <small>&copy; 2025 MyApp</small>
    </div>
</footer>
```
This defines the footer section that will appear at the bottom of all our web pages.  
**``templates/layout.html``**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MyApp</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    {% include 'partials/_navbar.html' %}

    <main class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-wrapper">
                    {% for category, message in messages %}
                        <div class="flash flash-{{ category }}">
                            <span class="flash-message">{{ message }}</span>
                            <button class="flash-dismiss" onclick="this.parentElement.style.display='none'">×</button>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        <section class="content">
	        {% block content %}{% endblock %}
        </section>
        {% include 'partials/_footer.html' %}
        </main>
</body>
</html>
```
Finally, this defines the shared layout template that all our web pages will use.   
Now we move to create our `register.html` and `login.html` templates  
**`templates/register.html`:**

```html
{% extends "layout.html" %}
{% block content %}
<h1 class="page-title">Create an account</h1>

<form method="POST" action="{{ url_for('auth.register') }}" class="form-card">
    {{ form.hidden_tag() }} 
    {{ form.username.label }}
    {{ form.username(id='username', required=True) }}
    {% for error in form.username.errors %}
        <span style="color:red;">{{ error }}</span><br>
    {% endfor %}

    {{ form.password.label }}
    {{ form.password(id='password', required=True) }}
    {% for error in form.password.errors %}
        <span style="color:red;">{{ error }}</span><br>
    {% endfor %}

    <div class="form-actions">
        <button type="submit" class="btn btn-primary">Register</button>
        <a href="{{ url_for('auth.login') }}" class="btn btn-link">Already have an account?</a>
    </div>
</form>
{% endblock %}
```
This template extends our shared `layout.html`, meaning it inherits the common structure and only replaces the `content` block with the registration form. The form itself is built using **Flask-WTF**, which integrates WTForms with Flask to simplify form creation, validation, and CSRF protection.  

Inside the form, `form.hidden_tag()` automatically generates a hidden CSRF token field the  `form.username` and `form.password` represent the actual input fields, while `form.username.label` and `form.password.label` generate their corresponding labels. The `{% for error in form.username.errors %}` loops are used to display validation error messages dynamically under each field, helping users correct mistakes easily.    

**`templates/login.html`:**
```html
{% extends "layout.html" %}
{% block content %}
<h1 class="page-title">Log in</h1>

<form method="POST" action="{{ url_for('auth.login') }}" class="form-card">
    {{ form.hidden_tag() }}

    {{ form.username.label }}
    {{ form.username(id='username', required=True) }}
    {% for error in form.username.errors %}
        <span style="color:red;">{{ error }}</span><br>
    {% endfor %}

    {{ form.password.label }}
    {{ form.password(id='password', required=True) }}
    {% for error in form.password.errors %}
        <span style="color:red;">{{ error }}</span><br>
    {% endfor %}

    <div class="form-actions">
        <button type="submit" class="btn btn-success">Login</button>
        <a href="{{ url_for('auth.register') }}" class="btn btn-link">Create account</a>
    </div>
</form>
{% endblock %}
```
Same as before, our login template extends the shared layout and adds a simple form with username and password fields   
**`templates/index.html`:**
```html
{% extends "layout.html" %}
{% block content %}
<h1 class="page-title">Welcome to MyApp</h1>
<p>Create and view wiki pages!</p>
{% endblock %}
```
Finally, this is our `index.html` template. It extends the shared layout and serves as the homepage, displayed when the user visits the `/` route.
### Adding Styles
Create a ``static`` folder and place your ``style.css`` file inside it. For this workshop, we will use the styles from the ``material`` folder.

### Environment Variables
We use **environment variables** to securely store sensitive configuration data, such as the secret key, instead of hardcoding them in our source code.  
To do this, we create a `.env` file in the root directory of our project:  
**`.env`**
```shell
SESSION_SECRET=your-very-secure-random-32-character-key
```
The **`python-dotenv`** library automatically loads these variables, allowing us to safely access them in our Flask app using `os.getenv('SESSION_SECRET')`.
### Configure The `app.py` file
The last thing we need to do is create the `app.py` file the main entry point of our application. Here, we configure our sessions and app settings, and register all our blueprints.  
**``app.py``**
```python
import os
from dotenv import load_dotenv
from flask import Flask, render_template, session
from flask_session import Session
from datetime import timedelta
from routes import auth, main

load_dotenv() 

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.getenv('SESSION_SECRET'),
    SESSION_TYPE='filesystem',             # Use server-side sessions
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
    SESSION_COOKIE_SECURE=True,            # Only send over HTTPS
    SESSION_COOKIE_HTTPONLY=True,          # Prevent access from JavaScript
    SESSION_COOKIE_SAMESITE='Lax'          # Helps prevent CSRF
)

# Initialize Flask-Session
Session(app)
# Simulated in-memory "database"
app.users = {}
app.pages = {}

# Register the blueprints
app.register_blueprint(auth.auth_bp)
app.register_blueprint(main.main_bp)

if __name__ == '__main__':
    app.run(debug=True, port=3000)
```
We start by calling `load_dotenv()`, which uses the **python-dotenv** library to load environment variables from our `.env` file. This allows us to securely access sensitive values such as `SESSION_SECRET`  without hardcoding them in our source code.  
Next, we configure **Flask-Session** to use **server-side sessions** by setting `SESSION_TYPE='filesystem'`. This means user session data is stored safely on the server instead of in client cookies.  
Other key configuration options include:  
- `SECRET_KEY`: Loaded from our `.env` file, used to sign session data and prevent tampering.
- `SESSION_COOKIE_SECURE=True`: Ensures cookies are only sent over HTTPS.
- `SESSION_COOKIE_HTTPONLY=True`: Blocks access to cookies from JavaScript, improving security.
- `SESSION_COOKIE_SAMESITE='Lax'`: Helps protect against CSRF attacks.
- `PERMANENT_SESSION_LIFETIME`: Sets how long a session remains active before expiring (1 hour in this case).

The line `Session(app)` initializes Flask-Session and links it to our Flask app, replacing the default cookie-based session behavior with the configured server-side storage.  
We then create two simple in-memory “databases” `app.users` and `app.pages` which temporarily store user and page data while the app is running. (In a real project, this would be replaced with a persistent database like SQLite or PostgreSQL.)  
Finally, we register two blueprints:
- `auth.auth_bp` for authentication routes (login, logout, register)
- `main.main_bp` for the main application routes


When you run the file, Flask launches the server on port `3000` with `debug=True` enabled for development.

## Rich Text and Pages

A wiki needs to support **rich text** so users can format their content with headings, bold text, and lists. However, allowing raw HTML would be insecure, as it could enable **Cross-Site Scripting (XSS)** attacks where malicious scripts are injected into pages. To keep things safe, we’ll use **Markdown**, a lightweight markup language that’s easy to learn and much safer when properly parsed. By converting Markdown to HTML on the server with the `Markdown` library, we allow users to create nicely formatted content without exposing our app to security risks.  
Install the **Markdown** library:
```shell 
pip install Markdown
```
### Login Check Decorator
Before creating the routes that handle displaying and creating wiki pages, we first need to add some access control. Inside the `utils/funcs` folder, we’ll create a new file and define a `login_required` decorator. This decorator checks whether a user is logged in if not, it redirects them to the login page. This helps protect our routes and ensures that only authenticated users can create or edit pages.  
**``utils/funcs.py``**
```python
from functools import wraps
from flask import redirect, url_for, session, flash
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('You must be logged in to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
```
This `login_required` function is a **decorator** used to protect routes that require authentication. It uses `functools.wraps` to preserve the original function’s metadata and checks whether a `'user'` key exists in the session (meaning someone is logged in).  
If the user is **not logged in**, it flashes a warning message and redirects them to the login page. Otherwise, it allows the original route function to run normally.
### Creating Form
Now we’ll create a new form that handles submitting new wiki pages.
**``utils/forms.py``**
```python 
from wtforms import StringField, PasswordField, validators, TextAreaField
from flask_wtf import FlaskForm

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=25)])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6)])

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class PageForm(FlaskForm):
    title = StringField('Title', [validators.DataRequired()])
    content = TextAreaField('Content', [validators.DataRequired()])
```
The new `PageForm` class defines a simple form for creating new wiki pages using **Flask-WTF**. It includes two fields:
- **`title`** a `StringField` that captures the page’s title. It uses the `DataRequired` validator to ensure the user doesn’t submit an empty title.
- **`content`** a `TextAreaField` for entering the main page content, also validated with `DataRequired`.
### Creating wiki route
Now we’ll create a new route blueprint that handles displaying existing wiki pages and creating new ones.   
**`routes/wiki.py`:**
```python
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
```

**GET /wiki/<page_name>**
- The route extracts the `page_name` from the URL.
- It looks up the page in our `current_app.pages` dictionary.
- If the page doesn't exist, we redirect the user to the main route and display flash message page not found `Page not Found!`.
- If the page is Markdown, it's converted to HTML using `markdown.markdown()`.
- Finally, it renders the `wiki_page.html` template.
    
**POST /create**
- The `@login_required` decorator ensures only logged-in users can access this.
- `Flask-WTF` validates the form.
- If valid, a new page entry is added to the `pages` dictionary with the content, author, and an `is_markdown` flag.
- The user is redirected to the newly created page.


**`@login_required` Decorator**  
In Python, a **decorator** is a function that wraps another function to add functionality. Here, `@login_required` checks if a user is in the session before running the route's view function. This is a clean and reusable way to protect multiple routes. 
### Templates for Wiki Pages
Finally, we’ll create the templates used for displaying existing wiki pages and for creating new ones.
**`templates/wiki_page.html`:**
```html
{% extends "layout.html" %}
{% block content %}
<h1>{{ page_name }}</h1>
<p><em>By: {{ page.author }}</em></p>
<hr>
<div>
    {{ page.html_content | safe }}
</div>
{% endblock %}
```
The `| safe` filter tells Jinja2 that the `html_content` is safe to render as HTML and should not be escaped. This is critical because our `markdown` library has already sanitized the input.   
**`templates/create_page.html`:**
```html
{% extends "layout.html" %}
{% block content %}
<h1 class="page-title">Create a Wiki Page</h1>

<form method="POST" action="{{ url_for('wiki.create_page') }}" class="form-card">
    {{ form.hidden_tag() }}

    {{ form.title.label }}
    {{ form.title(required=True) }}

    {{ form.content.label }}
    {{ form.content(rows=12, placeholder='# Heading...') }}

    <div class="form-actions">
        <button type="submit" class="btn btn-primary">Create Page</button>
    </div>
</form>
{% endblock %}
```
Here we use **WTForms (Flask-WTF)** form to handle page creation we renders the `PageForm` fields (`title` and `content`) along with CSRF protection via `form.hidden_tag()`. The form allows users to input a page title and Markdown-formatted content, which will be processed and saved when submitted.  
Finally we register the new route Blueprint by adding this to our ``app.py``
```python
app.register_blueprint(wiki.wiki_bp)
```
## Using CKEditor in Flask

While Markdown is simple, not everyone wants to learn a syntax. A more user-friendly option is **CKEditor**, which provides a visual text editor, much like a word processor. With CKEditor, users can style text directly, and the editor outputs HTML that we can store as-is. This means we no longer need to convert from Markdown., We start by installing Flask-CKEditor
```shell
pip install flask-ckeditor
```
### Editing the Form
We update our form to integrate **CKEditor**, a rich-text editor that provides a user-friendly interface for writing and formatting content. This allows users to create pages with styled text, lists, links, and more without needing to know Markdown or HTML.  
**`utils/forms.py`**
```python
from wtforms import StringField, PasswordField, validators 
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=25)])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6)])

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class PageForm(FlaskForm):
    title = StringField("Title", validators=[validators.DataRequired()])
    content = CKEditorField("Content", validators=[validators.DataRequired()])
```
We’ve updated the **`PageForm`** to use **`CKEditorField`** from the `flask_ckeditor` library instead of a plain `TextAreaField` for the `content` field.    
This allows users to write and format their wiki content using a **rich-text editor**, providing tools for bold text, headings, lists, and links all without writing Markdown or HTML manually.   
The CKEditor field is automatically rendered as an interactive editor in the browser, giving a much better writing experience.
### Editing Wiki Blueprint
Now we update our **wiki blueprint** since **CKEditor** returns formatted content as HTML, we no longer need to use **Markdown** for conversion.  
**`routes/wiki.py`**
```python 
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
        current_app.pages[title] = {'content': content, 'author': author}
        flash('Page created successfully!', 'success')
        return redirect(url_for('wiki.view_page', page_name=title))
    return render_template('create_page.html', form=form)
```
In this updated **wiki blueprint**, we modified the code to work with **CKEditor**. Since CKEditor already returns formatted HTML, we no longer convert the content from Markdown we directly store and render it as HTML. The `view_page` route retrieves the page from our in-memory database and displays it, while the `create_page` route lets logged-in users create new pages using the `PageForm`. Once a page is created, it’s saved in memory along with the author’s name and displayed immediately.
### Editing Create Page Template 
To include and activate **CKEditor** in our template, we need to add the following lines at the end of the `create_page.html` file:  
```html
{{ ckeditor.load() }}
{{ ckeditor.config(name='content') }}
```
- **`ckeditor.load()`**  loads all the necessary CKEditor JavaScript and assets into the page so the editor can function.
- **`ckeditor.config(name='content')`** initializes CKEditor for the field named `"content"` and applies the default configuration (we can also customize settings like toolbar options with it)

Our ``create_page.html`` template become as following
**``templates/create_page.html``**
```html
{% extends "layout.html" %}
{% block content %}

<h1 class="page-title">Create a Wiki Page</h1>
<form method="POST" action="{{ url_for('wiki.create_page') }}" class="form-card">
    {{ form.hidden_tag() }}
    {{ form.title.label }}
    {{ form.title(required=True) }}
    {{ form.content.label }}
    {{ form.content() }}
    <div class="form-actions">
        <button type="submit" class="btn btn-primary">Create Page</button>
    </div>
    {{ ckeditor.load() }}
    {{ ckeditor.config(name='content') }}
</form>
{% endblock %}
```
### Updating app.py
Finally, we update the **`app.py`** file to integrate **CKEditor** support into our application.  
**`app.py`**
```python 
import os
from dotenv import load_dotenv
from flask import Flask, render_template, session
from flask_session import Session
from datetime import timedelta
from routes import auth, main,wiki
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

# Simulated in-memory "database"
app.users = {}
app.pages = {}

# Register the blueprin
app.register_blueprint(auth.auth_bp)
app.register_blueprint(main.main_bp)
app.register_blueprint(wiki.wiki_bp)
  
if __name__ == '__main__':
    app.run(debug=True, port=3000)
```
We configure and initialize our app to use **CKEditor** by adding ``ckeditor = CKEditor(app)`` This line links CKEditor with our Flask application, enabling rich text editing for any `CKEditorField` in our forms. It automatically loads the necessary scripts and styles, allowing users to create and edit content using a user-friendly WYSIWYG editor.
## File Uploads
Allowing users to upload files, such as profile pictures or attachments, is a common feature in modern web apps. However, it introduces significant **security risks**, including the possibility of uploading malicious files or overloading the server.

In Flask, we’ll use the **Werkzeug** utilities and **Flask-WTF** for form handling. We’ll ensure only **authenticated users** can upload, **sanitize filenames**, **validate file types**, and **store files safely** outside the main application directory.  
**Installing Packages**
```shell
pip install python-magic-bin
```
**`python-magic`** is a Python library that identifies a file’s true type by reading its **binary signature**, known as _magic bytes_, instead of trusting the file’s extension or user input. This makes it a powerful security tool for verifying uploaded files  for example, detecting whether an uploaded `.jpg` is actually an image or a disguised executable.
### Creating The Upload Form
First, we’ll create a new upload form inside our `utils/forms.py` file:  
**``utils/forms.py``**
```python
from wtforms import StringField, PasswordField, validators,FileField
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
  
class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=25)])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6)])

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
  
class PageForm(FlaskForm):
    title = StringField("Title", validators=[validators.DataRequired()])
    content = CKEditorField("Content", validators=[validators.DataRequired()])
    
class UploadForm(FlaskForm):
    avatar = FileField('Upload Avatar', validators=[validators.DataRequired()])
```
In our `UploadForm` class, we define an **`avatar`** field using `FileField`. This creates a file input field that requires the user to select a file before submitting the form.
### Creating Helper Function
We’ll add a function to our `utils/funcs.py` file that helps us verify whether the uploaded file has an allowed extension.   
**`utils/funcs.py`**
```python
from functools import wraps
from flask import redirect, url_for, session, flash
import magic
from pathlib import Path
from werkzeug.utils import secure_filename
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
    
```
We created two  helper  function 
- allowed_file check if the file extension is on the ALLOWED_EXTENSIONS
- upload_file use allowed_file to check the file extension and use magic to check file mime type if both check pass we generate filename, save it on our server and return True with File name if any check file we return False with empty string 
### Creating the Profile Route
Now we’ll create a new route blueprint that handles displaying the user profile and uploading profile picture.  
**`routes/profile.py`:**
```python
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, abort
from utils.forms import UploadForm
from utils.funcs import login_required, upload_file

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UploadForm()
    username = session['user']
    user = current_app.users.get(username, {})
    avatar_path = user.get('avatar', None)
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files.get('avatar')
        if not file or file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('profile.profile'))
        status,filename = upload_file(file)
        if not status:
            flash('Only image files are allowed (.png, .jpg, .jpeg, .gif).', 'danger')
            return redirect(url_for('profile.profile'))
        user['avatar'] = filename
		current_app.users[username] = user
        flash('Avatar uploaded successfully!', 'success')
        return redirect(url_for('profile.profile'))
    return render_template('profile.html', form=form, user=user, avatar_path=avatar_path)
```
When the `/profile` get request, the @login_required check if the user is logged in or no,if he is logged in request continue else it will get redirected to login page, After the request pass the decorator, we retrice the logged-in username from the session (`session['user']`), then we loading the user record from `current_app.users` and we fetch the avatar, After that we have to path.   
If the request is Get or the form isn't valid we rendring the profile.html template.   
If the reques it Post and the Form is valid, we extract the file from the form, we check if it submitted  we use upload_file to check the file and upload it to our server and finally we edit the user avatar inside our memory with `user['avatar'] = filename` and  `current_app.users[username] = user`then we redirect the user to ``/profile`` with a succeed message, if the workflow fail we redirect ser to `/profile` with error message.

### Serving Uploaded Files Safely
To serve uploaded files securely, we’ll add another route inside `routes/profile.py`:
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_from_directory # we add send_from_directory to the import
from pathlib import Path

# We add this
UPLOAD_DIR = Path('./uploads/avatars')

# We add after the profile route
@profile_bp.route('/avatars/<filename>')
@login_required
def get_avatar(filename):
    return send_from_directory(UPLOAD_DIR, filename)
```
This new route `/avatars/<filename>` is responsible for **serving user-uploaded avatar images**. When a user’s profile page requests an image, Flask uses `send_from_directory()` to securely retrieve the file from the `UPLOAD_DIR`.  
The `@login_required` decorator ensures that only authenticated users can access uploaded avatars, preventing unauthorized access to user files.
### Template for Profile Page
Finally, we’ll create the profile page template.    
**`templates/profile.html`:**
```html
{% extends "layout.html" %}
{% block content %}
<h1>Welcome, {{ session['user'] }}</h1>
<div class="avatar-section">
    {% if user.avatar %}
        <img src="{{ url_for('profile.get_avatar', filename=user.avatar) }}" alt="User Avatar" class="avatar">
    {% else %}
        <p>No avatar uploaded yet.</p>
    {% endif %}
</div>

<form method="POST" enctype="multipart/form-data" action="{{ url_for('profile.profile') }}">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.avatar.label }}
        {{ form.avatar() }}
    </div>
    <div class="form-group">
        <button type="submit" class="btn btn-success">Upload</button>
    </div>
</form>
{% endblock %}
```
he form uses `enctype="multipart/form-data"` to enable file uploads. We also show the avatar (if available) using a route that will serve the image securely.
### Registering the Profile Blueprint
Finally, register the new route in the main application by importing the `profile` blueprint and adding the following line to your Flask app setup:  
**``app.py``**
```python
app.register_blueprint(profile.profile_bp)
```
## Handling Errors
Even the best-designed applications encounter errors such as users visiting non-existing pages or unexpected internal issues, By default, Flask returns simple, plain-text error responses (like “404 Not Found” or “500 Internal Server Error”), which are functional but not very user-friendly, To maintain a consistent user experience, we can **override Flask’s default error pages** with our own **custom templates** that match our site’s design and guide users back to safety.
### Creating the Error Blueprint
We’ll create a new file called **`routes/errors.py`**, where we define two custom error pages one for **404 (Not Found)** and one for **500 (Internal Server Error)**.
**``routes/errors.py``**
```python
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
```
Here we create  `errors_bp` Blueprint to handle application-wide errors in a clean, modular way. The `@errors_bp.app_errorhandler(404)` decorator catches all “Page Not Found” errors and renders a custom `404.html` template, displaying a user-friendly message along with the requested URL.   
Similarly, the `@errors_bp.app_errorhandler(500)` function handles unexpected server errors, showing a `500.html` template with a helpful message instead of a raw error page.   
Both functions retrieve the logged-in username from the session (if available) to personalize the error page and return the appropriate HTTP status code (404 or 500). This makes the app’s error handling consistent, user-friendly, and well-integrated across all routes.

### Create the Templates
Let’s now create two templates one for **404 errors** and one for **500 errors** that provide a consistent, branded look for your app.  
**``templates/404.html``**
```html
{% extends "layout.html" %}
{% block content %}
<div class="container text-center mt-5">
  <h1>404 - Page Not Found</h1>
  <p>Sorry, the page "{{ url }}" doesn’t exist.</p>
  <a href="{{ url_for('main.index') }}" class="btn btn-primary mt-3">Go Back Home</a>
</div>
{% endblock %}
```
**``templates/500.html``**
```html
{% extends "layout.html" %}
{% block content %}
<div class="container text-center mt-5">
  <h1>500 - Internal Server Error</h1>
  <p>{{ message }}</p>
  <a href="{{ url_for('main.index') }}" class="btn btn-secondary mt-3">Return to Home</a>
</div>
{% endblock %}
```
### Registering the Errors Blueprint
Finally, register the new route in the main application by importing the `errros` blueprint and adding the following line to our Flask app setup:   
**``app.py``**
```python
app.register_blueprint(errors.errors_bp)
```
## A Journey Through CSS Styling
### Act I: The Specific Approach (Class-per-Element)
When we first begin styling our web pages, the natural instinct is to give each element its own class and style it directly. For example:  
**Example CSS (not used in our app):**
```css
.login-page-button {
  background-color: blue;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
}
```
**HTML:**
```html
<button class="login-page-button">Login</button>
```
At first, this feels simple and organized every element gets its own “label,” and we know exactly where its style lives.
But very quickly, a problem appears:
- The Register button will need almost the same styles as the Login button.
- Input fields across different pages also share similar styling.
- Suddenly, we’re copying and pasting the same rules over and over.


This creates duplication and makes our CSS harder to maintain. Imagine having 5 different button classes scattered around your project if you want to change the padding, you’d need to edit all of them.  
To fix this, we need to step back and notice patterns. Many elements aren’t unique snowflakes they belong to the same component family. Buttons share common traits, inputs share common traits. Instead of treating them as separate cases, we can extract those shared features and place them into special reusable classes.  
This shift in thinking is what leads us toward the reusable component approach in Act II.
### Act II: The Reusable Component (Shared Classes)
To fix the duplication problem from Act I, we need to change how we see our elements. Instead of thinking about each button or input as a one-off element, we treat them as components.  
A component is simply a reusable piece of UI like a button, an input box, or a card. Each component has a base style that defines its common features. For example, all buttons might share padding, border-radius, and font weight.    
On top of that, we can add variations (or modifiers) that adjust the base style like giving one button a blue background (.btn-primary) and another a gray background (.btn-secondary).  
This way, our CSS is not about styling individual elements, but about describing what type of component the element is. When we create new elements in our HTML, we don’t invent a new class each time we simply apply the right combination of existing component classes.   
Here’s what that looks like in practice:  
**Our `style.css` (already implemented):**
```css
.btn {
  padding: 9px 14px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
}
.btn-primary {
  background: var(--accent);
  color: white;
  border-color: rgba(43,124,255,0.1);
}
```
**HTML in Templates:**
```html
<button class="btn btn-primary">Register</button>
```
This is exactly the approach that **Bootstrap** and other frameworks popularized. They provide base classes (`.btn`, `.form-control`, `.card`) and variations (`.btn-primary`, `.btn-danger`, `.btn-outline`), letting developers build entire UIs just by combining classes.
### Act III: The Utility-First Revolution
The component approach from Act II is a big improvement over one-class-per-element, but it isn’t perfect. Components come with predefined styles for things like padding, margin, and borders.  
But what if you need a button with slightly less padding? Or an input field with a custom margin? Suddenly, we’re stuck. we either:
- Override the existing class (which feels messy), or
- Create a brand-new variation (like .btn-small or .btn-wide) amnd before long, we’re back to the duplication problem from Act I.


To solve this, a new idea emerged: instead of making classes for components, why not make classes for single styling functions?
For example:
- p-4 → padding
- m-10 → margin
- text-lg → font size
- bg-blue-500 → background color
    

With this approach, we’re not writing CSS to describe componentswe’re building components directly in the HTML by stacking utility classes together.  
This is the philosophy behind utility-first frameworks like Tailwind CSS.  
**Example with Tailwind (hypothetical):**
```html
<button class="bg-blue-500 text-white p-4 rounded-md">Register</button>
```

Here, every class is doing one small job: background, text color, padding, border radius. Together, they form a complete button. It’s like snapping LEGO bricks together each brick is tiny and simple, but combined, they make something powerful.  
This approach has huge benefits:
- No need for CSS overrides we control spacing, sizing, and colors directly in the markup.
- Less CSS file bloat → most styles come from the framework.
- Faster prototyping we can build and tweak designs instantly without creating new CSS classes.
    

However, it does come with one small drawback: your HTML can look crowded with classes. A single element may end up with 6–10 classes, which feels like “class spam.” Some developers love this tradeoff, others find it messy.
