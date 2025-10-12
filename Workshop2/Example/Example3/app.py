from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/profile')
@app.route('/profile/<username>')
def profile(username="World"):
    return render_template('profile.html', username=username)

if __name__ == '__main__':
    app.run(port=3000,debug=True)