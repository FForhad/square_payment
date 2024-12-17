from django.urls import path
from .views import process_payment, test_payment_view, get_payment_details, list_all_payments

urlpatterns = [
    path('process-payment/', process_payment, name="process_payment"),
    path('test-payment/', test_payment_view, name='test_payment'),
    path('list-all-payments/', list_all_payments, name = 'list_all_payments'),
    path('payment-details/<str:payment_id>/', get_payment_details, name = 'payment_details'),
]
