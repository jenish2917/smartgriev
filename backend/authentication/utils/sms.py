from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_sms(to_number, message):
    """
    Send SMS using Twilio
    :param to_number: Recipient's phone number
    :param message: SMS content
    :return: bool indicating success/failure
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Format the number to E.164 format for Indian numbers
        if to_number.startswith('0'):
            to_number = '+91' + to_number[1:]
        elif not to_number.startswith('+'):
            to_number = '+91' + to_number

        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_FROM_NUMBER,
            to=to_number
        )
        
        logger.info(f"SMS sent successfully to {to_number}. SID: {message.sid}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send SMS to {to_number}. Error: {str(e)}")
        return False

def send_otp_sms(to_number, otp):
    """
    Send OTP via SMS
    :param to_number: Recipient's phone number
    :param otp: OTP to send
    :return: bool indicating success/failure
    """
    message = f"Your SmartGriev verification code is: {otp}. Valid for 10 minutes. Do not share this code with anyone."
    return send_sms(to_number, message)
