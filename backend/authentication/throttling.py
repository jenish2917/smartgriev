from rest_framework.throttling import UserRateThrottle

class EmailVerificationRateThrottle(UserRateThrottle):
    rate = '5/hour'
    scope = 'email_verification'

class MobileVerificationRateThrottle(UserRateThrottle):
    rate = '3/hour'
    scope = 'mobile_verification'

class PasswordResetRateThrottle(UserRateThrottle):
    rate = '3/hour'
    scope = 'password_reset'

class TwoFactorRateThrottle(UserRateThrottle):
    rate = '5/minute'
    scope = 'two_factor'
