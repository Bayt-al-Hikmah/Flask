from flask import Flask,request

app = Flask(__name__)

@app.route('/search')
def greet_user():
    query_param = request.args.get('query')
    if query_param:
        return f'You are searching for: {query_param}'
    else:
        return 'Please provide a search query.'

if __name__ == '__main__':
    app.run(port=3000, debug=True)