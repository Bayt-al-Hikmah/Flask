### Objectives
- What is Backend Development?
- Introduction to Flask
- The MVC Design Pattern in Flask
- Structure of a Flask App
- Creating Our First Flask Application
- Working with Routes, Parameters, and URL Arguments
### What is Backend Development?
When we interact with a website or a mobile app, we only see the front-end the buttons, text, and images displayed on our screen. But behind the scenes, there's a whole other world working to make that experience possible. This is the backend, also known as the server-side.  
Backend development is the work that goes on behind the scenes. It's responsible for everything the user doesn't see, such as:  
1. **Storing and Managing Data**: When we create a user account or post a photo, the backend saves that information in a database.
2. **Handling Business Logic**: It processes our requests, performs calculations, and enforces the rules of the application. For example, it checks if our password is correct when we try to log in.
3. **Communicating with the Front-End**: The backend receives requests from our browser (the client) and sends back the data needed to display the webpage.
4. **Authentication and Security**: It manages user sessions and protects sensitive data from unauthorized access.


Essentially, if the front-end is the part of the restaurant where we sit and eat, the backend is the kitchen where the food is prepared, cooked, and made ready to serve. We, as backend developers, are the chefs.

![Image](structure.jpg)
### Introduction to Flask
Flask is a **microframework** for web development in Python. But what does "microframework" mean?
- **Framework**: It provides us with a set of tools and a structure to build web applications without having to start from scratch. It handles the low-level details of web communication (like processing HTTP requests) so we can focus on our application's logic.
- **Micro**: This means Flask is lightweight and provides only the essential components for building a web application. It doesn't force us into a specific way of doing things or include tools we might not need (like a database layer or a form validation library). It's simple, flexible, and easy to learn.

We choose Flask when we want to start small, move fast, and have the freedom to select our own tools and libraries as our application grows.
### The MVC Design Pattern and Flask
**MVC (Model-View-Controller)** is a popular architectural pattern for organizing code in web applications. It separates the application into three interconnected parts:
1. **Model**: This is the data layer. It's responsible for managing the application's data and business logic. It interacts directly with the database (e.g., retrieving user information, storing new posts).
2. **View**: This is the presentation layer. It's what the user sees. In many web frameworks, this is an HTML template that gets filled with data from the Model.
3. **Controller**: This is the logic layer that acts as the middleman. It receives requests from the user, interacts with the Model to fetch or save data, and then tells the View what to display.

#### How Does Flask Use It?
Flask is unopinionated, meaning it doesn't force us to use the MVC pattern strictly. However, we can easily structure our Flask apps to follow these principles:
- **Controller**: Our Flask **route functions** act as the controllers. They handle incoming requests from specific URLs.
- **Model**: This is where we write our Python code to manage data. For now, we'll handle data directly in our functions, but in larger apps, we would connect to a database here.
- **View**: The view is the response we send back to the client. While this is often an HTML template, in modern web development, it's very common for the view to be data formatted as **JSON** (JavaScript Object Notation), especially when building APIs.

