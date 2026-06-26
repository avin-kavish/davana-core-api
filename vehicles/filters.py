import django_filters

from vehicles.models import Vehicle


class VehicleFilterSet(django_filters.FilterSet):
    vehicle_type = django_filters.CharFilter(field_name="vehicle_type")
    make = django_filters.CharFilter(method="filter_make")
    model = django_filters.CharFilter(method="filter_model")
    year_from = django_filters.NumberFilter(
        field_name="year_of_manufacture", lookup_expr="gte"
    )
    year_to = django_filters.NumberFilter(
        field_name="year_of_manufacture", lookup_expr="lte"
    )
    price_from = django_filters.NumberFilter(field_name="asking_price", lookup_expr="gte")
    price_to = django_filters.NumberFilter(field_name="asking_price", lookup_expr="lte")
    mileage_from = django_filters.NumberFilter(field_name="mileage_km", lookup_expr="gte")
    mileage_to = django_filters.NumberFilter(field_name="mileage_km", lookup_expr="lte")
    condition = django_filters.CharFilter(field_name="condition")
    registration = django_filters.CharFilter(field_name="registration_status")
    color = django_filters.CharFilter(method="filter_color")
    fuel = django_filters.CharFilter(field_name="fuel_type")
    transmission = django_filters.CharFilter(method="filter_transmission")
    hybrid = django_filters.CharFilter(method="filter_hybrid")

    class Meta:
        model = Vehicle
        fields: list[str] = []

    def filter_make(self, queryset, name, value):
        values = [item.strip() for item in value.split(",") if item.strip()]
        if not values:
            return queryset
        return queryset.filter(make__in=values)

    def filter_model(self, queryset, name, value):
        values = [item.strip() for item in value.split(",") if item.strip()]
        if not values:
            return queryset
        return queryset.filter(model__in=values)

    def filter_color(self, queryset, name, value):
        values = [item.strip() for item in value.split(",") if item.strip()]
        if not values:
            return queryset
        return queryset.filter(exterior_color__in=values)

    def filter_transmission(self, queryset, name, value):
        values = [item.strip() for item in value.split(",") if item.strip()]
        if not values:
            return queryset
        return queryset.filter(transmission__in=values)

    def filter_hybrid(self, queryset, name, value):
        values = [item.strip() for item in value.split(",") if item.strip()]
        if not values:
            return queryset
        return queryset.filter(hybrid_type__in=values)
