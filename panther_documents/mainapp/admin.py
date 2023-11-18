from django.contrib import admin

from mainapp.models import Passport, Country


@admin.register(Passport)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass
