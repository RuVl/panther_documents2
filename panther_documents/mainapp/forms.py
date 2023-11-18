from django import forms
from django.core.exceptions import ValidationError

from mainapp.models import Passport, BaseProduct


class GetProducts(forms.Form):
	products = forms.JSONField()
	response = {}

	def clean_products(self):
		req = self.cleaned_data['products']

		passports: list[dict] = req.get('passports')
		if passports is not None:
			self.response['passports'] = self._get_data_from_db(Passport, passports)

	@staticmethod
	def _get_data_from_db(model: BaseProduct, products: list[dict]) -> list[dict]:
		id_list = []
		for product in products:
			_id = product.get('id')
			if _id is None or product.get('count') is None:
				continue  # Skip non-valid data

			id_list.append(_id)

		products_qs = model.objects.filter(id__in=id_list).all()

		result = []
		for p in products_qs:
			prod = None
			for product in products:
				if p.id == product.get('id'):
					prod = product
					break

			if prod is None:
				raise ValidationError('Data error, please clear localStorage')

			p_dict = p.to_dict()
			if p_dict:
				result.append(p_dict | {
					'count': max(1, min(prod.get('count'), p_dict.get('max_count')))
				})

		return result
