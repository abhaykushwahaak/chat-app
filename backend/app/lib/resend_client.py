import resend
from app.lib.env import ENV

resend.api_key = ENV.RESEND_API_KEY

SENDER_EMAIL = ENV.EMAIL_FROM
SENDER_NAME = ENV.EMAIL_FROM_NAME
