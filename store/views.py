from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Seller
from .serializers import SellerSerializer
from .pagination import DefaultLimitOffsetPagination


class SellerViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = Seller.objects.select_related("credit").all()
    serializer_class = SellerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            self.queryset = self.queryset.filter(user=user)
        return super().get_queryset()
