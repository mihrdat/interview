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

from .models import Seller, Credit, DepositRequest, CreditTransactionLog
from .serializers import (
    SellerSerializer,
    CreditSerializer,
    DepositRequestSerializer,
    DepositRequestCreateSerializer,
    SaleChargeSerializer,
    CreditTransactionLogSerializer,
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

    @transaction.atomic
    @action(methods=["POST"], detail=False)
    def sale_charge(self, request, *args, **kwargs):
        seller = request.user.seller
        credit = seller.credit
        serializer = SaleChargeSerializer(
            data=request.data, context={"balance": credit.balance}
        )
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data["amount"]

        phone_number = serializer.validated_data["phone_number"]
        # Charge the customer's phone number
        # ...

        credit.balance -= amount
        credit.save(update_fields=["balance"])

        CreditTransactionLog.objects.create(
            credit=credit,
            amount=amount,
            type=CreditTransactionLog.TYPE_SALE,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action == "sale_charge":
            self.serializer_class = SaleChargeSerializer
        return super().get_serializer_class()


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

    def get_serializer_class(self):
        if self.action == "create":
            self.serializer_class = DepositRequestCreateSerializer
        return super().get_serializer_class()
