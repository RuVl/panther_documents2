python .\manage.py makemigrations authapp && ^
python .\manage.py makemigrations mainapp && ^
python .\manage.py makemigrations paymentapp && ^
python .\manage.py makemigrations && ^
python .\manage.py migrate
