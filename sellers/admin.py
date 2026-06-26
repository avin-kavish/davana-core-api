from django.contrib import admin
from django.utils.html import format_html

from sellers.models import Seller


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("name", "seller_type", "owner", "phone", "location_text", "created_at")
    list_filter = ("seller_type",)
    search_fields = ("name", "owner__username", "owner__email", "phone")
    readonly_fields = ("created_at", "logo_preview")

    @admin.display(description="Logo")
    def logo_preview(self, obj: Seller) -> str:
        if not obj.logo:
            return "—"
        return format_html(
            '<img src="{}" style="max-height: 80px; max-width: 120px;" />',
            obj.logo.url,
        )
