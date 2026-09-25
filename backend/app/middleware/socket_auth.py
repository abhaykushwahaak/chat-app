"""
Socket.IO authentication middleware — mirrors Node's socket.auth.middleware.js.

Registered on the sio server instance so every connection goes through JWT validation.
"""

from jose import JWTError
from beanie import PydanticObjectId
from app.lib.socket import sio, user_socket_map
from app.lib.utils import decode_token
from app.models.user import User


def _parse_jwt_cookie(cookie_header: str | None) -> str | None:
    """Extract the 'jwt' value from a raw Cookie header string."""
    if not cookie_header:
        return None
    for part in cookie_header.split(";"):
        part = part.strip()
        if part.startswith("jwt="):
            return part[len("jwt="):]
    return None


@sio.event
async def connect(sid: str, environ: dict, auth: dict | None = None):
    """Authenticate the socket connection using the JWT cookie."""
    cookie_header = environ.get("HTTP_COOKIE")
    token = _parse_jwt_cookie(cookie_header)

    if not token:
        print("Socket connection rejected: No token provided")
        raise ConnectionRefusedError("Unauthorized - No Token Provided")

    try:
        payload = decode_token(token)
        user_id: str = payload.get("userId")
        if not user_id:
            raise ConnectionRefusedError("Unauthorized - Invalid Token")
    except JWTError:
        print("Socket connection rejected: Invalid token")
        raise ConnectionRefusedError("Unauthorized - Invalid Token")

    user = await User.get(PydanticObjectId(user_id))
    if not user:
        print("Socket connection rejected: User not found")
        raise ConnectionRefusedError("User not found")

    # Attach user info to the socket session
    await sio.save_session(sid, {"user": user, "userId": str(user.id)})
    user_socket_map[str(user.id)] = sid

    print(f"A user connected: {user.full_name}")

    # Broadcast online users list to all clients
    await sio.emit("getOnlineUsers", list(user_socket_map.keys()))


@sio.event
async def disconnect(sid: str):
    """Clean up when a socket disconnects."""
    session = await sio.get_session(sid)
    user = session.get("user") if session else None
    user_id = session.get("userId") if session else None

    if user_id and user_id in user_socket_map:
        del user_socket_map[user_id]

    if user:
        print(f"A user disconnected: {user.full_name}")

    # Broadcast updated online users list
    await sio.emit("getOnlineUsers", list(user_socket_map.keys()))
