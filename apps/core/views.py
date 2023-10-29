
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.conf import settings

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import User, Payment
from .exceptions import (
	ZeroAmountError, 
	NegativeAmountError,
    InvalidAmountError,
    InvalidRecipientError,
)

import re
import json
import moncashify

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

# Create your views here.
@api_view(['GET'])
def get_api_info(request):
    data = {
        'title': 'Mezanmi Tech API',
        'version': 'v1',
        'description': 'Description',
        'terms_of_service': 'https://www.google.com/policies/terms/',
        'docs': request.build_absolute_uri('/swagger/'),
        'contact': {
            'email': 'info@mezanmi.com',
            'website': 'mezanmi.com'
        },
    }
    return Response(data)

# Create Payment Transaction
@csrf_exempt
@api_view(['POST'])
def create_payment(request):
    data = request.data
    # user_id = data.get('user_id')
    amount = data.get('amount')
    currency = data.get('currency')
    phone_number = data.get('phone_number')

    if amount:
        try:
            if not is_valid_amount(amount):
                raise InvalidAmountError()

            amount = float(amount)

            if amount == 0:
                raise ZeroAmountError()

            if amount < 0:
                raise NegativeAmountError()

            if phone_number == 8:
                phone_number = '509' + phone_number

            if not is_valid_haiti_phone_number(phone_number):
                raise InvalidRecipientError("Recipient is not a valid Haiti phone number.")

            moncash = moncashify.API(
                settings.MONCASH_CLIENT_ID, 
                settings.MONCASH_SECRET_KEY, 
                debug=settings.DEBUG
            )

            payment = moncash.payment('test1234', amount)

            if payment:
                    
                return Response({
                    "message": "Payment created successfully", 
                    "redirect_url": payment.redirect_url
                    }, status=status.HTTP_201_CREATED)

        except ZeroAmountError as e:
            error = json.loads(str(e))
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        except NegativeAmountError as e:
            error = json.loads(str(e))
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidAmountError as e:
            error = json.loads(str(e))
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidRecipientError as e:
            error = json.loads(str(e))
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "Missing required data"}, status=status.HTTP_400_BAD_REQUEST)

# Process Payment
@csrf_exempt
@api_view(['POST'])
def process_payment(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
        # Perform payment processing (charge the user's account, etc.)
        payment.status = 'completed'
        payment.save()
        return JsonResponse({"message": "Payment processed successfully"})
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Payment not found"}, status=404)

# Retrieve Payment Status
@api_view(['GET'])
def retrieve_payment(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
        return JsonResponse({
            "payment_id": payment.id,
            "status": payment.status,
            "amount": str(payment.amount),
            "recipient": payment.recipient,
            "payment_method": payment.payment_method
        })
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Payment not found"}, status=404)

# List User Payments
@api_view(['GET'])
def list_user_payments(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        payments = Payment.objects.filter(user=user)
        payment_data = [{
            "payment_id": payment.id,
            "status": payment.status,
            "amount": str(payment.amount),
            "recipient": payment.recipient,
            "payment_method": payment.payment_method
        } for payment in payments]
        return JsonResponse({"payments": payment_data})
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

# Refund Payment
@csrf_exempt
@api_view(['POST'])
def refund_payment(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
        # Perform refund processing (refund the user's account, etc.)
        payment.status = 'refunded'
        payment.save()
        return JsonResponse({"message": "Payment refunded successfully"})
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Payment not found"}, status=404)

# Capture Authorized Funds
@csrf_exempt
@api_view(['POST'])
def capture_funds(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
        # Perform fund capture (e.g., for pre-authorization transactions)
        payment.status = 'completed'
        payment.save()
        return JsonResponse({"message": "Funds captured successfully"})
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Payment not found"}, status=404)

# Void Authorized Funds
@csrf_exempt
@api_view(['POST'])
def void_funds(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
        # Perform fund voiding (cancelling authorized but unprocessed payment)
        payment.status = 'voided'
        payment.save()
        return JsonResponse({"message": "Funds voided successfully"})
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Payment not found"}, status=404)

# List Payment Methods (Payment Gateway Integration May Be Needed)
@api_view(['GET'])
def list_payment_methods(request):
    # You may need to integrate with a payment gateway to retrieve payment methods
    payment_methods = ["Credit Card", "PayPal", "Digital Wallet"]
    return JsonResponse({"payment_methods": payment_methods})

# Add/Update Payment Method (User Management May Be Needed)
@csrf_exempt
@api_view(['POST'])
def add_update_payment_method(request):
    data = request.POST
    user_id = data.get('user_id')
    payment_method = data.get('payment_method')
    # Implement logic to add or update payment method for the user
    return JsonResponse({"message": "Payment method added/updated successfully"})

# Remove Payment Method (User Management May Be Needed)
@csrf_exempt
@api_view(['POST'])
def remove_payment_method(request, method_id):
    # Implement logic to remove the payment method with the given method_id
    return JsonResponse({"message": "Payment method removed successfully"})

# Transaction History
@api_view(['GET'])
def transaction_history(request):
    # Retrieve and return transaction history (add pagination as needed)
    transactions = Payment.objects.all()
    transaction_data = [{
        "payment_id": payment.id,
        "status": payment.status,
        "amount": str(payment.amount),
        "recipient": payment.recipient,
        "payment_method": payment.payment_method
    } for payment in transactions]
    return JsonResponse({"transactions": transaction_data})

# Currency Exchange Rates
@api_view(['GET'])
def exchange_rates(request):
    # Provide current exchange rates for various currencies (if applicable)
    exchange_rates = {"USD to EUR": 0.88, "USD to GBP": 0.75}
    return JsonResponse({"exchange_rates": exchange_rates})

# Reports and Analytics
@api_view(['GET'])
def reports_and_analytics(request):
    # Provide access to reports and analytics data for payment transactions
    # Implement the necessary logic for generating and retrieving reports
    return JsonResponse({"message": "Reports and analytics data"})

# Authentication and User Management (Integrate Django's built-in authentication or third-party packages)
# Define views for user registration, login, and profile management here

