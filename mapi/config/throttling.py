from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class SafeAnonRateThrottle(AnonRateThrottle):
    def get_cache_key(self, request, view):
        if hasattr(request, 'client'):
            return None  # Only throttle unauthenticated requests.

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }

class SafeUserRateThrottle(UserRateThrottle):
    def get_cache_key(self, request, view):
        if hasattr(request, 'client'):
            ident = request.client.client_id
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }