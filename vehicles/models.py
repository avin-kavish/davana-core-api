from pathlib import Path

from django.db import models

from users.districts import SriLankaDistrict
from sellers.models import Seller
from vehicles.short_id import SHORT_ID_SIZE, generate_vehicle_short_id

from django.contrib.postgres.fields import ArrayField


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
    path = Path(filename)
    short_id = instance.vehicle.short_id
    unique_name = f"{path.stem}-{short_id}{path.suffix}"
    return f"vehicles/{short_id}/photos/{unique_name}"


class Vehicle(models.Model):
    FEATURE_CHOICES = (
        (
            "Safety",
            (
                ("Airbags", "Airbags"),
                ("ABS", "ABS"),
                ("Traction Control", "Traction Control"),
                ("Electronic Stability Control", "Electronic Stability Control"),
                ("Lane Assist", "Lane Assist"),
                ("Lane Departure Warning", "Lane Departure Warning"),
                ("Blind Spot Monitor", "Blind Spot Monitor"),
                ("Forward Collision Warning", "Forward Collision Warning"),
                ("Automatic Emergency Braking", "Automatic Emergency Braking"),
                ("Parking Sensors", "Parking Sensors"),
                ("Reverse Camera", "Reverse Camera"),
                ("360° Camera", "360° Camera"),
                ("Tyre Pressure Monitoring", "Tyre Pressure Monitoring"),
                ("ISOFIX Child Seat Anchors", "ISOFIX Child Seat Anchors"),
                ("Hill Start Assist", "Hill Start Assist"),
                ("Hill Descent Control", "Hill Descent Control"),
            ),
        ),
        (
            "Comfort",
            (
                ("Cruise Control", "Cruise Control"),
                ("Adaptive Cruise Control", "Adaptive Cruise Control"),
                ("Climate Control", "Climate Control"),
                ("Dual Zone Climate Control", "Dual Zone Climate Control"),
                ("Heated Seats", "Heated Seats"),
                ("Ventilated Seats", "Ventilated Seats"),
                ("Memory Seats", "Memory Seats"),
                ("Power Seats", "Power Seats"),
                ("Leather Seats", "Leather Seats"),
                ("Sunroof", "Sunroof"),
                ("Panoramic Roof", "Panoramic Roof"),
                ("Keyless Entry", "Keyless Entry"),
                ("Push Button Start", "Push Button Start"),
                ("Remote Start", "Remote Start"),
            ),
        ),
        (
            "Entertainment",
            (
                ("Bluetooth", "Bluetooth"),
                ("Navigation", "Navigation"),
                ("Radio", "Radio"),
                ("CD Player", "CD Player"),
                ("USB Port", "USB Port"),
                ("Apple CarPlay", "Apple CarPlay"),
                ("Android Auto", "Android Auto"),
                ("Wireless Phone Charging", "Wireless Phone Charging"),
                ("Premium Sound System", "Premium Sound System"),
            ),
        ),
        (
            "Driving",
            (
                ("Paddle Shifters", "Paddle Shifters"),
                ("Sport Mode", "Sport Mode"),
                ("Drive Mode Selector", "Drive Mode Selector"),
                ("Limited Slip Differential", "Limited Slip Differential"),
            ),
        ),
        (
            "Exterior",
            (
                ("Alloy Wheels", "Alloy Wheels"),
                ("Door Visors", "Door Visors"),
            ),
        ),
        (
            "Convenience",
            (
                ("Power Windows", "Power Windows"),
                ("Power Mirrors", "Power Mirrors"),
                ("Auto Dimming Mirror", "Auto Dimming Mirror"),
                ("Rain Sensing Wipers", "Rain Sensing Wipers"),
                ("Auto Headlights", "Auto Headlights"),
                ("Power Tailgate", "Power Tailgate"),
                ("Tow Bar", "Tow Bar"),
                ("Fog Lights", "Fog Lights"),
                ("LED Headlights", "LED Headlights"),
            ),
        ),
    )

    short_id = models.SlugField(max_length=SHORT_ID_SIZE, unique=True, blank=True, editable=False)
    title_suffix = models.CharField(max_length=255, blank=True)
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
    body_type = models.CharField(max_length=64, blank=True)
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

    district = models.CharField(
        max_length=32,
        choices=SriLankaDistrict.choices,
        default=SriLankaDistrict.COLOMBO,
    )
    town = models.CharField(max_length=128)
    
    features =  ArrayField(
        models.CharField(
            choices=FEATURE_CHOICES,
            max_length=100,
            blank=True,
            null=True
        ),
        blank=True,
        null=True
    )

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

    @property
    def title(self) -> str:
        parts = [self.make, self.model, str(self.year_of_manufacture)]
        suffix = self.title_suffix.strip()
        if suffix:
            parts.append(suffix)
        return " ".join(parts)

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = generate_vehicle_short_id()
        super().save(*args, **kwargs)


class VehicleActivityType(models.TextChoices):
    VIEW = "view", "View"
    CALL = "call", "Call"
    WHATSAPP = "whatsapp", "WhatsApp"


class VehicleActivity(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="activities"
    )
    activity_type = models.CharField(max_length=16, choices=VehicleActivityType.choices)
    visitor_id = models.CharField(max_length=64)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    utm_source = models.CharField(max_length=255, blank=True)
    utm_medium = models.CharField(max_length=255, blank=True)
    utm_campaign = models.CharField(max_length=255, blank=True)
    utm_term = models.CharField(max_length=255, blank=True)
    utm_content = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.vehicle.short_id} {self.activity_type} ({self.visitor_id})"


class VehiclePhoto(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="photos"
    )
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    section = models.CharField(max_length=64, blank=True)
    masonry_position = models.PositiveSmallIntegerField(null=True, blank=True)
    carousel_position = models.PositiveSmallIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to=vehicle_photo_upload_to)

    class Meta:
        ordering = ["masonry_position", "carousel_position", "id"]

    def __str__(self) -> str:
        return f"{self.vehicle.title} photo {self.pk}"
