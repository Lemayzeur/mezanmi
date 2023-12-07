from config.constants import DOMAIN_URL

import json 

class PaymentError(Exception):
    """Base class for payment-related errors."""
    def __init__(self, message, code, severity, documentation_link=None):
        self.message = message
        self.code = code
        self.severity = severity
        self.documentation_link = documentation_link

    def __str__(self):
        return json.dumps({"message": self.message, "code": self.code})

class ZeroAmountError(PaymentError):
    """Raised when the payment amount is zero."""
    def __init__(self, message="Payment amount cannot be zero."):
        code = 1001
        severity = "Error"
        documentation_link = f"http://{DOMAIN_URL}/errors/zero-amount"
        super().__init__(message, code, severity, documentation_link)
    
class NegativeAmountError(PaymentError):
    """Raised when the payment amount is negative."""
    def __init__(self, message="Payment amount cannot be negative."):
        code = 1002
        severity = "Error"
        documentation_link = f"http://{DOMAIN_URL}/errors/negative-amount"
        super().__init__(message, code, severity, documentation_link)

class InvalidAmountError(PaymentError):
    """Raised when the payment amount is not valid."""
    def __init__(self, message="Invalid payment amount"):
        code = 1003
        severity = "Error"
        documentation_link = f"http://{DOMAIN_URL}/errors/invalid-amount"
        super().__init__(message, code, severity, documentation_link)

class InvalidRecipientError(PaymentError):
    """Raised when the recipient is not a valid Haiti phone number."""
    def __init__(self, message="Invalid phone number"):
        code = 1004
        severity = "Error"
        documentation_link = f"http://{DOMAIN_URL}/errors/invalid-amount"
        super().__init__(message, code, severity)