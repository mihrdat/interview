from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=55, blank=True, null=True)
    last_name = models.CharField(max_length=55, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Credit(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)


class CreditTransactionLog(models.Model):
    TYPE_DEPOSIT = "DEPOSIT"
    TYPE_SALE = "SALE"

    TYPE_CHOICES = [
        (TYPE_DEPOSIT, "Deposit"),
        (TYPE_SALE, "Sale"),
    ]

    credit = models.ForeignKey(
        Credit, on_delete=models.CASCADE, related_name="transaction_logs"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


class DepositRequest(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    credit = models.ForeignKey(
        Credit, on_delete=models.CASCADE, related_name="deposit_requests"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Sale(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
