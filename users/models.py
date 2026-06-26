from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=32, blank=True)


    def __str__(self) -> str:
        return self.get_full_name() or self.username
