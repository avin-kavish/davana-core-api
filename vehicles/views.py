from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework_extensions.mixins import DetailSerializerMixin

from vehicles.filter_params import build_filter_params, filterset_data
from vehicles.filters import VehicleFilterSet
from vehicles.models import Vehicle, VehicleActivity
from vehicles.pagination import VehicleCursorPagination
from vehicles.serializers import (
    VehicleActivityCreateSerializer,
    VehicleDetailSerializer,
    VehicleListSerializer,
    VehicleSearchSuggestionSerializer,
)
from vehicles.suggestions import vehicle_search_suggestions

from django.shortcuts import get_object_or_404


class VehicleViewSet(DetailSerializerMixin, ReadOnlyModelViewSet):
    serializer_class = VehicleListSerializer
    serializer_detail_class = VehicleDetailSerializer
    lookup_field = "short_id"
    pagination_class = VehicleCursorPagination

    filter_backends = [DjangoFilterBackend]
    filterset_class = VehicleFilterSet

    queryset = (
        Vehicle.objects.filter(is_active=True)
        .select_related("thumbnail")
        .order_by("-created_at", "-pk")
    )
    queryset_detail = (
        Vehicle.objects.filter(is_active=True)
        .select_related("thumbnail")
        .prefetch_related("photos")
        .order_by("-created_at", "-pk")
    )

    def list(self, request, *args, **kwargs):
        filters = build_filter_params(request.query_params)
        queryset = self.get_queryset()
        filterset = self.filterset_class(
            filterset_data(filters),
            queryset=queryset,
            request=request,
        )

        if filterset.is_valid():
            queryset = filterset.qs

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        response = self.get_paginated_response(serializer.data)
        response.data["filters"] = filters
        return response

    @action(detail=False, methods=["get"])
    def suggestions(self, request):
        query = request.query_params.get("q")
        try:
            limit = int(request.query_params.get("limit", 10))
        except (TypeError, ValueError):
            limit = 10
        limit = max(1, min(limit, 25))

        suggestions = vehicle_search_suggestions(query, limit)
        serializer = VehicleSearchSuggestionSerializer(suggestions, many=True)
        return Response(serializer.data)


def get_client_ip(request) -> str | None:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class VehicleActivityViewSet(CreateModelMixin, GenericViewSet):
    authentication_classes = []
    serializer_class = VehicleActivityCreateSerializer
    queryset = VehicleActivity.objects.all()

    def perform_create(self, serializer):
        print(self.kwargs)
        print("here")
        vehicle = get_object_or_404(
            Vehicle,
            short_id=self.kwargs["short_id"],
            is_active=True,
        )
        serializer.save(vehicle=vehicle, ip_address=get_client_ip(self.request))
