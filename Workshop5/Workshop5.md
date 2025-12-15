## Objectives
- Understanding the shift from Server-Side Rendering to APIs.
- Building REST API with Flask
## Shifting from Server-Side Rendering to APIs.
### Introduction
In our past workshops, our apps used server-side rendering. With this approach, each request returned an entire HTML page. The problem is that every time we triggered an action in the web app or navigated to a new URL, the server re-rendered the whole page. This means we ended up downloading the full HTML again, even when only a small part of the page had changed.

This is referred to as a “Hotwire-like” approach, and while it works, it can slow down the application. Often, we only need to retrieve a small piece of data and update a specific section of the page, rather than reloading everything.

To fix this, we can use an API to send and receive small chunks of data and update just the required parts of the interface.
### API
API (**Application Programming Interface**) is a layer that we add to our web app to connect the frontend with the backend. Our app uses the API to retrieve and send data to the server. The backend receives the data, saves the results, processes whatever is needed, and then returns the updated information to the frontend.   
APIs make it easier to extend our application and make it available on platforms other than the browser. For example, if we want to build a mobile application for our web app, we only need to create the user interface and connect it to our web server using the API. The same backend logic and data can be reused without any changes.

![](./api.png)


### Javascript Role
To use the API in our web application, we rely on JavaScript.  
JavaScript handles communication with the server by fetching data from the API and then dynamically updating the DOM to reflect that data.

Now, instead of submitting a full form and reloading the page, we can let the user type in an input field, click a button, and then:
1. **Catch the click event** with JavaScript
2. **Send a request** to the API    
3. **Receive the response** from the server
4. **Update the DOM** using the data from the response


This way, only the necessary part of the page changes, and our app becomes much faster and smoother.
### REST API Architecture
There are many patterns to design APIs for our web apps, but the most common and beginner friendly one is the REST API.  
REST stands for Representational State Transfer. It is named this way because the server sends a representation of the requested resource usually as JSON, and the client is responsible for handling the state of the application on its side. 
### REST Main Properties
REST APIs are defined by several **mandatory constraints** that help achieve scalability, simplicity, and performance in a web service.
#### Stateless
Each request sent to the server must contain all the information needed to process it. The server does not store any information about previous requests. 
#### Client–Server Separation
The frontend and backend are separated.  
The frontend focuses only on the user interface and user experience, while the backend handles data storage and business logic. 
#### URLs Identify Resources
REST treats everything as a resource (users, tasks, posts, products, etc.).  
Each resource is identified by a clear and meaningful URL, for example:
- `/tasks`
- `/users/1`
#### Use of Standard HTTP Methods
REST relies on standard HTTP methods to describe actions instead of custom commands:
- **GET** Retrieve data
- **POST** Create new data
- **PUT / PATCH** Update existing data
- **DELETE** Remove data

By following these conventions, REST APIs remain predictable, easy to understand, and consistent across different applications.
## Building REST API with Flask
Now that we understand how REST APIs work, we will apply these concepts by building a Task Management REST API.

The API will be responsible for registering users, authenticating logins, updating user profiles (including name and profile picture), and displaying, editing, and deleting tasks associated with each user.
### Setting Our Envirenment
We start by creating a virtual environment to isolate our project dependencies.
```shell
python -m venv env
# use python3 on macOS and Linux
```
Then, we activate the virtual environment.
```shell
# Windows
.\env\Scripts\activate

# macOS / Linux
source env/bin/activate
```
### Installing Packages
After setting up our virtual environment, it’s time to install the packages required for our application.

For this project, we will use **Flask** as the web framework, Flask-Session for session management, SQLAlchemy for database interaction, and Flask-RESTful to simplify the creation of REST APIs with the Flask framework.
```shell
pip install flask flask-session sqlalchemy flask-restful flask-sqlalchemy argon2-cffi dotenv
```
### Creating Database Models 
Now we move to creating our database models. we only need two core models: the **User** model and the **Task** model.

The User model represents application users and stores their basic information such as username, password, email, and avatar. The Task model represents tasks created by users, including details like task name, description, creation time, and current state (active or done).

There is a one-to-many relationship between users and tasks:
- A user can have many tasks
- Each task belongs to exactly one user

