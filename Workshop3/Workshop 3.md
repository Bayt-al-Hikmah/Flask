### Objectives
- Implement user **registration, login, and logout** functionality using the Flask `session`.
- Build a simple wiki app where users can create and view pages.
- Handle **rich text** input safely using Markdown.
- Allow users to **upload files** (like avatars) and manage them securely.
- Explore the evolution of CSS: from component classes to **utility-first frameworks**.
### User Authentication
For This workshop, we'll build a simple wiki. The core of any multi-user application is authentication letting users sign up, log in, and log out. Since we're not using a database yet, we'll simulate our user storage with a simple Python dictionary.
#### Simulating Our Database
In our `app.py`, we'll create a dictionary to hold our user data. In a real application, this would be a database table.
```
# A simple in-memory "database" for users
users = {} # e.g., {'username': {'password': 'password123'}}
pages = {} # e.g., {'HomePage': {'content': 'Welcome!', 'author': 'admin'}}
```
#### The Flask `session`
How does our app remember who is logged in across different requests? It uses a **session**. A session is like a small, temporary storage for each user, saved in their browser as a secure cookie. We can put information in it, like a username, and check it on subsequent requests.  
To use sessions, Flask requires a `SECRET_KEY`. This key is used to cryptographically sign the session cookie, preventing users from modifying it.  
**`app.py`:**

```
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
# A secret key is required for session management
app.config['SECRET_KEY'] = 'your-super-secret-key-that-no-one-knows'
```
#### Registration, Login, and Logout Routes
Let's build the core authentication logic. We'll use `flash()` to show messages to the user (e.g., "Successfully logged in!").
**`app.py` we add the following:**
```
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        users[username] = {'password': password, 'avatar': None}
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username # Store username in the session
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None) # Remove username from the session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
```
Flask’s `flash()` function lets you send **temporary messages** to the user.
- These messages are stored in the session (so they persist across a redirect).
- They are cleared automatically after being displayed once.
- You can give them categories like `"success"`, `"danger"`, `"info"`, which makes it easy to style them differently.

