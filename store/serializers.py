from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Seller, Credit, Deposit, CreditTransactionLog, Sale

User = get_user_model()


class SellerSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField(read_only=True)
    total_sales = serializers.SerializerMethodField(read_only=True)
    total_deposits = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Seller
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "balance",
            "total_sales",
            "total_deposits",
        ]

    def get_balance(self, seller):
        return seller.credit.balance

    def get_total_sales(self, seller):
        return sum(sale.amount for sale in seller.sales.all())

    def get_total_deposits(self, seller):
        return sum(
            deposit.amount
            for deposit in seller.credit.deposit_requests.all()
            if deposit.status == "APPROVED"
        )


class CreditTransactionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransactionLog
        fields = ["id", "amount", "type", "created_at"]


class CreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credit
        fields = ["id", "seller", "balance"]


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ["id", "amount", "created_at", "status"]
        read_only_fields = ["credit", "created_at", "status"]

    def create(self, validated_data):
        validated_data["credit"] = self.context["request"].user.seller.credit
        return super().create(validated_data)


class SaleSerializer(serializers.ModelSerializer):
    AMOUNT_CHOICES = [1_000, 2_000, 5_000, 10_000, 20_000, 50_000]
    amount = serializers.ChoiceField(choices=AMOUNT_CHOICES)

    class Meta:
        model = Sale
        fields = ["id", "seller", "amount", "phone_number", "created_at"]
        read_only_fields = ["seller"]

    @transaction.atomic
    def create(self, validated_data):
        seller = self.context["request"].user.seller
        credit = Credit.objects.select_for_update().get(seller=seller)
        amount = validated_data["amount"]

        if amount > credit.balance:
            raise serializers.ValidationError(
                {
                    "amount": [
                        "Insufficient balance.",
                    ]
                }
            )

        credit.balance -= amount
        credit.save(update_fields=["balance"])

        CreditTransactionLog.objects.create(
            credit=credit,
            amount=amount,
            type=CreditTransactionLog.TYPE_SALE,
        )

        validated_data["seller"] = seller
        return super().create(validated_data)
