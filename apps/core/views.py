
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import views

from rest_framework_simplejwt.tokens import (
    RefreshToken,
    TokenError, UntypedToken
)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.conf import settings
from django.utils.decorators import method_decorator

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import User, Payment, Client
from .exceptions import (
	ZeroAmountError, 
	NegativeAmountError,
    InvalidAmountError,
    InvalidRecipientError,
)
from .serializers import CustomTokenRefreshSerializer
from .decorators import extract_client_credentials

from config.utils import (
    is_valid_haiti_phone_number,
    is_valid_amount,
)

import re
import json
import moncashify

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

class TokenObtainView(views.APIView):
    permission_classes = []

    @method_decorator(extract_client_credentials)
    def post(self, request, client_id, client_secret):
        # Verify client credentials
        client = Client.objects.filter(client_id=client_id, enabled=True).first()

        if not client or client.client_secret != client_secret:
            return Response(status=status.HTTP_401_UNAUTHORIZED)       

        # Generate a token for the client
        refresh = RefreshToken()

        # Add the client_id to the claim
        refresh['client_id'] = client_id

        data = {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'lifetime': int(refresh.access_token.lifetime.total_seconds()),
        }
        return Response(data)

class TokenRefreshView(views.APIView):
    permission_classes = []

    def post(self, request):
        # Get the refresh token from the request data
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_BAD_REQUEST)

        try:
            # Decode the refresh token
            refresh = RefreshToken(refresh_token)
            # Create a new access token
            new_access_token = refresh.access_token
        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_BAD_REQUEST)

        # Return the new access token
        return Response({'access_token': str(new_access_token)})

class TokenVerifyView(views.APIView):
    permission_classes = []

    def post(self, request):
        access_token = request.data.get('access_token')

        if not access_token:
            return Response({'detail': 'Token is required'}, status=status.HTTP_BAD_REQUEST)

        try:
            # Attempt to decode the token
            untyped_token = UntypedToken(access_token)

            # Token is valid
            return Response({'valid': True}, status=status.HTTP_200_OK)
        except TokenError:
            # Token is invalid
            return Response({'valid': False}, status=status.HTTP_200_OK)

# Create Payment Transaction
class PaymentView(views.APIView):
    permission_classes = []

    def post(self, request):
        data = request.data
        reference_id = data.get('reference_id', 'test1234')
        amount = data.get('amount')
        currency = data.get('currency')
        phone_number = data.get('phone_number', '')

        if amount and reference_id:
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

                payment = moncash.payment(reference_id, amount)

                if payment:
                        
                    return Response({
                        "message": "Payment created successfully", 
                        "redirect_url": payment.redirect_url
                        }, 
                        status=status.HTTP_201_CREATED
                    )

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
