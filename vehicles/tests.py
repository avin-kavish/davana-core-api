from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient

from sellers.models import Seller, SellerType
from vehicles.admin_forms import VehicleAdminForm
from vehicles.filters import VehicleFilterSet
from vehicles.models import Vehicle, VehicleCondition, VehiclePhoto, VehicleType
from vehicles.short_id import SHORT_ID_SIZE

User = get_user_model()


def make_test_image(name: str = "test.jpg") -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new("RGB", (8, 8), color="red").save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")


def create_vehicle(seller: Seller, **overrides) -> Vehicle:
    data = {
        "title": "Test Vehicle",
        "asking_price": Decimal("1000000"),
        "vehicle_type": VehicleType.CAR,
        "make": "Honda",
        "model": "Fit",
        "year_of_manufacture": 2010,
        "condition": VehicleCondition.USED,
        "registration_status": "registered",
        "transmission": "auto",
        "body_type": "Hatchback",
        "fuel_type": "petrol",
        "mileage_km": 100000,
        "location": "Colombo",
        "seller": seller,
    }
    data.update(overrides)
    return Vehicle.objects.create(**data)


class VehicleModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="seller1",
            password="password",
            phone="0112000000",
        )
        self.seller = Seller.objects.create(
            owner=self.user,
            seller_type=SellerType.PERSONAL,
            name="Amitha",
            phone="0773493079",
            location_text="Colombo",
        )

    def test_vehicle_short_id_is_generated_on_save(self):
        vehicle = create_vehicle(
            self.seller,
            title="Honda CR-V 2012",
            asking_price=Decimal("12000000"),
            vehicle_type=VehicleType.SUV,
            model="CR-V",
            year_of_manufacture=2012,
            mileage_km=140000,
        )
        self.assertEqual(len(vehicle.short_id), SHORT_ID_SIZE)

    def test_vehicle_short_ids_are_unique(self):
        first = create_vehicle(self.seller, title="First")
        second = create_vehicle(self.seller, title="Second")
        self.assertNotEqual(first.short_id, second.short_id)

    def test_admin_form_accepts_make_outside_suggestions(self):
        form = VehicleAdminForm(
            data={
                "title": "Custom Make Car",
                "asking_price": "1000000",
                "vehicle_type": VehicleType.CAR,
                "make": "Tata",
                "model": "Nano",
                "year_of_manufacture": 2015,
                "condition": VehicleCondition.USED,
                "registration_status": "registered",
                "transmission": "manual",
                "body_type": "Hatchback",
                "fuel_type": "petrol",
                "hybrid_type": "none",
                "mileage_km": 50000,
                "location": "Colombo",
                "seller": self.seller.pk,
                "features": "[]",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)


class VehicleFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller2", password="password")
        self.seller = Seller.objects.create(
            owner=self.user,
            seller_type=SellerType.BUSINESS,
            name="Dis Motor Traders",
        )
        self.cheap = create_vehicle(
            self.seller,
            title="Cheap Car",
            asking_price=Decimal("1000000"),
            make="Toyota",
            model="Vitz",
            mileage_km=90000,
            location="Kandy",
        )
        self.expensive = create_vehicle(
            self.seller,
            title="Expensive Car",
            asking_price=Decimal("12000000"),
            vehicle_type=VehicleType.SUV,
            model="CR-V",
            year_of_manufacture=2018,
            mileage_km=50000,
        )

    def test_price_range_filter(self):
        filterset = VehicleFilterSet(
            {"price_from": "5000000", "price_to": "15000000"},
            queryset=Vehicle.objects.all(),
        )
        self.assertTrue(filterset.is_valid())
        results = list(filterset.qs)
        self.assertEqual(results, [self.expensive])


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": "media"},
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
)
class VehicleApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="api-seller",
            password="password",
            phone="0112000000",
        )
        self.seller = Seller.objects.create(
            owner=self.user,
            seller_type=SellerType.PERSONAL,
            name="Amitha",
            phone="0773493079",
            location_text="Colombo",
        )
        self.vehicle = create_vehicle(
            self.seller,
            title="Honda CR-V 2012",
            description="Well maintained SUV.",
            asking_price=Decimal("12000000"),
            vehicle_type=VehicleType.SUV,
            model="CR-V",
            trim="EX-L",
            model_code="RM4",
            year_of_manufacture=2012,
            year_of_registration=2015,
            hybrid_type="none",
            drive_type="Front-wheel drive",
            engine_code="R20A",
            engine_capacity_cc=1997,
            exterior_color="Grey",
            interior_color="Black",
            interior_type="Fabric",
            mileage_km=140000,
            seats=5,
            doors=5,
            wheel_size_in=17,
            tyre_size="225/55 R17",
            is_active=True,
            features=["Bluetooth", "Reverse camera"],
        )
        VehiclePhoto.objects.create(
            vehicle=self.vehicle,
            description="Front view",
            section="Exterior",
            masonry_position=1,
            carousel_position=1,
            image=make_test_image(),
        )

    def test_list_endpoint_returns_vehicle_summary(self):
        response = self.client.get(reverse("vehicle-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        item = response.json()[0]
        self.assertEqual(item["short_id"], self.vehicle.short_id)
        self.assertEqual(item["title"], "Honda CR-V 2012")
        self.assertEqual(item["location"], "Colombo")
        self.assertEqual(item["mileage_km"], 140000)
        self.assertTrue(item["primary_photo_url"])

    def test_detail_endpoint_returns_vehicle_without_nested_seller(self):
        response = self.client.get(
            reverse("vehicle-detail", kwargs={"short_id": self.vehicle.short_id})
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["short_id"], self.vehicle.short_id)
        self.assertEqual(payload["seller"], self.seller.pk)
        self.assertEqual(len(payload["photos"]), 1)
        self.assertEqual(payload["features"], ["Bluetooth", "Reverse camera"])

    def test_inactive_vehicle_not_listed(self):
        self.vehicle.is_active = False
        self.vehicle.save(update_fields=["is_active"])
        response = self.client.get(reverse("vehicle-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
