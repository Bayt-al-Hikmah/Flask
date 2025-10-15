from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from models import db

class Page(db.Model):
    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)

    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship("User", back_populates="pages")