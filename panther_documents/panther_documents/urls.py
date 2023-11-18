"""panther_documents URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.templatetags.static import static
from django.urls import path, include
from django.views.generic import RedirectView
from django.views.i18n import JavaScriptCatalog

# noinspection SpellCheckingInspection
urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('mainapp.urls', namespace='main')),
    path('', include('paymentapp.urls', namespace='payment')),
    path('office/', include('authapp.urls', namespace='auth')),

    path('favicon.ico', RedirectView.as_view(url=static("favicon.ico"))),

    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name="javascript-catalog"), # No cache

    path('currencies/', include('currencies.urls'))
]
