from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    icon_path = Column(String(255), nullable=False, default="static/icons/efma.png")
    is_admin = Column(Boolean, default=False, nullable=False)
    language = Column(String(10), default="en", nullable=False)
    theme = Column(String(10), default="dark", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User {self.username} (admin={self.is_admin})>"

__all__ = ["User", "Base"]
