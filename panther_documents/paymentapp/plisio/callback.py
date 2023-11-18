import hashlib
import hmac
from collections import OrderedDict

from panther_documents.settings import PLISIO_SECRET_KEY


def verify_hash(data: dict) -> bool:
    temp = OrderedDict(sorted(data.items()))
    verify_hash = temp.pop('verify_hash')
    hashed = hmac.new(PLISIO_SECRET_KEY, temp, hashlib.sha1)
    return hashed.hexdigest() == verify_hash
