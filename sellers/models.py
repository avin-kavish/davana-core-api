from django.conf import settings
from django.db import models

from users.districts import SriLankaDistrict


class SellerType(models.TextChoices):
    PERSONAL = "personal", "Personal"
    BUSINESS = "business", "Business"


class Seller(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="seller_profile",
    )
    seller_type = models.CharField(max_length=16, choices=SellerType.choices)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="sellers/logos/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=32, blank=True)
    district = models.CharField(
        max_length=32,
        choices=SriLankaDistrict.choices,
        default=SriLankaDistrict.COLOMBO,
    )
    town = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
