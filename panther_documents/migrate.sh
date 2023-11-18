#!/bin/bash

python manage.py makemigrations authapp --no-input &&
python manage.py makemigrations mainapp --no-input &&
python manage.py makemigrations paymentapp --no-input &&
python manage.py makemigrations --no-input || { echo "Can't resolve migrations automatically" ; exit 3; }
python manage.py migrate || { echo "Can't migrate" ; exit 1; }

