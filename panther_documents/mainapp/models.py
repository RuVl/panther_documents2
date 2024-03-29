import json
from datetime import timedelta

from django.db import models
from django.utils.timezone import now
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from authapp.models import ShopUser
from mainapp.managers import CountryManager
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
            case 'en-us' | None:
                return self.title_en
            case _ as lang:
                raise Exception(f'No translation for {lang} language!')

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
        verbose_name = _('Document type')
        verbose_name_plural = _('Document types')
        ordering = ['country']


class PassportFile(BaseProductItem):
    number = models.CharField(_('Number'), max_length=15, default=None, null=True)

    # Путь был сформирован и отправлен на почту
    path_was_given = models.BooleanField(default=False, blank=True, editable=False)

    is_reserved = models.BooleanField(_('Is reserved'), default=False, blank=True)
    is_sold = models.BooleanField(_('Is sold'), default=False, blank=True)

    passport = models.ForeignKey(Passport, on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to='passports/', unique=True)

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = _('Passport')
        verbose_name_plural = _('Passports')


class Country(models.Model):
    flag = models.CharField(_('Flag'), max_length=30, null=True, default=None)

    title_en = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255)

    objects = CountryManager()

    def get_title(self):
        match get_language():
            case 'ru':
                return self.title_ru
            case 'en-us' | None:
                return self.title_en
            case _:
                raise Exception('No translation for this language!')

    def __str__(self):
        return self.get_title()

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')
