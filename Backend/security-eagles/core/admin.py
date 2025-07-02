from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "phone", "city")}),
        (_("Social"), {"fields": ("github", "linkedin", "portfolio_url", "cv_url", "profile_pic")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
        (_("SSO"), {"fields": ("sso_provider", "sso_id")}),
        (_("Extra"), {"fields": ("score", "type", "created_by", "meta_data")}),
    )
    list_display = ("id", "username", "email", "first_name", "last_name", "is_staff", "is_active", "type", "created_at")
    search_fields = ("username", "email", "first_name", "last_name", "sso_id")
    ordering = ("id",)
    autocomplete_fields = ["created_by"]
    readonly_fields = ("created_at", "updated_at")

