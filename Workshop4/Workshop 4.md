### Objectives
- Using Hashed Password and Decorator for Authentication 
- Introduce **SQLite** as a simple, file-based database.
- Interact with a database using raw SQL, then with a simple class, and finally with an **ORM (SQLAlchemy)**.
### Hashed Passwords and Authentication 
When we start building applications, authentication is one of the first challenges we face. In simple prototypes, we sometimes just store usernames and passwords in plain text, but this is dangerous and not scalable. Instead, we should always aim for an optimal and secure approach. Let’s walk through the important points.
#### Hashing Passowrd
If we save user passwords directly in our database, anyone who gains access to the database can see them. This is a serious risk because people often reuse the same password across different accounts. The safer approach is to store only a hashed version of the password.  
Hashing means we apply a one-way mathematical function to the password so that even we, as developers, cannot recover it. When a user logs in, we hash the entered password and compare it to the stored hash. If they match, the login succeeds.
In Flask, the recommended library for this is `werkzeug.security`, which provides:
- `generate_password_hash(password)` → to create a secure hash.
- `check_password_hash(hash, password)` → to verify login attempts.

Now lets Use the ``generate_password_hash(password)`` and ``check_password_hash(hash, password)`` , to create our Login and Register route
```
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super-secret-key"

# In-memory user store
users = {}  # {username: password_hash}

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        # Hash the password before saving
        password_hash = generate_password_hash(password)
        users[username] = password_hash

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username not in users:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

        stored_hash = users[username]
        if check_password_hash(stored_hash, password):
            session["user"] = username  # temporary way of tracking login
            flash("Logged in successfully!", "success")
            return redirect(url_for("profile"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

```
And here we can create the profile route that user can visit only if he logged in
```
@app.route("/profile")
def profile():
    if "user" not in session:
        flash("You need to log in first.", "warning")
        return redirect(url_for("login"))
    return f"Welcome {session['user']}! This is your profile."
```
At this point, we have working authentication with hashed passwords.
#### Protecting Routes with Decorators
So far, our login system works: once a user logs in, we store their details in the session and can check this before showing sensitive pages like the profile. But imagine we have multiple routes that require login a profile page, a dashboard, a settings page, maybe even a “create post” form. If we keep writing the same `if "user" not in session:` logic inside every route, our code will quickly become repetitive and harder to maintain. This goes against the principle of DRY (Don’t Repeat Yourself), which tells us to avoid duplicating the same code in multiple places.  
The cleaner and more scalable solution is to use a **decorator**. A decorator is like a wrapper that we can attach to any route function. Before the route itself runs, the decorator can perform checks for example, “is the user logged in?” If the check passes, the route runs normally. If it fails, the decorator can stop the request and redirect the user to the login page.  
Here’s how we can write one for authentication:  
```
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("You must log in to access this page.", "danger")
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view
```
Now, instead of repeating the login check in every route, we simply attach the decorator with one line:
```
@app.route("/profile")
@login_required
def profile():
    return "This is your profile page."
```
With this approach, any user who tries to access `/profile` without being logged in will be automatically redirected to the login page. More importantly, if we add new protected routes later, we don’t need to rewrite any logic we just reuse the same `@login_required` decorator. This makes our code much cleaner, easier to maintain, and consistent across the entire app.
### Working with SQLite
So far we stored our users in Python dictionaries right inside `app.py`. This worked perfectly... until we restarted the server. The moment our Flask app stopped, all our hard work every new user, every wiki page vanished forever.    
This is because dictionaries store data in RAM (Random Access Memory), which is volatile. It's temporary memory that gets wiped clean when the power is turned off. For any real application, we need a way to store data persistently, meaning it survives even when our application isn't running.  
This is why we need a **database**.  
A database is a structured system for storing, managing, and retrieving data. There are many powerful databases like PostgreSQL and MySQL, but for getting started, we'll use **SQLite**.  
**Why SQLite?**
- **Serverless**: It doesn't require a separate server process to be running.
- **File-Based**: An entire SQLite database is stored in a single file on our machine (e.g., `database.db`).
- **Built-in**: It comes standard with Python, so there's nothing extra to install.

