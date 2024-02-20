from django.db import models
from django.utils.translation import get_language


class ProductManager(models.Manager):
    def reserve(self):
        return super().get_queryset().filter()


class CategoryManager(models.Manager):
    pass


class CountryManager(models.Manager):
    def get_queryset(self):
        match get_language():
            case 'ru':
                return super().get_queryset().order_by('title_ru')
            case 'en-us' | None:
                return super().get_queryset().order_by('title_en')

    def get_available_countries_with_passports(self):
        queryset = super().get_queryset().prefetch_related('passport_set')

        for country in queryset:
            country.passports = [passport for passport in country.passport_set.all() if passport.get_count() > 0]

        result = [country for country in queryset if country.passports]
        return result
