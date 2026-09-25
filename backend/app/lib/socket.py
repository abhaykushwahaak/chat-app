"""
Socket.IO manager — equivalent to Node's socket.js.

Holds a single python-socketio AsyncServer instance shared across the app.
The ASGI app wraps both FastAPI and Socket.IO via socketio.ASGIApp.
"""

import socketio
from app.lib.env import ENV

# Async Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[ENV.CLIENT_URL],
    cors_credentials=True,
    always_connect=True,   # let the connect() handler reject via ConnectionRefusedError
    logger=True,
    engineio_logger=True,
)

# In-memory map of userId -> socketId  (mirrors Node's userSocketMap)
user_socket_map: dict[str, str] = {}


def get_receiver_socket_id(user_id: str) -> str | None:
    """Return the socket ID for a given userId, or None if offline."""
    return user_socket_map.get(str(user_id))
