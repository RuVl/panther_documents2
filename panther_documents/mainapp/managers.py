from django.db import models


class ProductManager(models.Manager):
    def reserve(self):
        return super().get_queryset().filter()


class CategoryManager(models.Manager):
    pass
