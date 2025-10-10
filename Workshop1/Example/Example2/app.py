from flask import Flask

app = Flask(__name__)

@app.route('/user/<username>')
def greet_user(username):
    return f"Hello, {username}"

if __name__ == '__main__':
    app.run(port=3000, debug=True)