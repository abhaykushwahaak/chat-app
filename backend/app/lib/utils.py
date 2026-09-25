from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Response
from app.lib.env import ENV

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7


def generate_token(user_id: str, response: Response) -> str:
    """Generate a JWT token and set it as an HttpOnly cookie on the response."""
    if not ENV.JWT_SECRET:
        raise ValueError("JWT_SECRET is not configured")

    expire = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS)
    payload = {"userId": user_id, "exp": expire}
    token = jwt.encode(payload, ENV.JWT_SECRET, algorithm=JWT_ALGORITHM)

    is_production = ENV.NODE_ENV != "development"

    response.set_cookie(
        key="jwt",
        value=token,
        max_age=JWT_EXPIRE_DAYS * 24 * 60 * 60,  # seconds
        httponly=True,       # prevent XSS attacks
        samesite="strict",   # prevent CSRF attacks
        secure=is_production,
    )

    return token


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token, raises JWTError on failure."""
    return jwt.decode(token, ENV.JWT_SECRET, algorithms=[JWT_ALGORITHM])
