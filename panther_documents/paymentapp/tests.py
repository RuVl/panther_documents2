from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from mainapp.models import Passport, Country, PassportFile
from paymentapp.forms import BuyProductForm
from paymentapp.utils import AllowedCurrencies


class CartFormTest(TestCase):
	def test_form(self):
		self.fill_db()
		form_data = {
			'email': 'lala@ru.co',
			'gateway': 'PLISIO',
			'products': [{
				'type': 'PASSPORT',
				'id': 1,
				'count': 9
			}]
		}
		form = BuyProductForm(data=form_data, user_email='ex@m.com')
		self.assertTrue(form.is_valid(), msg=form.errors)

	# noinspection DuplicatedCode
	@staticmethod
	def fill_db():
		c1 = Country.objects.create(title_en='USA', title_ru='США')
		c1_p1 = Passport.objects.create(title_en='ID Cart', title_ru='ID карта', country=c1, price=10, currency=AllowedCurrencies.USD)
		c1_p2 = Passport.objects.create(title_en='Passport', title_ru='Паспорт', country=c1, price=15, currency=AllowedCurrencies.USD)

		for i in range(10):
			PassportFile.objects.create(passport=c1_p1, file=SimpleUploadedFile(str(i), b'LALA-lala'))

		c1_p1.reserve(5)

		for i in range(7):
			PassportFile.objects.create(passport=c1_p2, file=SimpleUploadedFile(str(i), b'LALA-lala'))

		c2 = Country.objects.create(title_en='Russia', title_ru='Россия')
		c2_p1 = Passport.objects.create(title_en='ID Cart', title_ru='ID карта', country=c2, price=10, currency=AllowedCurrencies.USD)
		c2_p2 = Passport.objects.create(title_en='Passport', title_ru='Паспорт', country=c2, price=15, currency=AllowedCurrencies.USD)

		for i in range(15):
			PassportFile.objects.create(passport=c2_p1, file=SimpleUploadedFile(str(i), b'LALA-lala'))

		for i in range(20):
			PassportFile.objects.create(passport=c2_p2, file=SimpleUploadedFile(str(i), b'LALA-lala'))