We also need to create the `login.html` and `register.html` templates with simple forms. Remember to loop through flashed messages in your `layout.html` to display them!  
``templates/layout.html``
```
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{% block title %}Flask App{% endblock %}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="{{ url_for('home') }}">MyApp</a>
      <nav class="main-nav">
        {% if session.get('username') %}
          <span class="greet">Hello, {{ session['username'] }}</span>
          <a href="{{ url_for('logout') }}" class="nav-link">Logout</a>
        {% else %}
          <a href="{{ url_for('login') }}" class="nav-link">Login</a>
          <a href="{{ url_for('register') }}" class="nav-link">Register</a>
        {% endif %}
      </nav>
    </div>
  </header>

  <main class="container">
    <!-- Flash messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <div class="flash-wrapper">
          {% for category, message in messages %}
            <div class="flash flash-{{ category|lower }}">
              <span class="flash-message">{{ message }}</span>
              <button class="flash-dismiss" onclick="this.parentElement.style.display='none'">×</button>
            </div>
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}

    <!-- Page content -->
    <section class="content">
      {% block content %}{% endblock %}
    </section>
  </main>

  <footer class="site-footer">
    <div class="container">
      <small>© {{ (now().year if now is defined else "") }} MyApp</small>
    </div>
  </footer>
</body>
</html>

```
``templates/register.html``
```
{% extends "layout.html" %}
{% block title %}Register{% endblock %}

{% block content %}
  <h1 class="page-title">Create an account</h1>

  <form method="POST" class="form-card">
    <label for="username">Username</label>
    <input id="username" name="username" type="text" required>

    <label for="password">Password</label>
    <input id="password" name="password" type="password" required>

    <div class="form-actions">
      <button type="submit" class="btn btn-primary">Register</button>
      <a href="{{ url_for('login') }}" class="btn btn-link">Already have an account?</a>
    </div>
  </form>
{% endblock %}

```
``templates/login.html``
```
{% extends "layout.html" %}
{% block title %}Login{% endblock %}

{% block content %}
  <h1 class="page-title">Log in</h1>

  <form method="POST" class="form-card">
    <label for="username">Username</label>
    <input id="username" name="username" type="text" required>

    <label for="password">Password</label>
    <input id="password" name="password" type="password" required>

    <div class="form-actions">
      <button type="submit" class="btn btn-success">Login</button>
      <a href="{{ url_for('register') }}" class="btn btn-link">Create account</a>
    </div>
  </form>
{% endblock %}
```
`static/style.css`
```
/* Basic reset */
* { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; }

:root{
  --container-width: 900px;
  --accent: #2b7cff;
  --muted: #6b7280;
  --bg: #f7f8fb;
  --card: #ffffff;
  --danger: #ef4444;
  --success: #16a34a;
  --info: #0ea5e9;
}

/* Layout */
body {
  background: var(--bg);
  color: #111827;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  width: 92%;
  max-width: var(--container-width);
  margin: 0 auto;
  padding: 24px 0;
}

/* Header */
.site-header {
  background: var(--card);
  box-shadow: 0 1px 2px rgba(16,24,40,0.06);
  border-bottom: 1px solid rgba(16,24,40,0.04);
}
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}

.brand {
  font-weight: 700;
  color: var(--accent);
  text-decoration: none;
  font-size: 1.1rem;
}

.main-nav { display: flex; gap: 12px; align-items:center; }
.nav-link { text-decoration: none; color: var(--muted); font-size: 0.95rem; padding: 6px 8px; border-radius: 6px; }
.nav-link:hover { background: rgba(43,124,255,0.06); color: var(--accent); }

.greet { color: var(--muted); font-size: 0.95rem; margin-right: 8px; }

/* Flash messages */
.flash-wrapper { margin-bottom: 18px; display:flex; flex-direction:column; gap:10px; }
.flash {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 10px 12px;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(16,24,40,0.04);
  background: #fff;
  border: 1px solid rgba(16,24,40,0.04);
}
.flash-message { flex: 1; margin-right: 8px; font-size: 0.95rem; }
.flash-dismiss {
  background: transparent;
  border: none;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  color: var(--muted);
}

/* flash color variants */
.flash-success { border-color: rgba(22,163,74,0.15); background: rgba(22,163,74,0.05); color: #064e2b; }
.flash-danger  { border-color: rgba(239,68,68,0.15); background: rgba(239,68,68,0.05); color: #4c0505; }
.flash-info    { border-color: rgba(14,165,233,0.15); background: rgba(14,165,233,0.05); color: #063045; }

/* Content */
.page-title { font-size: 1.4rem; margin-bottom: 12px; color: #111827; }
.content { margin-top: 6px; }

/* Form card */
.form-card {
  display: grid;
  gap: 10px;
  padding: 18px;
  background: var(--card);
  border-radius: 10px;
  border: 1px solid rgba(16,24,40,0.04);
  max-width: 520px;
}
.form-card label { font-size: 0.9rem; color: var(--muted); }
.form-card input[type="text"],
.form-card input[type="password"],
.form-card input[type="email"],
.form-card textarea {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid rgba(16,24,40,0.08);
  font-size: 1rem;
  width: 100%;
  background: #fff;
}

/* Buttons */
.btn {
  display: inline-block;
  padding: 9px 14px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
}
.btn-primary { background: var(--accent); color: white; border-color: rgba(43,124,255,0.1); }
.btn-success { background: var(--success); color: white; border-color: rgba(22,163,74,0.08); }
.btn-link { background: transparent; color: var(--muted); text-decoration: none; padding-left: 8px; }
.form-actions { display:flex; gap:10px; align-items:center; margin-top:6px; }

/* Card */
.card {
  padding: 16px;
  border-radius: 10px;
  background: var(--card);
  border: 1px solid rgba(16,24,40,0.04);
}

/* Footer */
.site-footer {
  margin-top: auto;
  padding: 18px 0;
  text-align: center;
  color: var(--muted);
  font-size: 0.9rem;
}

```
### Rich Text and Pages
A wiki isn’t just about storing plain text; we also want users to format their writing with headings, bold text, lists, and more. This type of formatting is called **rich text**. The safest way to handle it is not by letting users write raw HTML (which could be dangerous), but by using **Markdown**, a simple text-based syntax. We can then convert the Markdown into HTML on the backend before displaying it.  
To make this work in Flask, we first install the `markdown2` library:  
`pip install markdown2`  
Inside our app, we add routes to view and create wiki pages. When someone visits a wiki page, we retrieve its content, convert it from Markdown to HTML, and then render it. When a user creates a new page, we store their Markdown text along with their username.
```
import markdown2

@app.route('/wiki/<page_name>')
def wiki_page(page_name):
    page = pages.get(page_name)
    if not page:
        return render_template('404.html'), 404
    
    page['html_content'] = markdown2.markdown(page['content'])
    return render_template('wiki_page.html', page=page, page_name=page_name)

@app.route('/create', methods=['GET', 'POST'])
def create_page():
    if 'username' not in session:
        flash('You must be logged in to create a page.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        page_name = request.form['title']
        content = request.form['content']
        pages[page_name] = {'content': content, 'author': session['username']}
        return redirect(url_for('wiki_page', page_name=page_name))
        
    return render_template('create_page.html')
```
In our `wiki_page.html` template, we must use the Jinja `| safe` filter so that the converted HTML is rendered properly. This tells Flask, “We trust this HTML because it was generated from Markdown.”
```
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

For creating new pages, we design a template with a form where users can enter a title and content in Markdown. To make things easier, we also add a quick reference card showing common Markdown syntax like headings, bold text, italics, and lists.
```
{% extends "layout.html" %}
{% block title %}Create Page{% endblock %}

