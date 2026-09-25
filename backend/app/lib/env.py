from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PORT: int = 8000
    MONGO_URI: str
    JWT_SECRET: str
    NODE_ENV: str = "development"
    DB_NAME: str = "chatify"
    CLIENT_URL: str = "http://localhost:5173"
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = ""
    EMAIL_FROM_NAME: str = "Chatify"
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    ARCJET_KEY: str = ""
    ARCJET_ENV: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


ENV = get_settings()
