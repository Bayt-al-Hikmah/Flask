### Objectives
- Render HTML templates instead of simple strings or JSON.
- Serve static files like CSS and images.
- Use the Jinja2 templating engine for dynamic content (variables, loops, conditions).
- Create reusable page layouts with template inheritance.
- Handle user input with HTML forms, both manually and with the Flask-WTF library.
### Rendering Basic HTML Templates
In our last session, we returned simple strings and JSON from our routes. While that's great for APIs, most web applications need to display rich, structured content to users. To do this, we use HTML templates.  
A template is just an HTML file that we can inject dynamic data into before sending it to the user's browser. This approach allows us to separate our application's logic (in Python) from its presentation (in HTML), which makes our code much cleaner and easier to manage.
#### The `templates` Folder
Flask is designed to look for HTML files in a specific folder named `templates`. We must create this folder in the root directory of our project, at the same level as our `app.py` file.  
Our project structure should now look like this:
```
my_flask_project/
├── static/          # We will add this later
├── templates/
│   └── index.html
├── venv/
└── app.py
```
#### Using `render_template()`
To serve an HTML file, we use Flask's built-in `render_template()` function. This function finds the specified file in our `templates` folder, renders it, and sends it back as a response.  
Let's modify our `app.py` and create a simple template.
**`templates/index.html`:**
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My First Template</title>
</head>
<body>
    <h1>Welcome to Our Website!</h1>
    <p>This page was rendered from a Flask template.</p>
</body>
</html>
```
**`app.py`:**
```
# Import render_template from flask
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # Instead of returning a string, we now render a template
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```
Now, when we run our app and visit the home page, we'll see our fully rendered HTML page instead of just plain text.
### Working with Static Files
 A website isn't complete without styling, images, and maybe some JavaScript. These files are called **static files** because they don't change. Just like with templates, Flask expects these files to be in a specific folder called `static`.    
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
└── app.py
```
#### Linking Static Files with `url_for()`
We can't just use a direct path like `static/css/style.css` in our HTML because it's not reliable. Instead, we let Flask generate the correct URL for the file. For this, we use the powerful `url_for()` function.  
The `url_for()` function takes two key arguments here:
1. **The Endpoint**: The first argument, `'static'`, is the name of the special endpoint that Flask automatically creates for serving files from our `static` folder.
2. **The `filename`**: This keyword argument is the path to our file _relative to the `static` folder_.


So, `url_for('static', filename='css/style.css')` tells Flask: "Find the URL for the static file endpoint, and then append the path to `css/style.css`."  
Let's create a simple CSS file and link it.  
**`static/css/style.css`:**
```
body {
    font-family: sans-serif;
    background-color: #f0f2f5;
    color: #333;
    text-align: center;
    margin-top: 50px;
}

img {
    width: 150px;
    border-radius: 10px;
}
```
Now, we'll update `index.html` to include our CSS and an image.
**`templates/index.html`:**
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Styled Page</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Our Logo">
    <h1>Welcome to Our Styled Website!</h1>
    <p>This page is now styled with an external CSS file.</p>
</body>
</html>
```
#### Why is `url_for()` better than a direct path
Using a direct path like `<link rel="stylesheet" href="/static/css/style.css">` might seem simpler, but it can easily break.
1. **Application Root Path**: If we deploy our app to a subdirectory, say `https://example.com/my-app/`, a hardcoded path like `/static/...` would point to `https://example.com/static/...`, which is wrong. The browser wouldn't find our files. `url_for()` is smart enough to generate the correct path, like `/my-app/static/...`, because it knows where our application is running.
2. **Cross-Platform Consistency**: While web URLs always use forward slashes (`/`), file systems on different operating systems don't. A path on Windows might be `static\css\style.css`, while on macOS or Linux it's `static/css/style.css`. By abstracting this away, `url_for()` ensures that our code generates a valid web path no matter what system we develop or deploy on.


