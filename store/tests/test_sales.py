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

    def list_sale(self, seller_id):
        url = reverse("seller-sales-list", kwargs={"seller_pk": seller_id})
        return self.client.get(url)

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
    def setUp(self):
        super().setUp()
        self.payload = {
            "amount": 1000.00,
            "phone_number": "09123456789",
        }

    def set_credit_balance(self, balance):
        credit = self.user.seller.credit
        credit.balance = balance
        credit.save(update_fields=["balance"])
        return credit

    def test_if_user_is_anonymous_returns_401(self):
        response = self.post_sale(json.dumps(self.payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_data_is_invalid_returns_400(self):
        payload = {}
        self.authenticate()

        response = self.post_sale(json.dumps(payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_if_balance_is_insufficient_returns_400(self):
        self.authenticate()

        response = self.post_sale(json.dumps(self.payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_if_data_is_valid_returns_201(self):
        self.set_credit_balance(2000.00)
        self.authenticate()

        response = self.post_sale(json.dumps(self.payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(response.data["id"], 0)

    def test_if_decreases_balance_returns_201(self):
        credit = self.set_credit_balance(2000.00)
        self.authenticate()

        response = self.post_sale(json.dumps(self.payload), self.user.seller.id)
        credit.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(credit.balance, 1000.00)

    def test_if_transaction_log_is_created_returns_201(self):
        credit = self.set_credit_balance(2000.00)
        self.authenticate()

        response = self.post_sale(json.dumps(self.payload), self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(credit.transaction_logs.count(), 0)


class TestListSale(TestCase):
    def setUp(self):
        self.SALES_COUNT = 10
        super().setUp()

        self.sales = baker.make(
            Sale, seller=self.user.seller, _quantity=self.SALES_COUNT
        )

    def test_if_user_is_anonymous_returns_401(self):
        response = self.list_sale(self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_user_is_admin_returns_200(self):
        self.authenticate(is_staff=True)

        response = self.list_sale(self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_if_user_is_not_owner_returns_403(self):
        another_user = baker.make(User)
        self.client.force_authenticate(another_user)

        response = self.list_sale(self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_if_sales_exists_and_correct_count_returns_200(self):
        self.authenticate()

        response = self.list_sale(self.user.seller.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), self.SALES_COUNT)


class TestRetrieveSale(TestCase):
    def setUp(self):
        super().setUp()
        self.sale = baker.make(Sale, seller=self.user.seller)

    def test_if_user_is_anonymous_returns_401(self):
        sale_id = self.sale.id

        response = self.get_sale(self.user.seller.id, sale_id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_if_user_is_admin_returns_200(self):
        sale_id = self.sale.id
        self.authenticate(is_staff=True)

        response = self.get_sale(self.user.seller.id, sale_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_if_user_is_not_owner_returns_403(self):
        sale_id = self.sale.id
        another_user = baker.make(User)
        self.client.force_authenticate(another_user)

        response = self.get_sale(self.user.seller.id, sale_id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
