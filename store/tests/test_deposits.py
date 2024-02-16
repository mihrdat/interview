import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase as BaseTestCase

from rest_framework import status
from rest_framework.test import APIClient

from model_bakery import baker

User = get_user_model()


class TestCase(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = baker.make(User)

    def authenticate(self, is_staff=False):
        if is_staff:
            self.user.is_staff = True
            self.user.save(update_fields=["is_staff"])

        self.client.force_authenticate(self.user)

    def post_deposit(self, payload, seller_id):
        url = reverse("seller-deposits-list", kwargs={"seller_pk": seller_id})
        return self.client.post(url, payload, content_type="application/json")


class TestCreateDeposit(TestCase):
    def test_if_user_is_anonymous_returns_401(self):
        payload = {
            "amount": 1000.00,
        }

        response = self.post_deposit(json.dumps(payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_data_is_invalid_returns_400(self):
        payload = {}
        self.authenticate()

        response = self.post_deposit(json.dumps(payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_if_data_is_valid_returns_201(self):
        payload = {
            "amount": 1000.00,
        }
        self.authenticate()

        response = self.post_deposit(json.dumps(payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(response.data["id"], 0)
