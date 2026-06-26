from rest_framework import serializers

from sellers.models import Seller


def image_url(image_field) -> str | None:
    if not image_field:
        return None
    return image_field.url


class SellerSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Seller
        fields = (
            "id",
            "seller_type",
            "name",
            "logo_url",
            "created_at",
            "phone",
            "location_text",
        )

    def get_logo_url(self, obj: Seller) -> str | None:
        return image_url(obj.logo)
