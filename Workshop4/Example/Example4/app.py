import os
from dotenv import load_dotenv
from flask import Flask
from flask_session import Session
from datetime import timedelta
from routes import auth, main, wiki, profile,errors
from flask_ckeditor import CKEditor 
from models import db


load_dotenv()

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.getenv('SESSION_SECRET'),
    SESSION_TYPE='filesystem',             # Use server-side sessions
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
    SESSION_COOKIE_SECURE=True,            # Only send over HTTPS
    SESSION_COOKIE_HTTPONLY=True,          # Prevent access from JavaScript
    SESSION_COOKIE_SAMESITE='Lax'          # Helps prevent CSRF
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
# Initialize Flask-Session
Session(app)

# Initialize CKEditor
ckeditor = CKEditor(app)

# Register the blueprin
app.register_blueprint(auth.auth_bp)
app.register_blueprint(main.main_bp)
app.register_blueprint(wiki.wiki_bp)
app.register_blueprint(profile.profile_bp)
app.register_blueprint(errors.errors_bp)

if __name__ == '__main__':
    app.run(debug=True, port=3000)