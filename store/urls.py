from rest_framework_nested import routers
from .views import SellerViewSet, CreditViewSet

router = routers.DefaultRouter()
router.register("sellers", SellerViewSet)
router.register("credits", CreditViewSet)

urlpatterns = router.urls
