from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Seller, Credit, Deposit, CreditTransactionLog, Sale
from .serializers import (
    SellerSerializer,
    CreditSerializer,
    DepositSerializer,
    CreditTransactionLogSerializer,
    SaleSerializer,
)
from .pagination import DefaultLimitOffsetPagination


class SellerViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = (
        Seller.objects.select_related("credit")
        .prefetch_related("sales", "credit__deposit_requests")
        .all()
    )
    serializer_class = SellerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            self.queryset = self.queryset.filter(user=user)
        return super().get_queryset()


class SaleViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        return super().get_queryset().filter(seller=self.kwargs["seller_pk"])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["balance"] = self.request.user.seller.credit.balance
        return context


class DepositViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet
):
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        return super().get_queryset().filter(credit__seller=self.kwargs["seller_pk"])


class CreditViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Credit.objects.prefetch_related("transaction_logs").all()
    serializer_class = CreditSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            self.queryset = self.queryset.filter(seller=user.seller)
        return super().get_queryset()


class CreditTransactionLogViewSet(ListModelMixin, GenericViewSet):
    queryset = CreditTransactionLog.objects.all()
    serializer_class = CreditTransactionLogSerializer
    permission_classes = [IsAdminUser]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        return super().get_queryset().filter(credit=self.kwargs["credit_pk"])
