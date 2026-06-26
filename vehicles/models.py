from django.db import models

from sellers.models import Seller
from vehicles.short_id import SHORT_ID_SIZE, generate_vehicle_short_id


class VehicleType(models.TextChoices):
    CAR = "car", "Car"
    VAN = "van", "Van"
    SUV = "suv", "SUV/4x4"


class VehicleCondition(models.TextChoices):
    BRAND_NEW = "brand-new", "Brand new"
    USED = "used", "Used"
    RECONDITIONED = "reconditioned", "Reconditioned"


class RegistrationStatus(models.TextChoices):
    REGISTERED = "registered", "Registered"
    UNREGISTERED = "unregistered", "Unregistered"


class FuelType(models.TextChoices):
    PETROL = "petrol", "Petrol"
    DIESEL = "diesel", "Diesel"
    ELECTRIC = "electric", "Electric"


class TransmissionType(models.TextChoices):
    AUTO = "auto", "Automatic"
    MANUAL = "manual", "Manual"
    TRIPTRONIC = "triptronic", "Triptronic"


class HybridType(models.TextChoices):
    NONE = "none", "None"
    HYBRID = "hybrid", "Hybrid"
    PLUG_IN = "plug-in", "Plug-in hybrid"

class DriveType(models.TextChoices):
    FWD = "fwd", "Front-wheel drive"
    RWD = "rwd", "Rear-wheel drive"
    AWD = "awd", "All-wheel drive"
    FOURBY = "4x4", "4x4"

def vehicle_photo_upload_to(instance: "VehiclePhoto", filename: str) -> str:
    return f"vehicles/{instance.vehicle_id}/photos/{filename}"


class Vehicle(models.Model):
    short_id = models.SlugField(max_length=SHORT_ID_SIZE, unique=True, blank=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    asking_price = models.DecimalField(max_digits=12, decimal_places=2)

    vehicle_type = models.CharField(max_length=16, choices=VehicleType.choices)
    make = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    trim = models.CharField(max_length=64, blank=True)
    model_code = models.CharField(max_length=64, blank=True)

    year_of_manufacture = models.PositiveSmallIntegerField()
    year_of_registration = models.PositiveSmallIntegerField(null=True, blank=True)
    condition = models.CharField(max_length=16, choices=VehicleCondition.choices)
    registration_status = models.CharField(
        max_length=16, choices=RegistrationStatus.choices
    )

    transmission = models.CharField(max_length=16, choices=TransmissionType.choices)
    body_type = models.CharField(max_length=64)
    fuel_type = models.CharField(max_length=16, choices=FuelType.choices)
    hybrid_type = models.CharField(
        max_length=16, choices=HybridType.choices, default=HybridType.NONE
    )
    drive_type = models.CharField(max_length=8, choices=DriveType.choices, blank=True)

    engine_code = models.CharField(max_length=64, blank=True)
    engine_capacity_cc = models.PositiveIntegerField(null=True, blank=True)

    exterior_color = models.CharField(max_length=64, blank=True)
    interior_color = models.CharField(max_length=64, blank=True)
    interior_type = models.CharField(max_length=64, blank=True)

    mileage_km = models.PositiveIntegerField()
    seats = models.PositiveSmallIntegerField(null=True, blank=True)
    doors = models.PositiveSmallIntegerField(null=True, blank=True)
    wheel_size_in = models.PositiveSmallIntegerField(null=True, blank=True)
    tyre_size = models.CharField(max_length=32, blank=True)

    location = models.CharField(max_length=128)
    features = models.JSONField(default=list, blank=True)

    seller = models.ForeignKey(
        Seller, on_delete=models.CASCADE, related_name="vehicles"
    )

    thumbnail = models.ForeignKey(
        "VehiclePhoto", 
        on_delete=models.SET_NULL, 
        related_name="+", 
        null=True, 
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = generate_vehicle_short_id()
        super().save(*args, **kwargs)


class VehiclePhoto(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="photos"
    )
    description = models.TextField(blank=True)
    section = models.CharField(max_length=64, blank=True)
    masonry_position = models.PositiveSmallIntegerField(null=True, blank=True)
    carousel_position = models.PositiveSmallIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to=vehicle_photo_upload_to)

    class Meta:
        ordering = ["masonry_position", "carousel_position", "id"]

    def __str__(self) -> str:
        return f"{self.vehicle.title} photo {self.pk}"