By using `url_for()`, we write more robust and portable code, ensuring that Flask always generates the correct path to our files, no matter how our application is configured or deployed
### Introduction to Jinja2 Templating
Flask uses a powerful templating engine called **Jinja2**. Jinja allows us to embed programming logic directly into our HTML files, making them truly dynamic.  
Jinja has two main types of syntax:
- `{{ ... }}`: For **expressions**, used to print a variable or the result of an expression to the template.
- `{% ... %}`: For **statements**, like conditionals (`if`/`else`) and loops (`for`).
#### Passing Data to Templates
We can pass Python variables from our route to our template as keyword arguments in the `render_template()` function. Once inside the template, we can not only display these variables but also modify them using **filters**.  
Filters are applied using the pipe `|` symbol and act like functions that transform the data right before it's displayed. Some common filters include:
- `{{ my_string | capitalize }}`: Capitalizes the first letter.
- `{{ my_list | length }}`: Returns the number of items in a list.
- `{{ my_variable | default('fallback value') }}`: Shows a default value if the variable is missing or empty.
- `{{ my_html_string | safe }}`: Renders a string as raw HTML (use with caution!).


**`app.py`:**
```
@app.route('/profile/<name>')
def profile(name):
    # Let's create a dictionary for user details
    user_details = {
        'username': name,
        'bio': 'Loves coding in Python and exploring new technologies.',
        'shopping_list': ['Apples', 'Oranges', 'Bananas']
    }
    # Pass the entire dictionary to the template
    return render_template('profile.html', user=user_details)
```
Now, we'll create a new template, `profile.html`, to display this data using expressions, control structures, and filters.
**`templates/profile.html`:**
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>User Profile</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <h1>Hello, {{ user.username | capitalize }}!</h1>
    <p><em>{{ user.bio }}</em></p>

    {% if user.shopping_list %}
        <p>You have {{ user.shopping_list | length }} item(s) on your shopping list:</p>
        <ul>
            {% for item in user.shopping_list %}
                <li>{{ item }}</li>
            {% endfor %}
        </ul>
    {% else %}
        <p>Your shopping list is empty!</p>
    {% endif %}
</body>
</html>
```
If we visit `/profile/alice`, Jinja will dynamically render the page, capitalizing her name and showing the count of her shopping list items.
#### Conditional Statements (`if`, `elif`, `else`)
Think about how we make decisions in real life. We might think, "**If** it's sunny, I'll wear sunglasses. **Else if** it's raining, I'll take an umbrella. **Else** (if it's neither), I'll just wear a hat."  
Jinja lets us add this same decision-making logic directly into our HTML templates. This allows us to show different content based on the data we receive from our Python code.  
**How It Works**
The structure is very straightforward and must always be closed with `{% endif %}`.
- `{% if condition %}`: This checks if a condition is true. The condition could be checking if a variable exists, if a number is greater than another, or if a user is logged in.
- `{% elif another_condition %}`: This is an optional "else if" check. We can have as many `elif` blocks as we need. It's only checked if the first `if` was false.
- `{% else %}`: This is also optional. The code inside this block runs if all the preceding `if` and `elif` conditions were false.
- `{% endif %}`: This is **required** to tell Jinja where the conditional block ends.

**Example**  
Let's create a route that passes a user's status to a template and displays a different welcome message for each status.
**`app.py`:**
```
@app.route('/dashboard/<status>')
def dashboard(status):
    return render_template('dashboard.html', user_status=status)
```
**`templates/dashboard.html`:**
```
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
Now, if we visit `/dashboard/admin`, we'll see the admin message. If we go to `/dashboard/member`, we get the member message, and for any other value like `/dashboard/visitor`, we'll see the guest message.
#### Loops (`for`)
A `for` loop is our tool for repeating a task. Imagine we have a list of groceries. To create a shopping list, we would go through each item one-by-one and write it down. A `for` loop does exactly that with data. It's perfect for displaying lists of users, products, blog posts, or anything else.  
**How It Works**  
The structure is `{% for item in my_list %}` and it must always be closed with `{% endfor %}`.
- `{% for item in my_list %}`: This tells Jinja to go through `my_list`. In each iteration, the current item from the list will be available in a temporary variable called `item`. We can name this variable anything we want (e.g., `product`, `user`, `post`).
- `{% endfor %}`: This is **required** to mark the end of the loop.

