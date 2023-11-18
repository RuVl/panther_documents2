import json
import logging
from typing import Union

from currencies.utils import convert
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseBadRequest, HttpRequest, HttpResponse, \
	HttpResponseForbidden, FileResponse
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, TemplateView

from mainapp.models import BaseProduct
from paymentapp import plisio
from paymentapp.forms import BuyProductForm, SendLinksForm
from paymentapp.models import Transaction, ProductFile, in_2_hours, PlisioGateway
from paymentapp.utils import send_transaction_links


logger = logging.getLogger('gunicorn')


# Get -> cart page, post -> JsonResponse
class CartView(FormView):
	form_class = BuyProductForm
	template_name = 'payment/cart_page.html'

	json_params = {'ensure_ascii': False}

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		if self.request.user.is_authenticated:
			kwargs['user_email'] = self.request.user.email
		return kwargs

	def form_valid(self, form):
		""" Create transaction and return JsonResponse with url """
		t = self.create_transaction(self.request.user, form)

		if t is None:
			response = {
				'success': False,
				'clean_cart': False,
				'reload_cart': True,
				'errors': {'cart': [_("Can not create transaction. Try again or write to support.")]},
				'url': self.request.path
			}
			return JsonResponse(response, json_dumps_params=self.json_params)

		self.success_url = t.get_gateway_url()
		response = {
			'success': True,
			'clean_cart': True,
			'reload_cart': False,
			'url': self.success_url
		}
		return JsonResponse(response, json_dumps_params=self.json_params)

	def form_invalid(self, form):
		response = {
			'success': False,
			'errors': form.errors,
			'clean_cart': False,
			'reload_cart': False,
			'url': self.request.path
		}
		return JsonResponse(response, json_dumps_params=self.json_params)

	@staticmethod
	def create_transaction(user, form: BuyProductForm) -> Union[Transaction, None]:
		email, gateway, products = (
			form.cleaned_data['email'],
			form.cleaned_data['gateway'],
			form.cleaned_data['products']
		)

		logger.info(f'Creating transaction for {email} with {gateway} and products: {products}')

		t = Transaction(email=email, gateway=gateway, invoice_price=0)  # invoice_price - for t.save()
		if user.is_authenticated:
			t.user_id = user.id

		reserved: list[tuple[BaseProduct, int]] = []

		try:
			for product in products:
				p: BaseProduct = BaseProduct.get_subclass(product['type']).objects.get(pk=product['id'])
				if not p.reserve(product['count']):  # Резервация товаров
					raise ValueError("Can not reserve")  # Резервация не удалась

				reserved.append((p, product['count']))
		except Exception as e:
			logger.error(str(e))
			for product, count in reserved:
				if not product.cancel_reserve(count):
					logger.warning(f'Failed to cancel reserve for product: {product.type} - {product.id}')

			return None

		t.save()  # Иначе нельзя ProductFile.create_from_base

		for product, count in reserved:
			# Раз нам пофиг кому какие достанутся - будем продавать любые зарезервированные
			for _ in range(count):
				ProductFile.create_from_base(product, t)

			# Считаем итоговую стоимость
			t.invoice_price += convert(product.price, product.currency, t.invoice_currency)

		t.save()

		return t


# Вьюшка для переадресации или вывода ошибки plisio
class PlisioPaymentView(View):
	def get(self, request, *args, **kwargs):
		t_id = kwargs.get('transaction_id')
		t_email = kwargs.get('email')

		if t_id is None:
			return HttpResponseNotFound()

		t: Transaction = Transaction.objects.filter(id=t_id, email=t_email).first()
		if t is None:
			return HttpResponseNotFound()

		if t.gateway != t.PaymentMethod.PLISIO:
			return HttpResponseNotFound()

		if t.check_if_sold():
			return HttpResponseRedirect(reverse_lazy('payment:success-payment'))

		p = self.create_invoice(t)
		if p is None:
			# Произошла ошибка платежного шлюза, попробуйте снова
			return HttpResponseBadRequest()

		t.plisio = p
		t.save()

		return HttpResponseRedirect(p.get_invoice_url())

	@staticmethod
	def create_invoice(transaction: Transaction) -> PlisioGateway | None:
		if transaction.plisio is not None:
			return transaction.plisio

		try:
			response = plisio.create_invoice(
				order_name=f'Transaction-{transaction.id}',
				order_number=str(transaction.id),
				source_amount=str(transaction.invoice_price),
				source_currency=transaction.invoice_currency,
				callback_url=str(reverse('payment:plisio-callback')),
				success_callback_url=str(reverse('payment:plisio-callback')),
				fail_callback_url=str(reverse('payment:plisio-callback')),
				email=transaction.email,
				expire_min=str((in_2_hours() - now()).seconds)
			)
		except plisio.PlisioException as e:
			logger.error(str(e))
			return None

		if response.get('status') == 'success':
			if (data := response.get('data')) is None:
				return None

			if data.get('txn_id') is None or data.get('invoice_url') is None:
				return None

			p = PlisioGateway(txn_id=data.get('txn_id'))
			p.update_fields(data)

			return p

		return None


# Вьюшка для получения статуса транзакции plisio
class PlisioStatus(View):
	# noinspection PyMethodMayBeStatic
	def post(self, request: HttpRequest, *args, **kwargs):
		response: dict = json.loads(request.body)
		if not plisio.verify_hash(response):
			return HttpResponseBadRequest()

		p: PlisioGateway = PlisioGateway.objects.filter(txn_id=response.get('txn_id')).first()
		if p is None:
			return HttpResponseBadRequest()

		if p.handle_callback(response):
			t = p.transaction
			if t.check_if_sold():
				send_transaction_links(t.email, [t], request.get_host(), request.scheme)

			return HttpResponse('ok')

		return HttpResponseBadRequest()


class SuccessPayment(TemplateView):
	template_name = 'payment/success_payment.html'


# Вьюшка для отправки ссылок на скачивание купленных товаров
class SendLinksFormView(FormView):
	form_class = SendLinksForm
	template_name = 'payment/send_links.html'
	success_url = reverse_lazy('main:home')

	def form_valid(self, form):
		domain = self.request.get_host()
		email = form.cleaned_data['email']

		if not send_transaction_links(email, form.transactions, domain, self.request.scheme):
			return self.form_invalid(form)

		return super().form_valid(form)


# Вьюшка для скачивания товаров
class DownloadLinksView(View):
	def get(self, request, *args, **kwargs):
		email = self.kwargs.get('email')
		security_code = self.kwargs.get('security_code')

		if email is None or security_code is None:
			return HttpResponseNotFound()

		try:
			product_info = ProductFile.objects.get(transaction__email=email, security_code=security_code)
		except ProductFile.DoesNotExist:
			return HttpResponseForbidden()

		return FileResponse(open(product_info.product_file.path, 'rb'))
