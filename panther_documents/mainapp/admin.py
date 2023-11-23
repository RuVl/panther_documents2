from django.contrib import admin

from mainapp.models import Passport, Country, PassportFile


@admin.register(Passport)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'price', 'currency')


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(PassportFile)
class PassportFileAdmin(admin.ModelAdmin):
    pass
