"""
Auth router — merges Node's auth.route.js + auth.controller.js.

Endpoints:
  POST /api/auth/signup
  POST /api/auth/login
  POST /api/auth/logout
  PUT  /api/auth/update-profile  (protected)
  GET  /api/auth/check           (protected)
"""

import re
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request

from app.models.user import User
from app.models.schemas import (
    SignupRequest,
    LoginRequest,
    UpdateProfileRequest,
    UserResponse,
)
from app.lib.utils import generate_token
from app.lib.cloudinary import upload_image
from app.lib.env import ENV
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter
from app.emails.email_handlers import send_welcome_email

router = APIRouter(prefix="/api/auth", tags=["auth"])

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(10)).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _user_to_response(user: User) -> dict:
    return {
        "_id": str(user.id),
        "fullName": user.full_name,
        "email": user.email,
        "profilePic": user.profile_pic,
    }


# ── POST /api/auth/signup ─────────────────────────────────────────────────────

@router.post("/signup", status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def signup(request: Request, body: SignupRequest, response: Response):
    if not body.full_name or not body.email or not body.password:
        raise HTTPException(status_code=400, detail="All fields are required")

    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    if not EMAIL_REGEX.match(body.email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    existing = await User.find_one(User.email == body.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = _hash_password(body.password)
    new_user = User(
        email=body.email,
        full_name=body.full_name,
        password=hashed_password,
    )
    await new_user.insert()

    generate_token(str(new_user.id), response)

    # Send welcome email asynchronously (non-blocking on failure)
    try:
        await send_welcome_email(new_user.email, new_user.full_name, ENV.CLIENT_URL)
    except Exception as e:
        print(f"Failed to send welcome email: {e}")

    return _user_to_response(new_user)


# ── POST /api/auth/login ──────────────────────────────────────────────────────

@router.post("/login")
@limiter.limit("100/minute")
async def login(request: Request, body: LoginRequest, response: Response):
    if not body.email or not body.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = await User.find_one(User.email == body.email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not _verify_password(body.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    generate_token(str(user.id), response)
    return _user_to_response(user)


# ── POST /api/auth/logout ─────────────────────────────────────────────────────

@router.post("/logout")
@limiter.limit("100/minute")
async def logout(request: Request, response: Response):
    response.delete_cookie("jwt")
    return {"message": "Logged out successfully"}


# ── PUT /api/auth/update-profile  (protected) ────────────────────────────────

@router.put("/update-profile")
async def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
):
    if not body.profile_pic:
        raise HTTPException(status_code=400, detail="Profile pic is required")

    secure_url = await upload_image(body.profile_pic)
    current_user.profile_pic = secure_url
    await current_user.save()

    return _user_to_response(current_user)


# ── GET /api/auth/check  (protected) ─────────────────────────────────────────

@router.get("/check")
async def check_auth(current_user: User = Depends(get_current_user)):
    return _user_to_response(current_user)
