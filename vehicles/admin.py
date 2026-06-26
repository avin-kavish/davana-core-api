from django.contrib import admin
from django.utils.html import format_html

from vehicles.admin_forms import VehicleAdminForm
from vehicles.models import Vehicle, VehiclePhoto


class VehiclePhotoInline(admin.TabularInline):
    model = VehiclePhoto
    extra = 1
    readonly_fields = ("image_preview",)

    @admin.display(description="Preview")
    def image_preview(self, obj: VehiclePhoto) -> str:
        if not obj.image:
            return "—"
        return format_html(
            '<img src="{}" style="max-height: 60px; max-width: 100px;" />',
            obj.image.url,
        )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    form = VehicleAdminForm
    inlines = [VehiclePhotoInline]
    list_display = ("title", "make", "model", "asking_price", "is_active", "created_at")
    list_filter = (
        "vehicle_type",
        "make",
        "condition",
        "fuel_type",
        "transmission",
        "hybrid_type",
        "registration_status",
        "is_active",
    )
    search_fields = ("title", "short_id", "make", "model")
    readonly_fields = ("short_id", "created_at")


@admin.register(VehiclePhoto)
class VehiclePhotoAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "section", "masonry_position", "carousel_position")
    list_filter = ("section",)
    readonly_fields = ("image_preview",)

    @admin.display(description="Preview")
    def image_preview(self, obj: VehiclePhoto) -> str:
        if not obj.image:
            return "—"
        return format_html(
            '<img src="{}" style="max-height: 80px; max-width: 120px;" />',
            obj.image.url,
        )
