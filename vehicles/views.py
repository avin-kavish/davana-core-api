from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_extensions.mixins import DetailSerializerMixin

from adrf.viewsets import ReadOnlyModelViewSet

from vehicles.filters import VehicleFilterSet
from vehicles.models import Vehicle
from vehicles.serializers import VehicleDetailSerializer, VehicleListSerializer


class VehicleViewSet(DetailSerializerMixin, ReadOnlyModelViewSet):
    serializer_class = VehicleListSerializer
    serializer_detail_class = VehicleDetailSerializer
    lookup_field = "short_id"
    pagination_class = None

    filter_backends = [DjangoFilterBackend]
    filterset_class = VehicleFilterSet

    queryset = Vehicle.objects.filter(is_active=True).order_by("-created_at")
    queryset_detail = (
        Vehicle.objects.filter(is_active=True)
        .prefetch_related("photos")
        .order_by("-created_at")
    )
