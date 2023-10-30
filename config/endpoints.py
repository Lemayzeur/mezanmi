from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

from .swagger import urlpatterns as swagger_urlpatterns

urlpatterns = [
    # Root API
    path('', lambda req : render(req, 'index.html')),

    path('api/v1/', include('apps.core.endpoints')),

    path('admin/', admin.site.urls),
    path('rest/', include('rest_framework.urls')),
]

urlpatterns += swagger_urlpatterns