import base64
from functools import wraps

from rest_framework.response import Response
from rest_framework import status

def extract_client_credentials(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Get the Authorization header from the request
        auth_header = request.META.get('HTTP_X_CLIENT_ID')

        if auth_header:
            # Remove the "Token" prefix and decode the base64-encoded credentials
            encoded_credentials = auth_header

            credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            
            # Split the credentials into client ID and client secret
            client_id, client_secret = credentials.split(':')
            
            # Pass the client ID and secret to the view function
            return view_func(request, client_id, client_secret, *args, **kwargs)
        
        # If the header is missing or not using "Token" authentication, return an error response
        return Response({'error': 'Invalid client credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    return _wrapped_view
