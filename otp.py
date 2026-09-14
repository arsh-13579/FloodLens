OTP_ENABLED = False  # flip to True once Twilio Verify Service is created (needs account upgrade)

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")

def _client():
    return Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_otp(phone_number):
    v = _client().verify.v2.services(VERIFY_SERVICE_SID).verifications.create(to=phone_number, channel="sms")
    return v.status  # "pending"

def check_otp(phone_number, code):
    v = _client().verify.v2.services(VERIFY_SERVICE_SID).verification_checks.create(to=phone_number, code=code)
    return v.status == "approved"