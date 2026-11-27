import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from starlette.middleware.sessions import SessionMiddleware

from ..users.user_manager import get_user_by_id, verify_password, get_admin_user_count

# Dependency to retrieve the current user based on session data.
# FastAPI's Request object is used to access the session dictionary.

async def get_current_user(request: Request) -> int:
    """Return the logged‑in user id or raise 401.

    The session cookie stores ``user_id`` when a user logs in.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")
    return user_id

async def get_current_user_obj(request: Request):
    user_id = await get_current_user(request)
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found")
    return user

async def is_admin(user=Depends(get_current_user_obj)):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin access required")
    return True

# Helper to create a new CSRF token for a session.

def generate_csrf_token(session: dict) -> str:
    token = secrets.token_urlsafe(32)
    session["csrf_token"] = token
    return token

# Helper to validate CSRF token.

def validate_csrf(request: Request, token: str) -> None:
    session_token = request.session.get("csrf_token")
    if not session_token or session_token != token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid CSRF token")

# Helper to log the user in.

def login_user(request: Request, user_id: int) -> None:
    request.session["user_id"] = user_id
    # Generate a fresh CSRF token on login
    request.session["csrf_token"] = secrets.token_urlsafe(32)

# Helper to log the user out.

def logout_user(request: Request) -> None:
    request.session.clear()

__all__ = [
    "get_current_user",
    "get_current_user_obj",
    "is_admin",
    "generate_csrf_token",
    "validate_csrf",
    "login_user",
    "logout_user",
]
