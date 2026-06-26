from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Contact (internal)",
            {"fields": ("phone",)},
        ),
    )
    list_display = ("username", "email", "phone", "is_staff")
