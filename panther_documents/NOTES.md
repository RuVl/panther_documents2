How to localize text in django
---
> ### Install [gettext](https://stackoverflow.com/questions/35101850/cant-find-msguniq-make-sure-you-have-gnu-gettext-tools-0-15-or-newer-installed)
> #### Add in templates header:
> ```html
> {% load i18n %}
> {% trans 'Some text' %}
> or:
> {% translate 'Some text' %}
>```
> #### Create new folder "locale" in app's folder.
> #### After that collect all text to translate with command:
> ```commandline
> django-admin makemessages -l ru
>```
> #### This command will create in "locale" folder file with all text to translate.
> #### It needs to be translated and after that compile all changes with command:
> ```commandline
> django-admin compilemessages
>```
> #### If you need to switch site language according client language add this line in settings middleware after CommonMiddleware:
> ```python
> 'django.middleware.locale.LocaleMiddleware',
> ```
---
How to make files private
---
> Django is not http server. \
> Web server give files to user when DEBUG = False in settings.py. \
> For this feature check django-sendfile2 repository.
> [StackOverflow](https://stackoverflow.com/a/28167298/15470970)
---
How to add reCAPTCHA
---
> Create site on [reCAPTCHA](https://www.google.com/recaptcha/admin/create). \
> Install django-recaptcha and add 'captcha' to INSTALLED_APPS settings. \
> Add to .env private and public keys. \
> Use field or widget in forms.
---
How to add currency switch
---
> Install lib:
> https://pypi.org/project/django-currencies/ \
> Add SHOP_CURRENCIES and SHOP_DEFAULT_CURRENCY settings. 
---