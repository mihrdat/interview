from rest_framework_nested import routers
from .views import (
    SellerViewSet,
    CreditViewSet,
    DepositRequestViewSet,
    CreditTransactionLogViewSet,
    SaleViewSet,
)

router = routers.DefaultRouter()
router.register("sellers", SellerViewSet)
router.register("credits", CreditViewSet)
router.register("deposit_requests", DepositRequestViewSet)

credit_router = routers.NestedSimpleRouter(router, "credits", lookup="credit")
credit_router.register(
    "transaction_logs", CreditTransactionLogViewSet, basename="credit-transaction-logs"
)

seller_router = routers.NestedSimpleRouter(router, "sellers", lookup="seller")
seller_router.register("sales", SaleViewSet, basename="seller-sales")

urlpatterns = router.urls + credit_router.urls + seller_router.urls
