from rest_framework import serializers
from .models import Seller, Credit


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["id", "user", "first_name", "last_name"]
