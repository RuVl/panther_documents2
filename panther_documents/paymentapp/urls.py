from django.urls import path

from .views import CartView, SendLinksFormView, DownloadLinksView, PlisioPaymentView, PlisioStatus, SuccessPayment

app_name = 'payment'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('transactions/plisio/<str:email>/<int:transaction_id>/', PlisioPaymentView.as_view(), name='plisio'),
    path('transaction/plisio/status/', PlisioStatus.as_view(), name='plisio-callback'),
    path('success-payment/', SuccessPayment.as_view(), name='success-payment'),
    path('get-files/', SendLinksFormView.as_view(), name='send-links'),
    path('get-file/<str:email>/<str:security_code>/', DownloadLinksView.as_view(), name='download')
]
