from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Seller, Credit

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
        read_only_fields = ["balance"]
