import cloudinary
from app.lib.env import ENV

cloudinary.config(
    cloud_name=ENV.CLOUDINARY_CLOUD_NAME,
    api_key=ENV.CLOUDINARY_API_KEY,
    api_secret=ENV.CLOUDINARY_API_SECRET,
)


async def upload_image(data_uri: str) -> str:
    """Upload a base64 data URI image to Cloudinary and return the secure URL."""
    import cloudinary.uploader
    result = cloudinary.uploader.upload(data_uri)
    return result["secure_url"]