We will use **SQLAlchemy**  to define our models, we create models folder inside it we define our classes, we start by creating ``__init__.py`` file
```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```
After that we difine the User model

**``models/User.py``**
```python
from models import db
from sqlalchemy.orm import Mapped

class User(db.Model):
    __tablename__ = 'users'
    id: Mapped[int]  = db.Column(db.Integer, primary_key=True)
    username: Mapped[str] = db.Column(db.String(80), unique=True, nullable=False)
    email: Mapped[str] = db.Column(db.String(120), unique=True, nullable=False)
    password: Mapped[str] = db.Column(db.String(255), nullable=False)
    avatar: Mapped[str] = db.Column(db.String(255), nullable=True)
    tasks = db.relationship('Task', backref='user', lazy=True)
```
**User Model**
- `id`: Primary key that uniquely identifies each user
- `username`: Unique username for login and identification
- `email`: User email address (also unique)
- `password`: Stores the hashed password (never store plain text passwords)
- `avatar`: Optional field to store a profile picture URL or file path

The `tasks` attribute defines a one-to-many relationship, allowing us to access a user’s tasks using `user.tasks`.

Finally we create the task model

**``models/Task.py``**
```python
from sqlalchemy.orm import Mapped
from models import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'tasks'
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    state: Mapped[str]  = db.Column(db.String(20), default='active')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
```
**Task Model**
- `id`: Primary key for each task
- `name`: Task title
- `description`: Optional detailed description of the task
- `created_at`: Timestamp automatically set when the task is created
- `state`: Represents the task status (`active` or `done`)

The `user_id` field is a foreign key that links each task to its owner. This ensures that every task belongs to a valid user.

### Initialize The Database
After defining our models, we need to initialize the database so that SQLAlchemy can create the corresponding tables.  To do this, we create a new file named **`index.py`** with the following code:  

**`index.py`**
```python
from app import app, db

with app.app_context():
    db.create_all()
```
This script imports the Flask application and the SQLAlchemy instance from `app.py`, then runs `db.create_all()` inside the application context.   

Running this script once will automatically generate the **users** and **tasks** tables in our `database.db` file based on the models we defined earlier.
### Building the REST API
Now it’s time to build our REST API to connect our application with the server and the database. The RESTful API exposes resources as endpoints, allowing the frontend to communicate with our backend using standard HTTP methods.

For this project, we will work with two main resources:
- **Users** responsible for managing user-related actions such as updating username, password, email, and avatar.    
- **Tasks**  responsible for creating, reading, updating, and deleting tasks that belong to authenticated users.

All task-related actions require the user to be logged in. We track authentication state using **Flask-Session**, and the API itself is built using the Flask-RESTful package.
#### Initial API Setup
We start by configuring Flask, SQLAlchemy, Flask-Session, and Flask-RESTful.

**``app.py``**
```python
import os
from dotenv import load_dotenv
from flask import Flask
from flask_session import Session
from datetime import timedelta
from models import db
from flask_restful import Api
load_dotenv()

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.getenv('SESSION_SECRET'),
    SESSION_TYPE='filesystem',           
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
    SESSION_COOKIE_SECURE=True,            
    SESSION_COOKIE_HTTPONLY=True,         
    SESSION_COOKIE_SAMESITE='Lax'          

)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
Session(app)
api = Api(app)
```
In this setup, we prepare the basic parts of our Flask application. We load environment variables, We configured Flask-Session to manage user login sessions and set simple security options for cookies. After that, we connected SQLAlchemy to a SQLite database and initialize it. Finally, we create a Flask-RESTful API instance, which we will use to build our API endpoints.

#### Creating API Resources
Now let’s start creating our API resources. We begin with the authentication resources, which are responsible for handling user registration and login. These resources manage how users create accounts, authenticate themselves, and start a session with the application.

**``api/Auth.py``**
```python
from flask import request, session
from flask_restful import Resource
from models import db
from models.User import User
from argon2 import PasswordHasher

ph = PasswordHasher()

class RegisterResource(Resource):
    def post(self):
        data = request.get_json()
        user = User(
            username=data['username'],
            email=data['email'],
            password=ph.hash(data['password']),   
            avatar=data.get('avatar')
        )

        db.session.add(user)
        db.session.commit()
        return {"message": "User registered successfully"}, 201


class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        try:
            verified = ph.verify(user.password , data['password'])
        except:
            verified = False
        if not user or not verified :
            return {"message": "Invalid email or password"}, 401
        session['user_id'] = user.id
        return {"message": "Login successful"}, 200
```
We defined two authentication API resources using **Flask-RESTful**. Both resources inherit from the `Resource` class and implement the `post` method to handle incoming POST requests.

