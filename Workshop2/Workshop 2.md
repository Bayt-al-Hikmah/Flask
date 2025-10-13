## Objectives

- Render HTML templates instead of simple strings or JSON.
- Serve static files like CSS and images.
- Use the Jinja2 templating engine for dynamic content (variables, loops, conditions).
- Create reusable page layouts with template inheritance.
- Understand and use Flask's request hooks and decorators to process requests.
- Handle user input with HTML forms, both manually and with the Flask-WTF library.
- Add CSRF Protection to our forms.

## Rendering Basic HTML Templates
In our previous session, we returned simple strings from our routes. While perfect for APIs, most web applications need to display rich, structured content. To achieve this, we use HTML templates.  
A template is an HTML file where we can embed dynamic data before sending it to the user's browser. This approach keeps our application's logic (written in Python) separate from its presentation (written in HTML), making our code cleaner and easier to maintain.
### The `templates` Folder
Flask, by convention, looks for templates in a folder named `templates`. This folder should be in the root directory of our project, alongside our main `app.py` file.  
Our project structure should now look like this:  
```
my_flask_project/
├── static/           # For static files, added later
├── templates/
│   └── index.html
├── venv/             # Virtual environment
├── app.py
└── requirements.txt
```

### Using `render_template()`
To serve an HTML template, we use Flask's `render_template()` function. Flask comes bundled with the **Jinja2** templating engine, which is powerful and lets us embed Python-like expressions directly in our HTML files.     
First, we start by creating our virtual environment as we did in the previous lecture. Then, we install Flask using `pip install Flask`. After that, we create our app as follows:  
We start by creating `templates` Folder, this folder will store our templates, Then after this we create our first template the `index.html` template.  
**`templates/index.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My First Template</title>
</head>
<body>
    <h1>Welcome to Our Website!</h1>
    <p>This page was rendered from a Flask template using Jinja2.</p>
</body>
</html>
```
After that, we create the `app.py` file, which will contain our application logic.  
**`app.py`**
```python
from flask import Flask, render_template

app = Flask(__name__)
  
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=3000,debug=True)
```
This time, we import an additional function called `render_template` from `flask`. This function is responsible for returning templates (HTML files) as responses when a user visits a specific route. In our example, when the user visits the main route `/`, the `home` function returns `render_template('index.html')`. This means Flask will look for a template named `index.html` inside the `templates` folder and send it as a response to the user’s request.
## Working with Static Files
A website isn’t complete without styling, images, or client-side JavaScript. These are called **static files**. In Flask, we serve them from a folder conventionally named `static`. Flask is pre-configured to automatically serve files from this folder.   
Our updated project structure:
```
my_flask_project/
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/
│       └── logo.png
├── templates/
│   └── index.html
├── app.py
...
```
### Serving Static Files
To link a static file in a template, we use the `url_for()` function. This function generates the correct URL for the file, which is more robust than hardcoding the path.  
Let’s create a CSS file and link it.  
**`static/css/style.css`:**  
```CSS
body {
    font-family: sans-serif;
    background-color: #f0f2f5;
    color: #333;
    text-align: center;
    margin-top: 50px;
}
```
Update **`templates/index.html`** to include the CSS,  using `url_for()`:
```Html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Styled Page</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <h1>Welcome to Our Styled Website!</h1>
    <p>This page is now styled with an external CSS file.</p>
</body>
</html>
```
The `url_for()` function takes two key arguments here:
1. **The Endpoint**: The first argument, `'static'`, is the name of the special endpoint that Flask automatically creates for serving files,
2. **The `filename`**: This keyword argument is the path to our file relative to the `static` folder.

Restart the server and visit `http://127.0.0.1:3000`. The page will now be styled.

### Why Use `url_for()`?

Using a direct path like `<link rel="stylesheet" href="/static/css/style.css">` might seem simpler, but it can easily break.

1. **Application Root Path**: If we deploy our app to a subdirectory, say `https://example.com/my-app/`, a hardcoded path like `/static/...` would point to `https://example.com/static/...`, which is wrong. The browser wouldn't find our files. `url_for()` is smart enough to generate the correct path, like `/my-app/static/...`, because it knows where our application is running.

