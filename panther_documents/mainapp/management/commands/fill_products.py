from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from mainapp.models import Passport, Country, PassportFile
from ._utils import load_from_json


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = load_from_json('passports.json')
        Passport.objects.all().delete()
        Country.objects.all().delete()

        for country_title, passports in data.items():
            c = Country.objects.create(
                title_en=country_title,
                title_ru=country_title
            )

            for passport in passports:
                p = Passport.objects.create(
                    type=Passport.ProductTypes.PASSPORT,
                    title_en=passport['title'],
                    title_ru=passport['title'],
                    price=float(passport['usd_cost']),
                    currency='USD',
                    country=c
                )

                for i in range(int(passport['count'])):
                    f = PassportFile(passport=p)
                    f.file.save(f'test/{p.id}_{i}.txt', ContentFile(f"TEST FILE {i}"))
                    f.save()