The `RegisterResource` receives user data in JSON format from the request, creates a new `User` object, saves it to the database, and returns a JSON response confirming successful registration.

The `LoginResource` also receives JSON data from the API request. It searches for the user in the database using the provided email and checks if the password matches. If the credentials are correct, the user’s ID is stored in the session to mark them as logged in, and a success message is returned. If the credentials are invalid, the API returns an error message with a **401 (Unauthorized)** status code.

After that we register our routes by adding the following code to our ``app.py``
```python
api.add_resource(RegisterResource, '/api/register')
api.add_resource(LoginResource, '/api/login')
```
These resources will run on the following routes:
- **POST `/api/register`** Register a new user
- **POST `/api/login`** Log in an existing user


Now that authentication is in place, we can move on to the **User resource**. This resource is responsible for managing user-related actions **after the user is logged in**.

Through the User resource, a logged-in user can view their profile information, update their username or email, change their password, and update their avatar. All these actions require authentication, so the user must have an active session before accessing these endpoints.

**``api/User.py``**
```python
from flask import request, session
from flask_restful import Resource
from models import db
from models.User import User
from argon2 import PasswordHasher

ph = PasswordHasher()

def require_login():
     return 'user_id' in session


class UserResource(Resource):
     def get(self):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          user = User.query.get(session['user_id'])
          return {
               "id": user.id,
               "username": user.username,
               "email": user.email,
               "avatar": user.avatar
          }, 200

     def put(self):
          if not require_login():
               return {"message": "Unauthorized"}, 401

          user = User.query.get(session['user_id'])
          data = request.get_json()
          user.username = data.get('username', user.username)
          user.email = data.get('email', user.email)
          user.avatar = data.get('avatar', user.avatar)
          db.session.commit()
          return {"message": "User profile updated successfully"}, 200

     def patch(self):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          user = User.query.get(session['user_id'])
          data = request.get_json()
          user.password = ph.hash(data['password'])
          db.session.commit()
          return {"message": "Password updated successfully"}, 200
```
As before here we defined a **User API resource** . This resource inherits from the `Resource` class and provides multiple HTTP methods to manage the logged-in user’s profile.

The `get` method retrieves the current user’s information from the database using the user ID stored in the session and returns it as a JSON response.

The `put` method allows the logged-in user to update their profile data, such as username, email, and avatar. Only the provided fields are updated, while the rest remain unchanged.

The `patch` method is used to update sensitive data, such as the user’s password. This action also requires the user to be authenticated.

After that, we register the resource by adding the following code to our `app.py`:
```python
api.add_resource(UserResource, '/api/user')
```
This resource will run on the following route:
- **GET `/api/user`** Retrieve the logged-in user’s profile
- **PUT `/api/user`** Update username, email, or avatar
- **PATCH `/api/user`** Change the user’s password

Finally, we create the **Task resource**, which is responsible for managing all task-related actions in our application. This resource allows a logged-in user to create new tasks, view their existing tasks, update task information, and delete tasks.

Each task is linked to the currently authenticated user using the session, ensuring that users can only access and modify their own tasks. All task endpoints are protected, so the user must be logged in before performing any task operation.

**``api/Tasks.py``**
```python
from flask import request, session
from flask_restful import Resource
from models import db
from models.Task import Task


def require_login():
     return 'user_id' in session

class TaskListResource(Resource):
     def get(self):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          tasks = Task.query.filter_by(user_id=session['user_id']).all()
          return [
               {
                    "id": task.id,
                    "name": task.name,
                    "state": task.state,
                    "created_at": task.created_at.isoformat()
               }
               for task in tasks
          ], 200

     def post(self):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          data = request.get_json()
          task = Task(
               name=data['name'],
               user_id=session['user_id']
          )
          db.session.add(task)
          db.session.commit()
          return {"message": "Task created successfully"}, 201

class TaskResource(Resource):
     def put(self, task_id):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          task = Task.query.filter_by(
               id=task_id,
               user_id=session['user_id']
          ).first()
          if not task:
               return {"message": "Task not found"}, 404
          data = request.get_json()
          task.name = data.get('name', task.name)
          task.state = data.get('state', task.state)
          db.session.commit()
          return {"message": "Task updated successfully"}, 200

     def delete(self, task_id):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          task = Task.query.filter_by(
               id=task_id,
               user_id=session['user_id']
          ).first()
          if not task:
               return {"message": "Task not found"}, 404
          db.session.delete(task)
          db.session.commit()
          return {"message": "Task deleted successfully"}, 200
```
We defined two task-related API resources using **Flask-RESTful**. 

