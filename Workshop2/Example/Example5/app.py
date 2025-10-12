from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/profile')
@app.route('/profile/<username>')
def profile(username="World"):
    return render_template('profile.html', username=username)

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