A great feature of Jinja's `for` loop is that it can also have an `{% else %}` block. The code in this block will only run if the list we are trying to loop over is empty.  
**Example**  
Let's create a page that displays a list of tasks.
**`app.py`:**
```
@app.route('/tasks')
def show_tasks():
    # A list of tasks we want to display
    task_list = [
        "Buy groceries",
        "Finish Flask workshop",
        "Go for a run"
    ]
    # We can also test with an empty list: task_list = []
    return render_template('tasks.html', tasks=task_list)
```
**`templates/tasks.html`:**
```
{% extends "layout.html" %}
{% block content %}
    <h1>My To-Do List</h1>
    <ul>
        {% for current_task in tasks %}
            <li>{{ current_task }}</li>
        
        {% else %}
            <li>You have no tasks. Great job!</li>

        {% endfor %}
    </ul>
{% endblock %}
```
This code will create a clean HTML list of all our tasks. If we pass an empty list from `app.py`, it will neatly display the "You have no tasks" message instead of just showing an empty list.
### Template Inheritance 
Most websites have a consistent layout a common header, footer, and navigation bar on every page. It would be inefficient to copy and paste this code into every single template. This is where template inheritance comes in.  
We can create a base layout template and then have other templates "extend" it, only filling in the parts that are unique to each page.  
First, we create our base layout file.  
**`templates/layout.html`:**
```
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
            <a href="{{ url_for('home') }}">Home</a> |
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
The key here is the `{% block content %}{% endblock %}` block. This defines a section that child templates can override.  
Now, we can simplify our `index.html` to extend this layout.  
**`templates/index.html` (updated):**
```
{% extends "layout.html" %}

{% block content %}
    <h1>Welcome to Our Website!</h1>
    <p>This page was rendered from a Flask template and uses a base layout.</p>
{% endblock %}
```
This is a much cleaner and more maintainable way to build multi-page applications.
#### Including Template Snippets with `{% include %}`
While `extends` is for the whole page structure, `{% include %}` is for inserting smaller, reusable **snippets** of HTML. It’s like copying and pasting a piece of another file. This is perfect for components like a navigation bar, a sidebar, or a specific card element that appears on multiple pages.  
Let's extract our navigation into a separate file.
**`templates/partials/_navbar.html`:** 
```
<nav>
    <a href="{{ url_for('home') }}">Home</a> |
    <a href="#">About</a> |
    <a href="#">Contact</a>
</nav>
```
Now, we update our `layout.html` to use `include` instead of having the nav code directly inside it.
**`templates/layout.html`**
```
<!DOCTYPE html>
<html lang="en">
<body>
    <header>
        {% include 'partials/_navbar.html' %}
    </header>

    <main>
        {% block content %}{% endblock %}
    </main>
    
    </body>
