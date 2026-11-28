
"""
EFMA Password Manager

Centralized password hashing and verification.

Uses Argon2id through pwdlib.
"""

from pwdlib import PasswordHash


# Recommended password hashing configuration.
# Currently uses Argon2id.
_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a password using the current configured algorithm.

    Returns:
        str: Encoded password hash suitable for database storage.

    Raises:
        ValueError: If the password is invalid.
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password cannot be empty")

    return _password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a stored password hash.

    Returns:
        bool: True if the password matches, otherwise False.

    Invalid or unsupported hashes fail closed.
    """
    if not isinstance(password, str) or not isinstance(hashed_password, str):
        return False

    if not password or not hashed_password:
        return False

    try:
        return _password_hash.verify(password, hashed_password)
    except Exception:
        # Never allow malformed or unsupported hashes to authenticate.
        return False


__all__ = [
    "hash_password",
    "verify_password",
]
