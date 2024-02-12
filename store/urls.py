from rest_framework_nested import routers
from .views import SellerViewSet, CreditViewSet, DepositRequestViewSet

router = routers.DefaultRouter()
router.register("sellers", SellerViewSet)
router.register("credits", CreditViewSet)
router.register("deposit_requests", DepositRequestViewSet)

urlpatterns = router.urls
