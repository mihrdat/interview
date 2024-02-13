from rest_framework_nested import routers
from .views import (
    SellerViewSet,
    CreditViewSet,
    CreditTransactionLogViewSet,
    SaleViewSet,
    DepositViewSet,
)

router = routers.DefaultRouter()
router.register("sellers", SellerViewSet)
router.register("credits", CreditViewSet)

credit_router = routers.NestedSimpleRouter(router, "credits", lookup="credit")
credit_router.register(
    "transaction_logs", CreditTransactionLogViewSet, basename="credit-transaction-logs"
)

seller_router = routers.NestedSimpleRouter(router, "sellers", lookup="seller")
seller_router.register("sales", SaleViewSet, basename="seller-sales")
seller_router.register("deposits", DepositViewSet, basename="seller-deposits")

urlpatterns = router.urls + credit_router.urls + seller_router.urls
