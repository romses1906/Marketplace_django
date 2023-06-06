from django.urls import path

from payment.views import CreateSessionView, PaymentView, SuccessView, CancelView

app_name = 'payment'


urlpatterns = [
    path('payment/<int:order_id>/', PaymentView.as_view(), name='payment_view'),
    path('create_session/<int:order_id>/', CreateSessionView.as_view(), name='create_session'),
    path('success_pay/<int:order_id>/', SuccessView.as_view(), name='success_pay'),
    path('cancel_pay/<int:order_id>/', CancelView.as_view(), name='cancel_pay'),
]
