from django.contrib import admin
from django.utils.html import format_html

from vehicles.admin_forms import VehicleAdminForm, VehiclePhotoInlineForm
from vehicles.models import Vehicle, VehicleActivity, VehiclePhoto


class VehiclePhotoInline(admin.TabularInline):
    model = VehiclePhoto
    form = VehiclePhotoInlineForm
    extra = 1
    fields = (
        "image_preview",
        "image",
        "section",
        "title",
        "masonry_position",
        "carousel_position",
        "description",
    )
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
    list_display = ("display_title", "make", "model", "asking_price", "is_active", "created_at")
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
    search_fields = ("title_suffix", "short_id", "make", "model")
    readonly_fields = ("short_id", "created_at", "display_title")

    @admin.display(description="Title")
    def display_title(self, obj: Vehicle) -> str:
        return obj.title


@admin.register(VehicleActivity)
class VehicleActivityAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "activity_type", "visitor_id", "ip_address", "created_at")
    list_filter = ("activity_type", "created_at")
    search_fields = ("visitor_id", "vehicle__short_id")
    readonly_fields = (
        "vehicle",
        "activity_type",
        "visitor_id",
        "ip_address",
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "created_at",
    )


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
