from captcha.fields import ReCaptchaField
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from mainapp.models import Passport, BaseProduct
from paymentapp.models import Transaction


class BuyProductForm(forms.Form):
    # Union queryset
    queryset: QuerySet[BaseProduct] = Passport.objects.exclude(passportfile__is_sold=True, passportfile__is_reserved=True)

    email = forms.EmailField(label=_('Email'))
    products = forms.JSONField(label=_('Choose products'))  # [{'type': str, 'id': int|str, 'count': int|str}]
    gateway = forms.ChoiceField(
        choices=Transaction.PaymentMethod.choices,
        label=_('Payment method')
    )

    def __init__(self, *, user_email=None, **kwargs):
        super().__init__(**kwargs)

        field = self.fields['products']
        field.widget = field.hidden_widget()

        self.fields['email'].widget.attrs.update({'autocomplete': 'on'})
        if user_email is not None:
            self.fields['email'].widget.attrs.update({'value': user_email, 'autocomplete': 'on'})

    def clean_products(self):
        products_data: list[dict] = self.cleaned_data['products']

        if not products_data:
            raise ValidationError('Should be products to buy', 'empty cart')

        for p in products_data:
            if not p:
                raise ValidationError('Empty product info', 'empty item')

            pk = p.get('id')
            if pk is None:
                raise ValidationError('Not valid id in product provided', 'wrong data')

            product_type = p.get('type')
            if product_type is None or product_type not in BaseProduct.ProductTypes:
                raise ValidationError('Not valid type in product provided', 'wrong data')

            count = p.get('count')
            if count is None:
                raise ValidationError('Not valid count in product provided', 'wrong data')

            try:
                product: BaseProduct = self.queryset.filter(type=product_type, pk=int(pk)).first()
            except:
                raise ValidationError('Not valid data provided')

            if product is None:
                raise ValidationError('No available products in the cart', 'wrong data')

            max_count = product.get_count()
            if max_count < int(count) or int(count) < 1:
                raise ValidationError(f'Not valid count of {product.title_en} (maximum is {max_count})', 'wrong data')

        return products_data


class SendLinksForm(forms.Form):
    email = forms.EmailField()
    captcha = ReCaptchaField()

    transactions: list[Transaction]

    def clean_email(self):
        email = self.cleaned_data['email']
        if not Transaction.objects.filter(email=email).exists():
            raise ValidationError(_('Email not found'), code='not found')

        self.transactions = list(t for t in Transaction.objects.filter(email=email).all() if t.check_if_sold())

        if len(self.transactions) == 0:
            raise ValidationError(_('Not paid'), code='not paid')

        return email
