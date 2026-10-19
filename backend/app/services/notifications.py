"""SMS notifications.

Dev (default): prints the message to the uvicorn console.
Prod: set SMS_PROVIDER=twilio plus TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM in .env.
"""
import logging
import os

logger = logging.getLogger("hayatconnect.sms")


async def send_sms(to: str, body: str) -> bool:
    provider = os.getenv("SMS_PROVIDER", "console").lower()

    if provider == "twilio":
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        sender = os.getenv("TWILIO_FROM")
        if not (sid and token and sender):
            logger.error("Twilio selected but credentials are missing")
            return False
        try:
            import httpx

            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(
                    f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
                    data={"To": to, "From": sender, "Body": body},
                    auth=(sid, token),
                )
            return r.status_code < 300
        except Exception as exc:  # never let SMS failure break matching
            logger.error("SMS send failed: %s", exc)
            return False

    print(f"\n[SMS -> {to}] {body}\n", flush=True)
    return True


async def notify_donor_new_request(phone: str, donor_name: str, blood_group: str,
                                   hospital: str, urgency: str) -> bool:
    body = (
        f"HayatConnect: {donor_name}, {urgency.upper()} request for {blood_group} blood "
        f"at {hospital}. Open My matches to accept or decline."
    )
    return await send_sms(phone, body)
