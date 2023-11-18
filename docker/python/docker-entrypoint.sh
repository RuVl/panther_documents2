#!/bin/sh

python3.11 manage.py collectstatic

python3.11 manage.py makemigrations
python3.11 manage.py migrate

python3.11 manage.py currencies --import=USD --import=EUR
python3.11 manage.py updatecurrencies oxr --base=USD
