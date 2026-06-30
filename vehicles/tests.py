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
from vehicles.filter_params import build_filter_params
from vehicles.filters import VehicleFilterSet
from vehicles.models import Vehicle, VehicleActivity, VehicleActivityType, VehicleCondition, VehiclePhoto, VehicleType
from vehicles.short_id import SHORT_ID_SIZE
from vehicles.suggestions import vehicle_search_suggestions
from vehicles.term_parser import parse_vehicle_term

User = get_user_model()


def make_test_image(name: str = "test.jpg") -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new("RGB", (8, 8), color="red").save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")


def create_vehicle(seller: Seller, **overrides) -> Vehicle:
    data = {
        "title_suffix": "",
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
            asking_price=Decimal("12000000"),
            vehicle_type=VehicleType.SUV,
            model="CR-V",
            year_of_manufacture=2012,
            mileage_km=140000,
        )
        self.assertEqual(vehicle.title, "Honda CR-V 2012")
        self.assertEqual(len(vehicle.short_id), SHORT_ID_SIZE)

    def test_vehicle_short_ids_are_unique(self):
        first = create_vehicle(self.seller, model="First")
        second = create_vehicle(self.seller, model="Second")
        self.assertNotEqual(first.short_id, second.short_id)

    def test_vehicle_photo_filename_includes_short_id(self):
        vehicle = create_vehicle(self.seller, model="CR-V", year_of_manufacture=2012)
        photo = VehiclePhoto.objects.create(
            vehicle=vehicle,
            image=make_test_image("drv-front.jpeg"),
        )
        expected_name = f"vehicles/{vehicle.short_id}/photos/drv-front-{vehicle.short_id}.jpeg"
        self.assertEqual(photo.image.name, expected_name)

    def test_admin_form_accepts_make_outside_suggestions(self):
        form = VehicleAdminForm(
            data={
                "title_suffix": "Limited Edition",
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

class VehicleTermParserTests(TestCase):
    def test_parses_make_and_model(self):
        self.assertEqual(
            parse_vehicle_term("honda civic"),
            {"make": "Honda", "model": "Civic"},
        )

    def test_parses_make_model_and_year(self):
        self.assertEqual(
            parse_vehicle_term("honda civic 2012"),
            {
                "make": "Honda",
                "model": "Civic",
                "year_from": "2012",
                "year_to": "2012",
            },
        )

    def test_parses_multi_word_make(self):
        self.assertEqual(
            parse_vehicle_term("mercedes-benz c-class"),
            {"make": "Mercedes-Benz", "model": "C-Class"},
        )

    def test_unknown_model_is_not_guessed(self):
        self.assertEqual(
            parse_vehicle_term("honda unknownmodel"),
            {"make": "Honda"},
        )

    def test_multi_word_model(self):
        self.assertEqual(
            parse_vehicle_term("toyota land cruiser"),
            {"make": "Toyota", "model": "Land Cruiser"},
        )


class VehicleFilterParamTests(TestCase):
    def test_term_is_zeroed_and_merged_into_filters(self):
        filters = build_filter_params({"term": "honda civic"})
        self.assertIsNone(filters["term"])
        self.assertEqual(filters["make"], "Honda")
        self.assertEqual(filters["model"], "Civic")

    def test_term_replaces_make_model_and_year(self):
        filters = build_filter_params(
            {
                "term": "honda civic",
                "make": "Toyota",
                "model": "Vitz",
                "year_from": "2015",
                "year_to": "2015",
            }
        )
        self.assertIsNone(filters["term"])
        self.assertEqual(filters["make"], "Honda")
        self.assertEqual(filters["model"], "Civic")
        self.assertIsNone(filters["year_from"])
        self.assertIsNone(filters["year_to"])


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
            asking_price=Decimal("1000000"),
            make="Toyota",
            model="Vitz",
            mileage_km=90000,
            location="Kandy",
        )
        self.expensive = create_vehicle(
            self.seller,
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
            features=["Bluetooth", "Reverse Camera"],
        )
        VehiclePhoto.objects.create(
            vehicle=self.vehicle,
            title="Front driver side",
            description="Front view",
            section="Exterior",
            masonry_position=1,
            carousel_position=1,
            image=make_test_image(),
        )
        self.vehicle.thumbnail = self.vehicle.photos.first()
        self.vehicle.save(update_fields=["thumbnail"])

    def test_list_endpoint_returns_vehicle_summary(self):
        response = self.client.get(reverse("vehicle-list"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["results"]), 1)
        self.assertIsNone(payload["next"])
        self.assertIsNone(payload["previous"])
        item = payload["results"][0]
        self.assertEqual(item["short_id"], self.vehicle.short_id)
        self.assertEqual(item["title"], "Honda CR-V 2012")
        self.assertEqual(item["location"], "Colombo")
        self.assertEqual(item["mileage_km"], 140000)
        self.assertTrue(item["thumbnail_url"])

    def test_list_endpoint_parses_term_into_filters(self):
        create_vehicle(
            self.seller,
            model="Civic",
            year_of_manufacture=2015,
            asking_price=Decimal("5000000"),
            mileage_km=80000,
            is_active=True,
        )
        response = self.client.get(reverse("vehicle-list"), {"term": "honda civic"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsNone(payload["filters"]["term"])
        self.assertEqual(payload["filters"]["make"], "Honda")
        self.assertEqual(payload["filters"]["model"], "Civic")
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(payload["results"][0]["title"], "Honda Civic 2015")

    def test_list_endpoint_supports_cursor_pagination(self):
        for index in range(3):
            create_vehicle(
                self.seller,
                model=f"Listed-{index}",
                is_active=True,
            )

        first_page = self.client.get(reverse("vehicle-list"), {"page_size": 2})
        self.assertEqual(first_page.status_code, 200)
        first_payload = first_page.json()
        self.assertEqual(len(first_payload["results"]), 2)
        self.assertIsNotNone(first_payload["next"])

        second_page = self.client.get(first_payload["next"])
        self.assertEqual(second_page.status_code, 200)
        second_payload = second_page.json()
        self.assertGreaterEqual(len(second_payload["results"]), 1)
        first_ids = {item["short_id"] for item in first_payload["results"]}
        second_ids = {item["short_id"] for item in second_payload["results"]}
        self.assertFalse(first_ids & second_ids)

    def test_list_endpoint_returns_empty_filters(self):
        response = self.client.get(reverse("vehicle-list"))
        self.assertIsNone(response.json()["filters"]["term"])

    def test_detail_endpoint_returns_vehicle_without_nested_seller(self):
        response = self.client.get(
            reverse("vehicle-detail", kwargs={"short_id": self.vehicle.short_id})
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["short_id"], self.vehicle.short_id)
        self.assertEqual(payload["seller"], self.seller.pk)
        self.assertEqual(len(payload["photos"]), 1)
        self.assertEqual(payload["photos"][0]["title"], "Front driver side")
        self.assertEqual(payload["photos"][0]["section"], "Exterior")
        self.assertEqual(
            payload["features"],
            [
                {"group": "Entertainment", "items": ["Bluetooth"]},
                {"group": "Safety", "items": ["Reverse Camera"]},
            ],
        )

    def test_inactive_vehicle_not_listed(self):
        self.vehicle.is_active = False
        self.vehicle.save(update_fields=["is_active"])
        response = self.client.get(reverse("vehicle-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])

    def test_suggestions_endpoint_returns_unique_makes_and_make_model_pairs(self):
        create_vehicle(
            self.seller,
            model="Civic",
            year_of_manufacture=2015,
            is_active=True,
        )
        create_vehicle(
            self.seller,
            model="Civic",
            year_of_manufacture=2015,
            is_active=True,
        )
        create_vehicle(
            self.seller,
            model="Fit",
            year_of_manufacture=2010,
            is_active=True,
        )

        response = self.client.get(reverse("vehicle-suggestions"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(
            payload,
            [
                {
                    "phrase": "Honda",
                    "make": "Honda",
                    "model": None,
                    "year": None,
                },
                {
                    "phrase": "Honda CR-V",
                    "make": "Honda",
                    "model": "CR-V",
                    "year": None,
                },
                {
                    "phrase": "Honda Civic",
                    "make": "Honda",
                    "model": "Civic",
                    "year": None,
                },
                {
                    "phrase": "Honda Fit",
                    "make": "Honda",
                    "model": "Fit",
                    "year": None,
                },
            ],
        )

    def test_suggestions_endpoint_filters_by_query(self):
        create_vehicle(
            self.seller,
            model="Civic",
            year_of_manufacture=2015,
            is_active=True,
        )

        response = self.client.get(reverse("vehicle-suggestions"), {"q": "civic"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["phrase"], "Honda Civic")
        self.assertEqual(payload[0]["model"], "Civic")
        self.assertIsNone(payload[0]["year"])

    def test_suggestions_endpoint_excludes_inactive_vehicles(self):
        create_vehicle(
            self.seller,
            model="Civic",
            year_of_manufacture=2015,
            is_active=False,
        )

        response = self.client.get(reverse("vehicle-suggestions"), {"q": "civic"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])


class VehicleSuggestionQueryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="suggestion-seller", password="password")
        self.seller = Seller.objects.create(
            owner=self.user,
            seller_type=SellerType.BUSINESS,
            name="Suggestion Motors",
        )
        create_vehicle(
            self.seller,
            make="Toyota",
            model="Vitz",
            year_of_manufacture=2018,
            is_active=True,
        )
        create_vehicle(
            self.seller,
            make="Honda",
            model="Fit",
            year_of_manufacture=2010,
            is_active=True,
        )

    def test_vehicle_search_suggestions_are_sorted(self):
        suggestions = vehicle_search_suggestions()
        self.assertEqual(
            [item["phrase"] for item in suggestions],
            ["Honda", "Honda Fit", "Toyota", "Toyota Vitz"],
        )


class VehicleSuggestionLimitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="suggestion-limit-seller",
            password="password",
        )
        self.seller = Seller.objects.create(
            owner=self.user,
            seller_type=SellerType.BUSINESS,
            name="Limit Motors",
        )

    def test_vehicle_search_suggestions_limits_each_query_before_merge(self):
        for index in range(12):
            create_vehicle(
                self.seller,
                make=f"Make-{index:02d}",
                model="Shared",
                year_of_manufacture=2010 + index,
                is_active=True,
            )

        suggestions = vehicle_search_suggestions(limit=5)
        self.assertEqual(len(suggestions), 5)
        self.assertEqual(
            [item["phrase"] for item in suggestions],
            [
                "Make-00",
                "Make-00 Shared",
                "Make-01",
                "Make-01 Shared",
                "Make-02",
            ],
        )


class VehicleActivityApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="activity-seller",
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
        self.vehicle = create_vehicle(self.seller, is_active=True)
        self.inactive_vehicle = create_vehicle(
            self.seller, model="Inactive", is_active=False
        )

    def test_create_view_activity(self):
        response = self.client.post(
            reverse(
                "vehicle-activity-list",
                kwargs={"short_id": self.vehicle.short_id},
            ),
            {
                "activity_type": VehicleActivityType.VIEW,
                "visitor_id": "visitor-123",
                "utm_source": "google",
                "utm_medium": "cpc",
            },
            format="json",
            REMOTE_ADDR="203.0.113.10",
        )
        self.assertEqual(response.status_code, 201)
        activity = VehicleActivity.objects.get()
        self.assertEqual(activity.vehicle, self.vehicle)
        self.assertEqual(activity.activity_type, VehicleActivityType.VIEW)
        self.assertEqual(activity.visitor_id, "visitor-123")
        self.assertEqual(activity.ip_address, "203.0.113.10")
        self.assertEqual(activity.utm_source, "google")
        self.assertEqual(activity.utm_medium, "cpc")

    def test_create_call_activity(self):
        response = self.client.post(
            reverse(
                "vehicle-activity-list",
                kwargs={"short_id": self.vehicle.short_id},
            ),
            {
                "activity_type": VehicleActivityType.CALL,
                "visitor_id": "visitor-456",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            VehicleActivity.objects.get().activity_type, VehicleActivityType.CALL
        )

    def test_create_whatsapp_activity(self):
        response = self.client.post(
            reverse(
                "vehicle-activity-list",
                kwargs={"short_id": self.vehicle.short_id},
            ),
            {
                "activity_type": VehicleActivityType.WHATSAPP,
                "visitor_id": "visitor-789",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            VehicleActivity.objects.get().activity_type,
            VehicleActivityType.WHATSAPP,
        )

    def test_create_activity_for_unknown_vehicle_returns_404(self):
        response = self.client.post(
            reverse(
                "vehicle-activity-list",
                kwargs={"short_id": "unknownshort"},
            ),
            {
                "activity_type": VehicleActivityType.VIEW,
                "visitor_id": "visitor-123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(VehicleActivity.objects.count(), 0)

    def test_create_activity_for_inactive_vehicle_returns_404(self):
        response = self.client.post(
            reverse(
                "vehicle-activity-list",
                kwargs={"short_id": self.inactive_vehicle.short_id},
            ),
            {
                "activity_type": VehicleActivityType.VIEW,
                "visitor_id": "visitor-123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(VehicleActivity.objects.count(), 0)

    def test_activity_endpoint_does_not_support_list(self):
        response = self.client.get(
            reverse(
                "vehicle-activity-list",
                kwargs={"short_id": self.vehicle.short_id},
            )
        )
        self.assertEqual(response.status_code, 405)
