from django.contrib import admin
from django.utils.html import format_html
from .models import Certification, UserCertification

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'category', 'difficulty', 'is_pro', 'price',
        'is_active', 'created_by', 'created_at', 'badge_preview'
    ]
    list_filter = ['category', 'difficulty', 'is_pro', 'is_active']
    search_fields = ['name', 'category', 'difficulty']
    readonly_fields = ['badge_preview', 'created_at', 'updated_at']

    def badge_preview(self, obj):
        if obj.badge_pic:
            return format_html('<img src="{}" width="80" height="auto" />', obj.badge_pic.url)
        return "-"
    badge_preview.short_description = "Badge"

@admin.register(UserCertification)
class UserCertificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'certification', 'completion', 'done_at', 'last_attend'
    ]
    list_filter = ['certification', 'done_at']
    search_fields = ['user__username', 'certification__name']