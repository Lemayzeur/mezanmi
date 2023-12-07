import re 

def is_valid_haiti_phone_number(recipient):
    # Validate recipient as a Haiti phone number (e.g., 509xxxxxxxx)
    pattern = r'^509\d{8}$'
    return re.match(pattern, recipient) is not None

def is_valid_amount(amount):
    """
    Validate the payment amount, allowing for string conversion if needed.

    Args:
    amount (int, float, or str): The payment amount to validate.

    Returns:
    bool: True if the amount is valid; False if it's not valid.
    """

    if isinstance(amount, (int, float)):
        # If it's already a numeric type, check if it's greater than 9
        return amount > 9
    elif isinstance(amount, str):
        try:
            # Try to convert the string to a numeric value and check if it's greater than 9
            numeric_amount = float(amount)
            return numeric_amount > 9
        except ValueError:
            return False  # Conversion to float failed
    else:
        return False  # Neither numeric nor string
