from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from sellers.models import Seller, SellerType

User = get_user_model()


class SellerApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="seller-api",
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

    def test_list_endpoint_returns_sellers(self):
        response = self.client.get(reverse("seller-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        item = response.json()[0]
        self.assertEqual(item["id"], self.seller.pk)
        self.assertEqual(item["name"], "Amitha")
        self.assertEqual(item["phone"], "0773493079")
        self.assertNotIn("owner", item)

    def test_detail_endpoint_returns_seller_profile(self):
        response = self.client.get(
            reverse("seller-detail", kwargs={"pk": self.seller.pk})
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["name"], "Amitha")
        self.assertEqual(payload["location_text"], "Colombo")
        self.assertNotIn("owner", payload)
