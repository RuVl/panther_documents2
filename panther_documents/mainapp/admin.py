from django.contrib import admin

from mainapp.models import Passport, Country, PassportFile


@admin.register(Passport)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'price', 'currency')
    fields = ['number', 'title_en', 'title_ru', 'price', 'currency', 'country']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('flag', '__str__')

    class Media:
        css = {
            'all': ('main/css/admin.css',)
        }


@admin.register(PassportFile)
class PassportFileAdmin(admin.ModelAdmin):
    list_display = ('passport__country', 'passport', '__str__',)
