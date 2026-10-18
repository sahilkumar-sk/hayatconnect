import random
import logging

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# In-memory OTP store for development (Redis in production)
_otp_store: dict[str, str] = {}

OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_LENGTH = 6


def generate_otp() -> str:
    """Generate a random 6-digit OTP."""
    return str(random.randint(100000, 999999))


async def send_otp(phone: str) -> bool:
    """
    Send OTP to a phone number.

    In dev mode (no Twilio credentials), stores OTP in memory and logs it.
    In production, sends via Twilio SMS.
    """
    code = generate_otp()
    _otp_store[phone] = code

    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        # TODO: Real Twilio integration
        # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # client.messages.create(
        #     body=f"Your HayatConnect verification code is: {code}",
        #     from_=settings.TWILIO_PHONE_NUMBER,
        #     to=phone,
        # )
        logger.info(f"OTP sent via Twilio to {phone}")
    else:
        # Dev mode — log the OTP so you can use it
        logger.warning(f"[DEV MODE] OTP for {phone}: {code}")
        print(f"\n{'='*40}")
        print(f"  DEV MODE — OTP for {phone}: {code}")
        print(f"{'='*40}\n")

    return True


async def verify_otp(phone: str, code: str) -> bool:
    """Verify an OTP code for a phone number."""
    stored_code = _otp_store.get(phone)

    if stored_code and stored_code == code:
        del _otp_store[phone]  # One-time use
        return True

    return False