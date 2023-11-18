from django.urls import path

from authapp.views import ShopUserRegisterView, ShopUserLoginView, office, ShopUserLogoutView, VerifyView

app_name = 'auth'

urlpatterns = [
    path('', office, name='office'),
    path('register/', ShopUserRegisterView.as_view(), name='register'),
    path('verify/', VerifyView.as_view(), name='wait_verify'),
    path('verify/<str:email>/<str:activation_key>/', VerifyView.as_view(), name='verify'),
    path('login/', ShopUserLoginView.as_view(), name='login'),
    path('logout/', ShopUserLogoutView.as_view(), name='logout')
]
