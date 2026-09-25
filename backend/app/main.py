"""
FastAPI application — equivalent to Node's server.js.

Startup:
    uvicorn app.main:app --reload --port 8000
"""

import socketio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.lib.db import connect_db
from app.lib.env import ENV
from app.lib.socket import sio
from app.middleware.rate_limit import limiter
from app.routers import auth, messages

# Import socket event handlers so they are registered on `sio`
import app.middleware.socket_auth  # noqa: F401


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Connect to MongoDB on startup."""
    await connect_db()
    yield


# ── FastAPI app ───────────────────────────────────────────────────────────────

fastapi_app = FastAPI(
    title="Chatify API",
    description="Python/FastAPI port of the Chatify Node.js backend",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate-limiting state + middleware
fastapi_app.state.limiter = limiter
fastapi_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
fastapi_app.add_middleware(SlowAPIMiddleware)

# CORS — mirrors Express cors({ origin: CLIENT_URL, credentials: true })
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[ENV.CLIENT_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
fastapi_app.include_router(auth.router)
fastapi_app.include_router(messages.router)


# ── Combine FastAPI + Socket.IO into a single ASGI app ───────────────────────
# Socket.IO handles /socket.io/* paths; everything else goes to FastAPI.

app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
