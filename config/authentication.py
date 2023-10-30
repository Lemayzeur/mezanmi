
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.core.models import Client

class SafeJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        client = self.get_client(validated_token)

        request.client = client 

        return client, validated_token

    def get_client(self, validated_token):
        """
        Attempts to find and return a client using the given validated token.
        """
        try:
            client_id = validated_token['client_id']
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable client identification"))

        try:
            client = Client.objects.get(client_id=client_id)
        except Client.DoesNotExist:
            raise AuthenticationFailed(_("Client not found"), code="client_not_found")

        if not client.enabled:
            raise AuthenticationFailed(_("Client is inactive"), code="client_inactive")

        

        return client