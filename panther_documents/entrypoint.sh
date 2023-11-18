#!/bin/sh

python3.11 manage.py collectstatic

sh migrate.sh || { echo "Can't resolve migrations" ; exit 2; }

python3.11 manage.py currencies --import=USD --import=EUR
python3.11 manage.py updatecurrencies oxr --base=USD

gunicorn -c gunicorn.py panther_documents.wsgi
