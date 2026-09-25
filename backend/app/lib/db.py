import motor.motor_asyncio
from beanie import init_beanie
from app.lib.env import ENV
from app.models.user import User
from app.models.message import Message


async def connect_db():
    """Initialize MongoDB connection and Beanie ODM."""
    if not ENV.MONGO_URI:
        raise ValueError("MONGO_URI is not set")

    client = motor.motor_asyncio.AsyncIOMotorClient(ENV.MONGO_URI)

    # Use DB_NAME from env, or fall back to the name embedded in the URI
    db = client[ENV.DB_NAME]

    await init_beanie(database=db, document_models=[User, Message])
    print(f"MongoDB connected: database='{ENV.DB_NAME}'")
