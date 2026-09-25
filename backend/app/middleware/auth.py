"""
HTTP authentication dependency — mirrors Node's auth.middleware.js (protectRoute).

Usage in a router:
    from app.middleware.auth import get_current_user
    ...
    async def my_endpoint(current_user: User = Depends(get_current_user)):
        ...
"""

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError
from beanie import PydanticObjectId
from app.lib.utils import decode_token
from app.models.user import User


async def get_current_user(jwt: str | None = Cookie(default=None)) -> User:
    """
    FastAPI dependency that extracts and verifies the JWT cookie,
    then fetches the corresponding user from MongoDB.
    """
    if not jwt:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized - No token provided",
        )

    try:
        payload = decode_token(jwt)
        user_id: str = payload.get("userId")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized - Invalid token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized - Invalid token",
        )

    user = await User.get(PydanticObjectId(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
