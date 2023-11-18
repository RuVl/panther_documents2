from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


def in_24_hours():
    return now() + timedelta(hours=24)


class ShopUser(AbstractUser):
    email = models.EmailField(unique=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    activation_key = models.CharField(max_length=128, blank=True)
    activation_key_expires = models.DateTimeField(default=in_24_hours)

    def is_activation_key_expired(self):
        return self.activation_key_expires <= now() and not self.is_deleted

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