{% block content %}
  <h1 class="page-title">Create a Wiki Page</h1>

  <form method="POST" class="form-card">
    <label for="title">Page Title</label>
    <input id="title" name="title" type="text" required>

    <label for="content">Content (Markdown supported)</label>
    <textarea id="content" name="content" rows="12" placeholder="# Heading
Write your text here...
- bullet list
**bold text**
*italic text*"></textarea>

    <div class="form-actions">
      <button type="submit" class="btn btn-primary">Create Page</button>
    </div>
  </form>

  <div class="card" style="margin-top:16px;">
    <h3>Markdown Quick Reference</h3>
    <ul>
      <li><code># Heading</code> → Heading</li>
      <li><code>**bold**</code> → <strong>bold</strong></li>
      <li><code>*italic*</code> → <em>italic</em></li>
      <li><code>- Item</code> → bullet list</li>
      <li><code>[Link](https://example.com)</code> → link</li>
    </ul>
  </div>
{% endblock %}
```
### Using CKEditor in Flask
While Markdown is simple, not everyone wants to learn a syntax. A more user-friendly option is **CKEditor**, which provides a visual text editor, much like a word processor. With CKEditor, users can style text directly, and the editor outputs HTML that we can store as-is. This means we no longer need to convert from Markdown.  
We start by installing Flask-CKEditor:  
`pip install flask-ckeditor`  
In our app, we initialize CKEditor and create a `PageForm` using Flask-WTF. The content field is now a `CKEditorField`, which gives us the rich text editor in the browser.
```
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

ckeditor = CKEditor(app)

class PageForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Create Page")

@app.route('/create', methods=['GET', 'POST'])
def create_page():
    if 'username' not in session:
        flash('You must be logged in to create a page.', 'danger')
        return redirect(url_for('login'))

    form = PageForm()
    if form.validate_on_submit():
        page_name = form.title.data
        content = form.content.data
        pages[page_name] = {'content': content, 'author': session['username']}
        return redirect(url_for('wiki_page', page_name=page_name))

    return render_template('create_page.html', form=form)

@app.route('/wiki/<page_name>')
def wiki_page(page_name):
    page = pages.get(page_name)
    if not page:
        return render_template('404.html'), 404
    return render_template('wiki_page.html', page=page, page_name=page_name)

```
The template for creating a page now uses the form fields from Flask-WTF. When we render `{{ form.content() }}`, CKEditor automatically appears.
```
{% extends "layout.html" %}
{% block content %}
  <h1>Create a Wiki Page</h1>
  <form method="POST">
      {{ form.hidden_tag() }}
      <div>
          {{ form.title.label }}<br>
          {{ form.title(size=40) }}
      </div>
      <div style="margin-top:12px;">
          {{ form.content.label }}<br>
          {{ form.content() }}
      </div>
      <div style="margin-top:12px;">
          {{ form.submit(class="btn btn-primary") }}
      </div>
  </form>
{% endblock %}

```
Finally, when viewing a wiki page, we don’t need Markdown conversion anymore. CKEditor already produces HTML, so we simply render it safely with the `| safe` filter:
```
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
### File Uploads
Now let’s take our application one step further and allow users to upload a profile picture, or avatar. Handling file uploads in Flask isn’t just about letting users select a file; we also need to make sure we process it securely and store it properly. There are three main steps we need to follow.  
First, we must update the HTML form so that it can actually handle file input. By default, forms only send text data, so for file uploads we need to add a special attribute: `enctype="multipart/form-data"`. Without this, the file will never reach our backend.  
Second, we have to configure Flask so it knows where files should be saved and which types of files we will allow. This ensures our app doesn’t accept every possible file type, which could be a big security risk.   
Finally, we need to write backend logic that processes the uploaded file, checks it against our allowed file types, and saves it to the server in a safe way.  
In our Flask application, we begin with configuration. We tell Flask which folder to use for saving profile pictures and which extensions are acceptable. For example, we may only allow `.png`, `.jpg`, `.jpeg`, and `.gif` files, since these are common image formats and we don’t want users uploading random or harmful files. We set this up in `app.py`:
```
UPLOAD_FOLDER = 'static/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
```
- Setup:
    - `UPLOAD_FOLDER` sets the specific directory (like `static/avatars`) where all images will be saved.
    - Crucial Step: This directory _must_ be created before running the app.
    - `ALLOWED_EXTENSIONS` is a list of approved file types (e.g., `.png`, `.jpg`) to restrict uploads.
- Request Handling:
    - The route immediately checks if the user is logged in; if not, it redirects them to the login page.
    - If the user is logged in, the app checks `request.files` to see if a file was included in the form submission.
    - If no file was selected, an error message is shown, and the page reloads.
- Validation and Saving:
    - A function (`allowed_file`) verifies that the file extension is one of the `ALLOWED_EXTENSIONS`.
    - The file's name is passed through `secure_filename()` to sanitize it, removing any malicious or problematic characters.
    - The file is saved to the final path within the `static/avatars` folder.
    - The user's database record is updated to store this new, safe filename.
    - Finally, a success message is flashed, and the profile page reloads.
    
```
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = users[username]

    if request.method == 'POST':
        if 'avatar' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['avatar']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            users[username]['avatar'] = filename
            flash('Avatar updated!', 'success')
            return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

```
On the frontend, we must not forget to update the form inside `profile.html`. For file uploads to work, the `<form>` tag needs an extra attribute:
```
{% extends "layout.html" %}

{% block content %}
  <div class="container">
    <h1>Welcome, {{ user['username'] }}</h1>

    <!-- Display flash messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul class="flashes">
          {% for category, message in messages %}
            <li class="flash {{ category }}">{{ message }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}

    <!-- Show current avatar if it exists -->
    <div class="avatar-section">
      {% if user.get('avatar') %}
        <img src="{{ url_for('static', filename='avatars/' ~ user['avatar']) }}" 
             alt="User Avatar" class="avatar">
      {% else %}
        <p>No avatar uploaded yet.</p>
      {% endif %}
    </div>

    <!-- File upload form -->
    <form action="{{ url_for('profile') }}" method="post" enctype="multipart/form-data">
      <label for="avatar">Upload new avatar:</label>
      <input type="file" id="avatar" name="avatar" accept="image/*" required>
      <button type="submit">Upload</button>
    </form>
  </div>
{% endblock %}
```
Notice the `enctype="multipart/form-data"`this is what allows files to be included in the request. Without it, the browser would only send the filename, not the file itself.
By following these steps, we give our users the ability to personalize their profiles with avatars, while also ensuring our app handles files safely and consistently.
### A Journey Through CSS Styling 
So far, our app looks functional but not very appealing. To understand styling, let’s look at how web design has evolved through three major phases.
#### Act I: The Specific Approach (Class-per-Element)
When we first start writing CSS, it feels natural to style each element with its own dedicated class. If we have a login button, we might call it `.login-page-button` and directly assign all of its properties background color, text color, padding, border radius, and so on. At first, this seems perfectly fine, because each element gets the exact style we want. However, the problem quickly appears when we need another button, like a register button, that looks the same. Since our styles are tied to a specific element name, we have to create a new class, such as `.register-page-button`, and copy all the styles over. This means we are repeating ourselves, which makes our CSS harder to maintain. If we ever decide to change the padding or the color of our buttons, we would have to update multiple classes in multiple places, which is inefficient and error-prone.

```
/* style.css */
.login-page-button {
  background-color: blue;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
}
```

```
<button class="login-page-button">Login</button>
```

**Problem**: What if we want a similar button on the register page? We'd have to create a new class, `register-page-button`, and copy all the styles. This is not DRY.
#### Act II: The Reusable Component (Shared Classes)
To solve this problem, we shift our thinking toward reusability. Instead of creating a brand-new class for each button on the site, we create a shared **component class** that captures what makes a button a button. For example, we might have a class `.btn` that defines padding and border-radius, and then we add another class like `.btn-primary` that gives the button its specific background and text color. Now, whether we are on the login page or the register page, we can use the same combination of `.btn btn-primary` to style both buttons. This change means we are no longer writing styles for each individual element, but rather describing a reusable piece that we can apply anywhere. By thinking in terms of components, we keep our CSS DRY (Don’t Repeat Yourself) and make updates much easier—if we want to change all our buttons, we only update the `.btn` class. This idea of building reusable pieces is the foundation behind frameworks like Bootstrap, which give us ready-made components like buttons, cards, alerts, and navbars.  
``CSS``
```
/* style.css */
.btn {
  padding: 10px 20px;
  border-radius: 5px;
}
.btn-primary {
  background-color: blue;
  color: white;
}
```
``HTML``
```
<button class="btn btn-primary">Login</button>
<button class="btn btn-primary">Register</button>
```
This is much better! We've created a reusable "button" component. This is the core idea behind frameworks like **Bootstrap**. We think in terms of components: cards, alerts, navbars, etc.
#### Act III: The Utility-First Revolution
What if we take this one step further? Instead of a `.btn-primary` class that sets three CSS properties, what if we had a class for each property?
- `bg-blue-500` sets the background color.
- `text-white` sets the text color.
- `p-4` sets the padding.
- `rounded-md` sets the border-radius.


These small, single-purpose classes are called **utility classes**. We are no longer inventing component names; we are building the look of our element directly in the HTML by combining utilities. We are creating our own mini styling library.  
This is the revolutionary idea behind **Tailwind CSS**.
