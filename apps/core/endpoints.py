
from django.urls import path

from . import views

from apps.core.views import (
    get_api_info,
)


urlpatterns = [

    # Root API
    path('', get_api_info),

    path('payments', views.create_payment, name='create_payment'),
    path('payments/<int:payment_id>/process', views.process_payment, name='process_payment'),
    path('payments/<int:payment_id>', views.retrieve_payment, name='retrieve_payment'),
    path('users/<int:user_id>/payments', views.list_user_payments, name='list_user_payments'),
    #path('payments/<int:payment_id>/refund', views.refund_payment, name='refund_payment'),
    #path('payments/<int:payment_id>/capture', views.capture_funds, name='capture_funds'),
    #path('payments/<int:payment_id>/void', views.void_funds, name='void_funds'),
    #path('payment-methods', views.list_payment_methods, name='list_payment_methods'),
    #path('payment-methods/add-update', views.add_update_payment_method, name='add_update_payment_method'),
    #path('payment-methods/remove/<int:method_id>', views.remove_payment_method, name='remove_payment_method'),
    #path('transactions', views.transaction_history, name='transaction_history'),
    path('exchange-rates', views.exchange_rates, name='exchange_rates'),
    #path('reports', views.reports_and_analytics, name='reports_and_analytics'),
    # Authentication and User Management URLs (Add your user-related URLs here)
]