The `TaskListResource` handles operations on multiple tasks.    
The `get` method retrieves all tasks that belong to the logged-in user, while the `post` method creates a new task and links it to the current user using the session.

The `TaskResource` handles operations on a single task.    
The `put` method updates task data such as name, description, or state, and the `delete` method removes a task from the database. In both cases, the task is first checked to ensure it belongs to the logged-in user.
We register them as following
```python 
api.add_resource(TaskListResource, '/api/tasks')
api.add_resource(TaskResource, '/api/tasks/<int:task_id>')
```
These resources will run on the following routes:
- **GET `/api/tasks`** Retrieve all tasks for the logged-in user
- **POST `/api/tasks`** Create a new task
- **PUT `/api/tasks/<task_id>`** Update an existing task
- **DELETE `/api/tasks/<task_id>`** Delete a task

### Creating The Interface
Now that our API is fully functional, we need a user interface to interact with it. Instead of the server rendering HTML pages for every route, we will serve a single HTML file (Single Page Application approach) and use JavaScript to fetch data from our API and update the DOM dynamically.
#### Serving the Entry Point
We need to update our `app.py` to serve the `index.html` file when a user visits the root URL.

**`app.py`**
```python

# ... existing code ... 
@app.route('/') 
def index(): 
	return render_template('index.html') 

if __name__ == '__main__': 
	app.run(debug=True)
```
Now, when you visit `http://127.0.0.1:5000/`, Flask will serve the HTML file, and the rest of the application interaction will happen via JavaScript calling our API endpoints.
#### The HTML Structure
We will create a simple interface with two main sections: a **Login** section and a **Dashboard** section. Initially, the dashboard will be hidden.

**`templates/index.html`**
```html
<!DOCTYPE html>

<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Manager API</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>

    <div class="container">
        <div id="login-view">
            <div class="auth-header">
                <h2>Welcome Back</h2>
                <p>Please login to manage your tasks.</p>
            </div>
            <form id="login-form">
                <div class="form-group">
                    <input type="email" id="login-email" placeholder="Email Address" required>
                </div>
                <div class="form-group">
                    <input type="password" id="login-password" placeholder="Password" required>
                </div>
                <button type="submit" class="btn-primary">Log In</button>
            </form>
            <p class="auth-switch">
                Don't have an account? <a href="#" onclick="showRegister()">Register here</a>
            </p>
            <p id="login-message" class="error-msg"></p>
        </div>
        <div id="register-view" style="display:none;">
            <div class="auth-header">
                <h2>Create Account</h2>
                <p>Join us to get organized.</p>
            </div>
            <form id="register-form">
                <div class="form-group">
                    <input type="text" id="reg-username" placeholder="Username" required>
                </div>
                <div class="form-group">
                    <input type="email" id="reg-email" placeholder="Email Address" required>
                </div>
                <div class="form-group">
                    <input type="password" id="reg-password" placeholder="Password" required>
                </div>
                <div class="form-group">
                    <label for="reg-avatar" class="file-label">Upload Profile Picture (URL or File)</label>
                    <input type="text" id="reg-avatar-url" placeholder="Paste Image URL">
                    </div>
                <button type="submit" class="btn-primary">Sign Up</button>
            </form>
            <p class="auth-switch">
                Already have an account? <a href="#" onclick="showLogin()">Login here</a>
            </p>
            <p id="register-message" class="error-msg"></p>
        </div>
        <div id="app-view" style="display:none;">
            <nav class="app-nav">
                <div class="user-info">
                    <img id="nav-avatar" src="" alt="User" class="avatar-small">
                    <span id="nav-username">User</span>
                </div>
                <div class="nav-links">
                    <button onclick="showTasks()" class="nav-btn active" id="btn-tasks">Tasks
                    </button>
                    <button onclick="showProfile()" class="nav-btn" id="btn-profile">Profile</button>
                </div>
            </nav>
            <div id="tasks-section">
                <div class="section-header">
                    <h3>My Tasks</h3>
                </div>
                <div class="task-form">
                    <input type="text" id="task-name" placeholder="What needs to be done?" required>
                    <button onclick="createTask()" class="btn-add">+</button>
                </div>
                <ul id="task-list">
                    </ul>
            </div>
            <div id="profile-section" style="display:none;">
                <div class="section-header">
                    <h3>Edit Profile</h3>
                </div>
                <div class="profile-card">
                    <div class="profile-image-wrapper">
                        <img id="profile-avatar-preview" src="https://via.placeholder.com/100" alt="Avatar">
                    </div>
                    <form id="profile-form">
                        <div class="form-group">
                            <label>Username</label>
                            <input type="text" id="profile-username">
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" id="profile-email">
                        </div>
                        <div class="form-group">
                            <label>Avatar URL</label>
                            <input type="text" id="profile-avatar">
                        </div>
                        <div class="form-actions">
                            <button type="button" onclick="updateProfile()" class="btn-primary">Save Changes</button>
                        </div>
                        <hr>
                        <div class="form-group">
                            <label>New Password</label>
                            <input type="password" id="profile-password" placeholder="Leave blank to keep current">
                        </div>
                        <button type="button" onclick="updatePassword()" class="btn-warning">Update Password</button>
                    </form>
                    <p id="profile-message"></p>
                </div>
            </div>
        </div>
    </div>
    <script src="{{ url_for('static', filename='app.js') }}"></script>
</body>
</html>
```
#### Styling the Application
For the style we will use the pre-set styling file that is stored inside the folder ``materials``

