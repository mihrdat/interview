import json
from random import randint
from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.login()

    def login(self):
        email = f"user{randint(20, 100)}@example.com"
        password = "123321mmp"

        register_payload = {"email": email, "password": password}
        response = self.client.post("/auth/users", register_payload)
        print(response.error)

        if response.status_code == 201:
            login_payload = {"email": email, "password": password}
            response = self.client.post("/auth/token/login/", json=login_payload)

            if response.status_code == 201:
                self.auth_token = response.json().get("token")
                self.client.headers.update(
                    {"Authorization": f"Token {self.auth_token}"}
                )
            else:
                print(f"Failed to authenticate. Status code: {response.status_code}")
        else:
            print(f"Failed to register user. Status code: {response.status_code}")

    @task(1)
    def view_sales(self):
        seller_id = randint(1, 10)
        self.client.get(
            f"/store/sellers/{seller_id}/sales", name="/store/sellers/:id/sales"
        )

    @task(1)
    def view_sale_detail(self):
        seller_id = randint(1, 10)
        sale_id = randint(1, 10)
        self.client.get(
            f"/store/sellers/{seller_id}/sales/{sale_id}",
            name="/store/sellers/:id/sales/:id",
        )

    @task(10)
    def sale(self):
        seller_id = randint(1, 10)
        self.client.post(
            f"/store/sellers/{seller_id}/sales/",
            name="/store/sellers/:id/sales",
            json={"amount": 1000, "phone_number": "09123456789"},
        )

    # def on_start(self):
    #     for seller_id in range(1, 11):
    #         seller = Seller.objects.get(pk=seller_id)
    #         seller.credit.balance = 1_000_000
    #         seller.credit.save(update_fields=["balance"])
