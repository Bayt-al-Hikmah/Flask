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
pip install flask flask-session sqlalchemy flask-restful
```
