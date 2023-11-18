import hashlib
import random
from datetime import timedelta

from django.db import models
from django.urls import reverse_lazy
from django.utils.timezone import now

from authapp.models import ShopUser
from mainapp.models import BaseProduct
from panther_documents import settings
from paymentapp.plisio import get_transaction_details, PlisioException
from paymentapp.utils import AllowedCurrencies


# Max expire period for download files
def in_7_days():
    return now() + timedelta(days=7)


# Max invoice expire period
def in_2_hours():
    return now() + timedelta(hours=2)


class Gateway(models.Model):
    def check_if_sold(self):
        raise NotImplementedError()

    class Meta:
        abstract = True


class Transaction(models.Model):
    class PaymentMethod(models.TextChoices):
        PLISIO = 'PLISIO', 'plisio'

    is_active = models.BooleanField(default=True)
    is_sold = models.BooleanField(default=False)

    email = models.EmailField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    # Цена, которую должны заплатить
    invoice_price = models.FloatField()
    invoice_currency = models.CharField(choices=AllowedCurrencies.choices, default=AllowedCurrencies.USD)

    # Цена, которую заплатили
    paid_price = models.FloatField(blank=True, null=True)
    paid_currency = models.CharField(choices=AllowedCurrencies.choices, null=True, blank=True)

    # What gateway we will use
    gateway = models.CharField(choices=PaymentMethod.choices)

    # Must be one of gateways
    plisio = models.OneToOneField('PlisioGateway', on_delete=models.SET_NULL, null=True, blank=True)

    # Переадресация в зависимости от метода оплаты
    def get_gateway_url(self):
        match self.gateway:
            case self.PaymentMethod.PLISIO:
                return reverse_lazy('payment:plisio', args=(self.email, self.id))
            case _:
                raise NotImplementedError()

    def get_gateway(self):
        match self.gateway:
            case self.PaymentMethod.PLISIO:
                return self.plisio
            case _:
                raise NotImplementedError()

    def check_if_sold(self):
        if self.is_sold:
            return True

        if not self.is_active:
            return False

        match self.gateway:
            case self.PaymentMethod.PLISIO:
                if self.plisio is None:
                    return False
                return self._try_sell(self.plisio)
            case _:
                raise NotImplementedError()

    def _try_sell(self, gateway: Gateway) -> bool:
        if gateway.check_if_sold():
            self.sell()
            return True
        return False

    def sell(self) -> bool:
        self.is_sold = True
        self.is_active = False
        self.save()

        for p in self.productfile_set:
            p.sell()

    # Каждый час запускать очистку занятых товаров
    @staticmethod
    def delete_expired():
        for t in Transaction.objects.filter(is_active=True, is_sold=False).all():
            if t.get_gateway().is_invoice_expired():
                t.is_active = False
                for p in t.productfile_set.all():
                    p.cancel_reserve()

    def __str__(self):
        return f'<Transaction {self.id}, owner {self.email}, is_sold {self.is_sold}>'


class ProductFile(BaseProduct):
    type = models.CharField(choices=BaseProduct.ProductTypes.choices)
    product_id = models.IntegerField()

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    path = models.FilePathField(path=settings.MEDIA_ROOT, max_length=255, unique=True)

    # Для ссылок на скачивание
    security_code = models.CharField(max_length=128, blank=True)
    security_code_expires = models.DateTimeField(default=in_7_days)

    # Помечаем как проданный
    def sell(self) -> bool:
        p: BaseProduct = self.get_subclass(self.type).objects.filter(pk=self.product_id).first()
        if p is not None:
            if not p.sell():
                return False

        return True

    def cancel_reserve(self, _) -> bool:
        p: BaseProduct = self.get_subclass(self.type).objects.filter(pk=self.product_id).first()
        if p is not None:
            if not p.cancel_reserve(1):
                return False

        return True

    def get_path(self):
        return self.path

    def is_security_code_expired(self) -> bool:
        return not self.security_code or self.security_code_expires <= now()

    def get_download_url(self):
        if not self.transaction.is_sold:
            return None

        if self.is_security_code_expired():
            self.security_code_expires = in_7_days()
            salt = hashlib.sha256(str(random.random()).encode('utf8')).hexdigest()
            self.security_code = hashlib.sha256((str(self.pk) + salt).encode('utf8')).hexdigest()
            self.save()

        return reverse_lazy('payment:download', args=[self.transaction.email, self.security_code])

    @staticmethod
    def create_from_base(base: BaseProduct, transaction: Transaction) -> 'ProductFile':
        return ProductFile.objects.create(
            type=base.type,
            product_id=base.pk,
            price=base.price,
            currency=base.currency,
            transaction=transaction,
            path=base.get_path()
        )


class PlisioGateway(Gateway):
    invoice_expire = models.DateTimeField(default=in_2_hours)
    invoice_closed = models.BooleanField(default=False)

    txn_id = models.CharField(max_length=255)

    status = models.CharField(max_length=255, null=True, blank=True)
    invoice_total_sum = models.FloatField(null=True, blank=True)

    # Callback
    amount = models.FloatField(null=True, blank=True)
    currency = models.CharField(choices=AllowedCurrencies.choices, null=True, blank=True)

    # If staged
    source_currency = models.FloatField(null=True, blank=True)
    source_amount = models.FloatField(null=True, blank=True)
    source_rate = models.FloatField(null=True, blank=True)

    # If received callback
    comment = models.CharField(max_length=255, null=True, blank=True)

    invoice_commission = models.FloatField(null=True, blank=True)
    invoice_sum = models.FloatField(null=True, blank=True)

    def check_if_sold(self) -> bool:
        if self.invoice_closed:
            return True
        return self._try_sell()

    def _try_sell(self) -> bool:
        try:
            response = get_transaction_details(self.txn_id)
        except PlisioException:
            return False

        if (data := response.get('data')) is None:
            return False

        if data.get('status') in ['completed', 'mismatch']:
            self.sell()
            self.update_fields(data)
            return True

        return False

    def handle_callback(self, response: dict) -> bool:
        if (data := response.get('data')) is None:
            return False

        if self.invoice_closed:
            return True

        match response.get('status'):
            case 'completed' | 'mismatch':
                self.sell()

            case 'expired':
                if data.get('amount') >= self.invoice_total_sum:
                    self.sell()

        self.update_fields(data)
        return True

    def sell(self) -> bool:
        self.invoice_closed = True
        self.save()

        return self.transaction.sell()

    def update_fields(self, data: dict):
        self.status = data.get('status', self.status)
        self.invoice_total_sum = data.get('invoice_total_sum', self.invoice_total_sum)

        self.amount = data.get('amount', self.amount)
        self.currency = data.get('currency', self.currency)

        self.source_currency = data.get('source_currency', self.source_currency)
        self.source_amount = data.get('source_currency', self.source_amount)
        self.source_rate = data.get('source_currency', self.source_rate)

        self.comment = data.get('comment', self.comment)

        self.invoice_commission = data.get('invoice_commission', self.invoice_commission)
        self.invoice_sum = data.get('invoice_sum', self.invoice_sum)

        self.save()

    def get_invoice_url(self):
        return f'https://plisio.net/invoice/{self.txn_id}'

    def is_invoice_expired(self):
        return self.invoice_expire <= now()
