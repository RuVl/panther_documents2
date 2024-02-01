import json
from datetime import timedelta

from django.db import models
from django.db.models import Count, Case, When, Value
from django.utils.timezone import now
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from authapp.models import ShopUser
from paymentapp.utils import AllowedCurrencies


def in_24_hours():
    return now() + timedelta(hours=24)


class BaseProductItem(models.Model):
    class Meta:
        abstract = True


class BaseProduct(models.Model):
    class ProductTypes(models.TextChoices):
        PASSPORT = 'PASSPORT', 'passport'

    # Make type non-field in db
    type = models.CharField(choices=ProductTypes.choices, null=True, blank=True, editable=False)

    @staticmethod
    def get_subclass(type_: str) -> 'BaseProduct':
        match type_:
            case BaseProduct.ProductTypes.PASSPORT:
                return Passport
            case _:
                raise ValueError()

    title_en = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255)

    price = models.FloatField()
    currency = models.CharField(choices=AllowedCurrencies.choices, default=AllowedCurrencies.USD)

    def reserve(self, count: int) -> bool:
        raise NotImplementedError()

    def cancel_reserve(self, count: int) -> bool:
        raise NotImplementedError()

    def sell(self) -> bool:
        raise NotImplementedError()

    def get_path(self) -> str:
        raise NotImplementedError()

    def get_count(self) -> int:
        raise NotImplementedError()

    def get_title(self) -> str:
        raise NotImplementedError()

    def to_dict(self) -> dict:
        raise NotImplementedError()

    def to_json(self) -> str:
        raise NotImplementedError()

    class Meta:
        abstract = True


class Passport(BaseProduct):
    type = models.CharField(default=BaseProduct.ProductTypes.PASSPORT, blank=True, editable=False)
    country = models.ForeignKey('Country', on_delete=models.PROTECT)

    def reserve(self, count: int) -> bool:
        """ Reserve any products """

        base_qs = self.passportfile_set.filter(is_reserved=False, is_sold=False)[:count]
        if base_qs.count() < count:
            return False

        self.passportfile_set.filter(pk__in=base_qs).update(is_reserved=True, path_was_given=False)
        return True

    def cancel_reserve(self, count: int = 1) -> bool:
        """ Cancel reserve products """

        base_qs = self.passportfile_set.filter(is_reserved=True, is_sold=False)[:count]
        if base_qs.count() < count:
            return False

        self.passportfile_set.filter(pk__in=base_qs).update(is_reserved=False, path_was_given=False)
        return True

    def sell(self) -> bool:
        """ Sell reserved product """

        f: PassportFile = self.passportfile_set.filter(is_reserved=True, is_sold=False).first()
        if f is None:
            return False

        f.is_sold = True
        f.is_reserved = False
        f.save()

    def get_path(self) -> str:
        """ Get path of reserved product """

        passport_file: PassportFile = self.passportfile_set.filter(path_was_given=False, is_reserved=True, is_sold=False).first()
        if passport_file is None:
            raise Exception('No available files!')

        passport_file.path_was_given = True
        passport_file.save()

        return passport_file.file.path

    def get_count(self) -> int:
        """ Count unreserved products """

        return self.passportfile_set.filter(is_sold=False, is_reserved=False).count()

    def get_title(self):
        match get_language():
            case 'ru':
                return self.title_ru
            case 'en-us':
                return self.title_en
            case _:
                raise Exception('No translation for this language!')

    def to_dict(self) -> dict:
        max_count = self.get_count()
        if max_count < 1:
            return {}

        return {
            "id": self.id,
            "type": self.type,
            "price": self.price,
            "currency": self.currency,
            "max_count": max_count,
            "title": self.get_title(),
            "country": {
                "title": self.country.get_title(),
            }
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True)

    def __str__(self):
        return self.get_title()

    class Meta:
        verbose_name = _('Passport')
        verbose_name_plural = _('Passports')
        ordering = ['country']


class PassportFile(BaseProductItem):
    number = models.IntegerField('Id', default=None, null=True)

    path_was_given = models.BooleanField(default=False, blank=True)

    is_reserved = models.BooleanField(default=False, blank=True)
    is_sold = models.BooleanField(default=False, blank=True)

    passport = models.ForeignKey(Passport, on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to='passports/', unique=True)

    def __str__(self):
        return f'{self.passport.get_title()} - {self.number}'


class Country(models.Model):
    flag = models.CharField(_('Flag'), max_length=30, null=True, default=None)

    title_en = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255)

    def get_title(self):
        match get_language():
            case 'ru':
                return self.title_ru
            case 'en-us':
                return self.title_en
            case _:
                raise Exception('No translation for this language!')

    def __str__(self):
        return self.get_title()

    @staticmethod
    def get_countries_with_passports():
        queryset = (Country.objects.exclude(passport__isnull=True)
                    # .exclude(passport__passportfile__isnull=True)  # Так нельзя - убирает все страны где нет всех товаров
                    # .exclude(passport__passportfile__is_sold=True)
                    # .exclude(passport__passportfile__is_reserved=True)
                    .prefetch_related('passport_set'))

        match get_language():
            case 'ru':
                queryset = queryset.order_by('title_ru')
            case 'en-us':
                queryset = queryset.order_by('title_en')

        for country in queryset:
            passports = country.passport_set.all()
            passports = [passport for passport in passports if passport.get_count() > 0]
            # print(dir(country.passport_set))
            print(passports)
            country.passport_set.set(passports)

        return queryset

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')
