from django.contrib import admin

from mainapp.models import Passport, Country, PassportFile


@admin.register(Passport)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'country', 'price', 'currency')
    list_filter = ('country',)

    fields = ['title_en', 'title_ru', 'price', 'currency', 'country']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('flag', '__str__')

    class Media:
        css = {
            'all': ('main/css/admin.css',)
        }


@admin.register(PassportFile)
class PassportFileAdmin(admin.ModelAdmin):
    list_display = ('get_country', 'passport', '__str__',)
    list_filter = ('passport__country',)
    search_fields = ('number',)

    def get_country(self, obj):
        return obj.passport.country
    get_country.short_description = 'Country'