In this workshop, we will focus on building APIs, so our "views" will be JSON responses. We won't be using HTML templates.
#### Structure of a Flask App
For a simple Flask application, our project structure can be very minimal. All we need is a virtual environment to manage our packages and a single Python file to write our code.  
Our initial structure will look like this:
```
my_flask_project/
├── venv/            # Our virtual environment folder
└── app.py           # Our main Flask application file
```
### Creating Our First Flask App
Let's build our first application. This will teach us how to set up our environment, install Flask, and create a simple web server.
#### Setting Up the Environment
First, we need to create an isolated environment for our project. This prevents conflicts between packages from different projects. We use a tool called `venv`.    
Open your terminal, navigate to your project directory, and run:
```
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```
We'll see `(venv)` appear at the beginning of our terminal prompt, which confirms our virtual environment is active.
#### Installing Flask
Now, with our environment active, we can install Flask using `pip`, Python's package manager.
```
pip install Flask
```
#### Creating the "Hello, World!" App
Now that Flask is installed, let’s build our very first application. This simple example will demonstrate the basic structure of a Flask app and show how we can serve a response from the server to a web browser.  
The first step is to create a new file in your project directory called **`app.py`**. This file will contain the main logic of our application. Open it in your code editor and add the following code:
```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home_page():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)

```
Here’s what each part of the code does. First, we import the `Flask` class from the `flask` package. This class is the foundation of our web application. Next, we create an instance of this class and store it in a variable named `app`. The argument `__name__` tells Flask where to look for resources like templates and static files, which becomes important in larger projects.  
After creating the app, we define a route using the `@app.route('/')` decorator. A **route** is the path that the user visits in their browser. In this case, the root path `/` corresponds to the homepage. When someone goes to this URL, Flask runs the function `home_page()` and returns its result in this case, the string `"Hello, World!"`.  
Finally, the block at the bottom ensures that the server only runs if we execute this file directly. The `debug=True` option is especially useful during development: it enables automatic reloading whenever we make changes to the code and provides detailed error messages if something goes wrong.  
Once the file is saved, open your terminal, navigate to the project directory, and run the application with the command:
```
python app.py
```
Our terminal will show an output indicating the server is running, usually at `http://127.0.0.1:5000/`. If we open this URL in our web browser, we will see the text "Hello, World!". We've just created our first web server!
### Working with Parameters and Arguments
Static pages are great, but most applications need to handle dynamic data. Flask makes it easy to capture information directly from the URL.
#### URL Parameters (Dynamic Routes)
Sometimes, we want to capture a part of the URL as a variable. For example, to show a user's profile page. We can do this by adding variable sections to our route.  
Let's add a new route to `app.py` to greet a user by name:
```
# Add this new route to your app.py file
@app.route('/user/<username>')
def show_user_profile(username):
    # The value captured from the URL is passed as an argument to our function
    return f'Hello, {username}!'
```
Now, if we run our app and go to `http://127.0.0.1:5000/user/Alice`, the page will display "Hello, Alice!". Flask captures "Alice" from the URL and passes it as the `username` argument to our function.
#### URL Query Arguments
Another way to pass data is through **query arguments**, which are key-value pairs added to the end of a URL after a `?`. For example: `/search?query=flask`.  
To access these, we need to import the `request` object from Flask. The `request.args` attribute gives us a dictionary-like object containing all the query arguments.  
Let's create a route that uses query arguments:
```
# Add 'request' to your import line
from flask import Flask, request

# ... (keep your existing code) ...

@app.route('/search')
def search():
    # request.args.get() retrieves the value for the 'query' key
    query_param = request.args.get('query')
    
    if query_param:
        return f'You are searching for: {query_param}'
    else:
        return 'Please provide a search query.'
```
If we visit `http://127.0.0.1:5000/search?query=python+tutorials`, the page will show "You are searching for: python tutorials".
### Final Application: Building a Simple JSON API
Now, let's combine everything we've learned to build a simple API that returns a JSON object. APIs are how modern applications communicate. Instead of returning text or HTML, we will return data that another application (like a mobile app or a JavaScript front-end) can easily use.  
Our goal is to create an endpoint that:
1. Accepts a product `id` as a URL parameter.
2. Accepts an optional `currency` as a query argument.
3. Returns a JSON object with the product details.

First, let's add `jsonify` to our imports. This is a Flask function that correctly formats our Python dictionaries into JSON responses.
```
# Update your import line
from flask import Flask, request, jsonify

# ... (keep your existing app instance and other routes) ...

# A little bit of fake data to act as our "database"
products_db = {
    "100": {"name": "Laptop", "price": 1200},
    "101": {"name": "Mouse", "price": 25},
    "102": {"name": "Keyboard", "price": 75}
}

@app.route('/api/products/<product_id>')
def get_product(product_id):
    # Get the product from our fake database
    product = products_db.get(product_id)
    
    # Check if the product exists
    if not product:
        # Return a JSON error message with a 404 status code
        return jsonify({"error": "Product not found"}), 404
        
    # Check for the optional 'currency' query argument
    currency = request.args.get('currency', 'USD') # Default to 'USD' if not provided
    
    # Create the response data
    response_data = {
        "id": product_id,
        "name": product["name"],
        "price": product["price"],
        "currency": currency
    }
    
    # Use jsonify to convert the dictionary to a JSON response
    return jsonify(response_data)
```
After adding this code, run the app and try visiting these URLs in your browser:
- `http://127.0.0.1:5000/api/products/101`
- `http://127.0.0.1:5000/api/products/101?currency=EUR`
- `http://127.0.0.1:5000/api/products/999` (to see the error message)

We'll see a clean JSON output directly in the browser. Congratulations! We've just built a simple, dynamic JSON API with Flask.