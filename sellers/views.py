from adrf.viewsets import ReadOnlyModelViewSet

from sellers.models import Seller
from sellers.serializers import SellerSerializer


class SellerViewSet(ReadOnlyModelViewSet):
    serializer_class = SellerSerializer
    pagination_class = None
    queryset = Seller.objects.all().order_by("-created_at")