#### Client-Side Logic (JavaScript)
This is the most important part. The JavaScript file acts as the bridge between the HTML events (clicks) and the Flask REST API.
```js

const API_BASE = '/api';

function switchView(viewId) {
 
    document.getElementById('login-view').style.display = 'none';
    document.getElementById('register-view').style.display = 'none';
    document.getElementById('app-view').style.display = 'none';
    const targetView = document.getElementById(viewId);
    if (targetView) {
        targetView.style.display = 'block';
    }
}

function displayMessage(elementId, message, isError = false) {
    const msgElement = document.getElementById(elementId);
    msgElement.innerText = message;
    msgElement.style.color = isError ? '#dc3545' : '#28a745';
}


document.addEventListener('DOMContentLoaded', () => {
    fetchUserProfile(false); 
});

function showRegister() {
    switchView('register-view');
    displayMessage('register-message', '');
}

function showLogin() {
    switchView('login-view');
    displayMessage('login-message', ''); 
}


document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    displayMessage('register-message', 'Registering...', false);

    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const avatar = document.getElementById('reg-avatar-url').value;

    const response = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, avatar })
    });

    const data = await response.json();

    if (response.ok) {
        displayMessage('register-message', data.message, false);
        document.getElementById('register-form').reset();
        setTimeout(showLogin, 2000); 
    } else {
        displayMessage('register-message', data.message || "Registration failed.", true);
    }
});


document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    displayMessage('login-message', 'Logging in...', false);

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    const response = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (response.ok) {
        displayMessage('login-message', data.message, false);
        document.getElementById('login-form').reset();
        switchView('app-view');
        showTasks(); 
        fetchUserProfile(true); 
    } else {
        displayMessage('login-message', data.message || "Invalid email or password.", true);
    }
});



function showTasks() {
    document.getElementById('tasks-section').style.display = 'block';
    document.getElementById('profile-section').style.display = 'none';
    document.getElementById('btn-tasks').classList.add('active');
    document.getElementById('btn-profile').classList.remove('active');
    fetchTasks();
}

function showProfile() {
    document.getElementById('tasks-section').style.display = 'none';
    document.getElementById('profile-section').style.display = 'block';
    document.getElementById('btn-profile').classList.add('active');
    document.getElementById('btn-tasks').classList.remove('active');
    fetchUserProfile(true); 
    displayMessage('profile-message', '');
}


async function fetchUserProfile(populateForm) {
    const response = await fetch(`${API_BASE}/user`);

    if (response.status === 401) {
        switchView('login-view');
        return;
    }

    if (response.ok) {
        const user = await response.json();
        
        
        document.getElementById('nav-username').innerText = user.username;
        const avatarUrl = user.avatar || 'https://via.placeholder.com/32?text=U';
        document.getElementById('nav-avatar').src = avatarUrl;
        
     
        if (!populateForm) {
            switchView('app-view');
            showTasks();
        }

        
        if (populateForm) {
            document.getElementById('profile-username').value = user.username;
            document.getElementById('profile-email').value = user.email;
            document.getElementById('profile-avatar').value = user.avatar;
            document.getElementById('profile-avatar-preview').src = avatarUrl;
        }
    } else {
        switchView('login-view');
    }
}

async function updateProfile() {
    displayMessage('profile-message', 'Saving profile...', false);
    
    const username = document.getElementById('profile-username').value;
    const email = document.getElementById('profile-email').value;
    const avatar = document.getElementById('profile-avatar').value;

    const response = await fetch(`${API_BASE}/user`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, avatar })
    });

    const data = await response.json();

    if (response.ok) {
        displayMessage('profile-message', data.message, false);
        fetchUserProfile(true); 
    } else {
        displayMessage('profile-message', data.message || "Failed to update profile.", true);
    }
}

async function updatePassword() {
    displayMessage('profile-message', 'Changing password...', false);
    
    const password = document.getElementById('profile-password').value;

    if (!password) {
        displayMessage('profile-message', 'Please enter a new password.', true);
        return;
    }

    const response = await fetch(`${API_BASE}/user`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
    });

    const data = await response.json();

    if (response.ok) {
        displayMessage('profile-message', data.message, false);
        document.getElementById('profile-password').value = ''; // Clear field
    } else {
        displayMessage('profile-message', data.message || "Failed to change password.", true);
    }
}

async function fetchTasks() {
    const response = await fetch(`${API_BASE}/tasks`);
    
    if (response.status === 401) return logout(); 
    
    const tasks = await response.json();
    const list = document.getElementById('task-list');
    list.innerHTML = ''; 

    if (tasks.length === 0) {
        list.innerHTML = '<li style="justify-content: center; color: #888;">No tasks yet! Add one above.</li>';
        return;
    }

    tasks.forEach(task => {
        const isDone = task.state === 'done';
        const li = document.createElement('li');
        li.className = isDone ? 'task-done' : '';

        const taskNameSpan = document.createElement('span');
        taskNameSpan.innerText = `${task.name} (${task.state})`;
        
        const toggleBtn = document.createElement('button');
        toggleBtn.innerText = isDone ? 'Reactivate' : 'Mark Done';
        toggleBtn.className = isDone ? 'delete-btn' : 'toggle-btn';
        toggleBtn.onclick = () => updateTaskState(task.id, isDone ? 'active' : 'done');

        const deleteBtn = document.createElement('button');
        deleteBtn.innerText = 'Delete';
        deleteBtn.className = 'delete-btn';
        deleteBtn.onclick = () => deleteTask(task.id);

        li.appendChild(taskNameSpan);
        li.appendChild(toggleBtn);
        li.appendChild(deleteBtn);
        list.appendChild(li);
    });
}

async function createTask() {
    const nameInput = document.getElementById('task-name');
    const name = nameInput.value.trim();
    if (!name) return;

    await fetch(`${API_BASE}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name })
    });

    nameInput.value = ''; 
    fetchTasks(); 
}

