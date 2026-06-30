from adrf.routers import DefaultRouter

from sellers.views import SellerViewSet
from vehicles.views import VehicleViewSet, VehicleActivityViewSet

router = DefaultRouter()
router.register("vehicles", VehicleViewSet, basename="vehicle")
router.register("sellers", SellerViewSet, basename="seller")
router.register(
    r"vehicles/(?P<short_id>[\w-]+)/activity", 
    VehicleActivityViewSet, 
    basename="vehicle-activity",
)

urlpatterns = [
    *router.urls,
]
