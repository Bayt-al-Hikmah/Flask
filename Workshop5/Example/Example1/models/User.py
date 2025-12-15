from models import db
from sqlalchemy.orm import Mapped

class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int]  = db.Column(db.Integer, primary_key=True)
    username: Mapped[str] = db.Column(db.String(80), unique=True, nullable=False)
    email: Mapped[str] = db.Column(db.String(120), unique=True, nullable=False)
    password: Mapped[str] = db.Column(db.String(255), nullable=False)
    avatar: Mapped[str] = db.Column(db.String(255), nullable=True)

    tasks = db.relationship('Task', backref='user', lazy=True)