from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Seller, Credit, DepositRequest

User = get_user_model()


class SellerSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Seller
        fields = ["id", "user", "first_name", "last_name", "balance"]

    def get_balance(self, seller):
        return seller.credit.balance


class CreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credit
        fields = ["id", "seller", "balance"]


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
