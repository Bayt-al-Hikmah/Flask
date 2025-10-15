from app import app, db
from models.user import User
from models.page import Page
with app.app_context():
    db.create_all()
    print("Database tables created.")