It's the perfect choice for learning, development, and small to medium-sized applications.
#### Creating the Database
Let’s create a schema for our database. This defines the structure of our tables.
**`schema.sql`:**
```
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

```
We run:  
`sqlite3 database.db < schema.sql`
#### Connect Flask with SQLite
Python comes with a built-in library called `sqlite3` that lets us talk to SQLite directly. We connect to the database, run SQL commands, and then close the connection.    
We start by connecting to our database with:   `conn = sqlite3.connect("database.db")`, This opens a connection to the file `database.db`. If the file doesn’t exist yet, SQLite will create it for us.
Next, we create a cursor: `cur = conn.cursor()` The cursor is like our tool for navigating the database. It lets us send commands (SQL queries) and read results, Once we have the cursor, we can start running commands using `cur.execute()`. For example:
`cur.execute("SELECT * FROM user WHERE username = ?", (username,))`  
Notice the `?` inside the SQL statement. This is a placeholder for values we pass in separately. By writing `(username,)`, we safely plug the value into the query. This approach is much safer than string formatting because it protects us from **SQL injection attacks**.  
When we run a query that returns data, we can fetch results in two main ways:
- `fetchone()` → gets the first row of the result.
- `fetchall()` → gets all the rows at once.
So the full flow is: connect then create cursor then execute a command then fetch results and finally close the connection when we’re done.
If we want to add data we use the `ÌNSERT` command, after each insert and delete we need to use ``curs.commit()`` to permanently save the changes to the disk
The `app.py` as following
```
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super-secret-key"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        # Check if username already exists
        cur.execute("SELECT * FROM user WHERE username = ?", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            flash("Username already exists!", "danger")
            conn.close()
            return redirect(url_for("register"))

        # Hash password and insert into database
        password_hash = generate_password_hash(password)
        cur.execute("INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, password_hash))
        conn.commit()
        conn.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM user WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()

        if user is None:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

        if check_password_hash(user["password"], password):
            session["user_id"] = user["id"]  # safer than storing the username
            session["username"] = user["username"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("profile"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")
```
#### Refactoring with a User Class
So far, our logic works we can register users, log them in, and talk to the database. But we quickly notice a problem: we are **mixing Python with raw SQL** directly inside our routes. Every time we want to add a new feature, like checking if a user exists or creating a new one, we end up writing `cur.execute(...)` again and again.  
This creates two big issues. First, it breaks the **DRY principle** (Don’t Repeat Yourself). If we need the same query in multiple routes, we repeat it everywhere, which makes the code harder to maintain. Second, it ties our route logic too closely with database details, so the business logic (what the app does) gets mixed with the data logic (how it’s stored).  
The better way is to **encapsulate** database operations inside classes. Each class represents a table (`User`, `Snippet`, etc.), and each method inside that class handles one operation, like finding a user by username or creating a new record. This way, our routes only call clean Python methods, while the SQL stays hidden in one place. The code becomes cleaner, easier to maintain, and closer to how big frameworks like SQLAlchemy.
```
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super-secret-key"

class User:
    @staticmethod
    def create(username, password):
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        password_hash = generate_password_hash(password)
        cur.execute("INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, password_hash))
        conn.commit()
        conn.close()

    @staticmethod
    def find_by_username(username):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM user WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()
        return user

# --- Routes ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.find_by_username(username):
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        User.create(username, password)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.find_by_username(username)
        if user is None or not check_password_hash(user["password"], password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash("Logged in successfully!", "success")
        return redirect(url_for("profile"))
    return render_template("login.html")
```
#### Using SQLAlchemy and Models
The approach with classes already gave us a cleaner separation of concerns. But we still write `SELECT`, `INSERT`, and `DELETE` statements manually, which means our Python and SQL are still somewhat mixed. If we want to change the database engine later (say from SQLite to PostgreSQL), we’d have to rewrite many queries.  
This is where **SQLAlchemy** comes in. SQLAlchemy is an **ORM** (Object Relational Mapper). With an ORM, each table in our database is represented as a Python **model class**, and each row is an object of that class. Instead of writing SQL by hand, we work with Python methods and attributes, while SQLAlchemy takes care of generating the correct SQL under the hood.   
Now our `app.py` become:
```
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# --- Flask setup ---
app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- User model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# --- Routes ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        # create new user
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user"] = user.username
            flash("Logged in successfully!", "success")
            return redirect(url_for("profile"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))
```
This is much cleaner: our routes only deal with Python objects, and SQLAlchemy generates all the SQL for us.  
With this approach, if our team grows, database engineers can define the models and relationships (e.g., between `User` and `Snippet`), while backend engineers only interact with the models as if they were normal Python classes. It’s more maintainable, easier to read, and robust enough to handle scaling to larger projects.
### Restucturing Our Project
So far, our project works, but if we look closely at `app.py`, everything is mixed in one place. We have routes, raw SQL or ORM code, helper logic, and even session handling all inside the same file. This might be fine for a very small demo, but the problem shows up as soon as the project grows.  
For example, say we add posts, comments, or file uploads. Each new feature adds more routes, more database queries, and more helper functions. Before long, `app.py` turns into a giant, messy file that’s hard to read, test, or maintain. We also repeat ourselves because the same database logic may appear in multiple routes, breaking the DRY principle.  
This is why larger projects separate responsibilities into different files. Each part of the project should have a clear job: one place for models, one for routes, one for helpers. That way, backend developers can focus on building routes, database engineers can shape the models, and no one has to scroll through hundreds of lines of mixed code just to make a small change.
#### A cleaner structure
Here’s a simple but much cleaner way to organize the project:
```
project/
│
├── app.py             # main entry point, routes live here
├── models.py          # database models (User, Post, etc.)
├── utils.py           # helper functions like login_required
├── templates/         # HTML templates
│   ├── login.html
│   ├── register.html
│   └── profile.html
└── static/            # CSS, JS, images

```
#### app.py
This is the main entry point. It creates the Flask app, sets the configuration, connects the database, and defines the routes. But importantly, it doesn’t contain the heavy logic anymore. Instead, it just _uses_ models and helpers from other files.
#### models.py
All database-related code lives here. We define each table as a class (`User`, `Post`, `Comment`, etc.). Each class encapsulates its own logic, like hashing a password or verifying credentials. This makes the database layer reusable and consistent.
#### utils.py
This file holds helper functions and decorators. A good example is `login_required`, which checks if a user is logged in before letting them access certain routes. Keeping these in one place avoids repeating the same checks inside every route.
#### templates/
This folder holds our HTML pages. Flask automatically looks here when we call `render_template()`. Separating templates makes it easy for frontend developers to work on the design without touching Python code.
#### static/
This is where we put CSS files, JavaScript, and images. Flask serves them as static assets, and they stay separate from both logic and templates.