2. **Cross-Platform Consistency**: While web URLs always use forward slashes (`/`), file systems on different operating systems don't. A path on Windows might be `static\css\style.css`, while on macOS or Linux it's `static/css/style.css`. By abstracting this away, `url_for()` ensures that our code generates a valid web path no matter what system we develop or deploy on.
## Introduction to Jinja2 Templating
Flask uses **Jinja2** as its templating engine, which lets us embed Python-like code directly in HTML. It's simple yet powerful, allowing us to add variables, conditionals, and loops.  
Jinja2 has two key delimiters: 
- `{{ ... }}`: For expressions to print to the template output (e.g., a variable's value).
- `{% ... %}`: For statements like `if` conditions or `for` loops.
### Passing Data to Templates
We can pass Python variables from our route to our template as keyword arguments in the `render_template()` function. Once inside the template, we can not only display these variables but also modify them using filters.    
Filters are applied using the pipe `|` symbol and act like functions that transform the data right before it's displayed. Some common filters include:

- `{{ my_string | capitalize }}`: Capitalizes the first letter.
- `{{ my_list | length }}`: Returns the number of items in a list.
- `{{ my_variable | default('fallback value') }}`: Shows a default value if the variable is missing or empty.
- `{{ my_html_string | safe }}`: Renders a string as raw HTML (use with caution!).

We create new route `profile/<username>` that will display the  username capitalized when we visit it.    
First we create new template called ``profile.html`` that will display the user profile.  
**`templates/profile.html`**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>User Profile</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <h1>Hello, {{ name|capitalize }}!</h1>
</body>
</html>
```
After this we add the new route to our ``app.py`` file.   
**`app.py`**
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/profile')
@app.route('/profile/<username>')
def profile(username = "World"):
    return render_template('profile.html', name=username)
  

if __name__ == '__main__':
    app.run(port=3000,debug=True)
```
Here, we created two routes: `/profile` and `/profile/<username>`. Both routes are handled by the same function, `profile()`, which accepts an optional argument `username` with a default value of `"World"`.

When a user visits the URL `/profile/<username>`, Flask captures the value from the URL and stores it in the `username` parameter. This value is then passed to the `profile.html` template as a variable named `name`.  
Inside the template, we can access it using `{{ name }}`.  
for example, `<h1>Hello, {{ name|capitalize }}!</h1>` will display a personalized greeting such as **“Hello, Alice!”**.

If the user visits `/profile` without providing a username, the function uses the default value `"World"`, and the page will display **“Hello, World!”**.
### Conditional Statements (`if`, `else`)
Jinja lets us add  decision-making logic directly into our HTML templates. This allows us to show different content based on the data we receive from our Python code.    
**How It Works**:  
- `{% if condition %}`: Checks if a condition is true.
- `{% elif another_condition %}`: Optional additional conditions.
- `{% else %}`: Optional fallback.
- `{% endif %}`: Required to close the block.


**Example**: A dashboard route with different messages.  
We create the new template `dashboard.html`  
**`templates/dashboard.html`:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>User Dashboard</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="welcome-message">
        {% if user_status == 'admin' %}
            <h1>Welcome, Administrator!</h1>
            <p>You have full access to the system controls.</p>
        {% elif user_status == 'member' %}
            <h1>Welcome, Valued Member!</h1>
            <p>Thank you for being a part of our community.</p>
        {% else %}
            <h1>Welcome, Guest!</h1>
            <p>Please sign up or log in to access member features.</p>
        {% endif %}
    </div>
</body>
</html>
```
In the dashboard template, we first check whether the `user_status` is **admin**. If it is, we display the message **“You have full access to the system controls.”**    
If the user is not an admin, we use an `elif` condition to check whether they are a **member**. In that case, we display a special message: **“Thank you for being a part of our community.”**  
Finally, if the user is neither an admin nor a member, we use an `else` condition as a fallback to display the message **“Please sign up or log in to access member features.”**
Now lets add the new route to our ``app.py``  
**`app.py`**
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/profile')
@app.route('/profile/<username>')
def profile(username = "World"):
    return render_template('profile.html', name=username)

@app.route('/dashboard')
@app.route('/dashboard/<status>')
def dashboard(status = ""):
    return render_template('dashboard.html', user_status=status)

if __name__ == '__main__':
    app.run(port=3000,debug=True)
```
Just like in the profile example, we created two routes: `/dashboard` and `/dashboard/<status>`, both handled by the same function.    
If the user provides a status in the URL (for example, `/dashboard/admin`), the function captures it and displays the appropriate content based on that status.    
If the user doesn’t provide a status and simply visits `/dashboard`, the `status` parameter will use its default value (`""`), and the page will treat the user as a guest.
### Loops (`for`)
Jinja2 loops let us iterate over lists, dictionaries, or other iterables and display them in our template.  
**How It Works**:
- `{% for item in items %}`: Iterates over `items`, making each element available as `item`.
- `{% else %}`: An optional block that runs if the list is empty.
- `{% endfor %}`: Required to close the loop.
    

**Example**: Displaying a task list.   
We create new templates called `tasks.html`  
**`templates/tasks.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Tasks</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <h1>My To-Do List</h1>
    <ul>
        {% for task in tasks %}
            <li>{{ task }}</li>
        {% else %}
            <li>You have no tasks. Great job!</li>
        {% endfor %}
    </ul>
</body>
</html>
```
Here, we created a **for loop** that iterates over a list of tasks. For each iteration, the current item is stored in a variable called `task`, and its value is displayed inside an `<li></li>` element.   
The `else` block handles the case when the tasks list is empty, displaying the message `<li>You have no tasks. Great job!</li>` to the user.    
Next, we update the `app.js` file to add and configure the new route.  
**`app.js`**
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/profile')
@app.route('/profile/<username>')
def profile(username = "World"):
    return render_template('profile.html', name=username)

@app.route('/dashboard')
@app.route('/dashboard/<status>')
def dashboard(status = ""):
    return render_template('dashboard.html', user_status=status)

@app.route('/tasks')
def tasks():
    task_list = [
        'Buy groceries',
        'Finish Flask workshop',
        'Go for a run'
    ]
    return render_template('tasks.html', tasks=task_list)
    
if __name__ == '__main__':
    app.run(port=3000,debug=True)
```
The new route is handled by the `tasks()` function.    
Inside this function, we define a variable called `task_list`, which contains a list of tasks. This list is then passed to the `tasks.html` template under the label `tasks`, allowing us to display each task dynamically in the template.
### Template Inheritance
Most websites share a consistent layout. Copying the header and footer into every template is inefficient. Jinja2’s **template inheritance** is a powerful feature that solves this elegantly. We create a base layout and then "extend" it in other templates.  
Create a base layout file:   
**`templates/layout.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Awesome App</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header>
        <nav>
            <a href="/">Home</a> |
            <a href="#">About</a> |
            <a href="#">Contact</a>
        </nav>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>
        <p>&copy; 2025 Our Company</p>
    </footer>
</body>
</html>
```
Now, update **`templates/index.html`** to inherit from this layout:
```
{% extends "layout.html" %}

{% block content %}
    <h1>Welcome to Our Website!</h1>
    <p>This page was rendered from a Flask template and uses a base layout.</p>
{% endblock %}
```

The `{% extends "layout.html" %}` line tells Jinja2 to use `layout.html` as the base. The content inside the `{% block content %}` ... `{% endblock %}` tags will be injected into the corresponding block in the parent template. This keeps our code DRY (Don’t Repeat Yourself) and makes site-wide changes incredibly easy.   
**``app.py``**
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
    
if __name__ == '__main__':
    app.run(port=3000,debug=True)
```
### Including Template Snippets with `{% include %}`
While `extends` is for the whole page structure, `{% include %}` is for inserting smaller, reusable **snippets** of HTML. It’s like copying and pasting a piece of another file. This is perfect for components like a navigation bar, a sidebar, or a specific card element that appears on multiple pages.  

Let's extract our navigation and footer into a separate file.
**`templates/partials/_navbar.html`:**
```html
<nav>
    <a href="{{ url_for('home') }}">Home</a> |
    <a href="#">About</a> |
    <a href="#">Contact</a>
</nav>
```
**`templates/partials/_footer.html`:**
```html
    <footer>
        <p>&copy; 2025 Our Company</p>
    </footer>
```
Now, we update our `layout.html` to use `include` instead of having the nav code directly inside it.
**`templates/layout.html`**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Awesome App</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header>
        {% include 'partials/_navbar.html' %}
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
	    {% include 'partials/_footer.html' %}
    </body>
</html>
```

By combining `extends` for our main layout and `include` for our reusable components, we can build complex, maintainable web pages with very little repeated code.
### The `routes` Folder
As our application grows, we may notice that having many routes in the same file makes the code harder to manage and maintain especially as we add more logic to each route.  
To solve this, it’s a good practice to organize our routes using **Blueprints** instead of keeping them all in `app.py`.  
A **Blueprint** allows us to group related routes and their logic together, helping keep our main application file clean, modular, and easier to maintain.

We’ll create a folder named `routes` and move our routes logic there.
```
my_flask_project/
├── routes/
│   └── main.py
│   └── profile.py
│   └── tasks.py
│   └── dashboard.py
├── static/
├── templates/
│   └── index.html
│   └── tasks.html
│   └── dashboard.html
│   └── layout.html
│   └── partials/
│       └── _footer.html
│       └── _navbar.html
├── venv/
├── app.py
└── requirements.txt
```
We start by creating our first route Blueprint to handel the `/` route .    
**`routes/main.py`:**
```python
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('index.html')
```
Here, instead of importing `Flask`, we import the `Blueprint` class. We then create a new instance of it named `main_bp`, using the arguments `'main'` and `__name__`, The first argument `'main'` is the name of the Blueprint, and `__name__` helps Flask locate resources such as templates and static files associated with it.  
After creating the Blueprint object, we define the routes it will handle just as we did before by using the `@route` decorator and writing functions to handle each route.  
We the same way we declare the rest of the Blueprints
**`routes/profile.py`:**
```python
from flask import Blueprint, render_template

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@profile_bp.route('/profile/<username>')
def profile(username="World"):
    return render_template('profile.html', username=username)
```
**`routes/dashboard.py`:**
```python
from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/dashboard/<status>')
def dashboard(status = ""):

    return render_template('dashboard.html', user_status=status)
```
**`routes/tasks.py`:**
```python
from flask import Blueprint, render_template

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks')
def tasks():
    task_list = [
        'Buy groceries',
        'Finish Flask workshop',
        'Go for a run'
    ]
    return render_template('tasks.html', tasks=task_list)
```
Next we edit the templates, the `templates/_layout.html` ,`templates/partials/_footer.html` and `templates/index.html` stay same we edit the rest.  
**`templates/partials/_navbar.html`**
```html
<nav>
    <a href="{{ url_for('main.home') }}">Home</a> |
    <a href="#">About</a> |
    <a href="#">Contact</a>
</nav>
```
Here, we updated the URL for our main page (`/`) using `url_for()` to generate it dynamically. We pass as an argument the name of the Blueprint that defines the route, followed by the name of the function that handles it.   
**`templates/profile.html`**
```html
{% block content %}
    <h1>Hello, {{ username|capitalize }}!</h1>
{% endblock %}
```
**`templates/dashboard.html`**
```html
{% extends "layout.html" %}
{% block content %}
    <div class="welcome-message">
        {% if user_status == 'admin' %}
            <h1>Welcome, Administrator!</h1>
            <p>You have full access to the system controls.</p>
        {% elif user_status == 'member' %}
            <h1>Welcome, Valued Member!</h1>
            <p>Thank you for being a part of our community.</p>
        {% else %}
            <h1>Welcome, Guest!</h1>
            <p>Please sign up or log in to access member features.</p>
        {% endif %}
    </div>
{% endblock %}
```
**`templates/tasks.html`**
```html
{% block content %}
    <h1>My To-Do List</h1>
    <ul>
        {% for task in tasks %}
            <li>{{ task }}</li>
        {% else %}
            <li>You have no tasks. Great job!</li>
        {% endfor %}
    </ul>
{% endblock %}
```
Now we edit our ``app.py`` To use those Blueprints.  
**`app.py`:**
```python
from flask import Flask
from routes import main,profile,tasks,dashboard

app = Flask(__name__)

  

# Register the blueprint with the main app
app.register_blueprint(main.main_bp)
app.register_blueprint(profile.profile_bp)
app.register_blueprint(tasks.tasks_bp)
app.register_blueprint(dashboard.dashboard_bp)

if __name__ == '__main__':
    app.run(debug=True, port=3000)
```
In our main `app.py`, we import and **register** the blueprint using `app.register_blueprint(main_bp)`. This connects all the routes defined in our blueprint to the main application.  
Run the app with `python app.py`, then visit `http://127.0.0.1:3000` in your browser. You’ll see a fully rendered HTML page.  
## Processing Requests with Decorators and Hooks
Before we dive into creating forms, let’s explore a key concept in Flask: **decorators** and **request hooks**. These are Python features that allow us to run code before or after a request is handled.
### What are Decorators and Hooks?
In Flask, we can "wrap" our route functions with decorators to add functionality. Request hooks are special decorators that register a function to run at specific points in the request-handling process. They have access to global objects like `request`.  
Common hooks include:
- `@app.before_request`: Runs before each request, regardless of the route.
- `@app.after_request`: Runs after each request if no exceptions were raised.
- `@app.teardown_request`: Runs at the very end of a request, even if there were exceptions.

Think of them as checkpoints: a request passes through the `before_request` checkpoint, then hits the route function, and finally passes through the `after_request` checkpoint.
### How Hooks Work
We define a hook by decorating a function. Here’s a simple example of a hook that logs the request method and URL:
```python
from flask import request
import time

@app.before_request
def log_request_info():
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] {request.method} {request.path}')
```
If we add this to `app.py`, every time we visit a page, we will see a log entry in our terminal. Unlike route functions, these hook functions don't need to return anything.    
Hooks can also modify the flow. For example, this hook could block a request:  
```python
from flask import request, abort

@app.before_request
def block_ip():
    if request.remote_addr == '192.168.1.100':
        abort(403)
```
### Why Hooks Matter
Hooks are what make Flask so extensible. They allow us to:
- Add cross-cutting functionality like logging, authentication, or database connections.
- Process requests before they reach routes (e.g., checking user permissions).
- Reuse code across the entire app.

## Handling HTML Forms
Forms are how users send data to our server. We’ll explore handling forms manually and then with the powerful **Flask-WTF** library for validation.

### The Basic Python Way
We'll create a contact form and process its data using Flask's `request` object.  
First we create the ``contact.html`` template  
**`templates/contact.html`**
```html
{% extends "layout.html" %}
{% block content %}
<h1>Contact Us</h1>
<form action="/contact" method="POST">
    <label for="name">Name:</label><br>
    <input type="text" id="name" name="name" required><br><br>
    <label for="message">Message:</label><br>
    <textarea id="message" name="message" required></textarea><br><br>
    <button type="submit">Submit</button>
</form>

{% if submitted_name %}
    <h2>Thanks for your message, {{ submitted_name }}!</h2>
{% endif %}
{% endblock %}
```
Now we create new Blueprint that handel submitted contact form  
**``routes/contact.py``**
```python
from flask import Blueprint, render_template, request

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    submitted_name = None
    if request.method == 'POST':
        name = request.form.get('name')
        message = request.form.get('message')
        print(f'Received message from {name}: {message}')
        submitted_name = name

    return render_template('contact.html', submitted_name=submitted_name)
```
Here, we first add a new import `request` from Flask. This allows us to access data sent by the user through forms.    
In our route definition, we specify the `methods` parameter as `['GET', 'POST']`, meaning this route can handle both **GET** requests (when the user simply opens the page) and **POST** requests (when the user submits the form).  
Inside the function, we check if the request method is `'POST'`. If it is, that means the user has submitted the form. We then retrieve the values of `name` and `message` from the form using `request.form.get()`, print them in the console, and store the submitted name in the variable `submitted_name`.  
Finally, we render the `contact.html` template, passing `submitted_name` to it so we can display it back to the user.    
If the user just opens the page (a **GET** request), the `if` block will be skipped, and the page will simply load the form without any submitted data.  
### The Flask-WTF Way
Handling forms manually with `request.form` works for simple cases, but as your application grows, it quickly becomes repetitive and error-prone. You have to manually check whether fields are empty, validate input formats, and implement security measures like CSRF protection yourself.  
To make this process easier and safer, Flask provides an extension called **Flask-WTF**, which integrates seamlessly with the **WTForms** library. WTForms is a flexible Python library for building and validating web forms. Flask-WTF acts as a bridge between Flask and WTForms, giving you a clean and powerful way to handle form input.  
Flask-WTF offers several advantages:  
- **CSRF Protection** Automatically includes a hidden security token in every form to prevent Cross-Site Request Forgery attacks.
- **Built-in Validation** Allows you to define validation rules directly in your form classes (e.g., required fields, email format, maximum length).
- **Cleaner Code** – Separates form logic (Python code) from form presentation (HTML templates), keeping your project organized.
- **Reusable Forms**  Define a form once in Python and reuse it across multiple templates or routes.


To install Flask-WTF, run the following command:
```shell
pip install Flask-WTF email-validator
```
We Also install another pachage that will help us to verify that the email input provided in a form is valid. It ensures the entered text follows a proper email format (like user@example.com).  
```shell
pip install email-validator
```
With Flask-WTF, each form is represented as a Python class that inherits from `FlaskForm`. Each field is an object with its own label, validation rules, and HTML rendering behavior, we define a form class in a new `forms.py` file.   

**`utils/forms.py`:**
```python
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Submit')
```

This class defines our form fields and attaches **validators** to them, which automatically check the input data.
- `StringField` creates a single-line text input field.
- `TextAreaField` creates a multi-line text box for longer messages.
- `SubmitField` generates the submit button.
- `DataRequired()` ensures that the field is not left empty.
- `Email()` validates that the input is in a proper email format.
- `Length(min=3, max=25)` ensures the input has at least 3 characters and no more than 25 characters.

Now, we edit the t Blueprint that handel submitted contact form 
```python
from utils.forms import ContactForm
from flask import Blueprint,redirect,render_template,url_for

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
```
We update our **Blueprint** to handle the submitted contact form. We start by importing the `ContactForm` class and creating a form instance inside the route. The route accepts both `GET` and `POST` requests: when accessed through a **GET** request, it simply renders the contact form, and when accessed through a **POST** request, it processes the submitted data.   
The `form.validate_on_submit()` method is a powerful shortcut provided by **Flask-WTF** it automatically checks whether the current request is a POST and then runs all the validators we defined in our `ContactForm` class, such as `DataRequired`, `Email`, and `Length`. If all validations pass, it returns `True`.   
Inside the `if` block, we access the submitted data using `form.field_name.data` (for example, `form.name.data` and `form.message.data`), print it for verification, and then redirect the user back to the `/contact` page. If the request is a **GET** or if validation fails, the route renders the `contact.html` template again, passing the form object so that the template can display errors or repopulate the input fields as needed.  
#### CSRF Protection
A CSRF (Cross-Site Request Forgery) attack is a type of web security vulnerability where a malicious website tricks a user’s browser into performing an unwanted action on another website where the user is already authenticated for example, submitting a form or changing account details without their consent. This happens because browsers automatically include session cookies with every request, even if it’s triggered by a third-party site.

To protect against this, **Flask-WTF** automatically includes a hidden **CSRF token** in every form. This token is a unique, random value generated for each session and verified on every POST request. If a request doesn’t include a valid token, Flask will reject it effectively blocking any cross-site request forgery attempts.  

To configure it we add `app.config['SECRET_KEY'] = 'a-very-secret-key'` to our ``app.py``. The `SECRET_KEY` is used internally by Flask and Flask-WTF to sign and validate CSRF tokens, ensuring that only requests originating from the legitimate form on our website are accepted. In a real-world application, this key should be a long, randomly generated string and never hard-coded in your source code. Instead, it should be stored securely, such as in an environment variable or a configuration file that’s not shared publicly.
**`app.py`**
```python
from flask import Flask
from routes import main,profile,tasks,dashboard,contact

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secret-key'

# Register the blueprints

app.register_blueprint(main.main_bp)
app.register_blueprint(profile.profile_bp)
app.register_blueprint(tasks.tasks_bp)
app.register_blueprint(dashboard.dashboard_bp)
app.register_blueprint(contact.contact_bp)

if __name__ == '__main__':
    app.run(debug=True, port=3000)
```
Finally we edit the contact template   
**`templates/contact.html`:**
```html
{% extends "layout.html" %}
{% block content %}
<h1>Contact Us</h1>
<form method="POST" action="">
    {{ form.hidden_tag() }}
        {{ form.name.label }}
        {{ form.name(size=30) }}
        <br>
        {% for error in form.name.errors %}
        <div>
            <span style="color: red;">{{ error }}</span>
        </div>
        {% endfor %}
        {{ form.email.label }}
        {{ form.email(size=30) }}
        <br>
        {% for error in form.email.errors %}
        <div>
            <span style="color: red;">{{ error }}</span>
            </div>
        {% endfor %}
        {{ form.message.label }}<br>
        {{ form.message(rows=5, cols=32) }}
        <br>
        {% for error in form.message.errors %}
        <div>
            <span style="color: red;">{{ error }}</span>
        </div>
        {% endfor %}
    {{ form.submit() }}
    {% if submitted_name %}
        <h2>Thanks for your message, {{ submitted_name }}!</h2>
    {% endif %}
</form>
{% endblock %}
```
Inside the `<form>`, `{{ form.hidden_tag() }}` automatically includes the hidden **CSRF token** for security. Each field (name, email, and message) is displayed with its label and input element, followed by an error loop that shows validation messages in red if the user submits invalid data.

Finally, `{{ form.submit() }}` creates the submit button, and if the form was successfully submitted, a thank-you message appears using the `submitted_name` variable.
## Task
In this project, you will build a **Quote Sharing Web Application** using Flask and Jinja2.  
The application will allow users to:
- Submit quotes anonymously by providing the author’s name and the quote text.
- Browse all submitted quotes in a styled interface.
- Search for quotes by a specific author.
- Use reusable layouts and static assets for a consistent design.
### Functional Requirements
#### Homepage (`/`)
- Displays a welcome message.
- Shows a list of all submitted quotes dynamically from a Python list or dictionary.
- Uses a Jinja2 `for` loop to render the quotes.

#### Quote Submission (`/share`)
- Provides a form (using `Flask-WTF`) with two fields:
    - Author name (`StringField`).
    - Quote text (`TextAreaField`).
- Validates input:
    - Author name must be at least 3 characters.
    - Quote must not exceed 300 characters.
- Displays validation error messages next to the fields.
- Includes automatic CSRF protection.
- On successful submission, adds the quote to the list and redirects back to the homepage.

#### Search Quotes (`/search`)
- Provides a simple form to enter an author’s name.
- On submission, displays all quotes from that author.
- If no quotes are found, shows a message: “No quotes found for this author.”
#### Layouts and Partials
- Create a `layout.html` with a header, footer, and a `{% block content %}` section.
- Create a `_navbar.html` partial and use `{% include '_navbar.html' %}` in your layout. The navbar should link to Home, Share Quote, and Search.
- Ensure all pages extend the main layout.