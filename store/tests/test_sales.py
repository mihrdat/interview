import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase as BaseTestCase

from rest_framework import status
from rest_framework.test import APIClient

from model_bakery import baker
from store.models import Sale

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

    def post_sale(self, payload, seller_id):
        url = reverse("seller-sales-list", kwargs={"seller_pk": seller_id})
        return self.client.post(url, payload, content_type="application/json")

    def get_sale(self, seller_id, sale_id):
        url = reverse(
            "seller-sales-detail", kwargs={"seller_pk": seller_id, "pk": sale_id}
        )
        return self.client.get(url)

    def delete_sale(self, seller_id, sale_id):
        url = reverse(
            "seller-sales-detail", kwargs={"seller_pk": seller_id, "pk": sale_id}
        )
        return self.client.delete(url)


class TestCreateSale(TestCase):
    def test_if_user_is_anonymous_returns_401(self):
        payload = {
            "amount": 1000.00,
            "phone_number": "09123456789",
        }

        response = self.post_sale(json.dumps(payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_data_is_invalid_returns_400(self):
        payload = {}
        self.authenticate()

        response = self.post_sale(json.dumps(payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_if_balance_is_insufficient_returns_400(self):
        payload = {
            "amount": 1000.00,
            "phone_number": "09123456789",
        }
        self.authenticate()

        response = self.post_sale(json.dumps(payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_if_data_is_valid_returns_201(self):
        credit = self.user.seller.credit
        credit.balance = 2000.00
        credit.save(update_fields=["balance"])
        payload = {
            "amount": 1000.00,
            "phone_number": "09123456789",
        }
        self.authenticate()

        response = self.post_sale(json.dumps(payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(response.data["id"], 0)

    def test_if_decreases_balance_returns_201(self):
        credit = self.user.seller.credit
        credit.balance = 2000.00
        credit.save(update_fields=["balance"])
        payload = {
            "amount": 1000.00,
            "phone_number": "09123456789",
        }
        self.authenticate()

        response = self.post_sale(json.dumps(payload), self.user.seller.id)
        credit.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(credit.balance, 1000.00)

    def test_if_transaction_log_is_created_returns_201(self):
        credit = self.user.seller.credit
        credit.balance = 2000.00
        credit.save(update_fields=["balance"])
        payload = {
            "amount": 1000.00,
            "phone_number": "09123456789",
        }
        self.authenticate()

        response = self.post_sale(json.dumps(payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(credit.transaction_logs.count(), 0)


class TestRetrieveSale(TestCase):
    def setUp(self):
        super().setUp()
        self.sale = baker.make(Sale, seller=self.user.seller)

    def test_if_user_is_anonymous_returns_401(self):
        sale_id = self.sale.id

        response = self.get_sale(self.user.seller.id, sale_id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_sale_does_not_exists_returns_404(self):
        sale_id = 0
        self.authenticate()

        response = self.get_sale(self.user.seller.id, sale_id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_if_sale_exists_returns_200(self):
        sale_id = self.sale.id
        self.authenticate()

        response = self.get_sale(self.user.seller.id, sale_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], sale_id)


class TestDeleteSale(TestCase):
    def setUp(self):
        super().setUp()
        self.sale = baker.make(Sale, seller=self.user.seller)

    def test_if_user_is_anonymous_returns_401(self):
        sale_id = self.sale.id

        response = self.delete_sale(self.user.seller.id, sale_id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_sale_deletion_not_allowed_returns_405(self):
        sale_id = self.sale.id
        self.authenticate()

        response = self.delete_sale(self.user.seller.id, sale_id)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
