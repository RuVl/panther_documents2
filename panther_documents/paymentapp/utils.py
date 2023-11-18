import logging
from smtplib import SMTPAuthenticationError

from django.core.mail import send_mail
from django.db import models
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from paymentapp.models import Transaction


logger = logging.getLogger('gunicorn')


# noinspection SpellCheckingInspection
class AllowedCurrencies(models.TextChoices):
    """ All possible currencies for purchase """
    ETH = 'ETH', 'Ethereum'
    BTC = 'BTC', 'Bitcoin'
    LTC = 'LTC', 'Litecoin'
    DASH = 'DASH', 'Dash'
    TZEC = 'TZEC', 'Zcash'
    DOGE = 'DOGE', 'Dogecoin'
    BCH = 'BCH', 'Bitcoin Cash'
    XMR = 'XMR', 'Monero'
    USDT = 'USDT', 'Tether ERC-20'
    USDC = 'USDC', 'USD Coin'
    SHIB = 'SHIB', 'Shiba Inu'
    BTT = 'BTT', 'BitTorrent TRC-20'
    USDT_TRX = 'USDT_TRX', 'Tether TRC-20'
    TRX = 'TRX', 'Tron'
    BNB = 'BNB', 'BNB Chain'
    BUSD = 'BUSD', 'Binance USD BEP-20'
    USDT_BSC = 'USDT_BSC', 'Tether BEP-20'

    USD = 'USD', '$'
    RUB = 'RUB', '₽'


def send_transaction_links(email: str, transactions: list['Transaction'], domain: str, scheme: str) -> bool:
    title = f'Купленные товары на сайте {domain}'
    message = 'Наименование товара - ссылка на скачивание\n'

    for t in transactions:
        if not t.check_if_sold():
            raise Exception("Transaction isn't sold!")

        for i, f in enumerate(t.productfile_set.all()):
            message += f'{i + 1}) {f.title} - {scheme}://{domain}{f.get_download_url()}\n'

    try:
        return send_mail(title, message, None, [email], fail_silently=False)
    except SMTPAuthenticationError as e:
        logger.error(str(e))

    return False  # Что-то не так с отправкой почтой
