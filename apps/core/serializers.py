from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Client

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('refresh')

	# def validate(self, attrs):

	# 	data = super().validate(attrs)
	# 	# refresh = RefreshToken(attrs['refresh'])
	# 	data['access_token'] = data.pop('access', None)

	# 	# data['lifetime'] = refresh.access_token.lifetime.total_seconds()
	# 	return data

    # def to_representation(self, token):
    #     # Customize the field names for the tokens here
    #     return {
    #         'access_token': token.access_token,
    #     }
