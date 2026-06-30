from rest_framework import serializers

from vehicles.feature_groups import group_and_sort_features
from vehicles.models import Vehicle, VehicleActivity, VehiclePhoto


def image_url(image_field) -> str | None:
    if not image_field:
        return None
    return image_field.url



class VehiclePhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = VehiclePhoto
        fields = (
            "title",
            "description",
            "section",
            "masonry_position",
            "carousel_position",
            "image_url",
        )

    def get_image_url(self, obj: VehiclePhoto) -> str:
        return image_url(obj.image) or ""


class VehicleListSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = (
            "short_id",
            "title",
            "asking_price",
            "district",
            "town",
            "mileage_km",
            "thumbnail_url",
            "created_at",
        )

    def get_thumbnail_url(self, obj: Vehicle) -> str | None:
        if not obj.thumbnail_id:
            return None
        return image_url(obj.thumbnail.image)


class VehicleDetailSerializer(serializers.ModelSerializer):
    photos = VehiclePhotoSerializer(many=True, read_only=True)
    seller = serializers.PrimaryKeyRelatedField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = (
            "short_id",
            "title",
            "description",
            "asking_price",
            "district",
            "town",
            "mileage_km",
            "thumbnail_url",
            "created_at",
            "vehicle_type",
            "make",
            "model",
            "trim",
            "model_code",
            "year_of_manufacture",
            "year_of_registration",
            "condition",
            "registration_status",
            "transmission",
            "body_type",
            "fuel_type",
            "hybrid_type",
            "drive_type",
            "engine_code",
            "engine_capacity_cc",
            "exterior_color",
            "interior_color",
            "interior_type",
            "seats",
            "doors",
            "wheel_size_in",
            "tyre_size",
            "features",
            "seller",
            "photos",
        )

    def get_thumbnail_url(self, obj: Vehicle) -> str | None:
        if not obj.thumbnail_id:
            return None
        return image_url(obj.thumbnail.image)

    def get_features(self, obj: Vehicle) -> list[dict[str, list[str] | str]]:
        return group_and_sort_features(obj.features)


class VehicleActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleActivity
        fields = (
            "activity_type",
            "visitor_id",
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
        )
