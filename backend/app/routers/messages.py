"""
Message router — merges Node's message.route.js + message.controller.js.

Endpoints:
  GET  /api/messages/contacts          — all users except self
  GET  /api/messages/chats             — users you have chatted with
  GET  /api/messages/{user_id}         — conversation with a specific user
  POST /api/messages/send/{user_id}    — send a message
"""

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.lib.cloudinary import upload_image
from app.lib.socket import get_receiver_socket_id, sio
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter
from app.models.message import Message
from app.models.schemas import SendMessageRequest
from app.models.user import User

router = APIRouter(prefix="/api/messages", tags=["messages"])


def _user_to_dict(user: User) -> dict:
    return {
        "_id": str(user.id),
        "fullName": user.full_name,
        "email": user.email,
        "profilePic": user.profile_pic,
    }


def _message_to_dict(msg: Message) -> dict:
    return {
        "_id": str(msg.id),
        "senderId": str(msg.sender_id),
        "receiverId": str(msg.receiver_id),
        "text": msg.text,
        "image": msg.image,
        "createdAt": msg.created_at.isoformat(),
        "updatedAt": msg.updated_at.isoformat(),
    }


# ── GET /api/messages/contacts ────────────────────────────────────────────────

@router.get("/contacts")
@limiter.limit("100/minute")
async def get_all_contacts(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Return all users except the logged-in user (no passwords)."""
    users = await User.find(User.id != current_user.id).to_list()
    return [_user_to_dict(u) for u in users]


# ── GET /api/messages/chats ───────────────────────────────────────────────────

@router.get("/chats")
@limiter.limit("100/minute")
async def get_chat_partners(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Return users the current user has exchanged at least one message with."""
    my_id = current_user.id

    messages = await Message.find(
        {
            "$or": [
                {"sender_id": my_id},
                {"receiver_id": my_id},
            ]
        }
    ).to_list()

    partner_ids = list(
        {
            str(msg.receiver_id) if msg.sender_id == my_id else str(msg.sender_id)
            for msg in messages
        }
    )

    partners = await User.find(
        {"_id": {"$in": [PydanticObjectId(pid) for pid in partner_ids]}}
    ).to_list()

    return [_user_to_dict(u) for u in partners]


# ── GET /api/messages/{user_id} ───────────────────────────────────────────────

@router.get("/{user_id}")
@limiter.limit("100/minute")
async def get_messages_by_user_id(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Fetch full message history between current user and another user."""
    my_id = current_user.id
    other_id = PydanticObjectId(user_id)

    messages = await Message.find(
        {
            "$or": [
                {"sender_id": my_id, "receiver_id": other_id},
                {"sender_id": other_id, "receiver_id": my_id},
            ]
        }
    ).to_list()

    return [_message_to_dict(m) for m in messages]


# ── POST /api/messages/send/{user_id} ────────────────────────────────────────

@router.post("/send/{user_id}", status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def send_message(
    user_id: str,
    body: SendMessageRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Send a text/image message to another user and push it via Socket.IO."""
    if not body.text and not body.image:
        raise HTTPException(status_code=400, detail="Text or image is required.")

    receiver_id = PydanticObjectId(user_id)
    sender_id = current_user.id

    if sender_id == receiver_id:
        raise HTTPException(status_code=400, detail="Cannot send messages to yourself.")

    receiver = await User.get(receiver_id)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found.")

    image_url: str | None = None
    if body.image:
        image_url = await upload_image(body.image)

    new_message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        text=body.text,
        image=image_url,
    )
    await new_message.insert()

    # Real-time delivery via Socket.IO
    receiver_socket_id = get_receiver_socket_id(str(receiver_id))
    if receiver_socket_id:
        await sio.emit("newMessage", _message_to_dict(new_message), room=receiver_socket_id)

    return _message_to_dict(new_message)
