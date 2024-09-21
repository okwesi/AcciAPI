from rest_framework.throttling import SimpleRateThrottle


class VerifyProfileThrottle(SimpleRateThrottle):
    """
    Throttle class to limit verification attempts.
    """
    rate = '1/min'
