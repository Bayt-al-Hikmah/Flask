from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from models import db

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    avatar: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Relationship: One user -> many pages
    pages: Mapped[list["Page"]] = relationship("Page", back_populates="author")