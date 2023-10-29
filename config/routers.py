from rest_framework import routers

class OptionalSlashRouter(routers.SimpleRouter):
    # Allow endpoints ending with slash or no slash
    def __init__(self):
        super().__init__()
        self.trailing_slash = '/?'