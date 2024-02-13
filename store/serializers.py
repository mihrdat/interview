from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Seller, Credit, DepositRequest, CreditTransactionLog

User = get_user_model()


class SellerSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Seller
        fields = ["id", "user", "first_name", "last_name", "balance"]

    def get_balance(self, seller):
        return seller.credit.balance


class CreditTransactionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransactionLog
        fields = ["id", "amount", "type", "created_at"]


class CreditSerializer(serializers.ModelSerializer):
    total_sales = serializers.SerializerMethodField(read_only=True)
    total_deposits = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Credit
        fields = ["id", "seller", "balance", "total_deposits", "total_sales"]

    def get_total_sales(self, credit):
        return sum(
            log.amount
            for log in credit.transaction_logs.all()
            if log.type == CreditTransactionLog.TYPE_SALE
        )

    def get_total_deposits(self, credit):
        return sum(
            log.amount
            for log in credit.transaction_logs.all()
            if log.type == CreditTransactionLog.TYPE_DEPOSIT
        )


class DepositRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositRequest
        fields = ["id", "credit", "amount", "status", "created_at", "updated_at"]


class DepositRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositRequest
        fields = ["id", "amount"]

    def create(self, validated_data):
        validated_data["credit"] = self.context["request"].user.seller.credit
        return super().create(validated_data)


class SaleChargeSerializer(serializers.Serializer):
    AMOUNT_CHOICES = [100, 200, 500, 1000]

    amount = serializers.ChoiceField(choices=AMOUNT_CHOICES)
    phone_number = serializers.CharField(max_length=15)

    def validate_amount(self, value):
        balance = self.context["balance"]
        if value > balance:
            raise serializers.ValidationError("Insufficient balance.")
        return value