</html>
```
By combining `extends` for our main layout and `include` for our reusable components, we can build complex, maintainable web pages with very little repeated code.
### Handling HTML Forms
Forms are the primary way we get input from users. Let's see how to handle form submissions in Flask.
#### The Basic HTML Way
We can handle forms using standard HTML and Flask's `request` object.  
First, let's create a contact page with a form.
**`templates/contact.html`:**
```
{% extends "layout.html" %}
{% block content %}
    <h1>Contact Us</h1>
    <form action="{{ url_for('contact') }}" method="POST">
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
Next, we create the route in `app.py`. This route needs to handle both `GET` requests (to display the form) and `POST` requests (to process the submitted data).
**`app.py`:**
```
from flask import Flask, render_template, request

# ... (keep existing code) ...

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    submitted_name = None
    # Check if the request method is POST (i.e., the form was submitted)
    if request.method == 'POST':
        # Access form data using request.form, which is a dictionary-like object
        name = request.form['name']
        message = request.form['message']
        print(f"Received message from {name}: {message}")
        submitted_name = name
    
    return render_template('contact.html', submitted_name=submitted_name)
```
#### The Flask-WTF Way 
Handling forms manually with `request.form` works, but it quickly becomes repetitive and error-prone. We have to check if fields are empty, validate input formats, and add security measures like CSRF protection ourselves. To avoid all this boilerplate, Flask provides an extension called Flask-WTF, which integrates with the WTForms library. This makes form handling much more secure, maintainable, and readable.
##### Why Use Flask-WTF
Flask-WTF offers several advantages:
- **CSRF Protection**: Every form includes a hidden token that prevents cross-site request forgery attacks.
- **Built-in Validation**: Define rules directly with each field (e.g., required, email format, max length).
- **Cleaner Code**: Separate form definitions (in Python) from form rendering (in HTML).
- **Reusable Forms**: Define a form once and reuse it across different templates.
##### Installation
We install Flask-WTF using:
```pip install Flask-WTF```
##### Configure the Application
Flask-WTF requires a secret key to sign the CSRF token. Without this, form submissions will fail.
`app.config['SECRET_KEY'] = 'a-very-secret-key'`
In a production application, we use a long random string and load it from a secure source such as an environment variable.
##### Defining a Form Class
With Flask-WTF, each form is represented as a Python class that inherits from `FlaskForm`. Each field is an object with its own label, validation rules, and HTML rendering behavior.
```
from flask_wtf import FlaskForm 
from wtforms import StringField, TextAreaField, SubmitField 
from wtforms.validators import DataRequired  
class ContactForm(FlaskForm):     
	name = StringField('Name', validators=[DataRequired()])     
	message = TextAreaField('Message', validators=[DataRequired()])     
	submit = SubmitField('Submit')`
```
Here:
- `StringField` creates a text input field.
- `TextAreaField` creates a multi-line text box.
- `SubmitField` creates a submit button.
- `validators=[DataRequired()]` ensures the field is not left empty.
##### Handling the Form in a Route
In the route function, we create an instance of the form and check whether it was submitted and passed validation.
```

@app.route('/contact-wt', methods=['GET', 'POST']) 
def contact_wt():
    form = ContactForm()
    submitted_name = None      
    if form.validate_on_submit():         
	    submitted_name = form.name.data         
	    message = form.message.data         
	    print(f"Received from {submitted_name}: {message}")          
	    # Clear form fields after submission         
	    form.name.data = ''         
	    form.message.data = ''      
	return render_template('contact_wt.html', form=form, submitted_name=submitted_name)
```
The method `validate_on_submit()` is a shortcut that checks:
1. The request method is `POST`.
2. All form validators pass successfully.

This saves us from writing multiple `if` conditions to validate inputs manually.
##### Rendering the Form in Templates
Rendering forms is also simplified. Each field object can generate its HTML input element when called in the template.
```
{% extends "layout.html" %}
{% block content %}
    <h1>Contact Us (WTForms)</h1>
    <form method="POST" action="">
        {{ form.hidden_tag() }}  {# Adds CSRF protection token automatically #}

        {{ form.name.label }}<br>
        {{ form.name(size=30) }}<br><br>

        {{ form.message.label }}<br>
        {{ form.message(rows=5, cols=30) }}<br><br>

        {{ form.submit() }}
    </form>

    {% if submitted_name %}
        <h2>Thanks for your message, {{ submitted_name }}!</h2>
    {% endif %}
{% endblock %}
```
Important details:
- `form.hidden_tag()` renders hidden fields, including the CSRF token.
- `form.name.label` renders the `<label>` element.
- `form.name()` renders the `<input>` field, and extra HTML attributes can be passed in (e.g., `size=30`).

##### Displaying Validation Errors
If validation fails, Flask-WTF stores error messages in `form.<field>.errors`. These can be displayed in the template:
```
<p>
    {{ form.name.label }}<br>
    {{ form.name() }}
    {% for error in form.name.errors %}
        <span style="color:red;">{{ error }}</span>
    {% endfor %}
</p>
```
If the user submits the form without filling in the name, the error message will be shown next to the field.
##### Using More Validators
Flask-WTF supports many built-in validators. We can combine them for stricter rules:
```
from wtforms.validators import DataRequired, Email, Length

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Submit')
```
- `Length(min=3, max=25)` ensures the name has a reasonable length.
- `Email()` ensures the input is in a valid email format.
- `Length(max=200)` prevents excessively long messages.