from sqlalchemy.orm import Mapped
from models import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'tasks'

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    state: Mapped[str]  = db.Column(db.String(20), default='active') 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)