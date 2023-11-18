import requests

from panther_documents.settings import PLISIO_SECRET_KEY
from . import PlisioAPIException, PlisioRequestException

session = requests.Session()
session.headers.update({
	"Content-Type": "application/json",
	"Accept": "application/json",
})


def validate_response(response: requests.Response) -> dict:
	if not 200 <= response.status_code < 300:
		raise PlisioAPIException(response)

	try:
		data: dict = response.json()
	except ValueError as exc:
		raise PlisioRequestException(f"Invalid JSON response: {response.text}") from exc

	return data


def create_invoice(
		order_name: str,
		order_number: str,
		currency=None,
		amount=None,
		source_currency=None,
		source_amount=None,
		allowed_psys_cids=None,
		description=None,
		callback_url=None,
		success_callback_url=None,
		fail_callback_url=None,
		email=None,
		language='en_US',
		redirect_to_invoice=None,
		expire_min=None) -> dict:
	""" https://plisio.net/documentation/endpoints/create-an-invoice """
	data = {
		'order_name': order_name,
		'order_number': order_number,
		'currency': currency,
		'amount': amount,
		'source_currency': source_currency,
		'source_amount': source_amount,
		'allowed_psys_cids': allowed_psys_cids,
		'description': description,
		'callback_url': callback_url,
		'success_callback_url ': success_callback_url,
		'fail_callback_url': fail_callback_url,
		'email': email,
		'language': language,
		'redirect_to_invoice': redirect_to_invoice,
		'api_key': PLISIO_SECRET_KEY,
		'expire_min': expire_min
	}

	response = session.get('https://plisio.net/api/v1/invoices/new', params=data)
	return validate_response(response)


def get_transaction_details(txn_id: str) -> dict:
	response = session.get(f'https://plisio.net/api/v1/operations/{txn_id}', params={'api_key': PLISIO_SECRET_KEY})
	return validate_response(response)
