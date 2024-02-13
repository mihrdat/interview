from django.db import transaction

from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import Seller, Credit, DepositRequest, CreditTransactionLog, Sale
from .serializers import (
    SellerSerializer,
    CreditSerializer,
    DepositRequestSerializer,
    CreditTransactionLogSerializer,
    SaleSerializer,
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
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        return super().get_queryset().filter(credit=self.kwargs["credit_pk"])


class DepositRequestViewSet(CreateModelMixin, GenericViewSet):
    queryset = DepositRequest.objects.all()
    serializer_class = DepositRequestSerializer
    permission_classes = [IsAuthenticated]


class SaleViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        return super().get_queryset().filter(seller=self.kwargs["seller_pk"])

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        credit = request.user.seller.credit
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Charge the customer's phone number
        # ...

        amount = serializer.validated_data["amount"]
        credit.balance -= amount
        credit.save(update_fields=["balance"])

        CreditTransactionLog.objects.create(
            credit=credit,
            amount=amount,
            type=CreditTransactionLog.TYPE_SALE,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["balance"] = self.request.user.seller.credit.balance
        return context
