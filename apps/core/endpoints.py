from django.urls import path

from . import views

from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [

    # Root API
    path('', views.get_api_info),

    path('token/', views.TokenObtainView.as_view()),
    path('token/refresh/', views.TokenRefreshView.as_view()),
    path('token/verify/', views.TokenVerifyView.as_view()),

    path('payments/', views.PaymentView.as_view(), name='create_payment'),
    path('payments/<int:payment_id>/process', views.process_payment, name='process_payment'),
]
