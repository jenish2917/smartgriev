from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_sms(to_number, message):
    """
    Send SMS - Console mode only (for testing/development)
    For production SMS, integrate with your preferred SMS provider
    :param to_number: Recipient's phone number
    :param message: SMS content
    :return: bool indicating success/failure
    """
    try:
        # Console mode - log the message for testing/development
        logger.info(f"[SMS] To: {to_number}")
        logger.info(f"[SMS] Message: {message}")
        print(f"\n{'='*60}")
        print(f"📱 SMS TO: {to_number}")
        print(f"📨 MESSAGE: {message}")
        print(f"{'='*60}\n")
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
