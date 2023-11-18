#!/bin/sh

python3.11 manage.py makemigrations authapp --no-input &&
python3.11 manage.py makemigrations mainapp --no-input &&
python3.11 manage.py makemigrations paymentapp --no-input &&
python3.11 manage.py makemigrations --no-input || { echo "Can't resolve migrations automatically" ; exit 3; }
python3.11 manage.py migrate || { echo "Can't migrate" ; exit 1; }
