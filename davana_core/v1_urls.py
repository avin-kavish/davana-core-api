from adrf.routers import DefaultRouter

from sellers.views import SellerViewSet
from vehicles.views import VehicleViewSet

router = DefaultRouter()
router.register("vehicles", VehicleViewSet, basename="vehicle")
router.register("sellers", SellerViewSet, basename="seller")

urlpatterns = router.urls
