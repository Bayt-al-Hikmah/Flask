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

![[Pasted image 20251209233754.png]]

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
pip install flask flask-session sqlalchemy flask-restful flask-sqlalchemy argon2-cffi
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
    description: Mapped[str]  = db.Column(db.Text, nullable=True)
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
from models import db, User
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
        if not user or not ph.verify(user.password , data['password']):
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
from models import db, User

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
from models import db, Task

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
                "description": task.description,
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
            description=data.get('description'),
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
        task.description = data.get('description', task.description)
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