async function updateTaskState(taskId, newState) {
    await fetch(`${API_BASE}/tasks/${taskId}`, {
        method: 'PUT', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: newState }) 
    });
    fetchTasks(); 
}


async function deleteTask(taskId) {
    if(!confirm("Are you sure you want to delete this task?")) return;

    await fetch(`${API_BASE}/tasks/${taskId}`, {
        method: 'DELETE'
    });
    fetchTasks(); 
}

```

This JavaScript file is the client-side logic that connects the HTML interface with our Flask REST API. It handles user interactions such as logging in, registering, viewing and updating the profile, and managing tasks.

The code listens for form submissions and button clicks, then makes API calls using fetch to the corresponding endpoints. For example, when a user logs in, it sends a POST request to ``/api/login``, stores the session, and updates the view to show tasks. Similarly, task actions like creating, updating state, or deleting a task are sent to the ``/api/tasks`` endpoints, and the page updates dynamically without reloading.

Helper functions manage view switching, display messages, and ensure only logged-in users can access protected sections. Overall, this file acts as a bridge between the user interface and the backend, keeping the app interactive and responsive.
### Token-Based Authentication 
In the current Task Manager API, we use Flask-Session to manage authentication. This approach is effective for traditional web applications where the server and client are closely tied, and the browser handles session cookies automatically.

However, modern APIs often require authentication that is **stateless** and can be easily used by various clients (mobile apps, other servers, JavaScript frontends). This is where Token-Based Authentication comes in.
#### How Tokens Work
Instead of the server storing session data for every user (stateful), the server issues a secure, self-contained token (like a JSON Web Token or JWT) upon successful login.
1. **Client Logs In:** The user sends credentials (username/password) to the `/api/login` endpoint.
2. **Server Generates Token:** If successful, the server creates a unique token containing the user's ID, expiration time, and a secure signature. The token is returned in the response.
3. **Client Stores Token:** The frontend (e.g., JavaScript) stores this token (usually in local storage).
4. **API Access:** For every subsequent request to protected endpoints (e.g., `/api/tasks`), the client includes this token in the `Authorization` header, typically prefixed with `Bearer`.
5. **Server Verification:** The server receives the request, verifies the token's signature, extracts the user ID, and grants access. No database lookup for a session is required, making the API stateless and faster.
#### Implementing Token Authentication with Flask
While Flask-RESTful is great for resource definition, it doesn't natively handle JWT generation and verification. We typically use a specialized library like **`Flask-JWT-Extended`** for this purpose.

First, we install it using:
```shell
pip install Flask-JWT-Extended PyJWT==2.9.0
```
Now in our **`app.py`** we remove the session configuration and we initialize the JWT extension and set a secret key for signing tokens:
```python
# ... existing imports ...
from flask_jwt_extended import JWTManager


