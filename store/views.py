from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action

from .models import Seller, Credit, DepositRequest
from .serializers import (
    SellerSerializer,
    CreditSerializer,
    DepositRequestSerializer,
    DepositRequestCreateSerializer,
)
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


class CreditViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Credit.objects.select_related("seller__user").all()
    serializer_class = CreditSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            self.queryset = self.queryset.filter(seller=user.seller)
        return super().get_queryset()


class DepositRequestViewSet(CreateModelMixin, GenericViewSet):
    queryset = DepositRequest.objects.all()
    serializer_class = DepositRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            self.serializer_class = DepositRequestCreateSerializer
        return super().get_serializer_class()
