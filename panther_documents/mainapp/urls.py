from django.urls import path
from django.views.decorators.cache import cache_page

from .views import PassportListView, SupportView, page_not_found, get_products

app_name = 'main'

urlpatterns = [
    path('', cache_page(60*60)(PassportListView.as_view()), name='home'),
    path('get-products/', get_products, name='get-products'),
    path('support/', cache_page(60*60)(SupportView.as_view()), name='support')
]

# Works only when DEBUG = False
handler404 = page_not_found
