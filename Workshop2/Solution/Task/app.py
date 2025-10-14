from flask import Flask
from routes import main,share,search

# Create the Flask app instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fXZAdJtkLu5zK7A1sbXsQutiO4TD3M74QXqsT0fcRjiGGvihe9Hb379oLwahxJjc'

app.Quotes = []
# Register the blueprint with the main app
app.register_blueprint(main.main_bp)
app.register_blueprint(share.share_bp)
app.register_blueprint(search.search_bp)

if __name__ == '__main__':
    app.run(debug=True, port=3000)