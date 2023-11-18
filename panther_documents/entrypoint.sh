#!/bin/sh

python3.11 manage.py collectstatic --noinput

sh migrate.sh

python3.11 manage.py currencies --import=USD --import=RUB
python3.11 manage.py updatecurrencies oxr --base=USD

gunicorn -c gunicorn.py panther_documents.wsgi