# ... existing app initialization ...

# Add a secret key for JWT signing
app.config.update(
    JWT_SECRET_KEY=os.getenv("JWT_SECRET"),
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1)
)
jwt = JWTManager(app)
```
Now we need to edit our  **`api/Auth.py`**, we modify the `LoginResource` to generate and return a token instead of setting a session variable:
```python
# In api/Auth.py
from flask_jwt_extended import create_access_token

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        try:
            verified = ph.verify(user.password , data['password'])
        except:
            verified = False
        if not user or not verified :
            return {"message": "Invalid email or password"}, 401
        
        access_token = create_access_token(identity=user.id)
        return {"message": "Login successful", "access_token": access_token}, 200
```
We returning access token to our front end, we can save them and send them in our requests.

Finally we add protection to `/api/Tasks` and `/api/Users`  , we use the `@jwt_required()` decorator. This automatically verifies the token in the request header, and if valid, makes the user's identity available via `get_jwt_identity()`:

**``api/User.py``**
```python
from flask import request
from flask_restful import Resource
from models import db
from models.User import User
from argon2 import PasswordHasher
from flask_jwt_extended import jwt_required, get_jwt_identity

ph = PasswordHasher()

class UserResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity() 
        user = User.query.get(current_user_id)
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar
        }, 200

    @jwt_required()
    def put(self):
        current_user_id = get_jwt_identity() 
        user = User.query.get(current_user_id)
        data = request.get_json()

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.avatar = data.get('avatar', user.avatar)
        db.session.commit()
        return {"message": "User profile updated successfully"}, 200
    @jwt_required()
    def patch(self):
        current_user_id = get_jwt_identity() 
        user = User.query.get(current_user_id)
        data = request.get_json()

        user.password = ph.hash(data['password'])
        db.session.commit()
        return {"message": "Password updated successfully"}, 200
```
**``api/Task.py``**
```python
from flask import request, session
from flask_restful import Resource
from models import db
from models.Task import Task
from flask_jwt_extended import jwt_required, get_jwt_identity

class TaskListResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity() 
        tasks = Task.query.filter_by(user_id=current_user_id).all()
        return [
            {
                "id": task.id,
                "name": task.name,
                "state": task.state,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ], 200

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity() 
        data = request.get_json()
        task = Task(
            name=data['name'],
            user_id=current_user_id
        )
        db.session.add(task)
        db.session.commit()
        return {"message": "Task created successfully"}, 201

class TaskResource(Resource):
    @jwt_required()
    def put(self, task_id):
        current_user_id = get_jwt_identity() 
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user_id
        ).first()

        if not task:
            return {"message": "Task not found"}, 404

        data = request.get_json()
        task.name = data.get('name', task.name)
        task.state = data.get('state', task.state)
        db.session.commit()
        return {"message": "Task updated successfully"}, 200
    @jwt_required()
    def delete(self, task_id):
        current_user_id = get_jwt_identity() 
    
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user_id
        ).first()
        if not task:
            return {"message": "Task not found"}, 404
        db.session.delete(task)
        db.session.commit()
        return {"message": "Task deleted successfully"}, 200
```
This simple change moves the application from stateful (session) to stateless (token) authentication, which is the standard for building high-performance APIs.
#### Editing the Javascript
Now we update our JavaScript to work with JWT authentication. When a user logs in, the backend returns a token, which we store in the browser using:
```javascript
localStorage.setItem('token', data.access_token);
```
For every subsequent API request, we need to include this token in the **Authorization header** so the backend can verify the user. This is done by adding:
```js
'Authorization': `Bearer ${localStorage.getItem('token')}` 
```
to the headers of each `fetch` request. This ensures that only authenticated users can access protected endpoints.

### API Rate Limiting
As our API gains more users, we need to protect it from abuse, excessive load, and denial-of-service (DoS) attacks. Rate Limiting is the practice of restricting the number of API requests a user (or IP address) can make within a specific time window.
#### Implementing Rate Limiting
The easiest way to implement rate limiting in Flask is by using the **`Flask-Limiter`** extension, we start by installing it using
```shell
pip install Flask-Limiter
```
#### Installing Redis
Redis (**Remote Dictionary Server**) is a very fast, in-memory data store. It is commonly used for **caching**, **sessions**, **queues**, and **rate limiting**. Because Redis keeps data in memory, it is much faster than traditional databases, which makes it ideal for tasks like tracking API requests in real time.

In our project, Redis is used by **Flask-Limiter** to store rate-limit data, allowing limits to persist and work correctly even if the server restarts or runs on multiple instances.  
We install it as following 

- Ubuntu / Debian:
```
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

```
- macOS (Homebrew):
```
brew install redis
brew services start redis
```

- Windows Redis is not officially supported on Windows, but we can use **Redis for Windows** provided by the community [Redis for Windows](https://github.com/tporadowski/redis/releases).
#### Configuring Limiter
After installing Redis, we create a new file called **`limiter.py`**. In this file, we initialize **Flask-Limiter**, which will protect our API from excessive requests.

We configure the limiter to:
- Use the client’s IP address to track requests
- Store rate-limit data in **Redis**
- Apply default limits to all API endpoints
```python
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379/0",
    default_limits=["200 per day", "50 per hour"])
```
With this setup, every endpoint in our application is automatically limited unless we override the limits on a specific route. Redis ensures that these limits are fast, reliable, and persistent even if the server restarts.
#### Apply the Rate Limit
Finally we can apply limits globally or to specific API routes.
**Global Limit:** The default limits above apply to every route unless overridden. we set this in `app.py` file by adding
```python
from limiter import limiter

limiter.init_app(app)
```
 **Specific Endpoint Limit:** We can use the `@limiter.limit` decorator on our resource methods, for example setting rate limit to 5 api call per minute:
```python
from limiter import limiter

class LoginResource(Resource):
    @limiter.limit("5 per minute")

    def post(self):
        # ... login logic ...
        pass
```
We can override the default rate limit and apply a much higher limit to a protected endpoint for a logged-in user, for example here we set 100 api call per minute:
```python
# In api/Tasks.py
from limiter import limiter

class TaskListResource(Resource):
    @jwt_required()
    @limiter.limit("100 per minute", override_defaults=True) # Higher limit for logged-in users
    def get(self):
        # ... task retrieval logic ...
        pass
```
Rate limiting ensures our API remains responsive and stable, providing a layer of security and robustness as our application scales.


