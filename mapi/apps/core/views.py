
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
from config.exrate import ExchangeRateBackend

import re
import json
import moncashify
import moncashify.errors

@api_view(['GET'])
def get_api_info(request):
    
    # Example usage:
    exchange_rate_backend = ExchangeRateBackend()
    result = exchange_rate_backend.engine('USD', system='brh')
    print('DIRI:', result)

    # 10 USD

    

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

        # TODO: Verification will come from a third secure server instead
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
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the refresh token
            refresh = RefreshToken(refresh_token)
            # Create a new access token
            new_access_token = refresh.access_token
        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)

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

class PaymentView(views.APIView):
    '''Create Payment Transaction'''
    permission_classes = [] # TODO: Pa bliye retire sa, pou pwoteje view a.

    def post(self, request):
        data = request.data # body of the request

        # Get mandatory data from the body
        reference_id = data.get('reference_id')
        amount = data.get('amount')
        currency = data.get('currency', 'HTG') # by default, it's HTG

        if amount and reference_id:
            try:
                if not is_valid_amount(amount):
                    raise InvalidAmountError()

                # get the exchange rate value in HTG
                exchange_rate_backend = ExchangeRateBackend()
                rate_value = exchange_rate_backend.engine(currency)

                # Amount in HTG
                amount = round( float(amount) * rate_value, 2)

                if amount == 0:
                    raise ZeroAmountError()

                if amount < 0:
                    raise NegativeAmountError()

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
            except moncashify.errors.TokenError as e:
                print(e)
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Missing required data"}, status=status.HTTP_400_BAD_REQUEST)

class PaymentProcessView(views.APIView):
    def post(self, request):
        transaction_id = request.data.get(settings.MONCASH_QUERY_KEY)

        # Check the status of the transaction from the provider
        try:
            # details = {'path': '/Api/v1/RetrieveTransactionPayment', 'payment': {'reference': '128b8dc1339', 'transactionId': '5766988876', 'cost': 1, 'message': 'successful', 'payer': '50938747485'}, 'timestamp': 1628890717030, 'status': 200} 
            moncash = moncashify.API(
                settings.MONCASH_CLIENT_ID, 
                settings.MONCASH_SECRET_KEY, 
                debug=settings.DEBUG
            )
            details = moncash.transaction_details(transaction_id=transaction_id)
                
            # See Moncashify details response example, here: 
            return Response(details)

        except moncashify.errors.TokenError as e:
            return Response(status=status.HTTP_401_UNAUTHORIZED) 
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PaymentVerifyView(views.APIView):
    def post(self, request, transaction_id):
        id = request.data.get(settings.MONCASH_QUERY_KEY)
        _type = request.data.get('type')

        # Check the status of the transaction from the provider
        try:
            # details = {'path': '/Api/v1/RetrieveTransactionPayment', 'payment': {'reference': '128b8dc1339', 'transactionId': '5766988876', 'cost': 1, 'message': 'successful', 'payer': '50938747485'}, 'timestamp': 1628890717030, 'status': 200} 
            moncash = moncashify.API(
                settings.MONCASH_CLIENT_ID, 
                settings.MONCASH_SECRET_KEY, 
                debug=settings.DEBUG
            )
            if _type == 'order_id':
                details = moncash.transaction_details(order_id=id)
            else:
                details = moncash.transaction_details(transaction_id=id)
            
            # See Moncashify details response example, here: 
            return Response(details)

        except moncashify.errors.TokenError as e:
            return Response(status=status.HTTP_401_UNAUTHORIZED) 
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
