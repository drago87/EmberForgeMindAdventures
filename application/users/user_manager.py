from datetime import datetime
from passlib.hash import bcrypt

from .database import SessionLocal
from .models import User



def create_user(username: str, password: str, icon_path: str = "static/icons/efma.png",
                 is_admin: bool = False, language: str = "en", theme: str = "dark") -> User:
    """Create a new user and persist it to the database.

    Raises ValueError if the username already exists.
    """
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == username).first():
            raise ValueError("Username already taken")
        hashed = bcrypt.hash(password)
        user = User(
            username=username,
            password_hash=hashed,
            icon_path=icon_path,
            is_admin=is_admin,
            language=language,
            theme=theme,
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def verify_password(user: User, password: str) -> bool:
    return bcrypt.verify(password, user.password_hash)


def get_user_by_username(username: str) -> User | None:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.username == username).first()
    finally:
        db.close()


def get_user_by_id(user_id: int) -> User | None:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


def get_admin_user_count() -> int:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.is_admin == True).count()
    finally:
        db.close()


def get_all_users() -> list[User]:
    db = SessionLocal()
    try:
        return db.query(User).all()
    finally:
        db.close()


def upgrade_user_to_admin(user_id: int) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_admin = True
            db.commit()
    finally:
        db.close()


def downgrade_user_from_admin(user_id: int) -> None:
    db = SessionLocal()
    try:
        if get_admin_user_count() <= 1:
            raise ValueError("Cannot remove the last administrator")
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_admin = False
            db.commit()
    finally:
        db.close()


def update_user_settings(user_id: int, *, username: str | None = None,
                          icon_path: str | None = None,
                          language: str | None = None,
                          theme: str | None = None) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return
        if username:
            # Ensure unique
            if db.query(User).filter(User.username == username, User.id != user_id).first():
                raise ValueError("Username already taken")
            user.username = username
        if icon_path:
            user.icon_path = icon_path
        if language:
            user.language = language
        if theme:
            user.theme = theme
        db.commit()
    finally:
        db.close()

__all__ = [
    "create_user",
    "verify_password",
    "get_user_by_username",
    "get_user_by_id",
    "get_admin_user_count",
    "get_all_users",
    "upgrade_user_to_admin",
    "downgrade_user_from_admin",
    "update_user_settings",
]
