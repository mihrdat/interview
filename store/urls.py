from rest_framework_nested import routers
from .views import SellerViewSet

router = routers.DefaultRouter()
router.register("sellers", SellerViewSet)

urlpatterns = router.urls
