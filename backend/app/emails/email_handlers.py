import resend
from app.lib.resend_client import SENDER_EMAIL, SENDER_NAME
from app.emails.email_templates import create_welcome_email_template


async def send_welcome_email(email: str, name: str, client_url: str) -> None:
    """Send a welcome email to a newly registered user — mirrors Node's emailHandlers.js."""
    params: resend.Emails.SendParams = {
        "from": f"{SENDER_NAME} <{SENDER_EMAIL}>",
        "to": [email],
        "subject": "Welcome to Chatify!",
        "html": create_welcome_email_template(name, client_url),
    }

    response = resend.Emails.send(params)

    if not response or "id" not in response:
        raise RuntimeError("Failed to send welcome email")

    print(f"Welcome email sent successfully to {email}, id={response['id']}")
