from rest_framework_nested import routers
from .views import (
    SellerViewSet,
    CreditViewSet,
    DepositRequestViewSet,
    CreditTransactionLogViewSet,
)

router = routers.DefaultRouter()
router.register("sellers", SellerViewSet)
router.register("credits", CreditViewSet)
router.register("deposit_requests", DepositRequestViewSet)

credit_router = routers.NestedSimpleRouter(router, "credits", lookup="credit")
credit_router.register(
    "transaction_logs", CreditTransactionLogViewSet, basename="credit-transaction-logs"
)

urlpatterns = router.urls + credit_router.urls
